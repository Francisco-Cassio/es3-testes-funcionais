# Trabalho 2 – Testes Funcionais Automatizados (Engenharia de Software III)

Repositório com a matriz de casos de teste, Page Objects e suítes de testes funcionais E2E automatizadas com **Selenium** e **pytest** em **Python**.

## Equipe
- **Francisco de Cássio da Silva Mourão Júnior**
- **Álvaro Miguel Rodrigues Aquino Costa**

## Versões Utilizadas
- **Python:** `3.12.10`
- **Selenium:** `4.54.0`
- **Pytest / Pytest-HTML:** `pytest 9.2.0`, `pytest-html 4.2.0`
- **Flask:** `3.1.3` (Pacote A)
- **Django / Vue:** `Django 6.1`, `djangorestframework 3.18.0`, `Vue 3.5` (Projeto Anterior)

## Estrutura do Repositório

```text
.
├── README.md
├── matriz_casos_de_teste.csv          # 30 casos especificados (partição, valor-limite e tabela de decisão)
├── relatorio_funcional.md             # Relatório completo em Markdown
├── relatorio.pdf                      # Relatório final em PDF (4 páginas)
├── slides.pdf                         # Slides da apresentação da equipe
├── pacote-A/
│   ├── app/app.py                     # Sistema A (Sabor Express + Matrícula Acadêmica)
│   ├── exemplo/                       # Exemplo resolvido A: Fluxo de pedido (CT01 a CT05)
│   └── desafio/                       # Desafio A: Portal de Matrícula (Page Objects + CT-A01 a CT-A10)
│       ├── conftest.py
│       ├── pages/matricula_pages.py
│       └── test_matricula.py
├── pacote-B/
│   ├── app.py                         # Sistema B (Portal ADS + Inscrições em Minicursos)
│   ├── web/                           # Telas HTML do Sistema B
│   ├── exemplo/                       # Exemplo resolvido B: Login no Portal ADS
│   └── desafio/                       # Desafio B: Inscrições em Minicursos (Page Object + CT-B01 a CT-B12)
│       ├── conftest.py
│       ├── pages/inscricoes_page.py
│       └── test_inscricoes.py
├── projeto-anterior/
│   ├── backend/                       # API Django REST da Clínica Agenda
│   ├── frontend/                      # Aplicação Vue 3 (com atributos id e data-testid adicionados)
│   ├── pages/clinica_pages.py         # Page Objects da Clínica Agenda
│   ├── seed_clinica.py                # Popula o banco local da Clínica Agenda
│   ├── run_server_clinica.py          # Sobe API + SPA Vue unificados em http://127.0.0.1:8001
│   └── test_clinica_funcional.py      # 8 casos funcionais cobrindo 2 fluxos (CT-C01 a CT-C08)
└── resultados/
    ├── pacote-A/                      # Relatórios HTML e XML do Exemplo A e das 3 execuções do Desafio A
    ├── pacote-B/                      # Relatórios HTML e XML do Exemplo B e das 3 execuções do Desafio B
    └── projeto-anterior/              # Relatórios HTML e XML das 3 execuções da Clínica Agenda
```

---

## 1. Preparação do Ambiente

Clone o repositório, crie o ambiente virtual e instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS / Git Bash
# .venv\Scripts\Activate.ps1     # Windows PowerShell

python -m pip install flask selenium pytest pytest-html requests -r projeto-anterior/backend/requirements.txt
```

> **Nota:** O Google Chrome deve estar instalado. O Selenium Manager baixa o driver automaticamente no primeiro uso. Para rodar sem abrir a janela do navegador, defina `HEADLESS=1` (ou `$env:HEADLESS="1"` no Windows PowerShell).

---

## 2. Pacote A – Sabor Express e Portal de Matrícula

### Subir o sistema A (Terminal 1)
```bash
python pacote-A/app/app.py
# Servidor disponível em http://127.0.0.1:5000
```

### Rodar o Exemplo Resolvido A – Fluxo de Pedido (Terminal 2)
```bash
HEADLESS=1 pytest pacote-A/exemplo/test_fluxo_pedido.py -v --html=resultados/pacote-A/exemplo/relatorio.html --self-contained-html --junitxml=resultados/pacote-A/exemplo/resultado_exemplo_a.xml
```

### Rodar o Desafio A – Portal de Matrícula (3 execuções completas)
```bash
HEADLESS=1 pytest pacote-A/desafio/test_matricula.py -v --html=resultados/pacote-A/desafio/relatorio_r1.html --self-contained-html --junitxml=resultados/pacote-A/desafio/resultado_r1.xml

HEADLESS=1 pytest pacote-A/desafio/test_matricula.py -v --html=resultados/pacote-A/desafio/relatorio_r2.html --self-contained-html --junitxml=resultados/pacote-A/desafio/resultado_r2.xml

HEADLESS=1 pytest pacote-A/desafio/test_matricula.py -v --html=resultados/pacote-A/desafio/relatorio_r3.html --self-contained-html --junitxml=resultados/pacote-A/desafio/resultado_r3.xml
```

---

## 3. Pacote B – Portal ADS e Inscrições em Minicursos

### Subir o sistema B (Terminal 1)
```bash
python pacote-B/app.py
# Servidor disponível em http://127.0.0.1:8000
```

### Rodar o Exemplo Resolvido B – Login no Portal (Terminal 2)
```bash
HEADLESS=1 pytest pacote-B/exemplo/test_login.py -v --html=resultados/pacote-B/exemplo/relatorio_login.html --self-contained-html --junitxml=resultados/pacote-B/exemplo/resultado_login.xml
```

### Rodar o Desafio B – Inscrições em Minicursos (3 execuções sequenciais)
```bash
HEADLESS=1 pytest pacote-B/desafio/test_inscricoes.py -v --html=resultados/pacote-B/desafio/relatorio_r1.html --self-contained-html --junitxml=resultados/pacote-B/desafio/resultado_r1.xml

HEADLESS=1 pytest pacote-B/desafio/test_inscricoes.py -v --html=resultados/pacote-B/desafio/relatorio_r2.html --self-contained-html --junitxml=resultados/pacote-B/desafio/resultado_r2.xml

HEADLESS=1 pytest pacote-B/desafio/test_inscricoes.py -v --html=resultados/pacote-B/desafio/relatorio_r3.html --self-contained-html --junitxml=resultados/pacote-B/desafio/resultado_r3.xml
```

---

## 4. Projeto Anterior – Clínica Agenda (Django REST + Vue 3)

### Popular o banco local e subir o servidor unificado (Terminal 1)
```bash
python projeto-anterior/seed_clinica.py
python projeto-anterior/run_server_clinica.py
# Aplicação Web Vue + API Django disponível em http://127.0.0.1:8001
```

### Rodar a suíte funcional da Clínica Agenda (3 execuções completas)
```bash
HEADLESS=1 pytest projeto-anterior/test_clinica_funcional.py -v --html=resultados/projeto-anterior/relatorio_r1.html --self-contained-html --junitxml=resultados/projeto-anterior/resultado_r1.xml

HEADLESS=1 pytest projeto-anterior/test_clinica_funcional.py -v --html=resultados/projeto-anterior/relatorio_r2.html --self-contained-html --junitxml=resultados/projeto-anterior/resultado_r2.xml

HEADLESS=1 pytest projeto-anterior/test_clinica_funcional.py -v --html=resultados/projeto-anterior/relatorio_r3.html --self-contained-html --junitxml=resultados/projeto-anterior/resultado_r3.xml
```
