"""
PROJETO ANTERIOR - Trabalho 2: Clínica Agenda (Vue 3 + Django REST)
Suíte de testes funcionais E2E com Selenium + pytest + Page Objects.

Cobre 2 fluxos completos e 8 casos de teste (CT-C01 a CT-C08):
  Fluxo 1 - Autenticação JWT e Controle de Acesso por Perfil:
    - CT-C01: Login válido com perfil interno carrega painel de Gestão interna
    - CT-C02: Login com senha inválida exibe alerta de erro e permanece em /entrar
    - CT-C03: Acesso direto a /painel sem sessão autenticada redireciona para /entrar
    - CT-C04: Logout encerra a sessão e redireciona para a página inicial
  Fluxo 2 - Gestão de Especialidades e Agendamento de Consultas:
    - CT-C05: Cadastro de nova especialidade ('Neurologia') pelo usuário interno
    - CT-C06: Rejeição de especialidade duplicada case-insensitive ('cardiologia') sem duplicar registro
    - CT-C07: Paciente filtra horários disponíveis por especialidade ('Cardiologia')
    - CT-C08: Paciente realiza agendamento completo de consulta pelo modal e visualiza em Minhas consultas
"""
import pytest
import requests
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.clinica_pages import LoginClinicaPage, PainelInternoPage, PainelPacientePage


@pytest.fixture(autouse=True)
def resetar_banco_clinica(base_url):
    """Restaura o estado inicial do banco de dados da Clínica Agenda via API antes de cada teste."""
    resp = requests.post(f"{base_url}/api/reset-teste/", timeout=15)
    assert resp.status_code == 200


# ===========================================================================
# FLUXO 1: AUTENTICAÇÃO E CONTROLE DE ACESSO (CT-C01 a CT-C04)
# ===========================================================================
def test_ct_c01_login_interno_valido(driver, base_url):
    LoginClinicaPage(driver, base_url).abrir().entrar("admin_avaliador", "avaliador123")
    painel = PainelInternoPage(driver).aguardar_carregamento()

    assert driver.current_url.endswith("/painel")
    assert painel.titulo_secao().casefold() == "gestão interna"
    assert painel.total_especialidades() == 3


def test_ct_c02_login_invalido_exibe_alerta(driver, base_url):
    login = LoginClinicaPage(driver, base_url).abrir().entrar("admin_avaliador", "senha_errada")

    assert "Usuário ou senha inválidos" in login.mensagem_erro()
    assert "/entrar" in driver.current_url


def test_ct_c03_rota_painel_sem_login_redireciona(driver, base_url):
    LoginClinicaPage(driver, base_url).abrir_painel_direto()
    WebDriverWait(driver, 5).until(EC.url_contains("/entrar"))

    assert "/entrar" in driver.current_url


def test_ct_c04_logout_encerra_sessao(driver, base_url):
    login = LoginClinicaPage(driver, base_url).abrir().entrar("admin_avaliador", "avaliador123")
    PainelInternoPage(driver).aguardar_carregamento()

    login.fazer_logout()
    WebDriverWait(driver, 5).until(lambda d: not d.current_url.endswith("/painel"))
    assert not driver.current_url.endswith("/painel")


# ===========================================================================
# FLUXO 2: GESTÃO DE ESPECIALIDADES E AGENDAMENTO DE CONSULTAS (CT-C05 a CT-C08)
# ===========================================================================
def test_ct_c05_cadastrar_nova_especialidade_sucesso(driver, base_url):
    LoginClinicaPage(driver, base_url).abrir().entrar("admin_avaliador", "avaliador123")
    painel = PainelInternoPage(driver).aguardar_carregamento()
    assert painel.total_especialidades() == 3

    painel.cadastrar_especialidade("Neurologia")

    assert "Especialidade cadastrada com sucesso." in painel.texto_aviso()
    WebDriverWait(driver, 5).until(lambda _: painel.total_especialidades() == 4)
    assert "Neurologia" in painel.nomes_especialidades()


def test_ct_c06_especialidade_duplicada_case_insensitive_rejeitada(driver, base_url):
    LoginClinicaPage(driver, base_url).abrir().entrar("admin_avaliador", "avaliador123")
    painel = PainelInternoPage(driver).aguardar_carregamento()
    qtd_antes = painel.total_especialidades()

    # 'Cardiologia' já existe no seed; tentar cadastrar 'cardiologia' em minúsculas
    painel.cadastrar_especialidade("cardiologia")

    aviso = painel.texto_aviso().lower()
    assert "já existe" in aviso or "especialidade" in aviso
    assert painel.total_especialidades() == qtd_antes


def test_ct_c07_paciente_filtra_horarios_por_especialidade(driver, base_url):
    LoginClinicaPage(driver, base_url).abrir().entrar("paciente01", "SenhaForte123!")
    painel = PainelPacientePage(driver).aguardar_carregamento()

    painel.filtrar_por_especialidade_texto("Cardiologia")
    especialidades_visiveis = painel.especialidades_das_vagas_visiveis()

    assert len(especialidades_visiveis) > 0
    assert all(esp == "Cardiologia" for esp in especialidades_visiveis)


def test_ct_c08_paciente_agenda_consulta_com_sucesso(driver, base_url):
    LoginClinicaPage(driver, base_url).abrir().entrar("paciente01", "SenhaForte123!")
    painel = PainelPacientePage(driver).aguardar_carregamento()
    assert painel.quantidade_minhas_consultas() == 0

    painel.agendar_primeiro_horario()

    assert "Consulta agendada com sucesso" in painel.texto_aviso()
    WebDriverWait(driver, 5).until(lambda _: painel.quantidade_minhas_consultas() == 1)
    assert painel.cards_consultas_confirmadas() == 1
