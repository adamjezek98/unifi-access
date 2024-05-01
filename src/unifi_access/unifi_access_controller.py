import requests
import websocket
import typing
import ssl
import json
from .unifi_access_door import UnifiAccessDoor


class UnifiAccessController():
    def __init__(self, host: str, api_key: str, port: int = 12445, verify_ssl: bool = False):
        self.host = host
        self.port = port
        self.verify_ssl = verify_ssl
        self.api_key = api_key
        self.base_url = f"https://{host}:{port}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }
        self.doors: typing.Dict[str, UnifiAccessDoor] = {}
        self.ws = None

    def load_and_connect(self):
        self.load_doors()
        self.connect_websocket()

    def connect_websocket(self):
        ws_url = f"wss://{self.host}:{self.port}/api/v1/developer/devices/notifications"
        self.ws = websocket.WebSocketApp(
            ws_url,
            header=self.headers,
            on_message=self.handle_websocket,
            on_open=lambda ws: print("websocket opened"),
            on_close=lambda ws: print("websocket closed"),
            on_error=lambda ws, error: print("websocket error", error),
        )
        print("making websocket app")

    def run_websocket(self):
        sslopt = {"cert_reqs": ssl.CERT_NONE} if not self.verify_ssl else None
        print("running websocket")
        self.ws.run_forever(sslopt=sslopt, reconnect=3)
        print("forever wasn't forever")

    def make_request(self, method: str, endpoint: str, data: dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data, verify=self.verify_ssl)
        return response

    def load_doors(self) -> dict:
        response = self.make_request("GET", "/api/v1/developer/doors/")
        doors = response.json().get("data", [])
        print("fetched doors")
        for door in doors:
            door_uuid = door.get("id")
            door["uuid"] = door.pop("id")
            self.doors[door_uuid] = UnifiAccessDoor(ua_controller=self, **door)
        return response.json()

    def unlock_door(self, door_uuid: str) -> bool:
        response = self.make_request("PUT", f"/api/v1/developer/doors/{door_uuid}/unlock/")
        return response.ok

    def get_doors(self) -> typing.Dict[str, UnifiAccessDoor]:
        return self.doors

    def handle_websocket(self, wsapp, message):
        print(message)
        message = json.loads(message)
        if message == "Hello":
            return
        event = message.get("event")
        if event == "access.data.device.update":
            self.handle_door_update(message)


    def handle_door_update(self, message):
        device_type = message.get("data", {}).get("device_type")
        if device_type in ('UAH-Ent',):
            pass

