"""
DESAFIO A - Trabalho 2: Portal de Matrícula Acadêmica (Selenium + pytest + Page Objects)

Cobre os 10 casos especificados na matriz (CT-A01 a CT-A10) para as regras R1 a R7:
  - CT-A01: R1 - Login válido abre a oferta de disciplinas
  - CT-A02: R1 - Login inválido (parametrizado: senha errada, matrícula inexistente, campos vazios)
  - CT-A03: R2 - Acesso direto a /matricula/disciplinas sem login redireciona para /matricula/login
  - CT-A04: R3 - Limite 0 disciplinas exibe 'Selecione ao menos uma disciplina.' e não altera vagas
  - CT-A05: R3/R7 - Limite 1 disciplina efetiva matrícula, gera COMP-NNNNNN e desconta 1 vaga
  - CT-A06: R3/R7 - Limite 5 disciplinas sem choque efetiva matrícula com as 5 listadas
  - CT-A07: R3 - Limite 6 disciplinas (acima do máximo) exibe 'Máximo de 5 disciplinas por semestre.'
  - CT-A08: R4 - Duas disciplinas no mesmo horário (ES3 e RED em SEG-19h) exibe erro de choque
  - CT-A09: R5 - Disciplina sem vagas (MOB esgotada via API) exibe 'Vagas esgotadas: MOB.'
  - CT-A10: R6 - Aluno já matriculado no semestre (via API) exibe 'Aluno já possui matrícula neste semestre.'
"""
import re
import pytest
import requests
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.matricula_pages import ComprovantePage, DisciplinasPage, LoginMatriculaPage


@pytest.fixture(autouse=True)
def sistema_zerado(base_url):
    """Garante independência total entre os testes zerando o estado via API antes de cada caso."""
    resp = requests.post(f"{base_url}/api/admin/reset", timeout=5)
    assert resp.status_code == 200


def test_ct_a01_login_valido(driver, base_url):
    LoginMatriculaPage(driver, base_url).abrir().entrar("20260001", "senha123")
    oferta = DisciplinasPage(driver, base_url)
    assert oferta.esta_aberta()
    assert oferta.usuario_logado() == "20260001"


@pytest.mark.parametrize(
    "matricula,senha",
    [
        ("20260001", "senha_errada"),
        ("99999999", "senha123"),
        ("", "senha123"),
    ],
)
def test_ct_a02_login_invalido(driver, base_url, matricula, senha):
    login = LoginMatriculaPage(driver, base_url).abrir().entrar(matricula, senha)
    assert login.mensagem_erro() == "Matrícula ou senha inválidas."
    assert driver.current_url.endswith("/matricula/login")


def test_ct_a03_acesso_sem_login_redireciona(driver, base_url):
    DisciplinasPage(driver, base_url).abrir_direto()
    WebDriverWait(driver, 5).until(EC.url_contains("/matricula/login"))
    assert driver.current_url.endswith("/matricula/login")


def test_ct_a04_zero_disciplinas_exibe_erro(driver, base_url):
    LoginMatriculaPage(driver, base_url).abrir().entrar("20260001", "senha123")
    oferta = DisciplinasPage(driver, base_url)
    vagas_antes = oferta.vagas_da_disciplina("ES3")

    oferta.confirmar()

    assert oferta.mensagem_erro() == "Selecione ao menos uma disciplina."
    assert oferta.vagas_da_disciplina("ES3") == vagas_antes


def test_ct_a05_uma_disciplina_sucesso_e_desconta_vaga(driver, base_url):
    LoginMatriculaPage(driver, base_url).abrir().entrar("20260001", "senha123")
    oferta = DisciplinasPage(driver, base_url)
    vagas_iniciais = oferta.vagas_da_disciplina("ES3")

    oferta.selecionar_disciplinas(["ES3"]).confirmar()

    comprovante = ComprovantePage(driver)
    assert comprovante.mensagem_sucesso() == "Matrícula realizada com sucesso!"
    assert re.fullmatch(r"COMP-\d{6}", comprovante.codigo_comprovante())
    assert comprovante.disciplinas_listadas() == ["ES3"]

    # Reabre a tela de disciplinas para comprovar que 1 vaga foi descontada na interface
    oferta.abrir_direto()
    assert oferta.vagas_da_disciplina("ES3") == vagas_iniciais - 1


def test_ct_a06_cinco_disciplinas_limite_maximo_sucesso(driver, base_url):
    LoginMatriculaPage(driver, base_url).abrir().entrar("20260002", "senha123")
    oferta = DisciplinasPage(driver, base_url)
    grade_5 = ["ES3", "BD2", "PW2", "IHC", "EMP"]

    oferta.selecionar_disciplinas(grade_5).confirmar()

    comprovante = ComprovantePage(driver)
    assert comprovante.mensagem_sucesso() == "Matrícula realizada com sucesso!"
    assert re.fullmatch(r"COMP-\d{6}", comprovante.codigo_comprovante())
    assert comprovante.disciplinas_listadas() == grade_5


def test_ct_a07_seis_disciplinas_acima_do_limite_exibe_erro(driver, base_url):
    LoginMatriculaPage(driver, base_url).abrir().entrar("20260003", "senha123")
    oferta = DisciplinasPage(driver, base_url)
    vagas_mob_antes = oferta.vagas_da_disciplina("MOB")

    oferta.selecionar_disciplinas(["ES3", "BD2", "PW2", "IHC", "EMP", "MOB"]).confirmar()

    assert oferta.mensagem_erro() == "Máximo de 5 disciplinas por semestre."
    assert oferta.vagas_da_disciplina("MOB") == vagas_mob_antes


def test_ct_a08_choque_de_horario_exibe_erro(driver, base_url):
    LoginMatriculaPage(driver, base_url).abrir().entrar("20260004", "senha123")
    oferta = DisciplinasPage(driver, base_url)
    vagas_es3_antes = oferta.vagas_da_disciplina("ES3")
    vagas_red_antes = oferta.vagas_da_disciplina("RED")

    # ES3 e RED ocorrem ambas em SEG-19h
    oferta.selecionar_disciplinas(["ES3", "RED"]).confirmar()

    assert oferta.mensagem_erro() == "Choque de horário entre disciplinas selecionadas."
    assert oferta.vagas_da_disciplina("ES3") == vagas_es3_antes
    assert oferta.vagas_da_disciplina("RED") == vagas_red_antes


def test_ct_a09_disciplina_sem_vagas_exibe_erro(driver, base_url):
    # Prepara pela API a ocupação das 5 vagas da disciplina MOB
    for idx in range(1, 6):
        r = requests.post(
            f"{base_url}/api/matriculas",
            json={"aluno": f"2026000{idx}", "disciplinas": ["MOB"]},
            timeout=5,
        )
        assert r.status_code == 201

    LoginMatriculaPage(driver, base_url).abrir().entrar("20260010", "senha123")
    oferta = DisciplinasPage(driver, base_url)
    assert oferta.vagas_da_disciplina("MOB") == 0

    oferta.selecionar_disciplinas(["MOB"]).confirmar()

    assert oferta.mensagem_erro() == "Vagas esgotadas: MOB."
    assert oferta.vagas_da_disciplina("MOB") == 0


def test_ct_a10_aluno_ja_matriculado_exibe_erro(driver, base_url):
    # Prepara matrícula prévia para o aluno 20260001 via API
    r = requests.post(
        f"{base_url}/api/matriculas",
        json={"aluno": "20260001", "disciplinas": ["ES3"]},
        timeout=5,
    )
    assert r.status_code == 201

    LoginMatriculaPage(driver, base_url).abrir().entrar("20260001", "senha123")
    oferta = DisciplinasPage(driver, base_url)
    vagas_bd2_antes = oferta.vagas_da_disciplina("BD2")

    oferta.selecionar_disciplinas(["BD2"]).confirmar()

    assert oferta.mensagem_erro() == "Aluno já possui matrícula neste semestre."
    assert oferta.vagas_da_disciplina("BD2") == vagas_bd2_antes
