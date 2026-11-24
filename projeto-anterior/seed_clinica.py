"""
Script utilitário para inicializar e popular o banco local da Clínica Agenda
para os testes de desempenho (Trabalho 1) e testes funcionais (Trabalho 2).

Cria:
  - 1 usuário interno/admin: admin_avaliador / avaliador123
  - 3 especialidades: Cardiologia, Dermatologia, Ortopedia
  - 3 especialistas credenciados com agendas para todos os dias da semana (gerando horários disponíveis)
  - 30 pacientes (paciente01..paciente30 / SenhaForte123!)
"""
import os
import sys
from datetime import time
from pathlib import Path

# Aponta para a pasta do projeto Django (dentro do próprio repositório ou na pasta raiz)
_LOCAL_BACKEND = Path(__file__).resolve().parent / "backend"
DJANGO_DIR = _LOCAL_BACKEND if _LOCAL_BACKEND.exists() else (Path(__file__).resolve().parents[2] / "Teste-Tecnico_Backend-Django")
sys.path.insert(0, str(DJANGO_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

import django
from django.conf import settings

# Se USE_SQLITE=1 estiver definido, usa SQLite local para rodar sem depender de container Postgres externo
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

from django.core.management import call_command
from agendamentos.models import Agenda, Consulta, Especialidade, HorarioGerado
from agendamentos.services import criar_agenda
from usuarios.models import Especialista, Paciente, TipoUsuario, Usuario


def popular_dados():
    call_command("migrate", verbosity=0)

    # Limpa fisicamente os dados anteriores (contornando o soft-delete do CommonModel)
    for model in (Consulta, HorarioGerado, Agenda, Especialista, Paciente, Especialidade):
        model.all_objects.all()._raw_delete(model.all_objects.db)
    Usuario.objects.all().delete()

    # 1. Usuário Interno / Admin
    admin = Usuario.objects.create_superuser(
        username="admin_avaliador",
        email="admin@clinica.local",
        password="avaliador123",
        first_name="Admin",
        last_name="Avaliador",
        tipo_usuario=TipoUsuario.INTERNO,
        cpf="11122233344",
        telefone="11999990000",
    )

    # 2. Especialidades
    nomes_esp = ["Cardiologia", "Dermatologia", "Ortopedia"]
    especialidades = [
        Especialidade.objects.create(nome_especialidade=nome) for nome in nomes_esp
    ]

    # 3. Especialistas e Agendas
    medicos = [
        ("dra.ana", "Ana", "Silva", "52998224725", "CRM-SP 123456", especialidades[0]),
        ("dr.carlos", "Carlos", "Mendes", "12345678909", "CRM-SP 654321", especialidades[1]),
        ("dra.beatriz", "Beatriz", "Costa", "98765432100", "CRM-SP 112233", especialidades[2]),
    ]
    for username, fname, lname, cpf, crm, esp in medicos:
        u = Usuario.objects.create_user(
            username=username,
            email=f"{username}@clinica.local",
            password="SenhaForte123!",
            first_name=fname,
            last_name=lname,
            tipo_usuario=TipoUsuario.ESPECIALISTA,
            cpf=cpf,
            telefone="11988887777",
        )
        perfil_esp = Especialista.objects.create(usuario=u, especialidade=esp, crm=crm)
        # Cria agendas para 3 dias da semana garantindo dezenas de horários disponíveis
        for dia in (0, 2, 4):
            criar_agenda(
                especialista=perfil_esp,
                dias_semana=dia,
                hora_inicio_expediente=time(8, 0),
                hora_fim_expediente=time(12, 0),
                quantidade_vagas_dia=6,
            )

    # 4. Pacientes (paciente01 a paciente30)
    for i in range(1, 31):
        u_pac = Usuario.objects.create_user(
            username=f"paciente{i:02d}",
            email=f"paciente{i:02d}@clinica.local",
            password="SenhaForte123!",
            first_name=f"Paciente {i:02d}",
            last_name="Teste",
            tipo_usuario=TipoUsuario.PACIENTE,
            cpf=f"{10000000000 + i:011d}",
            telefone="11977776666",
        )
        Paciente.objects.create(usuario=u_pac)

    print(
        f"Seed concluído: {Especialidade.objects.count()} especialidades, "
        f"{Especialista.objects.count()} especialistas, "
        f"{HorarioGerado.objects.count()} horários gerados, "
        f"{Paciente.objects.count()} pacientes."
    )


if __name__ == "__main__":
    popular_dados()
