import socket
import sys
import threading
import time

import pytest
import uvicorn
from playwright.sync_api import sync_playwright

from app import database, main

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def _browser_launch_kwargs() -> dict:
    # Windows: use the locally installed Edge; other platforms (e.g. the Ubuntu
    # GitHub Actions runner): let Playwright use its bundled Chromium.
    kwargs: dict = {"headless": True}
    if sys.platform == "win32":
        kwargs["executable_path"] = EDGE_PATH
    return kwargs


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def live_server(tmp_path, monkeypatch):
    db_path = tmp_path / "e2e.db"
    database.initialize(db_path)
    monkeypatch.setattr(main, "DB_PATH", db_path)

    port = _free_port()
    config = uvicorn.Config(main.app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    for _ in range(100):
        if server.started:
            break
        time.sleep(0.1)

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(**_browser_launch_kwargs())
        context = browser.new_context()
        yield context
        context.close()
        browser.close()


@pytest.fixture
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()
