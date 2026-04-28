import json
import os
from pathlib import Path

def generate_config():
    """사용자 입력으로 sites_config.json 생성"""
    
    config_file = "sites_config.json"
    
    # 기존 설정 로드 (있으면)
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {
            "telegram": {
                "bot_token": "8329873618:AAEwkyoYYE_2TJ4sCS9T2jxk1C5T1EYwDI0",
                "chat_id": "7659807850"
            },
            "sites": []
        }
    
    print("=" * 60)
    print("🔧 사이트 모니터링 설정 생성기")
    print("=" * 60)
    
    while True:
        print("\n[옵션]")
        print("1. 새 사이트 추가")
        print("2. 기존 사이트 보기")
        print("3. 사이트 삭제")
        print("4. 저장 및 종료")
        
        choice = input("\n선택: ").strip()
        
        if choice == "1":
            add_site(config)
        elif choice == "2":
            view_sites(config)
        elif choice == "3":
            delete_site(config)
        elif choice == "4":
            save_config(config, config_file)
            break
        else:
            print("❌ 잘못된 선택입니다.")

def add_site(config: dict):
    """새 사이트 추가"""
    print("\n" + "=" * 60)
    print("➕ 새 사이트 추가")
    print("=" * 60)
    
    # 사이트 이름
    name = input("\n📌 사이트 이름 (예: 부산대 기계공학부): ").strip()
    if not name:
        print("❌ 사이트 이름을 입력해주세요.")
        return
    
    # URL
    url = input("🔗 URL (예: https://me.pusan.ac.kr/...): ").strip()
    if not url:
        print("❌ URL을 입력해주세요.")
        return
    
    # 전체 CSS Selector (자동 파싱)
    print("\n📋 전체 CSS Selector 입력 방법:")
    print("   1. F12를 눌러 개발자 도구 열기")
    print("   2. 게시글 제목 링크에 우클릭 → '검사' 클릭")
    print("   3. 우클릭 → 'Copy' → 'Copy selector' 선택")
    print("   4. 아래에 붙여넣기\n")
    
    full_selector = input("📍 전체 CSS Selector: ").strip()
    if not full_selector:
        print("❌ CSS Selector를 입력해주세요.")
        return
    
    # 자동 파싱: full_selector에서 css_selector와 link_selector 분리
    css_selector, link_selector = parse_selector(full_selector)
    
    # Interval (기본값 5분)
    interval_input = input("\n⏱️  체크 간격 (분, 기본값: 5): ").strip()
    interval_minutes = 5
    if interval_input:
        try:
            interval_minutes = int(interval_input)
        except ValueError:
            print("⚠️  숫자가 아니므로 기본값(5분)으로 설정합니다.")
    
    # 새 사이트 추가
    new_site = {
        "name": name,
        "url": url,
        "css_selector": css_selector,
        "link_selector": link_selector,
        "interval_minutes": interval_minutes,
        "enabled": True
    }
    
    config["sites"].append(new_site)
    print(f"\n✅ '{name}' 사이트가 추가되었습니다!")
    print(f"   - URL: {url}")
    print(f"   - CSS Selector: {css_selector}")
    print(f"   - Link Selector: {link_selector}")
    print(f"   - 체크 간격: {interval_minutes}분")

# 새로운 파싱 함수 추가
def parse_selector(full_selector: str) -> tuple[str, str]:
    """
    전체 selector를 css_selector와 link_selector로 분리
    예: "#fboardlist > div > ul > li:nth-child(2) > div.td_subject > div > a"
    결과: ("#fboardlist > div > ul > li", "div.td_subject > div > a")
    """
    # :nth-child(n) 제거
    import re
    cleaned = re.sub(r':nth-child$$\d+$$', '', full_selector)
    
    # 마지막 > a 분리
    if ' > a' in cleaned:
        parts = cleaned.rsplit(' > a', 1)
        css_selector = parts[0].strip()
        link_selector = 'a'  # 간단하게 'a'만 사용
    elif cleaned.endswith('a'):
        parts = cleaned.rsplit('>', 1)
        css_selector = parts[0].strip()
        link_selector = parts[1].strip()
    else:
        # a 태그가 없으면 전체를 css_selector로
        css_selector = cleaned
        link_selector = 'a'
    
    return css_selector, link_selector

def view_sites(config: dict):
    """기존 사이트 보기"""
    if not config["sites"]:
        print("\n❌ 등록된 사이트가 없습니다.")
        return
    
    print("\n" + "=" * 60)
    print("📋 등록된 사이트 목록")
    print("=" * 60)
    
    for i, site in enumerate(config["sites"], 1):
        status = "✅ 활성" if site.get("enabled", True) else "❌ 비활성"
        print(f"\n[{i}] {site['name']} {status}")
        print(f"    URL: {site['url']}")
        print(f"    CSS Selector: {site['css_selector']}")
        print(f"    Link Selector: {site['link_selector']}")
        print(f"    체크 간격: {site['interval_minutes']}분")

def delete_site(config: dict):
    """사이트 삭제"""
    if not config["sites"]:
        print("\n❌ 등록된 사이트가 없습니다.")
        return
    
    view_sites(config)
    
    try:
        idx = int(input("\n삭제할 사이트 번호: ")) - 1
        if 0 <= idx < len(config["sites"]):
            deleted = config["sites"].pop(idx)
            print(f"\n✅ '{deleted['name']}'이(가) 삭제되었습니다.")
        else:
            print("❌ 잘못된 번호입니다.")
    except ValueError:
        print("❌ 숫자를 입력해주세요.")

def save_config(config: dict, config_file: str):
    """설정 저장"""
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 설정이 '{config_file}'에 저장되었습니다!")

if __name__ == "__main__":
    generate_config()