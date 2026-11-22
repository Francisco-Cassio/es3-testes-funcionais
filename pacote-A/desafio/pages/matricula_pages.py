"""
Page Objects do Portal de Matrícula Acadêmica (Desafio A - Trabalho 2).

Boas práticas cumpridas:
  - Localizadores estáveis (By.ID e By.CSS_SELECTOR com data-testid), zero XPath absoluto
  - Esperas explícitas (WebDriverWait + expected_conditions), zero time.sleep
  - Uma classe por tela (LoginMatriculaPage, DisciplinasPage, ComprovantePage)
  - Asserções ficam exclusivamente no arquivo de teste
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginMatriculaPage:
    CAMPO_MATRICULA = (By.ID, "matricula")
    CAMPO_SENHA = (By.ID, "senha")
    BOTAO_ENTRAR = (By.ID, "btn-entrar")
    MENSAGEM_ERRO = (By.ID, "mensagem-erro")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 5)

    def abrir(self):
        self.driver.get(f"{self.base_url}/matricula/login")
        self.wait.until(EC.visibility_of_element_located(self.CAMPO_MATRICULA))
        return self

    def entrar(self, matricula: str, senha: str):
        campo_mat = self.wait.until(EC.visibility_of_element_located(self.CAMPO_MATRICULA))
        campo_mat.clear()
        campo_mat.send_keys(matricula)

        campo_sen = self.driver.find_element(*self.CAMPO_SENHA)
        campo_sen.clear()
        campo_sen.send_keys(senha)

        botao = self.driver.find_element(*self.BOTAO_ENTRAR)
        botao.click()
        return self

    def mensagem_erro(self) -> str:
        el = self.wait.until(EC.visibility_of_element_located(self.MENSAGEM_ERRO))
        return el.text.strip()


class DisciplinasPage:
    TABELA = (By.ID, "tabela-disciplinas")
    BOTAO_CONFIRMAR = (By.ID, "btn-confirmar")
    MENSAGEM_ERRO = (By.ID, "mensagem-erro")
    USUARIO_LOGADO = (By.ID, "usuario-logado")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 5)

    def abrir_direto(self):
        self.driver.get(f"{self.base_url}/matricula/disciplinas")
        return self

    def esta_aberta(self) -> bool:
        self.wait.until(EC.visibility_of_element_located(self.TABELA))
        return self.driver.current_url.endswith("/matricula/disciplinas")

    def usuario_logado(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.USUARIO_LOGADO)).text.strip()

    def vagas_da_disciplina(self, codigo: str) -> int:
        seletor = (By.CSS_SELECTOR, f"[data-testid='disc-{codigo}'] .vagas")
        texto = self.wait.until(EC.visibility_of_element_located(seletor)).text.strip()
        return int(texto)

    def selecionar_disciplinas(self, codigos: list[str]):
        self.wait.until(EC.visibility_of_element_located(self.TABELA))
        for codigo in codigos:
            chk = self.driver.find_element(By.ID, f"chk-{codigo}")
            if not chk.is_selected():
                chk.click()
        return self

    def confirmar(self):
        self.driver.find_element(*self.BOTAO_CONFIRMAR).click()
        self.wait.until(
            lambda d: len(d.find_elements(*self.MENSAGEM_ERRO)) > 0
            or len(d.find_elements(By.ID, "mensagem-sucesso")) > 0
        )
        return self

    def mensagem_erro(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.MENSAGEM_ERRO)).text.strip()


class ComprovantePage:
    MENSAGEM_SUCESSO = (By.ID, "mensagem-sucesso")
    CODIGO_COMPROVANTE = (By.ID, "comprovante")
    DISCIPLINAS_MATRICULADAS = (By.ID, "disciplinas-matriculadas")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def mensagem_sucesso(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.MENSAGEM_SUCESSO)).text.strip()

    def codigo_comprovante(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.CODIGO_COMPROVANTE)).text.strip()

    def disciplinas_listadas(self) -> list[str]:
        texto = self.wait.until(EC.visibility_of_element_located(self.DISCIPLINAS_MATRICULADAS)).text.strip()
        return [c.strip() for c in texto.split(",") if c.strip()]
