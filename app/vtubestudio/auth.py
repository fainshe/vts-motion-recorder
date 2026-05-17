import json
from pathlib import Path
from .models import PluginAuth


class AuthManager:
    def __init__(self, config_file: str = "vts_config.json"):
        self.config_file = Path(config_file)
        self._token: str | None = None

    def load_token(self) -> str | None:
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text())
                self._token = data.get("token")
                return self._token
            except (json.JSONDecodeError, KeyError):
                pass
        return None

    def save_token(self, token: str):
        self._token = token
        self.config_file.write_text(json.dumps({"token": token}, indent=2))

    def get_token(self) -> str | None:
        return self._token

    def clear_token(self):
        self._token = None
        if self.config_file.exists():
            self.config_file.unlink()

    def build_token_request(self, auth: PluginAuth) -> dict:
        return {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "token_request",
            "messageType": "AuthenticationTokenRequest",
            "data": {
                "pluginName": auth.plugin_name,
                "pluginDeveloper": auth.plugin_developer,
            }
        }

    def build_auth_request(self, auth: PluginAuth) -> dict:
        payload = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "auth_request",
            "messageType": "AuthenticationRequest",
            "data": {
                "pluginName": auth.plugin_name,
                "pluginDeveloper": auth.plugin_developer,
            }
        }
        if auth.plugin_token:
            payload["data"]["authenticationToken"] = auth.plugin_token
        return payload
