# Relatório Técnico – Trabalho 2: Testes Funcionais Automatizados

**Equipe:** Francisco de Cássio da Silva Mourão Júnior e Álvaro Miguel Rodrigues Aquino Costa  
**Disciplina:** Engenharia de Software III  
**Ferramentas:** Selenium 4.54.0 + pytest 9.2.0 + pytest-html 4.2.0 (Python 3.12.10)  
**Data:** 21/11/2026 a 25/11/2026

---

## 1. Regras Cobertas e Matriz de Casos de Teste

A especificação completa dos **30 casos de teste** foi elaborada antes da automação no arquivo [`matriz_casos_de_teste.csv`](./matriz_casos_de_teste.csv), aplicando sistematicamente **Partição de Equivalência**, **Análise de Valor-Limite** e **Tabela de Decisão**:

### 1.1 Desafio A – Portal de Matrícula Acadêmica (`http://127.0.0.1:5000/matricula/login`)
Foram especificados **10 casos de teste (`CT-A01` a `CT-A10`)** e automatizados **12 testes executáveis** (incluindo 3 variações via `@pytest.mark.parametrize` no `CT-A02`), cobrindo integralmente as regras **R1 a R7**:

| ID | Regra | Técnica | Dados / Limite | Resultado Esperado (da Regra) | Status (3 reps) |
|---|---|---|---|---|---|
| `CT-A01` | R1 – Login válido | Partição válida | `20260001` / `senha123` | Abre `/matricula/disciplinas` com `#tabela-disciplinas` | Aprovado (3/3) |
| `CT-A02` | R1 – Login inválido | Partição inválida (`parametrize`) | Senha errada, matrícula inexistente e vazia | Permanece no login e exibe `"Matrícula ou senha inválidas."` | Aprovado (3/3) |
| `CT-A03` | R2 – Acesso protegido | Tabela de decisão | `GET /matricula/disciplinas` sem sessão | Redireciona para `/matricula/login` | Aprovado (3/3) |
| `CT-A04` | R3 – Quantidade (0) | Valor-limite (`0` disciplinas) | Nenhuma checkbox marcada | Exibe `"Selecione ao menos uma disciplina."` e mantém vagas | Aprovado (3/3) |
| `CT-A05` | R3 e R7 – Sucesso (1) | Valor-limite (`1` disciplina) | `["ES3"]` (40 vagas) | Exibe `"Matrícula realizada com sucesso!"`, `COMP-000001` e vagas de `ES3 = 39` | Aprovado (3/3) |
| `CT-A06` | R3 e R7 – Sucesso (5) | Valor-limite (`5` disciplinas) | `["ES3", "BD2", "PW2", "IHC", "EMP"]` | Emite comprovante listando as 5 disciplinas | Aprovado (3/3) |
| `CT-A07` | R3 – Quantidade (6) | Valor-limite (`6` disciplinas) | 6 disciplinas selecionadas | Exibe `"Máximo de 5 disciplinas por semestre."` e não desconta vaga | Aprovado (3/3) |
| `CT-A08` | R4 – Choque de horário | Tabela de decisão | `["ES3", "RED"]` (ambas `SEG-19h`) | Exibe `"Choque de horário entre disciplinas selecionadas."` | Aprovado (3/3) |
| `CT-A09` | R5 – Vagas esgotadas | Tabela de decisão (estado) | 5 vagas de `MOB` ocupadas via API | Exibe `"Vagas esgotadas: MOB."` e mantém `0` vagas | Aprovado (3/3) |
| `CT-A10` | R6 – Matrícula única | Tabela de decisão (estado) | Aluno `20260001` já matriculado via API | Exibe `"Aluno já possui matrícula neste semestre."` | Aprovado (3/3) |

### 1.2 Desafio B – Inscrições em Minicursos (`http://127.0.0.1:8000/inscricoes`)
Foram especificados e automatizados os **12 casos de teste (`CT-B01` a `CT-B12`)** distribuídos nas 4 famílias exigidas:

| Família | IDs | Casos Automatizados | Resultado Esperado | Status (3 reps) |
|---|---|---|---|---|
| **1. Fluxos válidos (2)** | `CT-B01`, `CT-B02` | Inscrição válida com espaços aparados; mesmo e-mail inscrito em outro curso (`curso 1` e `curso 2`) | `"Inscrição realizada"` em `#sucesso` e itens presentes em `#lista` | Aprovado (3/3) |
| **2. Obrigatórios e formato (3)** | `CT-B03`, `CT-B04`, `CT-B05` | Nome em branco (`"   "`); e-mail sem `@` (`email-sem-arroba.com`); curso não selecionado (`""`) | Mensagens específicas em `#erro` e `#lista` permanece vazia (`0` itens) | Aprovado (3/3) |
| **3. Valores-limite de Nome (4)** | `CT-B06` a `CT-B09` | Parametrização com `2` chars (rejeita), `3` chars (aceita), `60` chars (aceita) e `61` chars (rejeita) | Limites `[3, 60]` aprovam; `2` e `61` exibem `"Nome deve ter de 3 a 60 caracteres"` | Aprovado (3/3) |
| **4. Regras com estado (3)** | `CT-B10`, `CT-B11`, `CT-B12` | Duplicidade com `"  ALUNO@ADS.LOCAL  "` no mesmo curso; 3ª inscrição em curso de 2 vagas; cancelamento via `[data-testid="cancelar-1"]` seguido de nova inscrição | `"Inscrição já existente"`, `"Curso sem vagas"`, `"Inscrição cancelada"` e vaga liberada para novo aluno | Aprovado (3/3) |

### 1.3 Projeto Anterior – Clínica Agenda (`http://127.0.0.1:8001`)
Foram escolhidos **2 fluxos principais** da aplicação Vue 3 + Django REST e automatizados **8 casos de teste (`CT-C01` a `CT-C08`)**:
- **Fluxo 1 – Autenticação JWT e Controle de Acesso por Perfil (`CT-C01` a `CT-C04`):** Login válido como usuário interno (`admin_avaliador`), rejeição de senha incorreta (`[data-testid='login-error']`), proteção de rota `/painel` sem token JWT (redirecionando para `/entrar`) e encerramento de sessão via botão Sair (`#btn-logout`).
- **Fluxo 2 – Gestão de Especialidades e Agendamento de Consultas (`CT-C05` a `CT-C08`):** Cadastro de nova especialidade (`Neurologia`), bloqueio de regra de negócio para especialidade duplicada case-insensitive (`cardiologia` vs. `Cardiologia`), filtragem de vagas disponíveis por especialidade no painel do paciente (`paciente01`) e reserva completa de consulta pelo modal de confirmação com atualização imediata da aba *Minhas consultas*.

---

## 2. Estrutura do Código: Page Objects, Localizadores, Esperas e Fixtures

1. **Padrão Page Objects:** Cada tela possui sua própria classe isolando localizadores e interações (`LoginMatriculaPage`, `DisciplinasPage`, `ComprovantePage` no Pacote A; `InscricoesPage` no Pacote B; `LoginClinicaPage`, `PainelInternoPage`, `PainelPacientePage` na Clínica Agenda). Nenhum `assert` reside nos Page Objects — todas as asserções ficam nos arquivos `test_*.py`.
2. **Localizadores Estáveis e Melhorias no Projeto Anterior:** Foram utilizados exclusivamente seletores `By.ID` e `By.CSS_SELECTOR` baseados em `data-testid` (zero XPath absoluto). Na aplicação Vue 3 da **Clínica Agenda**, adicionamos atributos `id` e `data-testid` nos componentes `LoginView.vue`, `AppHeader.vue`, `InternalDashboard.vue` e `PatientDashboard.vue` (ex.: `data-testid="login-error"`, `data-testid="slot-card"`, `data-testid="btn-agendar-slot"`, `id="btn-confirmar-consulta"`), garantindo testes imunes a mudanças de estilo CSS.
3. **Esperas Explícitas (`WebDriverWait`):** Nenhum script utiliza `time.sleep()`. O `driver.implicitly_wait(0)` é configurado no `conftest.py` e todas as transições aguardam condições explícitas do DOM (visibilidade de elementos, atualização assíncrona do `fetch` em `#sucesso`/`#erro` ou mudança de URL no Vue Router).
4. **Independência e Preparação de Estado por API:** Cada caso de teste é precedido por uma fixture `autouse=True` que zera o estado via API (`POST /api/admin/reset` no Pacote A, `POST /api/reset` no Pacote B e `POST /api/reset-teste/` na Clínica Agenda). Cenários de estado prévio (como esgotar as 5 vagas de `MOB` na regra R5 ou lotar as 2 vagas de um minicurso em `CT-B11`) são montados rapidamente via `requests.post` na preparação do teste, enquanto a ação avaliada e a verificação principal ocorrem 100% pela interface gráfica.

---

## 3. Resultado das 3 Execuções de Cada Suíte (Verificação de Oscilação / Flakiness)

Todas as suítes foram executadas **3 vezes consecutivas** em modo headless (`Chrome 151.0`), gerando relatórios HTML e JUnit XML independentes em `resultados/`:

| Suíte de Teste | Casos / Testes | Execução 1 (`r1`) | Execução 2 (`r2`) | Execução 3 (`r3`) | Testes que Oscilaram (Flaky) |
|---|---:|---|---|---|---:|
| **Exemplo A – Fluxo de Pedido** | 5 testes | 5 aprovados (43,97 s) | - | - | 0 |
| **Desafio A – Portal de Matrícula** | 12 testes (10 CTs) | **12 aprovados** (49,88 s) | **12 aprovados** (47,88 s) | **12 aprovados** (49,46 s) | **0 (0% de oscilação)** |
| **Exemplo B – Login Portal ADS** | 2 testes | 2 aprovados (6,90 s) | - | - | 0 |
| **Desafio B – Inscrições Minicursos** | 12 testes (12 CTs) | **12 aprovados** (44,80 s) | **12 aprovados** (44,89 s) | **12 aprovados** (44,92 s) | **0 (0% de oscilação)** |
| **Projeto Anterior – Clínica Agenda** | 8 testes (8 CTs) | **8 aprovados** (34,42 s) | **8 aprovados** (34,15 s) | **8 aprovados** (34,38 s) | **0 (0% de oscilação)** |

---

## 4. Defeitos Encontrados, Dificuldades e Limitações

1. **Análise de Defeitos Funcionais nos Sistemas Testados:**
   - Todos os três sistemas cumpriram as regras de negócio especificadas para os fluxos avaliados (0 falhas de regra de negócio nas 36 execuções somadas).
   - **Observação de Usabilidade / Segurança Didática no Pacote B (`/login` e `/painel`):** Conforme documentado no próprio código do Sistema B, a rota `/painel` é uma página estática que não valida cookie de sessão no servidor caso seja acessada diretamente pela URL sem passar por `/login` (diferentemente do Pacote A e da Clínica Agenda, que bloqueiam o acesso direto a `/matricula/disciplinas` e `/painel`).
2. **Dificuldades Técnicas Superadas:**
   - **Sincronização em formulários com redirect no Chrome 151 (Pacote A):** O uso de `EC.staleness_of(tabela)` após o submit do formulário de matrícula em `POST /matricula/confirmar` podia lançar `WebDriverException: Node with given id does not belong to the document` no Chrome 151 quando o redirect `302 -> GET /matricula/disciplinas` completava no mesmo milissegundo do clique. A substituição por uma espera explícita pela presença de `#mensagem-erro` ou `#mensagem-sucesso` eliminou 100% da instabilidade.
   - **Exclusão Lógica (*Soft Delete*) no Projeto Anterior (Clínica Agenda):** O `CommonModel` da Clínica Agenda sobrescreve `.delete()` para apenas marcar `ativo=False`, mantendo o registro físico na tabela e acionando a constraint `UNIQUE` case-insensitive (`especialidade_nome_unico_case_insensitive`) durante a limpeza entre testes. A solução foi utilizar `_raw_delete` no endpoint de reset de testes.
3. **Limitações da Cobertura:**
   - Os testes foram executados em um único navegador (Google Chrome 151 no Windows 11) e resolução desktop (`1280x900`), não cobrindo testes cross-browser (Firefox/Safari) ou viewports mobile.

---

## 5. Tabela de Contribuição dos Integrantes

| Integrante | Contribuições Principais no Trabalho 2 |
|---|---|
| **Francisco de Cássio da Silva Mourão Júnior** | Estruturação do repositório, execução do Exemplo A (Sabor Express), implementação dos Page Objects e dos 12 testes automatizados do **Desafio A (Portal de Matrícula R1 a R7)**, adição de `data-testid` e Page Objects da **Clínica Agenda** e elaboração do `README.md`. |
| **Álvaro Miguel Rodrigues Aquino Costa** | Especificação da [`matriz_casos_de_teste.csv`](./matriz_casos_de_teste.csv) (30 casos), execução do Exemplo B, implementação do Page Object e dos 12 casos do **Desafio B (Inscrições em Minicursos)**, implementação dos 8 casos funcionais da **Clínica Agenda** e redação do relatório e slides. |
