"""
Inicia o servidor local unificado da Clínica Agenda (API Django REST + Frontend Vue 3 SPA)
na porta 8001 com banco SQLite local para os testes funcionais (Selenium).
"""
import mimetypes
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DJANGO_DIR = BASE_DIR / "backend"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
sys.path.insert(0, str(DJANGO_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1")

import django
from django.conf import settings

if os.getenv("USE_SQLITE", "1") == "1":
    settings.DATABASES["default"].update({
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DJANGO_DIR / "db_teste_local.sqlite3"),
        "OPTIONS": {"timeout": 30},
    })
    settings.PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
        "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    ]

django.setup()

from django.http import FileResponse, HttpResponse, JsonResponse
from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt
import setup.urls as setup_urls
from seed_clinica import popular_dados


@csrf_exempt
def api_reset_view(request):
    """Endpoint utilitário para restaurar rapidamente o estado inicial entre os testes funcionais."""
    from agendamentos.models import Consulta, Especialidade, HorarioGerado, StatusHorario

    Consulta.all_objects.all()._raw_delete(Consulta.all_objects.db)
    HorarioGerado.all_objects.all().update(status=StatusHorario.DISPONIVEL, ativo=True)
    Especialidade.all_objects.exclude(
        nome_especialidade__in=["Cardiologia", "Dermatologia", "Ortopedia"]
    )._raw_delete(Especialidade.all_objects.db)
    Especialidade.all_objects.filter(
        nome_especialidade__in=["Cardiologia", "Dermatologia", "Ortopedia"]
    ).update(ativo=True)
    return JsonResponse({"status": "resetado"})


def spa_view(request, resource=""):
    """Serve os arquivos estáticos do build do Vue (frontend/dist) ou fallback para index.html."""
    caminho = (FRONTEND_DIST / resource.lstrip("/")).resolve()
    if resource and caminho.is_file() and str(caminho).startswith(str(FRONTEND_DIST.resolve())):
        ctype, _ = mimetypes.guess_type(str(caminho))
        return FileResponse(open(caminho, "rb"), content_type=ctype or "application/octet-stream")
    index_file = FRONTEND_DIST / "index.html"
    return HttpResponse(index_file.read_bytes(), content_type="text/html; charset=utf-8")


setup_urls.urlpatterns = [
    re_path(r"^api/reset-teste/$", api_reset_view),
    *setup_urls.urlpatterns,
    re_path(r"^(?P<resource>.*)$", spa_view),
]

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    porta = os.getenv("PORTA_CLINICA", "8001")
    execute_from_command_line(["manage.py", "runserver", f"127.0.0.1:{porta}", "--noreload"])
