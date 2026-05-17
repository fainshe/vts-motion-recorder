import asyncio
import json
import logging
import threading
from typing import Callable
import websockets

from ..core.config import config
from ..core.bridge import bridge
from .models import PluginAuth, LiveParameters
from .auth import AuthManager

logger = logging.getLogger(__name__)


class VTSClient:
    def __init__(self):
        self.ws = None
        self.auth = AuthManager(config.config_file)
        self._plugin_auth = PluginAuth(
            plugin_name=config.plugin_name,
            plugin_developer=config.plugin_developer,
        )
        self._running = False
        self._connected = False
        self._authenticated = False
        self._reconnect_delay = 2.0
        self._max_reconnect_delay = 30.0
        self._loop = None
        self._thread = None
        self._parameter_names: list[str] = []
        self._on_parameter_update: Callable | None = None
        self._poll_interval = 1.0 / 60
        self._last_error = ""

    async def _connect(self):
        uri = f"ws://{config.vts_host}:{config.vts_port}"
        logger.info(f"Connecting to {uri}")
        try:
            self.ws = await asyncio.wait_for(
                websockets.connect(uri), timeout=5.0
            )
            self._connected = True
            self._reconnect_delay = 2.0
            self._last_error = ""
            bridge.emit_connection_status("connected")
            logger.info("Connected to VTube Studio")
            await self._authenticate()
        except asyncio.TimeoutError:
            self._last_error = "Connection timeout - is VTube Studio running?"
            logger.error(self._last_error)
            bridge.emit_connection_status("error", message=self._last_error)
            raise
        except ConnectionRefusedError:
            self._last_error = f"Connection refused on {uri}"
            logger.error(self._last_error)
            bridge.emit_connection_status("error", message=self._last_error)
            raise
        except Exception as e:
            self._last_error = f"Connection failed: {e}"
            logger.error(self._last_error)
            bridge.emit_connection_status("error", message=self._last_error)
            raise

    async def _recv_response(self) -> dict:
        raw = await asyncio.wait_for(self.ws.recv(), timeout=10.0)
        data = json.loads(raw)
        return data

    async def _request_token(self) -> str | None:
        token_request = self.auth.build_token_request(self._plugin_auth)
        logger.info("Sending AuthenticationTokenRequest...")
        await self.ws.send(json.dumps(token_request))

        data = await self._recv_response()
        logger.info(f"Token response: {json.dumps(data, indent=2)}")

        if "data" in data and "authenticationToken" in data["data"]:
            token = data["data"]["authenticationToken"]
            self.auth.save_token(token)
            self._plugin_auth.plugin_token = token
            logger.info("Received and saved new authentication token")
            return token
        else:
            self._last_error = data.get("message", "Failed to get token")
            logger.error(f"Token request failed: {self._last_error}")
            return None

    async def _authenticate_with_token(self) -> bool:
        auth_request = self.auth.build_auth_request(self._plugin_auth)
        logger.info("Sending AuthenticationRequest...")
        await self.ws.send(json.dumps(auth_request))

        data = await self._recv_response()
        logger.info(f"Auth response: {json.dumps(data, indent=2)}")

        if data.get("data", {}).get("authenticated", False):
            logger.info("Authentication successful")
            return True
        else:
            self._last_error = data.get("message", "Authentication failed")
            logger.error(f"Auth failed: {self._last_error}")
            return False

    async def _authenticate(self):
        saved_token = self.auth.load_token()

        if saved_token:
            logger.info("Using saved authentication token")
            self._plugin_auth.plugin_token = saved_token
            success = await self._authenticate_with_token()
            if success:
                self._authenticated = True
                bridge.emit_connection_status("authenticated")
                await self._discover_parameters()
                return
            else:
                logger.info("Saved token invalid, requesting new token...")
                self.auth.clear_token()

        token = await self._request_token()
        if token:
            success = await self._authenticate_with_token()
            if success:
                self._authenticated = True
                bridge.emit_connection_status("authenticated")
                await self._discover_parameters()
            else:
                bridge.emit_connection_status("auth_error", message=self._last_error)
        else:
            bridge.emit_connection_status("auth_error", message=self._last_error)

    async def _discover_parameters(self):
        logger.info("Discovering parameters...")
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "param_list",
            "messageType": "InputParameterListRequest",
            "data": {}
        }
        await self.ws.send(json.dumps(request))
        data = await self._recv_response()
        logger.info(f"Parameter list response keys: {list(data.get('data', {}).keys())}")

        param_list = []
        if "data" in data:
            param_list.extend(data["data"].get("defaultParameters", []))
            param_list.extend(data["data"].get("customParameters", []))

        if param_list:
            self._parameter_names = [p["name"] for p in param_list]
            bridge.emit_parameters_discovered(
                count=len(self._parameter_names),
                names=self._parameter_names
            )
            logger.info(f"Discovered {len(self._parameter_names)} parameters")
        else:
            logger.warning("No parameters found in response")

    async def _poll_parameters(self):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "get_params",
            "messageType": "InputParameterListRequest",
            "data": {}
        }
        await self.ws.send(json.dumps(request))
        data = await self._recv_response()

        params = {}
        if "data" in data:
            for p in data["data"].get("defaultParameters", []):
                params[p["name"]] = p["value"]
            for p in data["data"].get("customParameters", []):
                params[p["name"]] = p["value"]

        if params:
            bridge.emit_parameter_update(params)
            logger.debug(f"Polled {len(params)} parameters")
        else:
            logger.warning("No parameters in poll response")

    async def _run(self):
        while self._running:
            try:
                await self._connect()

                while self._running and self._connected and self._authenticated:
                    try:
                        await self._poll_parameters()
                    except Exception as e:
                        logger.warning(f"Poll error: {e}")
                    await asyncio.sleep(self._poll_interval)

            except (websockets.ConnectionClosed, ConnectionError) as e:
                self._connected = False
                self._authenticated = False
                if self._running:
                    logger.warning(f"Disconnected: {e}")
                    bridge.emit_connection_status("reconnecting",
                             delay=self._reconnect_delay)
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(
                        self._reconnect_delay * 1.5,
                        self._max_reconnect_delay
                    )
            except Exception as e:
                if self._running:
                    logger.error(f"Unexpected error: {e}")
                    bridge.emit_connection_status("error", message=str(e))
                    await asyncio.sleep(self._reconnect_delay)

    def connect(self):
        self._running = True
        self._thread = threading.Thread(target=self._run_thread, daemon=True)
        self._thread.start()

    def _run_thread(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._run())
        except RuntimeError:
            pass
        finally:
            try:
                pending = asyncio.all_tasks(self._loop)
                for task in pending:
                    task.cancel()
                if pending:
                    self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass
            self._loop.close()

    def disconnect(self):
        self._running = False
        self._connected = False
        self._authenticated = False
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        bridge.emit_connection_status("disconnected")

    def set_parameter_callback(self, callback: Callable):
        self._on_parameter_update = callback

    def set_poll_interval(self, interval: float):
        self._poll_interval = interval

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def parameter_names(self) -> list[str]:
        return self._parameter_names.copy()

    @property
    def last_error(self) -> str:
        return self._last_error
