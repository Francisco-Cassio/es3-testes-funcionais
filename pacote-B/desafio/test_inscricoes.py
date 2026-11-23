"""
DESAFIO B - Trabalho 2: Inscrições em Minicursos (Selenium + pytest + Page Objects)

Cobre os 12 casos obrigatórios divididos nas 4 famílias do Guia do Aluno:
  1. Fluxos válidos (2):
     - CT-B01: Inscrição válida
     - CT-B02: Mesmo e-mail em outro curso
  2. Obrigatórios e formato (3):
     - CT-B03: Nome vazio (ou apenas espaços)
     - CT-B04: E-mail inválido
     - CT-B05: Curso ausente
  3. Valores-limite de Nome (4):
     - CT-B06: Nome com 2 caracteres (inválido)
     - CT-B07: Nome com 3 caracteres (válido)
     - CT-B08: Nome com 60 caracteres (válido)
     - CT-B09: Nome com 61 caracteres (inválido)
  4. Regras com estado (3):
     - CT-B10: Duplicidade com maiúsculas e espaços nas pontas no mesmo curso
     - CT-B11: Lotação (3ª inscrição no mesmo curso de 2 vagas)
     - CT-B12: Cancelamento remove da lista ('Inscrição cancelada') e libera a vaga para nova inscrição
"""
import pytest
import requests

from pages.inscricoes_page import InscricoesPage


@pytest.fixture(autouse=True)
def resetar_inscricoes(base_url):
    """Restaura as inscrições em memória via POST /api/reset antes de cada caso."""
    resp = requests.post(f"{base_url}/api/reset", json={}, timeout=5)
    assert resp.status_code == 200


# ===========================================================================
# FAMÍLIA 1: FLUXOS VÁLIDOS (2 casos)
# ===========================================================================
def test_ct_b01_inscricao_valida(driver, base_url):
    pagina = InscricoesPage(driver, base_url).abrir()
    pagina.inscrever("  Maria Oliveira  ", "maria@ads.local", "1")

    assert pagina.mensagem_sucesso() == "Inscrição realizada"
    pagina.aguardar_quantidade_na_lista(1)
    itens = pagina.textos_da_lista()
    assert len(itens) == 1
    assert "Maria Oliveira / maria@ads.local / curso 1" in itens[0]


def test_ct_b02_mesmo_email_em_outro_curso(driver, base_url):
    # Prepara 1ª inscrição no curso 1 via API
    r = requests.post(
        f"{base_url}/api/inscricoes",
        json={"nome": "Maria Oliveira", "email": "maria@ads.local", "curso": 1},
        timeout=5,
    )
    assert r.status_code == 201

    pagina = InscricoesPage(driver, base_url).abrir()
    pagina.aguardar_quantidade_na_lista(1)

    # Inscreve o mesmo e-mail no curso 2 (Java) pela interface
    pagina.inscrever("Maria Oliveira", "maria@ads.local", "2")

    assert pagina.mensagem_sucesso() == "Inscrição realizada"
    pagina.aguardar_quantidade_na_lista(2)
    itens = "\n".join(pagina.textos_da_lista())
    assert "curso 1" in itens and "curso 2" in itens


# ===========================================================================
# FAMÍLIA 2: OBRIGATÓRIOS E FORMATO (3 casos)
# ===========================================================================
def test_ct_b03_nome_vazio_rejeitado(driver, base_url):
    pagina = InscricoesPage(driver, base_url).abrir()
    pagina.inscrever("   ", "joao@ads.local", "1")

    assert pagina.mensagem_erro() == "Nome deve ter de 3 a 60 caracteres"
    assert pagina.quantidade_na_lista() == 0


def test_ct_b04_email_invalido_rejeitado(driver, base_url):
    pagina = InscricoesPage(driver, base_url).abrir()
    pagina.inscrever("Joao Santos", "email-sem-arroba.com", "1")

    assert pagina.mensagem_erro() == "E-mail inválido"
    assert pagina.quantidade_na_lista() == 0


def test_ct_b05_curso_ausente_rejeitado(driver, base_url):
    pagina = InscricoesPage(driver, base_url).abrir()
    pagina.inscrever("Joao Santos", "joao@ads.local", "")

    assert pagina.mensagem_erro() == "Curso obrigatório"
    assert pagina.quantidade_na_lista() == 0


# ===========================================================================
# FAMÍLIA 3: VALORES-LIMITE DE NOME (4 casos: 2, 3, 60 e 61 caracteres)
# ===========================================================================
@pytest.mark.parametrize(
    "tamanho,espera_sucesso",
    [
        (2, False),   # CT-B06: limite inferior inválido (2 chars)
        (3, True),    # CT-B07: limite inferior válido (3 chars)
        (60, True),   # CT-B08: limite superior válido (60 chars)
        (61, False),  # CT-B09: limite superior inválido (61 chars)
    ],
)
def test_ct_b06_a_b09_valores_limite_nome(driver, base_url, tamanho, espera_sucesso):
    nome_teste = "A" * tamanho
    email_teste = f"limite{tamanho}@ads.local"

    pagina = InscricoesPage(driver, base_url).abrir()
    pagina.inscrever(nome_teste, email_teste, "1")

    if espera_sucesso:
        assert pagina.mensagem_sucesso() == "Inscrição realizada"
        pagina.aguardar_quantidade_na_lista(1)
        assert pagina.quantidade_na_lista() == 1
    else:
        assert pagina.mensagem_erro() == "Nome deve ter de 3 a 60 caracteres"
        assert pagina.quantidade_na_lista() == 0


# ===========================================================================
# FAMÍLIA 4: REGRAS COM ESTADO (3 casos: duplicidade, lotação e cancelamento)
# ===========================================================================
def test_ct_b10_duplicidade_maiusculas_e_espacos(driver, base_url):
    r = requests.post(
        f"{base_url}/api/inscricoes",
        json={"nome": "Aluno Um", "email": "aluno@ads.local", "curso": 1},
        timeout=5,
    )
    assert r.status_code == 201

    pagina = InscricoesPage(driver, base_url).abrir()
    pagina.aguardar_quantidade_na_lista(1)

    # Tenta inscrever o mesmo e-mail com espaços e letras maiúsculas no mesmo curso
    pagina.inscrever("Aluno Duplicado", "  ALUNO@ADS.LOCAL  ", "1")

    assert pagina.mensagem_erro() == "Inscrição já existente"
    assert pagina.quantidade_na_lista() == 1


def test_ct_b11_lotacao_terceira_inscricao_rejeitada(driver, base_url):
    # Preenche as 2 vagas do curso 3 (Testes de Software) via API
    for idx in (1, 2):
        r = requests.post(
            f"{base_url}/api/inscricoes",
            json={"nome": f"Inscrito {idx}", "email": f"vaga{idx}@ads.local", "curso": 3},
            timeout=5,
        )
        assert r.status_code == 201

    pagina = InscricoesPage(driver, base_url).abrir()
    pagina.aguardar_quantidade_na_lista(2)

    # Tenta a 3ª inscrição no curso 3 pela tela
    pagina.inscrever("Terceiro Candidato", "terceiro@ads.local", "3")

    assert pagina.mensagem_erro() == "Curso sem vagas"
    assert pagina.quantidade_na_lista() == 2
    assert all("terceiro@ads.local" not in t for t in pagina.textos_da_lista())


def test_ct_b12_cancelamento_seguido_de_nova_inscricao(driver, base_url):
    # Lota o curso 1 (Python) com 2 inscrições via API (IDs 1 e 2)
    for idx in (1, 2):
        r = requests.post(
            f"{base_url}/api/inscricoes",
            json={"nome": f"Aluno {idx}", "email": f"aluno{idx}@ads.local", "curso": 1},
            timeout=5,
        )
        assert r.status_code == 201

    pagina = InscricoesPage(driver, base_url).abrir()
    pagina.aguardar_quantidade_na_lista(2)

    # Cancela a inscrição ID 1 pela interface ([data-testid="cancelar-1"])
    pagina.cancelar_inscricao(1)
    assert pagina.mensagem_sucesso() == "Inscrição cancelada"
    assert pagina.quantidade_na_lista() == 1

    # Realiza uma nova inscrição ocupando a vaga recém-liberada no curso 1
    pagina.inscrever("Novo Aluno", "novo@ads.local", "1")
    assert pagina.mensagem_sucesso() == "Inscrição realizada"
    pagina.aguardar_quantidade_na_lista(2)
    assert any("novo@ads.local" in t for t in pagina.textos_da_lista())
