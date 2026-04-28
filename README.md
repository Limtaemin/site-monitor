# Site Monitor Telegram Bot

사이트 게시글 변화를 감지해서 텔레그램으로 알림을 보내는 Python 모니터링 봇입니다.

---

## 기능

* 여러 사이트 동시 모니터링
* 새 게시글 감지 시 텔레그램 알림 전송
* CSS Selector 기반 게시글 추출
* Render 서버 배포 가능
* UptimeRobot을 이용한 서버 슬립 방지
* 사용자별 텔레그램 봇 토큰 사용 가능

---

## 파일 구성

```
site-monitor/
├─ site_monitor.py
├─ app.py
├─ config_generator.py
├─ sites_config.json
├─ monitor_state.json
├─ requirements.txt
├─ Procfile
├─ .env.example
├─ .gitignore
└─ README.md
```

---

## 1. 설치

```
git clone https://github.com/Limtaemin/site-monitor.git
cd site-monitor
pip install -r requirements.txt
```

---

## 2. 텔레그램 봇 준비

### Bot Token 발급

1. 텔레그램에서 `BotFather` 검색
2. `/newbot` 입력
3. 봇 생성
4. 토큰 복사

### Chat ID 확인

1. 봇에게 아무 메시지 전송
2. 아래 주소 접속

```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

3. `"chat":{"id": ... }` 값 확인

---

## 3. 환경변수 설정

```
copy .env.example .env
```

`.env` 파일 내용:

```
TELEGRAM_BOT_TOKEN=YOUR_TOKEN
TELEGRAM_CHAT_ID=YOUR_CHAT_ID
SEND_STARTUP_ALERT=false
```

---

## 4. 사이트 설정

`sites_config.json` 수정:

```
{
  "sites": [
    {
      "name": "부산대 공지",
      "url": "https://me.pusan.ac.kr/new/sub05/sub01_05.php",
      "css_selector": "table tbody tr",
      "link_selector": "a",
      "title_selector": "a",
      "interval_minutes": 1,
      "enabled": true
    }
  ]
}
```

---

## 5. CSS Selector 찾기

1. 사이트 접속
2. F12
3. 게시글 우클릭 → 검사
4. 우클릭 → Copy → Copy selector

---

## 6. config_generator.py 사용

```
python config_generator.py
```

메뉴:

```
1. 새 사이트 추가
2. 기존 사이트 보기
3. 사이트 삭제
4. 저장 및 종료
```

---

## 7. 실행

```
python site_monitor.py
```

초기화:

```
python site_monitor.py --reset
```

---

## 8. Render 배포

### 설정

```
Runtime: Python
Build: pip install -r requirements.txt
Start: gunicorn app:app
```

### 환경변수

```
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
SEND_STARTUP_ALERT=false
```

---

## 9. 서버 안 꺼지게 하기

### UptimeRobot

1. https://uptimerobot.com
2. Add Monitor

설정:

```
Type: HTTP
URL: https://your-render-url.onrender.com
Interval: 5 minutes
```

---

## 10. GitHub에 올리면 안 되는 파일

```
.env
monitor_state.json
__pycache__/
*.pyc
```

---

## 11. 문제 해결

### 시작 알림 반복

```
SEND_STARTUP_ALERT=false
```

---

### 중복 알림

```
monitor_state.json 초기화 문제
```

---

### CSS Selector 오류

* 너무 구체적인 selector 사용 금지
* nth-child 제거

---

### Render에서 크롤링 안됨

로그 확인:

```
selenium
chrome
timeout
```

---

## 12. 주의

* 토큰 공유 금지
* .env 업로드 금지
* 무료 서버는 재시작될 수 있음

---

## License

Free for personal use
