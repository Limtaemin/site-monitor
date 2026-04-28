# Site Monitor Telegram Bot

웹사이트 게시판의 새 게시글을 감지해서 텔레그램으로 알림을 보내는 Python 모니터링 봇입니다.

---

## 📌 기능

- 여러 사이트 동시 모니터링
- 새 게시글 자동 감지
- 텔레그램 알림 전송
- Render 서버 24시간 실행 가능
- UptimeRobot으로 서버 sleep 방지
- 사용자별 텔레그램 봇 사용 가능

---

## 📂 프로젝트 구조

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

## 🚀 설치 방법

### 1. 다운로드

```bash
git clone https://github.com/Limtaemin/site-monitor.git
cd site-monitor
```

또는 ZIP 다운로드 후 압축 해제

---

### 2. Python 설치 확인

```bash
python --version
```
---

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```
---

## 🤖 텔레그램 봇 만들기

### 1. BotFather
- 텔레그램에서 `BotFather` 검색
- `/newbot` 입력
- 이름 설정
- 토큰 복사

---

### 2. Chat ID 확인
1. 봇에게 메시지 보내기  
2. 아래 주소 접속

```
https://api.telegram.org/bot<토큰>/getUpdates
```

3. 결과에서:
```
"chat":{"id": 123456789}
```
→ 이 숫자가 chat_id

---
## 🔑 환경 변수 설정
### Windows

```cmd
copy .env.example .env
```
`.env` 수정:
```
TELEGRAM_BOT_TOKEN=여기에_토큰
TELEGRAM_CHAT_ID=여기에_chat_id
SEND_STARTUP_ALERT=false
```
---
## 🌐 사이트 설정
모니터링할 사이트는 `sites_config.json`에 저장됩니다.
예시:

```json
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

각 항목 의미:
| 항목 | 설명 |
|---|---|
| `name` | 텔레그램 알림에 표시될 사이트 이름 |
| `url` | 감시할 게시판 주소 |
| `css_selector` | 게시글 목록에서 “게시글 한 줄 전체”를 잡는 선택자 |
| `link_selector` | `css_selector`로 잡은 게시글 안에서 링크 `<a>`를 찾는 선택자 |
| `title_selector` | `css_selector`로 잡은 게시글 안에서 제목 텍스트를 찾는 선택자 |
| `interval_minutes` | 몇 분마다 이 사이트를 확인할지 |
| `enabled` | `true`면 감시함, `false`면 감시하지 않음 |

가장 중요한 것은 `css_selector`입니다.  
이 값은 게시글 하나만 잡는 게 아니라, 게시글 목록의 각 줄을 반복해서 잡아야 합니다.

좋은 예:
```text
table tbody tr
.board-list li
.post-item
```

나쁜 예:
```text
body > div > div:nth-child(3) > ul > li:nth-child(1) > a
```

`nth-child(1)`처럼 특정 순서를 가리키는 선택자는 게시글 순서가 바뀌면 쉽게 깨질 수 있습니다.

---

## 🔍 CSS Selector 찾기
CSS Selector는 브라우저 개발자 도구로 찾을 수 있습니다.

### 기본 방법
1. 감시할 게시판 사이트에 접속합니다.
2. 키보드에서 `F12`를 누릅니다.
3. 게시글 제목 또는 게시글 한 줄에 마우스를 올립니다.
4. 우클릭 → `검사`를 누릅니다.
5. 개발자 도구에서 해당 HTML 요소가 선택됩니다.
6. 선택된 요소에서 우클릭합니다.
7. `Copy` → `Copy selector`를 누릅니다.
8. 복사된 값을 `sites_config.json`에 넣습니다.

---
### 어떤 요소를 잡아야 하나?
게시글 제목 하나만 잡기보다, 가능하면 **게시글 한 줄 전체**를 잡는 것이 좋습니다.

예를 들어 게시판 HTML이 아래처럼 되어 있다면:

```html
<table>
  <tbody>
    <tr>
      <td><a href="/post/1">첫 번째 글</a></td>
    </tr>
    <tr>
      <td><a href="/post/2">두 번째 글</a></td>
    </tr>
  </tbody>
</table>
```

이 경우 설정은 보통 이렇게 합니다.
```json
{
  "css_selector": "table tbody tr",
  "link_selector": "a",
  "title_selector": "a"
}
```

의미:
```text
css_selector   → 게시글 줄 전체인 tr들을 찾음
link_selector  → 각 tr 안에서 a 태그를 찾음
title_selector → 각 tr 안에서 a 태그의 텍스트를 제목으로 사용
```

---

### 리스트 구조 사이트 예시
HTML이 아래처럼 되어 있다면:
```html
<ul class="board-list">
  <li>
    <div class="title">
      <a href="/notice/1">공지사항 1</a>
    </div>
  </li>
  <li>
    <div class="title">
      <a href="/notice/2">공지사항 2</a>
    </div>
  </li>
</ul>
```

설정은 이렇게 할 수 있습니다.
```json
{
  "css_selector": ".board-list li",
  "link_selector": ".title a",
  "title_selector": ".title a"
}
```

의미:
```text
css_selector   → 게시글 하나하나인 li를 찾음
link_selector  → li 안에서 .title a 링크를 찾음
title_selector → li 안에서 .title a 텍스트를 제목으로 사용
```

---

## ⚙️ config_generator.py 사용
`config_generator.py`는 `sites_config.json`을 직접 수정하기 어려운 사용자를 위한 설정 도우미입니다.

실행:
```bash
python config_generator.py
```

Windows CMD에서는 프로젝트 폴더에서 실행합니다.
```cmd
cd C:\site-monitor
python config_generator.py
```

실행하면 메뉴가 나옵니다.
```text
1. 새 사이트 추가
2. 기존 사이트 보기
3. 사이트 삭제
4. 저장 및 종료
```

---

### 새 사이트 추가 방법

메뉴에서 `1`을 입력합니다.
입력 예시:
```text
사이트 이름: 부산대 기계공학부 공지
URL: https://me.pusan.ac.kr/new/sub05/sub01_05.php
전체 CSS Selector: table tbody tr
체크 간격: 1
```

저장하면 `sites_config.json`에 사이트가 추가됩니다.

---
### config_generator.py가 하는 일
사용자가 입력한 CSS Selector를 바탕으로 아래 값을 만들어줍니다.

```json
{
  "name": "사이트 이름",
  "url": "게시판 주소",
  "css_selector": "게시글 목록 선택자",
  "link_selector": "a",
  "interval_minutes": 1,
  "enabled": true
}
```

즉, 사용자가 개발자 도구에서 복사한 selector를 넣으면 프로그램이 최대한 자동으로 `css_selector`와 `link_selector`를 나누려고 합니다.

다만 사이트마다 HTML 구조가 다르기 때문에, 자동 생성 결과가 항상 완벽하지는 않습니다.
---

### 추가 후 확인하기
사이트를 추가한 뒤 메뉴에서 `2`를 입력하면 현재 등록된 사이트 목록을 볼 수 있습니다.

```text
2. 기존 사이트 보기
```

확인할 것:
```text
URL이 맞는지
CSS Selector가 너무 길지 않은지
체크 간격이 맞는지
enabled가 true인지
```
---
### 직접 수정이 필요한 경우
`config_generator.py`로 추가했는데 감지가 안 되면 `sites_config.json`을 직접 열어서 수정합니다.

예를 들어 자동 생성 결과가 너무 길게 나오면:

```text
body > div > div:nth-child(2) > table > tbody > tr:nth-child(1) > td > a
```

이걸 더 일반적인 형태로 바꿉니다.

```text
table tbody tr
```

그리고 링크와 제목은 보통 아래처럼 둡니다.

```json
"link_selector": "a",
"title_selector": "a"
```
---
### 설정 테스트
설정 후 실행합니다.

```bash
python site_monitor.py
```

정상이라면 콘솔에 아래처럼 나옵니다.
```text
부산대 공지 — 초기화 완료
부산대 공지 — 변경 없음
```
만약 아래처럼 나오면 selector가 잘못된 것입니다.
```text
CSS Selector를 찾을 수 없습니다
게시글을 가져오지 못했습니다
```

이 경우 다시 개발자 도구에서 selector를 확인해야 합니다.
## ▶️ 실행
```bash
python site_monitor.py
```
초기화:
```bash
python site_monitor.py --reset
```

---
## ☁️ Render 배포

### 설정
```
Runtime: Python
Build: pip install -r requirements.txt
Start: gunicorn app:app
```
---
### 환경변수 설정
```
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
SEND_STARTUP_ALERT=false
```
---

## 💤 서버 안 꺼지게 하기
### UptimeRobot

https://uptimerobot.com

설정:
```
Type: HTTP
URL: https://your-render-url.onrender.com
Interval: 5 minutes
```

---
## 🚫 GitHub에 올리면 안 되는 것

```
.env
monitor_state.json
__pycache__/
*.pyc
```

---
## ❗ 문제 해결
### 시작 알림 계속 옴

```
SEND_STARTUP_ALERT=false
```

---
### 중복 알림
```
monitor_state.json 초기화됨
```

---
### selector 오류
- nth-child 제거
- 너무 긴 selector 금지

---
### Render 크롤링 실패
로그 확인:
```
selenium
chrome
timeout
```

---
## 🔐 보안
- 토큰 절대 공유 금지
- .env GitHub 업로드 금지

---
## 📌 사용 흐름
### 로컬

```
설치 → .env 작성 → 실행
```
### 서버
```
GitHub → Render → UptimeRobot
```

---
## License
Free for personal use