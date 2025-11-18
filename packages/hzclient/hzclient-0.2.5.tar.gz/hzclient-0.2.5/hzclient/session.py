"""Handles low-level API communication."""

import curl_cffi as requests
from hashlib import md5
import logging
import socketio

from hzclient.models import Response, Config

logging.getLogger("socketio.client").setLevel(logging.WARNING)
logging.getLogger("engineio.client").setLevel(logging.WARNING)

class Session:
  """Handles low-level API communication."""

  def __init__(self, config: Config, client):
    self.config = config
    self.session = requests.Session()
    self.client = client
    self.logger = logging.getLogger(self.__class__.__name__)

    # HTTP headers
    self.session.headers.update({
      "origin": self.config.base_url,
      "referer": f"{self.config.base_url}/",
    })

    # --- Socket.IO client ---
    self.sio = socketio.Client()
    self._register_socketio_handlers()

  # ---------- SOCKET.IO PART ----------

  def _build_ws_headers(self) -> dict:
    """Forward cookies & headers from HTTP session if needed."""
    headers = {
      "Origin": self.config.base_url,
      "Referer": f"{self.config.base_url}/",
    }
    if self.session.cookies:
      cookie_header = "; ".join(
        f"{k}={v}" for k, v in self.session.cookies.get_dict().items()
      )
      headers["Cookie"] = cookie_header
    return headers

  def _register_socketio_handlers(self):
    @self.sio.on("requestClientInfo")
    def on_request_client_info(data):
      self.sio.emit("message", {
        "type": "requestClientInfoResponse",
        "data": {
          "game_id": "hero",
          "server_id": self.config.server_id,
          "user_id": self.state.user.id,
          "session_id": self.state.user.session_id,
        }
      })

    @self.sio.on("syncGame")
    def sync_game(data):
      self.client.sync_game(sync_type="full")

    @self.sio.on("syncGameAndGuild")
    def sync_game_and_guild(data):
      self.client.sync_game(sync_type="guild")
      self.client.sync_game(sync_type="full")

    @self.sio.on("syncGuildLog")
    def sync_guild_log(data):
      self.client.sync_guild_log()

  def connect_socket(self):
    """Connect to the game Socket.IO endpoint (listen-only)."""
    if self.sio.connected:
      self.logger.info("Socket.IO already connected.")
      return

    headers = self._build_ws_headers()

    # This tells python-socketio to use WebSocket directly
    self.logger.info(f"Connecting Socket.IO to {self.config.ws_url}")
    self.sio.connect(self.config.ws_url, headers=headers, transports=["websocket"])

  def close_socket(self):
    if self.sio.connected:
      self.sio.disconnect()

  # ---------- HTTP PART (unchanged) ----------

  def _get_auth(self, action: str, user_id: int) -> str:
    """Generate authentication hash for requests."""
    s = action + "GN1al351" + str(user_id)
    return md5(s.encode("utf-8")).hexdigest()

  def request(
    self,
    action: str,
    user_id: int,
    session_id: str,
    client_version: str,
    build_number: str,
    extra_params: dict | None
  ) -> Response:
    """Make an authenticated request to the game API."""

    params = {
      "action": action,
      "user_id": user_id,
      "user_session_id": session_id,
      "client_version": f"html5_{client_version}",
      "build_number": build_number,
      "auth": self._get_auth(action, user_id),
      "rct": 2,
      "keep_active": "true",
      "device_type": "web"
    }

    if extra_params:
      params.update(extra_params)

    try:
      response = self.session.post(
        f"{self.config.base_url}/request.php",
        data=params,
        timeout=self.config.timeout,
        impersonate=self.config.impersonate
      )
      response.raise_for_status()

      self.logger.debug(f"Request {action} successful")
      return Response(response.status_code, response.json())
    except Exception as e:
      self.logger.error(f"Request {action} failed: {e}")
      return Response(500, error=str(e))

  def attach_state(self, state):
    """Attach a GameState instance to the session for state updates."""
    self.state = state