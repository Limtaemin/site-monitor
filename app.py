import threading
import time
from flask import Flask

app = Flask(__name__)

monitor_started = False


def run_monitor():
    import site_monitor
    site_monitor.main()


def start_monitor_once():
    global monitor_started

    if not monitor_started:
        monitor_started = True
        t = threading.Thread(target=run_monitor, daemon=True)
        t.start()
        print("[APP] site_monitor 백그라운드 실행 시작")


@app.route("/")
def home():
    start_monitor_once()
    return "site-monitor alive"


@app.route("/health")
def health():
    start_monitor_once()
    return "ok"


# Render에서 앱이 import될 때 모니터 시작
start_monitor_once()