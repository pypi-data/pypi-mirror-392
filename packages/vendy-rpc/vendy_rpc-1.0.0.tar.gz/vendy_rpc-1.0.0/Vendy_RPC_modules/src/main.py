#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord RPC 모듈
Discord Gateway WebSocket을 통한 Rich Presence 관리
"""

import json
import threading
import time
import http.client
from typing import Optional, Dict, Any, Callable, List, Union, TypedDict
from enum import IntEnum
import websocket


class ActivityType(IntEnum):
    """Discord Activity Types"""
    PLAYING = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


# Backward compatibility
ActivityTypes = {
    **{t.name: t.value for t in ActivityType},
    **{t.value: t.name for t in ActivityType}
}


class DiscordRPCError(Exception):
    """Base exception for Discord RPC errors"""
    pass


class WebSocketNotConnectedError(DiscordRPCError):
    """Raised when WebSocket is not connected"""
    pass


class RPCConfig(TypedDict, total=False):
    """RPC Manager Configuration"""
    RESTART_INTERVAL_MS: int  # 자동 재시작 간격 (밀리초), 예: 10 * 60 * 1000 = 10분
    STATUS_CHECK_INTERVAL_MS: int  # 상태 확인 간격 (밀리초), 예: 60 * 1000 = 1분
    LOGIN_RETRIES: int  # 로그인 재시도 횟수
    LOGIN_RETRY_DELAY_MS: int  # 로그인 재시도 간격 (밀리초)


class RPCUser(TypedDict, total=False):
    """RPC User Data"""
    userID: str  # Discord 사용자 ID (숫자 문자열)
    token: str  # Discord 사용자 토큰 (개발자 도구에서 확인, 절대 공유하지 마세요)
    name: str  # 표시할 이름 (임의로 설정 가능)
    type: str  # 활동 타입: "PLAYING", "STREAMING", "LISTENING", "WATCHING", "COMPETING"
    state: str  # 상태 텍스트 (위쪽에 표시)
    details: str  # 상세 텍스트 (아래쪽에 표시)
    large_image: str  # 큰 이미지 키 또는 Discord CDN URL
    largete: str  # 큰 이미지 호버 텍스트
    small_image: str  # 작은 이미지 키 또는 Discord CDN URL
    smallte: str  # 작은 이미지 호버 텍스트
    button1: str  # 첫 번째 버튼 라벨
    button1link: str  # 첫 번째 버튼 링크 (URL)
    button2: str  # 두 번째 버튼 라벨
    button2link: str  # 두 번째 버튼 링크 (URL)


class RichPresenceAssets:
    """Rich Presence assets (images and texts)"""
    
    CDN_PREFIXES = (
        'https://cdn.discordapp.com/',
        'http://cdn.discordapp.com/',
        'https://media.discordapp.net/',
        'http://media.discordapp.net/',
    )
    
    def __init__(self, activity: 'RichPresence', assets: Optional[Dict[str, Any]] = None):
        self.activity = activity
        self.large_image: Optional[str] = None
        self.large_text: Optional[str] = None
        self.small_image: Optional[str] = None
        self.small_text: Optional[str] = None
        if assets:
            self._patch(assets)
    
    def _patch(self, assets: Dict[str, Any]) -> None:
        """Update assets from dictionary"""
        self.large_image = assets.get('large_image') or assets.get('largeImage')
        self.large_text = assets.get('large_text') or assets.get('largeText')
        self.small_image = assets.get('small_image') or assets.get('smallImage')
        self.small_text = assets.get('small_text') or assets.get('smallText')
    
    @staticmethod
    def parse_image(image: Optional[str]) -> Optional[str]:
        """Parse and normalize image URL"""
        if not isinstance(image, str) or not image:
            return None
        
        if image.startswith(('http://', 'https://')):
            for prefix in RichPresenceAssets.CDN_PREFIXES:
                if image.startswith(prefix):
                    return f"mp:{image[len(prefix):]}"
            raise ValueError('INVALID_URL: External URLs must be from Discord CDN')
        
        return image
    
    def to_json(self) -> Optional[Dict[str, str]]:
        """Convert to JSON-serializable format"""
        result = {}
        if self.large_image:
            result['large_image'] = self.parse_image(self.large_image)
        if self.large_text:
            result['large_text'] = self.large_text
        if self.small_image:
            result['small_image'] = self.parse_image(self.small_image)
        if self.small_text:
            result['small_text'] = self.small_text
        return result if result else None
    
    def set_large_image(self, image: str) -> 'RichPresenceAssets':
        """Set large image"""
        self.large_image = self.parse_image(image)
        return self
    
    def set_small_image(self, image: str) -> 'RichPresenceAssets':
        """Set small image"""
        self.small_image = self.parse_image(image)
        return self
    
    def set_large_text(self, text: str) -> 'RichPresenceAssets':
        """Set large image text"""
        self.large_text = text
        return self
    
    def set_small_text(self, text: str) -> 'RichPresenceAssets':
        """Set small image text"""
        self.small_text = text
        return self


class RichPresence:
    """Discord Rich Presence"""
    
    def __init__(self, client: 'Client', data: Optional[Dict[str, Any]] = None):
        if not client:
            raise ValueError("Client is required")
        self.client = client
        self.name: Optional[str] = None
        self.type: Union[int, str] = ActivityType.PLAYING
        self.application_id: Optional[str] = None
        self.state: Optional[str] = None
        self.details: Optional[str] = None
        self.url: Optional[str] = None
        self.timestamps: Dict[str, int] = {}
        self.buttons: List[str] = []
        self.metadata: Dict[str, List[str]] = {"button_urls": []}
        self.assets = RichPresenceAssets(self)
        
        if data:
            self._patch(data)
    
    def _patch(self, data: Dict[str, Any]) -> None:
        """Update from dictionary"""
        if 'name' in data:
            self.name = data['name']
        if 'type' in data:
            self.type = data['type']
        if 'application_id' in data or 'applicationId' in data:
            self.application_id = data.get('application_id') or data.get('applicationId')
        if 'state' in data:
            self.state = data['state']
        if 'details' in data:
            self.details = data['details']
        if 'url' in data:
            self.url = data['url']
        if 'assets' in data:
            self.assets._patch(data['assets'])
        if 'timestamps' in data:
            self.timestamps = data['timestamps']
        if 'buttons' in data:
            self.buttons = data['buttons']
        if 'metadata' in data:
            self.metadata = data['metadata']
    
    def set_application_id(self, app_id: str) -> 'RichPresence':
        """Set application ID"""
        self.application_id = app_id
        return self
    
    def set_type(self, activity_type: Union[int, str]) -> 'RichPresence':
        """Set activity type"""
        if isinstance(activity_type, str):
            self.type = ActivityTypes.get(activity_type, ActivityType.PLAYING)
        else:
            self.type = activity_type
        return self
    
    def set_state(self, state: str) -> 'RichPresence':
        """Set state text"""
        self.state = state
        return self
    
    def set_name(self, name: str) -> 'RichPresence':
        """Set activity name"""
        self.name = name
        return self
    
    def set_details(self, details: str) -> 'RichPresence':
        """Set details text"""
        self.details = details
        return self
    
    def set_start_timestamp(self, timestamp: Union[int, float]) -> 'RichPresence':
        """Set start timestamp"""
        if not self.timestamps:
            self.timestamps = {}
        self.timestamps['start'] = int(timestamp)
        return self
    
    def set_assets_large_image(self, image: str) -> 'RichPresence':
        """Set large image"""
        self.assets.set_large_image(image)
        return self
    
    def set_assets_large_text(self, text: str) -> 'RichPresence':
        """Set large image text"""
        self.assets.set_large_text(text)
        return self
    
    def set_assets_small_image(self, image: str) -> 'RichPresence':
        """Set small image"""
        self.assets.set_small_image(image)
        return self
    
    def set_assets_small_text(self, text: str) -> 'RichPresence':
        """Set small image text"""
        self.assets.set_small_text(text)
        return self
    
    def add_button(self, name: str, url: str) -> 'RichPresence':
        """Add button to presence"""
        if not name or not url:
            raise ValueError('Button must have name and url')
        self.buttons.append(name)
        if 'button_urls' not in self.metadata:
            self.metadata['button_urls'] = []
        self.metadata['button_urls'].append(url)
        return self
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable format"""
        result: Dict[str, Any] = {
            'type': self.type if isinstance(self.type, int) else ActivityTypes.get(self.type, ActivityType.PLAYING)
        }
        
        if self.name:
            result['name'] = self.name
        if self.application_id:
            result['application_id'] = self.application_id
        if self.state:
            result['state'] = self.state
        if self.details:
            result['details'] = self.details
        if self.url:
            result['url'] = self.url
        
        assets_json = self.assets.to_json()
        if assets_json:
            result['assets'] = assets_json
        if self.timestamps:
            result['timestamps'] = self.timestamps
        if self.buttons:
            result['buttons'] = self.buttons
        if self.metadata.get('button_urls'):
            result['metadata'] = {'button_urls': self.metadata['button_urls']}
        
        return result


class Client:
    """Discord Client for Rich Presence"""
    
    API_BASE = "discord.com"
    API_VERSION = "v10"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    GATEWAY_VERSION = "10"
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.token: Optional[str] = None
        self.user: Optional[Dict[str, Any]] = None
        self.ws: Optional[websocket.WebSocketApp] = None
        self.session_id: Optional[str] = None
        self.ready_at: Optional[float] = None
        self.options = options or {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._running = False
    
    def on(self, event: str, handler: Callable) -> 'Client':
        """Register event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        return self
    
    def _emit(self, event: str, *args: Any) -> None:
        """Emit event to registered handlers"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(*args)
            except Exception as e:
                print(f"Event handler error ({event}): {e}")
    
    def _make_request(self, method: str, path: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make HTTP request to Discord API"""
        conn = http.client.HTTPSConnection(self.API_BASE)
        default_headers = {"User-Agent": self.USER_AGENT}
        if headers:
            default_headers.update(headers)
        
        try:
            conn.request(method, path, headers=default_headers)
            response = conn.getresponse()
            data = response.read().decode()
            
            if response.status == 200:
                return json.loads(data)
            else:
                raise DiscordRPCError(f"HTTP {response.status}: {data}")
        finally:
            conn.close()
    
    def _fetch_user_info(self) -> Dict[str, Any]:
        """Fetch current user information"""
        if not self.token:
            raise ValueError("Token is required")
        
        return self._make_request(
            "GET",
            f"/api/{self.API_VERSION}/users/@me",
            headers={
                "Authorization": self.token,
                "Content-Type": "application/json"
            }
        )
    
    def _get_gateway_url(self) -> str:
        """Get Discord Gateway WebSocket URL"""
        data = self._make_request("GET", f"/api/{self.API_VERSION}/gateway")
        return f"{data['url']}?v={self.GATEWAY_VERSION}&encoding=json"
    
    def _connect_websocket(self) -> None:
        """Connect to Discord Gateway WebSocket"""
        gateway_url = self._get_gateway_url()
        self._running = True
        
        def on_message(ws: websocket.WebSocketApp, message: str) -> None:
            try:
                packet = json.loads(message)
                self._handle_packet(packet)
            except Exception as e:
                if self._running:
                    self._emit('error', DiscordRPCError(str(e)))
        
        def on_error(ws: websocket.WebSocketApp, error: Exception) -> None:
            if self._running:
                self._emit('error', error)
        
        def on_close(ws: websocket.WebSocketApp, *args: Any) -> None:
            self._running = False
        
        def on_open(ws: websocket.WebSocketApp) -> None:
            self._send_identify()
        
        self.ws = websocket.WebSocketApp(
            gateway_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        ws_thread.start()
        time.sleep(1)  
    
    def _send_identify(self) -> None:
        """Send Identify packet"""
        identify = {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "os": "Windows",
                    "browser": "Chrome",
                    "device": ""
                },
                "intents": 0
            }
        }
        self._send_json(identify)
    
    def _send_json(self, data: Dict[str, Any]) -> None:
        """Send JSON data through WebSocket"""
        if not self.ws or not self._running:
            raise WebSocketNotConnectedError("WebSocket is not connected")
        self.ws.send(json.dumps(data))
    
    def _handle_packet(self, packet: Dict[str, Any]) -> None:
        """Handle incoming WebSocket packet"""
        op = packet.get('op')
        if op == 0:  
            self._handle_dispatch(packet)
        elif op == 10:
            interval = packet.get('d', {}).get('heartbeat_interval', 41250)
            self._start_heartbeat(interval)
        elif op == 11: 
            pass
    
    def _handle_dispatch(self, packet: Dict[str, Any]) -> None:
        """Handle Dispatch packet"""
        event_type = packet.get('t')
        if event_type == 'READY':
            self.session_id = packet.get('d', {}).get('session_id')
            self.ready_at = time.time()
            self._emit('ready')
    
    def _start_heartbeat(self, interval_ms: int) -> None:
        """Start heartbeat loop"""
        if self._heartbeat_thread:
            return
        
        def heartbeat_loop() -> None:
            while self._running:
                time.sleep(interval_ms / 1000.0)
                if self._running and self.ws:
                    try:
                        self._send_json({"op": 1, "d": None})
                    except Exception:
                        break
        
        self._heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
    
    def _set_activity(self, activity: RichPresence) -> None:
        """Set activity/presence"""
        if not self.ws or not self._running:
            raise WebSocketNotConnectedError("WebSocket is not connected")
        
        activity_data = activity.to_json()
        activity_type = activity_data.get('type', ActivityType.PLAYING)
        if isinstance(activity_type, str):
            activity_type = ActivityTypes.get(activity_type, ActivityType.PLAYING)
        
        since = activity_data.get('timestamps', {}).get('start') or int(time.time() * 1000)
        
        activity_obj: Dict[str, Any] = {
            "name": activity_data.get('name', 'Unknown'),
            "type": activity_type,
        }
        
       
        for key in ['application_id', 'state', 'details', 'url', 'assets', 'timestamps', 'buttons', 'metadata']:
            if key in activity_data and activity_data[key]:
                activity_obj[key] = activity_data[key]
        
        presence = {
            "op": 3,
            "d": {
                "since": since,
                "activities": [activity_obj],
                "status": "online",
                "afk": False
            }
        }
        
        self._send_json(presence)
    
    def login(self, token: str) -> str:
        """Login with user token"""
        if not token:
            raise ValueError("Token is required")
        
        self.token = token
        user_info = self._fetch_user_info()
        
        self.user = {
            "id": user_info.get("id"),
            "username": user_info.get("username"),
            "discriminator": user_info.get("discriminator"),
            "avatar": user_info.get("avatar"),
            "bot": user_info.get("bot", False),
            "setActivity": lambda activity: self._set_activity(activity)
        }
        
        self._connect_websocket()
        return self.token
    
    def destroy(self) -> None:
        """Destroy client and cleanup resources"""
        self._running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None
        self._event_handlers.clear()
        self._heartbeat_thread = None


class RPCManager:
    """Manages multiple Discord RPC clients"""
    
    # 고정된 Discord Application ID
    DEFAULT_APPLICATION_ID = "817229550684471297"
    
    def __init__(self, config: Optional[RPCConfig] = None, users: Optional[List[RPCUser]] = None):
        """
        Initialize RPC Manager
        
        Args:
            config: Configuration dictionary with:
                - RESTART_INTERVAL_MS: Auto-restart interval in milliseconds (default: 10 minutes)
                - STATUS_CHECK_INTERVAL_MS: Status check interval in milliseconds (default: 60 seconds)
                - LOGIN_RETRIES: Number of login retry attempts (default: 3)
                - LOGIN_RETRY_DELAY_MS: Delay between login retries in milliseconds (default: 5000)
            users: List of user dictionaries with:
                - userID: User ID
                - token: Discord user token
                - name: Display name
                - type: Activity type (PLAYING, STREAMING, etc.)
                - state: Activity state text
                - details: Activity details text
                - large_image: Large image key/URL
                - largete: Large image text (typo in original, kept for compatibility)
                - small_image: Small image key/URL
                - smallte: Small image text (typo in original, kept for compatibility)
                - button1: First button label
                - button1link: First button URL
                - button2: Second button label
                - button2link: Second button URL
        """
        import signal
        import sys
        
        self.clients: List[Client] = []
        self._restarting = False
        default_config = {
            "RESTART_INTERVAL_MS": 10 * 60 * 1000,
            "STATUS_CHECK_INTERVAL_MS": 60 * 1000,
            "LOGIN_RETRIES": 3,
            "LOGIN_RETRY_DELAY_MS": 5000,
        }
        if config:
            default_config.update(config)
        self.config = default_config
        self.config["APPLICATION_ID"] = self.DEFAULT_APPLICATION_ID
        self.users = users or []
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        import signal
        import sys
        
        def handler(sig, frame):
            print('\n종료 신호(SIGINT) 감지, 클라이언트 종료 중...')
            self.shutdown()
            sys.exit(0)
        signal.signal(signal.SIGINT, handler)
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """Get users with valid tokens"""
        return [u for u in self.users if u.get('token')]
    
    def safe_login(self, client: Client, token: str, retries: Optional[int] = None) -> bool:
        """Login with retry logic"""
        retries = retries or self.config['LOGIN_RETRIES']
        for attempt in range(1, retries + 1):
            try:
                client.login(token)
                return True
            except Exception as err:
                print(f"로그인 실패 ({attempt}/{retries}): {err}")
                if attempt < retries:
                    time.sleep(self.config['LOGIN_RETRY_DELAY_MS'] / 1000.0)
        return False
    
    def _create_presence(self, client: Client, user_data: Dict[str, Any]) -> RichPresence:
        """Create RichPresence from user data"""
        r = RichPresence(client)
        r.set_application_id(self.config['APPLICATION_ID'])
        r.set_type(user_data.get('type', 'PLAYING'))
        r.set_state(user_data.get('state', ''))
        r.set_name(user_data.get('name', ''))
        r.set_details(user_data.get('details', ''))
        r.set_start_timestamp(time.time() * 1000)
        
        if user_data.get('large_image'):
            r.set_assets_large_image(user_data['large_image'])
        if user_data.get('largete'):
            r.set_assets_large_text(user_data['largete'])
        if user_data.get('small_image'):
            r.set_assets_small_image(user_data['small_image'])
        if user_data.get('smallte'):
            r.set_assets_small_text(user_data['smallte'])
        
        if user_data.get('button1') and user_data.get('button1link'):
            r.add_button(user_data['button1'], user_data['button1link'])
        if user_data.get('button2') and user_data.get('button2link'):
            r.add_button(user_data['button2'], user_data['button2link'])
        
        return r
    
    def _setup_client_handlers(self, client: Client, user_data: Dict[str, Any]) -> None:
        """Setup event handlers for client"""
        user_id = user_data.get('userID')
        name = user_data.get('name', 'Unknown')
        
        def on_ready():
            print(f"{name} ({user_id}) 준비 완료!")
            try:
                r = self._create_presence(client, user_data)
                client.user['setActivity'](r)
            except Exception as err:
                print(f"RPC 설정 오류 ({user_id}): {err}")
        
        def on_error(error):
            print(f"클라이언트 오류 발생 ({user_id}): {error}")
        
        client.on('ready', on_ready)
        client.on('error', on_error)
    
    def initialize_clients(self) -> None:
        """Initialize all clients"""
        users = self.get_active_users()
        if not users:
            print('등록된 사용자가 없습니다.')
            return
        
        for user_data in users:
            try:
                token = user_data.get('token', '').strip()
                if not token:
                    print(f"사용자 {user_data.get('userID')} 토큰이 없습니다. 건너뜁니다.")
                    continue
                
                client = Client()
                self._setup_client_handlers(client, user_data)
                
                if not self.safe_login(client, token):
                    print(f"사용자 {user_data.get('userID')} 로그인 실패")
                    continue
                
                self.clients.append(client)
            except Exception as err:
                print(f"사용자 {user_data.get('userID')} 초기화 오류: {err}")
    
    def status_check_loop(self) -> None:
        """Periodic status check loop"""
        while True:
            time.sleep(self.config['STATUS_CHECK_INTERVAL_MS'] / 1000.0)
            for client in self.clients:
                if not client.user:
                    continue
                try:
                    username = client.user.get('username', 'Unknown')
                    print(f"클라이언트 {username} 상태 확인")
                except Exception as err:
                    print(f"상태 확인 오류: {err}")
    
    def restart_loop(self) -> None:
        """Automatic restart loop"""
        while True:
            time.sleep(self.config['RESTART_INTERVAL_MS'] / 1000.0)
            if self._restarting:
                continue
            
            self._restarting = True
            try:
                print("[재시작] 모든 클라이언트 종료 중...")
                self.shutdown()
                print("[재시작] 재초기화 시작...")
                self.initialize_clients()
                print("[재시작] 재초기화 완료.")
            except Exception as e:
                print(f"[재시작] 오류: {e}")
            finally:
                self._restarting = False
    
    def shutdown(self) -> None:
        """Shutdown all clients"""
        for client in self.clients:
            try:
                client.destroy()
            except Exception:
                pass
        self.clients.clear()
    
    def run(self) -> None:
        """Start the RPC manager"""
        self.initialize_clients()
        
        threading.Thread(target=self.status_check_loop, daemon=True).start()
        threading.Thread(target=self.restart_loop, daemon=True).start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()