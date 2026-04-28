"""
사이트 새 게시글 모니터링 & 텔레그램 알림 봇
사용법: python site_monitor.py
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
import time
import json
import os
import hashlib
from datetime import datetime, timedelta
import sys
from dotenv import load_dotenv
import os
load_dotenv()

# ──────────────────────────────────────────
# ⚙️ 알림 시간 설정
# ──────────────────────────────────────────
NO_POST_ALERT_SECONDS = 3600
CHECK_INTERVAL_SECONDS = 10
TELEGRAM_RETRY_COUNT = 3  # 텔레그램 재시도 횟수
TELEGRAM_RETRY_DELAY = 2  # 재시도 간격 (초)

# ──────────────────────────────────────────
# 설정 파일 로드
# ──────────────────────────────────────────

CONFIG_FILE = "sites_config.json"
STATE_FILE = "monitor_state.json"

def load_config() -> dict:
    """설정 파일 로드"""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ {CONFIG_FILE} 파일을 찾을 수 없습니다!")
        sys.exit(1)
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"❌ {CONFIG_FILE} 파일 형식이 잘못되었습니다!")
        sys.exit(1)

CONFIG = load_config()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SITES = [s for s in CONFIG["sites"] if s.get("enabled", True)]

# ──────────────────────────────────────────
# Selenium 드라이버 설정
# ──────────────────────────────────────────

def create_driver():
    """Chrome 드라이버 생성"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"[Selenium 오류] Chrome 드라이버를 찾을 수 없습니다: {e}")
        sys.exit(1)

# ──────────────────────────────────────────
# 텔레그램 메시지 전송 (재시도 로직)
# ──────────────────────────────────────────

def send_telegram(message: str) -> bool:
    """텔레그램으로 메시지 전송 (재시도 포함)"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    
    for attempt in range(TELEGRAM_RETRY_COUNT):
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            return True
        except requests.exceptions.Timeout:
            if attempt < TELEGRAM_RETRY_COUNT - 1:
                print(f"[텔레그램 재시도] {attempt + 1}/{TELEGRAM_RETRY_COUNT} - {TELEGRAM_RETRY_DELAY}초 대기 중...")
                time.sleep(TELEGRAM_RETRY_DELAY)
            else:
                print(f"[텔레그램 오류] 최대 재시도 횟수 초과")
                return False
        except requests.exceptions.ConnectionError:
            if attempt < TELEGRAM_RETRY_COUNT - 1:
                print(f"[텔레그램 재시도] {attempt + 1}/{TELEGRAM_RETRY_COUNT} - {TELEGRAM_RETRY_DELAY}초 대기 중...")
                time.sleep(TELEGRAM_RETRY_DELAY)
            else:
                print(f"[텔레그램 오류] 네트워크 연결 실패")
                return False
        except Exception as e:
            print(f"[텔레그램 오류] {e}")
            return False
    
    return False

# ──────────────────────────────────────────
# Alert 처리
# ──────────────────────────────────────────

def handle_alert(driver):
    """페이지의 Alert가 있으면 처리"""
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        print(f"[Alert 처리] {alert_text}")
        time.sleep(1)
    except NoAlertPresentException:
        pass
    except Exception as e:
        print(f"[Alert 오류] {e}")

# ──────────────────────────────────────────
# 사이트 크롤링 (Selenium)
# ──────────────────────────────────────────

def fetch_posts(site: dict, driver) -> list[dict]:
    """Selenium으로 게시글 목록을 가져옴"""
    try:
        driver.get(site["url"])
        
        # Alert 처리
        handle_alert(driver)
        
        # 페이지 로딩 대기
        wait = WebDriverWait(driver, 10)
        
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, site["css_selector"])))
        except TimeoutException:
            print(f"[타임아웃] {site['name']}: CSS Selector '{site['css_selector']}'를 찾을 수 없습니다")
            return []
        
        # 게시글 요소 찾기
        elements = driver.find_elements(By.CSS_SELECTOR, site["css_selector"])
        posts = []
        
        for el in elements:
            try:
                # 링크 추출
                link = ""
                if site.get("link_selector"):
                    try:
                        a = el.find_element(By.CSS_SELECTOR, site["link_selector"])
                        href = a.get_attribute("href")
                        if href:
                            if not href.startswith("http"):
                                base_url = "/".join(site["url"].split("/")[:3])
                                link = base_url + href
                            else:
                                link = href
                    except:
                        pass
                
                # 제목 추출
                if site.get("title_selector"):
                    try:
                        title_el = el.find_element(By.CSS_SELECTOR, site["title_selector"])
                        title = title_el.text.strip()
                    except:
                        title = ""
                elif link:
                    try:
                        a = el.find_element(By.CSS_SELECTOR, site["link_selector"])
                        title = a.text.strip()
                    except:
                        title = ""
                else:
                    title = el.text.strip()
                
                if title and len(title) >= 2:
                    posts.append({"title": title, "link": link})
            except:
                continue
        
        return posts[:30]

    except Exception as e:
        print(f"[크롤링 오류] {site['name']}: {e}")
        return []

# ──────────────────────────────────────────
# 상태 저장/불러오기
# ──────────────────────────────────────────

def load_state() -> dict:
    """이전 상태 불러오기"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                old_state = json.load(f)
            
            new_state = {}
            for key, value in old_state.items():
                if isinstance(value, list):
                    new_state[key] = {
                        "hashes": value,
                        "last_new_post_time": now_timestamp(),
                        "last_post": None,
                        "no_post_alert_sent": False
                    }
                elif isinstance(value, dict):
                    if "last_post" not in value:
                        value["last_post"] = None
                    new_state[key] = value
            
            return new_state
        except:
            return {}
    return {}

def save_state(state: dict):
    """현재 상태 저장"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def normalize_post_key(post: dict) -> str:
    """
    게시글 고유값 생성.
    조회수/작성자/날짜가 바뀌어도 알림이 안 오게
    가능하면 링크를 기준으로 판단하고,
    링크가 없으면 제목 첫 줄만 사용.
    """
    link = post.get("link", "").strip()
    title = post.get("title", "").strip()

    if link:
        return link

    return title.splitlines()[0].strip()


def posts_to_hash_set(posts: list[dict]) -> set[str]:
    """게시글 목록을 해시 집합으로 변환"""
    return {
        hashlib.md5(normalize_post_key(p).encode("utf-8")).hexdigest()
        for p in posts
    }

# ──────────────────────────────────────────
# 시간 변환 함수
# ──────────────────────────────────────────

def format_alert_time(seconds: int) -> str:
    """초를 읽기 좋은 형식으로 변환"""
    if seconds < 60:
        return f"{seconds}초"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        if secs == 0:
            return f"{minutes}분"
        else:
            return f"{minutes}분 {secs}초"
    else:
        hours = seconds // 3600
        remaining = seconds % 3600
        minutes = remaining // 60
        secs = remaining % 60
        
        parts = [f"{hours}시간"]
        if minutes > 0:
            parts.append(f"{minutes}분")
        if secs > 0:
            parts.append(f"{secs}초")
        
        return " ".join(parts)

# ──────────────────────────────────────────
# 모니터링 로직
# ──────────────────────────────────────────

def check_site(site: dict, state: dict, driver) -> dict:
    """단일 사이트 체크"""
    name = site["name"]
    posts = fetch_posts(site, driver)
    
    if not posts:
        print(f"[{now()}] {name} — 게시글을 가져오지 못했습니다.")
        return state

    current_hashes = posts_to_hash_set(posts)
    
    # 사이트 상태 초기화
    if name not in state:
        state[name] = {
            "hashes": list(current_hashes),
            "last_new_post_time": now_timestamp(),
            "last_post": posts[0] if posts else None,
            "no_post_alert_sent": False
        }
        print(f"[{now()}] {name} — 초기화 완료 ({len(posts)}개 게시글 저장)")
        return state

    prev_hashes = set(state[name]["hashes"])
    new_hashes = current_hashes - prev_hashes
    
    if new_hashes:
        # 새 글 발견!
        new_posts = [p for p in posts if hashlib.md5(p["title"].encode()).hexdigest() in new_hashes]
        print(f"[{now()}] {name} — 새 글 {len(new_posts)}개 발견! 🎉")

        # 텔레그램 메시지
        msg_lines = [f"🔔 <b>{name}</b> 새 게시글 {len(new_posts)}개\n"]
        for p in new_posts[:5]:
            if p["link"]:
                msg_lines.append(f'• <a href="{p["link"]}">{p["title"]}</a>')
            else:
                msg_lines.append(f'• {p["title"]}')
        
        if len(new_posts) > 5:
            msg_lines.append(f"... 외 {len(new_posts)-5}개")
        
        msg_lines.append(f'\n🔗 <a href="{site["url"]}">게시판 바로가기</a>')

        send_telegram("\n".join(msg_lines))
        
        # 상태 업데이트
        state[name]["hashes"] = list(current_hashes)
        state[name]["last_new_post_time"] = now_timestamp()
        state[name]["last_post"] = new_posts[0]
        state[name]["no_post_alert_sent"] = False
    else:
        print(f"[{now()}] {name} — 변경 없음")
        
        # N초 동안 새 글이 없으면 알림
        last_time = state[name].get("last_new_post_time")
        if last_time:
            last_datetime = datetime.fromisoformat(last_time)
            elapsed = datetime.now() - last_datetime
            elapsed_seconds = elapsed.total_seconds()
            
            if elapsed_seconds >= NO_POST_ALERT_SECONDS:
                if not state[name].get("no_post_alert_sent", False):
                    last_post = state[name].get("last_post")
                    alert_time_str = format_alert_time(NO_POST_ALERT_SECONDS)
                    
                    if last_post:
                        if last_post.get("link"):
                            last_post_msg = f'<a href="{last_post["link"]}">{last_post["title"]}</a>'
                        else:
                            last_post_msg = last_post["title"]
                        
                        msg = (
                            f"⚠️ <b>{name}</b>\n\n"
                            f"{alert_time_str} 동안 새 게시글이 없습니다.\n\n"
                            f"마지막 글:\n"
                            f"{last_post_msg}\n\n"
                            f"마지막 업데이트: {last_time}"
                        )
                    else:
                        msg = (
                            f"⚠️ <b>{name}</b>\n\n"
                            f"{alert_time_str} 동안 새 게시글이 없습니다.\n"
                            f"마지막 업데이트: {last_time}"
                        )
                    
                    send_telegram(msg)
                    state[name]["no_post_alert_sent"] = True
                    print(f"[{now()}] {name} — {alert_time_str} 무글 알림 전송")
            else:
                state[name]["no_post_alert_sent"] = False

    return state

def now() -> str:
    """현재 시간 반환"""
    return datetime.now().strftime("%H:%M:%S")

def now_timestamp() -> str:
    """현재 시간을 ISO 형식으로 반환"""
    return datetime.now().isoformat()

# ──────────────────────────────────────────
# 메인 루프
# ──────────────────────────────────────────

def main():
    # 명령줄 인자 확인 (--reset 옵션)
    reset_state = "--reset" in sys.argv
    
    if reset_state and os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print(f"[초기화] {STATE_FILE} 파일을 삭제했습니다.\n")
    
    alert_time_str = format_alert_time(NO_POST_ALERT_SECONDS)
    
    print("=" * 60)
    print("  🚀 사이트 모니터링 시작")
    print("=" * 60)
    print(f"설정 파일: {CONFIG_FILE}")
    print(f"모니터링 사이트: {len(SITES)}개")
    print(f"무글 알림 시간: {alert_time_str}")
    print(f"체크 간격: {CHECK_INTERVAL_SECONDS}초")
    if reset_state:
        print(f"상태 초기화: ✓")
    print()

    # 텔레그램 연결 테스트
    if os.getenv("SEND_STARTUP_ALERT", "false").lower() == "true":
        site_list = "\n".join(f"• {s['name']} ({s['interval_minutes']}분마다)" for s in SITES)
        test_msg = (
            f"✅ 모니터링 시작!\n\n"
            f"⚙️ 설정:\n"
            f"• 무글 알림: {alert_time_str}\n"
            f"• 체크 간격: {CHECK_INTERVAL_SECONDS}초\n\n"
            f"📋 모니터링 사이트:\n{site_list}"
        )

        if send_telegram(test_msg):
            print("[✓] 텔레그램 연결 성공!\n")
        else:
            print("[⚠] 텔레그램 연결 실패\n")
    # Selenium 드라이버 생성
    driver = create_driver()
    
    state = load_state()
    timers = {s["name"]: 0 for s in SITES}

    try:
        while True:
            current_time = time.time()
            for site in SITES:
                elapsed = current_time - timers[site["name"]]
                if elapsed >= site["interval_minutes"] * 60:
                    state = check_site(site, state, driver)
                    save_state(state)
                    timers[site["name"]] = time.time()
            
            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n\n[⏹] 모니터링 중지됨")
        send_telegram("⏹ 모니터링이 중지되었습니다.")
        driver.quit()
        sys.exit(0)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
