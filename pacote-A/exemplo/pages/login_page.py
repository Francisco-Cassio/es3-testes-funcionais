"""Page Object da tela de login da Sabor Express.

Ideia do padrão Page Object: o TESTE fala a língua do negócio
("entrar com usuário e senha"); a PÁGINA sabe os detalhes técnicos
(ids, cliques, esperas). Se o HTML mudar, só esta classe muda.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    CAMPO_USUARIO = (By.ID, "usuario")
    CAMPO_SENHA = (By.ID, "senha")
    BOTAO_ENTRAR = (By.ID, "btn-entrar")
    MENSAGEM_ERRO = (By.CSS_SELECTOR, "[data-testid='erro']")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 5)

    def abrir(self):
        self.driver.get(f"{self.base_url}/login")
        return self

    def entrar(self, usuario, senha):
        u = self.wait.until(EC.visibility_of_element_located(self.CAMPO_USUARIO))
        s = self.driver.find_element(*self.CAMPO_SENHA)
        self.driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[2].value = arguments[3];",
            u,
            usuario,
            s,
            senha,
        )
        self.driver.find_element(By.ID, "form-login").submit()

    def mensagem_erro(self):
        return self.wait.until(EC.visibility_of_element_located(self.MENSAGEM_ERRO)).text
