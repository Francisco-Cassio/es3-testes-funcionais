"""Page Object da tela de cardápio da Sabor Express."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CardapioPage:
    TITULO = (By.TAG_NAME, "h1")
    QTD_CARRINHO = (By.ID, "qtd-carrinho")
    USUARIO_LOGADO = (By.ID, "usuario-logado")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def esta_aberta(self):
        return self.wait.until(EC.text_to_be_present_in_element(self.TITULO, "Cardápio"))

    def usuario_logado(self):
        return self.driver.find_element(*self.USUARIO_LOGADO).text

    def adicionar_item(self, item_id):
        qtd_antes = self.quantidade_no_carrinho()
        form = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"form[action='/carrinho/adicionar/{item_id}']"))
        )
        form.submit()
        self.wait.until(
            lambda d: len(d.find_elements(*self.QTD_CARRINHO)) > 0
            and int(d.find_element(*self.QTD_CARRINHO).text) == qtd_antes + 1
        )
        return self

    def quantidade_no_carrinho(self):
        return int(self.wait.until(EC.visibility_of_element_located(self.QTD_CARRINHO)).text)
