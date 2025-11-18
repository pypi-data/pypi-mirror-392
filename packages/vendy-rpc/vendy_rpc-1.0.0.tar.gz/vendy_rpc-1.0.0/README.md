# Vendy RPC Modules

Discord RPC 모듈 - Discord Gateway WebSocket을 통한 Rich Presence 관리

## 설치

```bash
pip install vendy-rpc-modules
```

## 사용법

### 기본 사용

```python
from Vendy_RPC_modules import RPCManager, RPCConfig, RPCUser

# 설정
CONFIG: RPCConfig = {
    "RESTART_INTERVAL_MS": 10 * 60 * 1000,  # 10분
    "STATUS_CHECK_INTERVAL_MS": 60 * 1000,  # 1분
    "LOGIN_RETRIES": 3,
    "LOGIN_RETRY_DELAY_MS": 5000,
}

# 사용자 데이터
USERS: list[RPCUser] = [
    {
        "userID": "YOUR_USER_ID",
        "token": "YOUR_DISCORD_TOKEN",
        "name": "사용자 이름",
        "type": "PLAYING",
        "state": "상태 텍스트",
        "details": "상세 정보",
        "large_image": "",
        "largete": "",
        "small_image": "",
        "smallte": "",
        "button1": "",
        "button1link": "",
        "button2": "",
        "button2link": "",
    },
]

# 실행
if __name__ == "__main__":
    manager = RPCManager(config=CONFIG, users=USERS)
    manager.run()
```

### 고급 사용

```python
from Vendy_RPC_modules import Client, RichPresence, ActivityType

# 단일 클라이언트 사용
client = Client()
client.on('ready', lambda: print("준비 완료!"))
client.on('error', lambda err: print(f"오류: {err}"))

client.login("YOUR_DISCORD_TOKEN")

# Rich Presence 설정
presence = RichPresence(client)
presence.set_application_id("817229550684471297")
presence.set_type(ActivityType.PLAYING)
presence.set_state("게임 중")
presence.set_details("상세 정보")
presence.set_assets_large_image("image_key")
presence.add_button("버튼", "https://example.com")

client.user['setActivity'](presence)
```

## 기능

- ✅ Discord Gateway WebSocket을 통한 Rich Presence 관리
- ✅ 여러 클라이언트 동시 관리
- ✅ 자동 재시작 기능
- ✅ 상태 확인 루프
- ✅ 로그인 재시도 로직
- ✅ 타입 힌트 지원 (IDE 자동완성)

## 요구사항

- Python 3.7 이상
- websocket-client >= 1.6.0

## 라이선스

MIT License

## 기여

이슈 및 풀 리퀘스트를 환영합니다!

