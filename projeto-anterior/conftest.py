"""
Configuração compartilhada do pytest (fixtures) para o Projeto Anterior - Clínica Agenda (Vue + Django).
"""
import os
import pathlib
import re

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8001")


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    if os.environ.get("HEADLESS", "1") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    if os.environ.get("CHROME_BINARY"):
        options.binary_location = os.environ["CHROME_BINARY"]
    service = Service(os.environ["CHROMEDRIVER"]) if os.environ.get("CHROMEDRIVER") else Service()
    browser = webdriver.Chrome(options=options, service=service)
    browser.implicitly_wait(0)
    yield browser
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        dest = pathlib.Path("evidencias")
        dest.mkdir(exist_ok=True)
        name = re.sub(r"[^a-zA-Z0-9_-]", "_", request.node.nodeid)
        browser.save_screenshot(str(dest / (name + ".png")))
    browser.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
