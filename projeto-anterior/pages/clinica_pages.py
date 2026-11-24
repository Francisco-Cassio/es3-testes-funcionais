"""
Page Objects da aplicação Clínica Agenda (Vue 3 + Django REST) - Projeto Anterior (Trabalho 2).

Utiliza os atributos id e data-testid adicionados aos componentes Vue:
  - LoginView.vue: #login-username, #login-password, #login-submit, [data-testid='login-error']
  - AppHeader.vue: #btn-header-entrar, #header-profile, #btn-logout
  - InternalDashboard.vue: [data-testid='internal-dashboard'], #internal-eyebrow, #stat-especialidades,
    #btn-novo-registro, #input-nome-especialidade, #btn-salvar-especialidade, #internal-notice
  - PatientDashboard.vue: [data-testid='patient-dashboard'], #patient-eyebrow, #filtro-especialidade,
    [data-testid='slot-card'], [data-testid='btn-agendar-slot'], [data-testid='modal-confirmar'],
    #btn-confirmar-consulta, #patient-notice, #badge-minhas-consultas, [data-testid='appointment-card']
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


class LoginClinicaPage:
    CAMPO_USUARIO = (By.ID, "login-username")
    CAMPO_SENHA = (By.ID, "login-password")
    BOTAO_ENTRAR = (By.ID, "login-submit")
    ALERTA_ERRO = (By.CSS_SELECTOR, "[data-testid='login-error']")
    BOTAO_HEADER_ENTRAR = (By.ID, "btn-header-entrar")
    BOTAO_LOGOUT = (By.ID, "btn-logout")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 8)

    def abrir(self):
        self.driver.get(f"{self.base_url}/entrar")
        self.wait.until(EC.visibility_of_element_located(self.CAMPO_USUARIO))
        return self

    def abrir_painel_direto(self):
        self.driver.get(f"{self.base_url}/painel")
        return self

    def entrar(self, username: str, password: str):
        u = self.wait.until(EC.visibility_of_element_located(self.CAMPO_USUARIO))
        u.clear()
        u.send_keys(username)

        p = self.driver.find_element(*self.CAMPO_SENHA)
        p.clear()
        p.send_keys(password)

        self.driver.find_element(*self.BOTAO_ENTRAR).click()
        return self

    def mensagem_erro(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.ALERTA_ERRO)).text.strip()

    def fazer_logout(self):
        self.driver.refresh()
        btn = self.wait.until(EC.element_to_be_clickable(self.BOTAO_LOGOUT))
        btn.click()
        self.driver.refresh()
        self.wait.until(EC.visibility_of_element_located(self.BOTAO_HEADER_ENTRAR))
        return self


class PainelInternoPage:
    CONTAINER = (By.CSS_SELECTOR, "[data-testid='internal-dashboard']")
    EYEBROW = (By.ID, "internal-eyebrow")
    STAT_ESPECIALIDADES = (By.ID, "stat-especialidades")
    BOTAO_NOVO = (By.ID, "btn-novo-registro")
    INPUT_ESPECIALIDADE = (By.ID, "input-nome-especialidade")
    BOTAO_SALVAR_ESP = (By.ID, "btn-salvar-especialidade")
    AVISO = (By.ID, "internal-notice")
    CARDS_ESPECIALIDADE = (By.CSS_SELECTOR, ".management-card strong")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 8)

    def aguardar_carregamento(self):
        self.wait.until(EC.visibility_of_element_located(self.CONTAINER))
        self.wait.until(lambda d: int(d.find_element(*self.STAT_ESPECIALIDADES).text.strip() or "0") >= 3)
        return self

    def titulo_secao(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.EYEBROW)).text.strip()

    def total_especialidades(self) -> int:
        return int(self.wait.until(EC.visibility_of_element_located(self.STAT_ESPECIALIDADES)).text.strip())

    def nomes_especialidades(self) -> list[str]:
        return [el.text.strip() for el in self.driver.find_elements(*self.CARDS_ESPECIALIDADE)]

    def cadastrar_especialidade(self, nome: str):
        self.wait.until(EC.element_to_be_clickable(self.BOTAO_NOVO)).click()
        campo = self.wait.until(EC.visibility_of_element_located(self.INPUT_ESPECIALIDADE))
        campo.clear()
        campo.send_keys(nome)
        self.driver.find_element(*self.BOTAO_SALVAR_ESP).click()
        self.wait.until(EC.visibility_of_element_located(self.AVISO))
        return self

    def texto_aviso(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.AVISO)).text.strip()


class PainelPacientePage:
    CONTAINER = (By.CSS_SELECTOR, "[data-testid='patient-dashboard']")
    EYEBROW = (By.ID, "patient-eyebrow")
    FILTRO_ESPECIALIDADE = (By.ID, "filtro-especialidade")
    CARDS_VAGA = (By.CSS_SELECTOR, "[data-testid='slot-card']")
    ESPECIALIDADES_VAGAS = (By.CSS_SELECTOR, "[data-testid='slot-card'] .slot-especialidade")
    BOTOES_AGENDAR = (By.CSS_SELECTOR, "[data-testid='btn-agendar-slot']")
    MODAL_CONFIRMAR = (By.CSS_SELECTOR, "[data-testid='modal-confirmar']")
    BOTAO_CONFIRMAR_MODAL = (By.ID, "btn-confirmar-consulta")
    AVISO = (By.ID, "patient-notice")
    BADGE_CONSULTAS = (By.ID, "badge-minhas-consultas")
    CARDS_CONSULTA = (By.CSS_SELECTOR, "[data-testid='appointment-card']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 8)

    def aguardar_carregamento(self):
        self.wait.until(EC.visibility_of_element_located(self.CONTAINER))
        self.wait.until(lambda d: len(d.find_elements(*self.CARDS_VAGA)) > 0)
        return self

    def filtrar_por_especialidade_texto(self, nome_especialidade: str):
        self.wait.until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#filtro-especialidade option")) >= 4
        )
        select_el = self.driver.find_element(*self.FILTRO_ESPECIALIDADE)
        Select(select_el).select_by_visible_text(nome_especialidade)
        self.wait.until(
            lambda d: len(d.find_elements(*self.ESPECIALIDADES_VAGAS)) > 0
            and all(
                el.text.strip() == nome_especialidade
                for el in d.find_elements(*self.ESPECIALIDADES_VAGAS)
            )
        )
        return self

    def especialidades_das_vagas_visiveis(self) -> list[str]:
        return [el.text.strip() for el in self.driver.find_elements(*self.ESPECIALIDADES_VAGAS)]

    def agendar_primeiro_horario(self):
        botoes = self.wait.until(lambda d: d.find_elements(*self.BOTOES_AGENDAR))
        botoes[-1].click()
        self.wait.until(EC.visibility_of_element_located(self.MODAL_CONFIRMAR))
        self.wait.until(EC.element_to_be_clickable(self.BOTAO_CONFIRMAR_MODAL)).click()
        self.wait.until(EC.visibility_of_element_located(self.AVISO))
        return self

    def texto_aviso(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.AVISO)).text.strip()

    def quantidade_minhas_consultas(self) -> int:
        return int(self.wait.until(EC.visibility_of_element_located(self.BADGE_CONSULTAS)).text.strip())

    def cards_consultas_confirmadas(self) -> int:
        self.wait.until(lambda d: len(d.find_elements(*self.CARDS_CONSULTA)) > 0)
        return len(self.driver.find_elements(*self.CARDS_CONSULTA))
