"""
Configuração compartilhada do pytest (fixtures) para o Desafio A - Portal de Matrícula.
"""
import os
import pathlib

import pytest
from selenium import webdriver

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def driver(request):
    opcoes = webdriver.ChromeOptions()
    if os.getenv("HEADLESS", "1") == "1":
        opcoes.add_argument("--headless=new")
    if os.getenv("CI") == "1":
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=opcoes)
    drv.implicitly_wait(0)  # Apenas esperas explícitas (WebDriverWait)
    yield drv
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        pasta = pathlib.Path("evidencias")
        pasta.mkdir(exist_ok=True)
        drv.save_screenshot(str(pasta / f"{request.node.name}.png"))
    drv.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
