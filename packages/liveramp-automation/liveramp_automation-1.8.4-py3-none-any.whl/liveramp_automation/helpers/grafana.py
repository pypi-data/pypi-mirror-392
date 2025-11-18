import json
import copy
import multiprocessing
from typing import Dict, Any, Optional
import threading
import traceback
import uuid
import queue
import inspect
import os

from liveramp_automation.utils.allure import allure_attach_json, allure_attach_text
from playwright.sync_api import sync_playwright, Response
from liveramp_automation.utils.log import Logger

from typing import Any


class GrafanaAuthenticationError(Exception):
    """Custom exception for Grafana authentication failures."""
    pass


class GrafanaAPIError(Exception):
    """Custom exception for Grafana API failures."""
    pass


class _GrafanaWorker:
    """
    Internal class to be run in a separate process.
    It contains the original, synchronous Playwright logic.
    """

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str,
        headless: bool,
        timeout: int,
        cmd_queue: multiprocessing.Queue,
        res_queue: multiprocessing.Queue,
    ):
        self._username = username
        self._password = password
        self._base_url = base_url
        self._headless = headless
        self._timeout = timeout
        self._cmd_queue = cmd_queue
        self._res_queue = res_queue
        self._p = None
        self._browser = None
        self._context = None
        self._page = None
        self._login_url = f"{self._base_url}/login"
        self._api_url = f"{self._base_url}/api/ds/query"
        self._is_authenticated = False
        self._reports_dir = os.path.join(os.getcwd(), "reports", "grafana")

    def _cleanup(self):
        # Stop and export trace before closing context
        if self._context:
            try:
                trace_path = os.path.join(self._reports_dir, "trace.zip")
                self._context.tracing.stop(path=trace_path)
                Logger.info(f"Trace exported to {trace_path}")
            except Exception as e:
                Logger.warning(f"Error exporting trace: {e}")
        
        resources = [
            (self._page, "close"),
            (self._context, "close"),
            (self._browser, "close"),
            (self._p, "stop"),
        ]
        for resource, method_name in resources:
            if resource:
                try:
                    getattr(resource, method_name)()
                except Exception as e:
                    Logger.warning(f"Error during cleanup of {resource.__class__.__name__}: {e}")

    def _authenticate(self):
        Logger.debug("Starting authentication...")
        self._page.goto(self._login_url, timeout=self._timeout)
        self._page.wait_for_load_state("networkidle", timeout=self._timeout)
        login_button = self._page.get_by_role("link", name="Sign in with Grafana.com")
        login_button.click()
        username_field = self._page.get_by_role("textbox", name="Email or username")
        username_field.fill(self._username)
        next_button = self._page.get_by_role("button", name="Sign In")
        next_button.click()
        password_field = self._page.get_by_role("textbox", name="Password")
        password_field.fill(self._password)
        submit_button = self._page.get_by_role("button", name="Sign In")
        submit_button.click()
        self._page.wait_for_url("**/home", timeout=30000)
        self._is_authenticated = True
        Logger.info("Authentication successful!")

    def run(self):
        """Main method for the worker process."""
        try:
            Logger.info("Initializing Playwright in worker process...")
            
            # Create reports directory if it doesn't exist
            os.makedirs(self._reports_dir, exist_ok=True)
            Logger.info(f"Reports directory: {self._reports_dir}")
            
            self._p = sync_playwright().start()
            self._browser = self._p.chromium.launch(
                headless=self._headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                ],
            )
            
            # Enable video recording and tracing
            self._context = self._browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_video_dir=self._reports_dir,
                record_video_size={"width": 1920, "height": 1080},
            )
            
            # Start tracing
            self._context.tracing.start(
                screenshots=True,
                snapshots=True,
                sources=True,
            )
            Logger.info("Tracing started for Grafana authentication")
            
            self._page = self._context.new_page()
            self._authenticate()
            
            # Signal the main process that initialization is complete
            self._res_queue.put({"status": "ready"})

            # Main loop to listen for commands
            while True:
                command = self._cmd_queue.get()
                if command["action"] == "exit":
                    break
                
                method_name = command["action"]
                args = command.get("args", {})
                request_id = command.get("request_id")

                try:
                    method_to_call = getattr(self, method_name)
                    result = method_to_call(**args)
                    self._res_queue.put({"status": "success", "data": result, "request_id": request_id})
                except Exception as e:
                    self._res_queue.put({
                        "status": "error",
                        "message": str(e),
                        "traceback": traceback.format_exc(),
                        "request_id": request_id,
                    })

        except Exception as e:
            try:
                self._res_queue.put({
                    "status": "error",
                    "message": f"Initialization failed: {e}",
                    "traceback": traceback.format_exc(),
                })
            except Exception:
                # If even reporting fails, just proceed to cleanup
                pass
        finally:
            self._cleanup()


    def query_loki(self, payload: dict, from_timestamp: str = None, to_timestamp: str = None) -> Dict[str, Any]:
        """Query Grafana Loki API endpoint with request/response details attached to Allure report.
        
        This method sends a POST request to the Grafana Loki datasource API endpoint. All request
        details (URL, headers, params, payload) and response details (status, body) are automatically
        attached to the Allure test report for debugging and traceability.
        
        Args:
            payload: Loki query payload dictionary. Must contain the query structure expected by
                    Grafana's Loki datasource API. Common fields include:
                    - queries: List of query objects with refId, expr, queryType, etc.
                    - from: Start timestamp (milliseconds, optional if from_timestamp provided)
                    - to: End timestamp (milliseconds, optional if to_timestamp provided)
            from_timestamp: Optional override for the 'from' timestamp in milliseconds.
                          If provided, will override any 'from' field in the payload.
            to_timestamp: Optional override for the 'to' timestamp in milliseconds.
                        If provided, will override any 'to' field in the payload.
        
        Returns:
            Dict[str, Any]: Parsed JSON response from the Grafana/Loki API. The response structure
                           depends on the query type but typically contains:
                           - results: Query results with data frames
                           - status: Response status information
        
        Raises:
            GrafanaAPIError: If the client is not authenticated, the API call fails, the response
                           status is not OK, or the response cannot be parsed as JSON.
        
        Example:
            >>> payload = {
            ...     "queries": [{
            ...         "refId": "A",
            ...         "expr": '{job="varlogs"}',
            ...         "queryType": "range",
            ...         "datasource": {"type": "loki", "uid": "grafanacloud-logs"}
            ...     }],
            ...     "from": "1609459200000",
            ...     "to": "1609545600000"
            ... }
            >>> result = worker.query_loki(payload)
            >>> print(result["results"]["A"]["frames"])
        """
        if not self._is_authenticated:
            raise GrafanaAPIError("Client not authenticated.")

        # 1. Prepare request data
        payload = copy.deepcopy(payload)
        if from_timestamp:
            payload["from"] = from_timestamp
        if to_timestamp:
            payload["to"] = to_timestamp
        
        headers = {"content-type": "application/json"}
        params = {"ds_type": "loki"}

        # 2. Attach all request details (they are known before the call)
        allure_attach_text("Grafana API URL", self._api_url)
        allure_attach_json("Grafana API Request Headers", headers)
        allure_attach_json("Grafana API Request Params", params)
        allure_attach_json("Grafana API Request Payload", payload)

        try:
            # 3. Make the API call
            response: Response = self._context.request.post(
                self._api_url,
                data=json.dumps(payload),
                headers=headers,
                params=params,
                timeout=self._timeout,
            )

            # 4. Always attach the response status
            allure_attach_text("Grafana API Response Status", f"{response.status} {response.status_text}")

            # 5. Handle success or failure
            if response.ok:
                try:
                    # Success: Parse JSON, attach, and return
                    response_json = response.json()
                    allure_attach_json("Grafana API Response Body", response_json)
                    Logger.info(f"API query successful. Status: {response.status}")
                    return response_json
                except Exception as json_error:
                    # Handle cases where 2xx response isn't valid JSON
                    Logger.error(f"API query succeeded ({response.status}) but failed to parse JSON: {json_error}")
                    try:
                        response_text = response.text()
                        allure_attach_text("Grafana API Response Body (Raw)", str(response_text))
                    except Exception:
                        # If response.text() fails, skip attaching raw text
                        pass
                    raise GrafanaAPIError(f"API query failed: {json_error}")
            else:
                # Failure: Attach error text and raise
                error_text = response.text()
                allure_attach_text("Grafana API Error Response", error_text)
                error_message = (
                    f"API query failed.\n"
                    f"Status Code: {response.status}\n"
                    f"Response Text: {error_text}"
                )
                Logger.error(error_message)
                raise GrafanaAPIError(error_message)

        except GrafanaAPIError:
            raise  # Re-raise errors we've already formatted
        except Exception as e:
            # Catch connection errors, timeouts, etc.
            Logger.error(f"API query failed with unexpected exception: {e}")
            raise GrafanaAPIError(f"API query failed: {e}")

# --------------------------------------------------------------------------------------------------

def _worker_entry(
    username: str,
    password: str,
    base_url: str,
    headless: bool,
    timeout: int,
    cmd_queue: multiprocessing.Queue,
    res_queue: multiprocessing.Queue,
):
    """Top-level process entry point to satisfy spawn/fork pickling rules."""
    worker = _GrafanaWorker(
        username=username,
        password=password,
        base_url=base_url,
        headless=headless,
        timeout=timeout,
        cmd_queue=cmd_queue,
        res_queue=res_queue,
    )
    worker.run()


class GrafanaClient:
    """
    GrafanaClient provides a context-managed interface for authenticating with Grafana
    using a dedicated child process to avoid blocking the main thread.
    """

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str = "https://liveramp.grafana.net",
        headless: bool = True,
        timeout: int = 60000,
    ):
        self._username = username
        self._password = password
        self._base_url = base_url.rstrip("/")
        self._headless = headless
        self._timeout = timeout
        self._cmd_queue: Optional[multiprocessing.Queue] = None
        self._res_queue: Optional[multiprocessing.Queue] = None
        self._process: Optional[multiprocessing.Process] = None
        self._call_lock: threading.Lock = threading.Lock()

    def __enter__(self):
        Logger.info("Starting GrafanaClient worker process...")
        self._cmd_queue = multiprocessing.Queue()
        self._res_queue = multiprocessing.Queue()
        self._process = multiprocessing.Process(
            target=_worker_entry,
            args=(
                self._username,
                self._password,
                self._base_url,
                self._headless,
                self._timeout,
                self._cmd_queue,
                self._res_queue,
            )
        )
        self._process.daemon = True # Ensure the worker process exits with the main process
        self._process.start()

        # Wait for worker to signal readiness with a timeout
        handshake_timeout_sec = max(10.0, min(60.0, (self._timeout / 1000.0) + 10.0))
        try:
            result = self._res_queue.get(timeout=handshake_timeout_sec)
        except queue.Empty:
            self._process.terminate()
            self._process.join()
            raise GrafanaAuthenticationError("Worker failed to initialize within timeout.")

        if result.get("status") == "error":
            self._process.join()
            raise GrafanaAuthenticationError(
                f"Worker failed to initialize: {result.get('message')}"
            )
        
        Logger.info("GrafanaClient worker started and authenticated successfully.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        Logger.info("Stopping GrafanaClient worker process.")
        if self._process and self._process.is_alive():
            try:
                # Send the exit command
                if self._cmd_queue is not None:
                    self._cmd_queue.put({"action": "exit"})
                # Wait for the process to finish
                self._process.join(timeout=5)
                # If it's still alive, terminate it forcefully
                if self._process.is_alive():
                    self._process.terminate()
            except Exception as e:
                Logger.warning(f"Error during worker process cleanup: {e}")
            finally:
                self._process.close()
        # Close queues
        for q in (self._cmd_queue, self._res_queue):
            try:
                if q is not None:
                    q.close()
                    q.join_thread()
            except Exception:
                pass
        Logger.info("GrafanaClient worker process stopped.")

    def __getattr__(self, name: str):
        """Dynamic proxy for public methods defined on the worker.

        Any callable attribute on `_GrafanaWorker` that doesn't start with `_`
        is exposed transparently on the client. Calls are marshalled via IPC
        and executed in the worker process.
        """
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # Only expose methods that exist on the worker and are callable
        worker_attr = getattr(_GrafanaWorker, name, None)
        if worker_attr is None or not callable(worker_attr):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        def proxy_method(*args, **kwargs):
            # Map positional args to keyword args using the worker method signature.
            try:
                sig = inspect.signature(worker_attr)
                # Prepend dummy for 'self'
                bound = sig.bind_partial(None, *args, **kwargs)
                # Strip 'self'
                call_args = {k: v for k, v in bound.arguments.items() if k != 'self'}
            except Exception:
                # Fallback: require keyword-only if signature binding fails
                if args:
                    raise TypeError(f"Method '{name}' requires keyword arguments")
                call_args = kwargs

            return self._invoke(action=name, args=call_args)

        return proxy_method

    def _ensure_running(self):
        if not self._process or not self._process.is_alive():
            raise GrafanaAPIError("Worker process is not running.")

    def _invoke(self, action: str, args: Dict[str, Any], timeout: Optional[float] = None) -> Any:
        """Send a command to the worker and wait for the response.

        Args:
            action: Worker method name to call.
            args: Keyword arguments for the worker method.
            timeout: Optional timeout in seconds for the call.

        Returns:
            The `data` field from the worker response.
        """
        self._ensure_running()
        call_timeout_sec = float(timeout) if timeout is not None else max(10.0, (self._timeout / 1000.0) + 5.0)
        request_id = uuid.uuid4().hex
        with self._call_lock:
            self._cmd_queue.put({
                "action": action,
                "args": args,
                "request_id": request_id,
            })
            try:
                result = self._res_queue.get(timeout=call_timeout_sec)
            except queue.Empty:
                raise GrafanaAPIError(f"Worker method '{action}' timed out after {call_timeout_sec} seconds.")

        if result.get("status") == "error":
            message = result.get("message", "Unknown error")
            raise GrafanaAPIError(f"Worker method '{action}' failed: {message}")

        return result.get("data")

    def query_loki(self, payload: dict, from_timestamp: str = None, to_timestamp: str = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Proxy to worker's query_loki using IPC.

        Args:
            payload: Loki query payload.
            from_timestamp: Optional override for the 'from' timestamp.
            to_timestamp: Optional override for the 'to' timestamp.
            timeout: Optional timeout in seconds for the call.

        Returns:
            Parsed JSON response from Grafana/Loki.
        """
        return self._invoke(
            action="query_loki",
            args={
                "payload": payload,
                "from_timestamp": from_timestamp,
                "to_timestamp": to_timestamp,
            },
            timeout=timeout,
        )

"""
if __name__ == "__main__":

    username="qe.eng.testing@liveramp.com"
    password="xxxxxxxxxxxxxxx"
    config = {
        "username": username,
        "password": password,
        "headless": False,  # Set True on CI
        "timeout": 60000,   # ms
    }

    # Example Loki query payload (adjust as needed)
    loki_payload = {
        "queries": [
            {
                "refId": "A",
                "expr": '{team="opi", cluster_name="opi-prod-2", exporter="OTLP", environment="prod"} |= `6507093151`',
                "queryType": "range",
                "datasource": {"type": "loki", "uid": "grafanacloud-logs"},
                "maxLines": 1000,
                "direction": "backward",
            }
        ],
        # Example millisecond timestamps; set to your window
        "from": "1756131268306",
        "to": "1756217668306",
    }

    try:
        with GrafanaClient(**config) as client:
            result = client.query_loki(loki_payload)
            try:
                pretty = json.dumps(result, indent=2)
            except Exception:
                pretty = str(result)
            Logger.info(f"Loki query results: {pretty}")
    except GrafanaAuthenticationError as e:
        Logger.error(f"Authentication failed: {e}")
    except GrafanaAPIError as e:
        Logger.error(f"API error: {e}")
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
"""