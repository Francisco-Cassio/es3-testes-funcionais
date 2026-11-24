"""
Page Object da tela de Inscrições em Minicursos (/inscricoes) - Desafio B (Trabalho 2).

Seletores exigidos no Guia do Aluno:
  - #nome
  - #email
  - #curso
  - #confirmar
  - #erro
  - #sucesso
  - #lista
  - [data-testid="cancelar-ID"]
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


class InscricoesPage:
    CAMPO_NOME = (By.ID, "nome")
    CAMPO_EMAIL = (By.ID, "email")
    SELECT_CURSO = (By.ID, "curso")
    BOTAO_CONFIRMAR = (By.ID, "confirmar")
    MSG_ERRO = (By.ID, "erro")
    MSG_SUCESSO = (By.ID, "sucesso")
    LISTA = (By.ID, "lista")
    ITENS_LISTA = (By.CSS_SELECTOR, "#lista li")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 5)

    def abrir(self):
        self.driver.get(f"{self.base_url}/inscricoes")
        self.wait.until(lambda d: d.find_element(*self.CAMPO_NOME).is_displayed())
        return self

    def preencher_formulario(self, nome: str, email: str, curso_valor: str = ""):
        el_nome = self.driver.find_element(*self.CAMPO_NOME)
        el_nome.clear()
        if nome:
            el_nome.send_keys(nome)

        el_email = self.driver.find_element(*self.CAMPO_EMAIL)
        el_email.clear()
        if email:
            el_email.send_keys(email)

        select = Select(self.driver.find_element(*self.SELECT_CURSO))
        select.select_by_value(str(curso_valor))
        return self

    def confirmar(self):
        self.driver.find_element(*self.BOTAO_CONFIRMAR).click()
        # Aguarda até que #sucesso ou #erro receba texto após o fetch assíncrono
        self.wait.until(
            lambda d: bool(d.find_element(*self.MSG_SUCESSO).text.strip())
            or bool(d.find_element(*self.MSG_ERRO).text.strip())
        )
        return self

    def inscrever(self, nome: str, email: str, curso_valor: str = ""):
        return self.preencher_formulario(nome, email, curso_valor).confirmar()

    def mensagem_sucesso(self) -> str:
        self.wait.until(lambda d: bool(d.find_element(*self.MSG_SUCESSO).text.strip()))
        return self.driver.find_element(*self.MSG_SUCESSO).text.strip()

    def mensagem_erro(self) -> str:
        self.wait.until(lambda d: bool(d.find_element(*self.MSG_ERRO).text.strip()))
        return self.driver.find_element(*self.MSG_ERRO).text.strip()

    def textos_da_lista(self) -> list[str]:
        return [li.text for li in self.driver.find_elements(*self.ITENS_LISTA)]

    def quantidade_na_lista(self) -> int:
        return len(self.driver.find_elements(*self.ITENS_LISTA))

    def aguardar_quantidade_na_lista(self, qtd_esperada: int):
        self.wait.until(lambda d: len(d.find_elements(*self.ITENS_LISTA)) == qtd_esperada)
        return self

    def cancelar_inscricao(self, inscricao_id: int):
        qtd_antes = self.quantidade_na_lista()
        seletor = (By.CSS_SELECTOR, f'[data-testid="cancelar-{inscricao_id}"]')
        botao = self.wait.until(lambda d: d.find_element(*seletor))
        botao.click()
        self.wait.until(
            lambda d: d.find_element(*self.MSG_SUCESSO).text.strip() == "Inscrição cancelada"
            and len(d.find_elements(*self.ITENS_LISTA)) == max(0, qtd_antes - 1)
        )
        return self
