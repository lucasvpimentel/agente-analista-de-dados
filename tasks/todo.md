# Task List: DataLens (Agente IA Analista de Dados)

Ver `tasks/plan.md` para arquitetura, grafo de dependências, riscos e questões em aberto.

---

## Fase 0: Scaffold

### Task 1: Estrutura de pastas, config, requirements, tema
- [x] Done

**Description:** Criar esqueleto do projeto: `app.py` na raiz, pacote `src/` (vazio com
`__init__.py` nos submódulos previstos: `ingestion`, `profiling`, `agent`, `export`, `ui`),
`src/config.py` com `MODELS`, `DEFAULT_MODEL`, limites e thresholds, `requirements.txt`,
`.streamlit/config.toml` (tema), `.gitignore` (cobrindo `.env`, `.streamlit/secrets.toml`,
`__pycache__`, `.venv`).

**Acceptance criteria:**
- [x] `streamlit run app.py` sobe sem erro e mostra página placeholder
- [x] `src/config.py` é o único lugar com nomes de modelo/limites (nada hardcoded alhures)
- [x] `.gitignore` cobre `.env` e `.streamlit/secrets.toml`

**Verification:**
- [x] Manual: `streamlit run app.py` abre local sem exceção
- [x] Manual: `git status` não lista `.env`/`secrets.toml` se criados

**Dependencies:** None

**Files likely touched:**
- `app.py`
- `src/config.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `.gitignore`

**Estimated scope:** Medium: 3-5 files

---

### Task 2: CI com GitHub Actions
- [x] Done

**Description:** Workflow que roda `ruff check` e `pytest` em push/PR, Python 3.11 e 3.12,
sem precisar de chave de API real (testes do agente usam mock).

**Acceptance criteria:**
- [x] Workflow roda em push e pull_request
- [x] Falha se lint ou teste falhar
- [x] Não depende de secret nenhum para passar

**Verification:**
- [x] Manual: workflow YAML validado (sintaxe checada com `yaml.safe_load`)
- [ ] Push de teste mostra CI verde no GitHub (pendente: nenhum push ao remoto ainda)

**Dependencies:** Task 1

**Files likely touched:**
- `.github/workflows/ci.yml`

**Estimated scope:** Small: 1-2 files

---

## Checkpoint: Fase 0
- [x] `streamlit run app.py` funciona sem erro
- [x] CI configurada (verde localmente: `ruff`/`pytest`; verde no GitHub pendente do primeiro push)
- [ ] Revisão com humano antes de prosseguir

---

## Fase 1: Ingestão (fatia vertical: upload → preview)

### Task 3: Módulo de ingestão
- [x] Done

**Description:** `src/ingestion.py` com função que recebe arquivo enviado (bytes/objeto do
Streamlit) e retorna `DataFrame` + metadados (nome da aba escolhida, encoding/separador
detectados, se foi amostrado). CSV: detectar separador (`,`, `;`, `\t`) e encoding
(UTF-8, Latin-1) automaticamente, com fallback explícito se detecção falhar. Excel: listar
abas e ler a escolhida. Aplicar `MAX_FILE_SIZE_MB` e amostragem acima de
`MAX_ROWS_FULL_PROFILE` (de `src/config.py`).

**Acceptance criteria:**
- [x] CSV com `;` e vírgula decimal (padrão BR) é lido corretamente
- [x] CSV UTF-8 e Latin-1 são lidos corretamente
- [x] Excel com múltiplas abas retorna lista de abas para escolha
- [x] Arquivo acima do limite de tamanho é rejeitado com mensagem clara
- [x] Dataset acima de `MAX_ROWS_FULL_PROFILE` é amostrado e o metadado indica isso

**Verification:**
- [x] Tests pass: `pytest tests/test_ingestion.py`
- [x] Manual: nenhum

**Dependencies:** Task 1

**Files likely touched:**
- `src/ingestion.py`
- `tests/test_ingestion.py`

**Estimated scope:** Medium: 3-5 files

---

### Task 4: UI de upload + preview
- [x] Done

**Description:** Página principal com `st.file_uploader` (csv/xlsx), seletor de aba
quando Excel tem múltiplas, exibição de metadados de leitura (separador/encoding
detectados, se foi amostrado) e preview das primeiras linhas.

**Acceptance criteria:**
- [x] Upload de CSV BR e Excel multi-aba funciona ponta a ponta na UI
- [x] Preview mostra as primeiras linhas do dataset carregado
- [x] Mensagem de erro amigável para arquivo inválido/corrompido

**Verification:**
- [x] Manual: `streamlit run app.py` sobe limpo com uploader wired (teste de upload real no navegador ainda pendente pelo usuário)

**Dependencies:** Task 3

**Files likely touched:**
- `app.py`
- `src/ui/upload.py`

**Estimated scope:** Small: 1-2 files

---

## Checkpoint: Fase 1
- [x] Upload local de CSV `;`, CSV Latin-1 e Excel multi-aba funciona (coberto por teste automatizado de roteamento; upload manual no navegador pendente de validação do usuário)
- [x] `pytest tests/test_ingestion.py` passa
- [ ] Revisão com humano antes de prosseguir

---

## Fase 2: Profile determinístico (fatia vertical: dados → abas de análise)

### Task 5: Inferência de tipo + overview geral
- [x] Done

**Description:** `src/profiling/overview.py`: nº linhas/colunas, uso de memória, linhas
duplicadas, % nulos total. `src/profiling/types.py`: inferir tipo por coluna (numérica,
categórica, data/hora, texto livre, booleana, ID de alta cardinalidade) com função que
permite override manual do tipo inferido (recebe dict de overrides).

**Acceptance criteria:**
- [x] Overview retorna todos os números esperados para um DataFrame de teste conhecido
- [x] Inferência de tipo acerta os 6 tipos em um dataset sintético com um exemplo de cada
- [x] Override manual de tipo é respeitado no retorno

**Verification:**
- [x] Tests pass: `pytest tests/test_profiling_overview.py tests/test_profiling_types.py`

**Dependencies:** Task 3

**Files likely touched:**
- `src/profiling/overview.py`
- `src/profiling/types.py`
- `tests/test_profiling_overview.py`
- `tests/test_profiling_types.py`

**Estimated scope:** Medium: 3-5 files

---

### Task 6: Estatísticas numéricas + outliers
- [x] Done

**Description:** `src/profiling/numeric.py`: média, mediana, desvio padrão, mín, máx,
quartis, IQR, assimetria, curtose, contagem de zeros/negativos, outliers por IQR e por
z-score. Funções separadas para dados de histograma/boxplot (Plotly fica na Task 11).

**Acceptance criteria:**
- [x] Todas as métricas batem com cálculo de referência (numpy/scipy) num dataset conhecido
- [x] Outliers IQR e z-score retornam índices/contagens consistentes com dataset sintético
  com outliers propositais

**Verification:**
- [x] Tests pass: `pytest tests/test_profiling_numeric.py`

**Dependencies:** Task 5

**Files likely touched:**
- `src/profiling/numeric.py`
- `tests/test_profiling_numeric.py`

**Estimated scope:** Small: 1-2 files

---

### Task 7: Estatísticas categóricas
- [ ] Not started

**Description:** `src/profiling/categorical.py`: cardinalidade, moda, top N frequências,
alerta de categoria rara (abaixo de threshold configurável em `config.py`).

**Acceptance criteria:**
- [ ] Cardinalidade e moda corretas em dataset de teste
- [ ] Categorias abaixo do threshold aparecem no alerta de "rara"

**Verification:**
- [ ] Tests pass: `pytest tests/test_profiling_categorical.py`

**Dependencies:** Task 5

**Files likely touched:**
- `src/profiling/categorical.py`
- `tests/test_profiling_categorical.py`

**Estimated scope:** Small: 1-2 files

---

### Task 8: Estatísticas de data/hora
- [ ] Not started

**Description:** `src/profiling/datetime_stats.py`: intervalo (min/max), granularidade
detectada (diária/mensal/etc.), lacunas temporais, série de contagem por período.

**Acceptance criteria:**
- [ ] Granularidade detectada corretamente para série diária e mensal sintéticas
- [ ] Lacunas (datas faltantes) detectadas corretamente em série com buraco proposital

**Verification:**
- [ ] Tests pass: `pytest tests/test_profiling_datetime.py`

**Dependencies:** Task 5

**Files likely touched:**
- `src/profiling/datetime_stats.py`
- `tests/test_profiling_datetime.py`

**Estimated scope:** Small: 1-2 files

---

### Task 9: Qualidade de dados
- [ ] Not started

**Description:** `src/profiling/quality.py`: nulos por coluna (para mapa de nulos),
colunas constantes, colunas quase-únicas, possíveis linhas duplicadas, lista de alertas
priorizados por severidade (combina sinais das tasks 5-8).

**Acceptance criteria:**
- [ ] Coluna 100% nula, coluna constante e coluna quase-única são detectadas em dataset
  sintético desenhado para isso
- [ ] Alertas saem ordenados por severidade

**Verification:**
- [ ] Tests pass: `pytest tests/test_profiling_quality.py`

**Dependencies:** Task 5, Task 6, Task 7

**Files likely touched:**
- `src/profiling/quality.py`
- `tests/test_profiling_quality.py`

**Estimated scope:** Small: 1-2 files

---

### Task 10: Correlações
- [ ] Not started

**Description:** `src/profiling/correlations.py`: matriz Pearson e Spearman para numéricas,
destaque de pares acima de `CORRELATION_THRESHOLD`; Cramér's V opcional para categóricas.
Cap de nº de colunas na matriz para evitar custo O(n²) em datasets largos.

**Acceptance criteria:**
- [ ] Matrizes Pearson/Spearman corretas num dataset com correlação conhecida
- [ ] Pares acima do threshold aparecem destacados
- [ ] Nº de colunas acima do cap é truncado com aviso, não trava o app

**Verification:**
- [ ] Tests pass: `pytest tests/test_profiling_correlations.py`

**Dependencies:** Task 5, Task 6

**Files likely touched:**
- `src/profiling/correlations.py`
- `tests/test_profiling_correlations.py`

**Estimated scope:** Small: 1-2 files

---

### Task 11: Abas Streamlit de análise + cache
- [ ] Not started

**Description:** Abas "Visão Geral", "Colunas", "Qualidade", "Correlações" no `app.py`
usando `src/ui/tabs/`. Gráficos Plotly (histograma, boxplot, barras, mapa de nulos,
heatmap de correlação). `st.cache_data` no cálculo do profile, chaveado pelo conteúdo do
arquivo (hash), nunca pela chave de API.

**Acceptance criteria:**
- [ ] Todas as 4 abas renderizam com dataset de exemplo sem chave de API configurada
- [ ] Recarregar o mesmo arquivo não recalcula o profile (cache hit observável)
- [ ] Trocar de arquivo invalida o cache corretamente

**Verification:**
- [ ] Manual: testar as 4 abas com `sample_data/` (placeholder simples nesta fase)
- [ ] Manual: confirmar cache hit/miss via `st.cache_data` (log ou contador)

**Dependencies:** Task 6, Task 7, Task 8, Task 9, Task 10

**Files likely touched:**
- `app.py`
- `src/ui/tabs/visao_geral.py`
- `src/ui/tabs/colunas.py`
- `src/ui/tabs/qualidade.py`
- `src/ui/tabs/correlacoes.py`

**Estimated scope:** Large: 5-8 files (considerar dividir por aba se crescer)

---

## Checkpoint: Fase 2
- [ ] App funciona 100% sem chave de API com as 4 abas de análise mostrando dados reais
- [ ] `pytest tests/test_profiling_*.py` todos passam
- [ ] Revisão com humano antes de prosseguir

---

## Fase 3: Configuração da chave de API (sidebar)

### Task 12: Interface LLMProvider + OpenAIProvider (validação)
- [ ] Not started

**Description:** `src/agent/provider.py`: classe abstrata `LLMProvider` com
`generate_summary(profile) -> str`, `chat(messages, profile) -> Iterator[str]` e
`validate_key() -> ValidationResult` (status: válida/inválida/sem créditos/erro de rede).
`OpenAIProvider` implementa usando o SDK oficial, recebendo `api_key` e `model` só no
construtor.

**Acceptance criteria:**
- [ ] `validate_key()` distingue chave inválida, sem créditos e chave válida (mockando a
  API da OpenAI nos testes)
- [ ] Nenhum método lê `st.session_state` ou variável global — tudo por parâmetro/atributo
  de instância

**Verification:**
- [ ] Tests pass: `pytest tests/test_agent_provider.py` (client OpenAI mockado)

**Dependencies:** Task 1

**Files likely touched:**
- `src/agent/provider.py`
- `tests/test_agent_provider.py`

**Estimated scope:** Medium: 3-5 files

---

### Task 13: Sidebar de configuração da chave
- [ ] Not started

**Description:** `src/ui/sidebar.py`: campo de senha para a chave, seletor de modelo
(opções de `config.MODELS`, default `config.DEFAULT_MODEL`), botão "Validar", botão
"Limpar chave" (reseta `session_state` da chave e do agente), link para gerar chave na
OpenAI, texto curto de aviso de uso só-na-sessão. Indicador visual de status.

**Acceptance criteria:**
- [ ] Chave nunca é reexibida na tela (nem mascarada parcialmente além do necessário para
  confirmação)
- [ ] "Limpar chave" remove a chave de `session_state` e volta app para estado "não
  configurada"
- [ ] Estado inválida/sem créditos mostra mensagem amigável sem stack trace

**Verification:**
- [ ] Manual: inserir chave falsa → ver "inválida"; limpar → ver "não configurada"
- [ ] Manual: `print`/log da sessão não deve conter a chave em nenhum ponto (checar código)

**Dependencies:** Task 12

**Files likely touched:**
- `src/ui/sidebar.py`
- `app.py`

**Estimated scope:** Small: 1-2 files

---

## Checkpoint: Fase 3
- [ ] Fluxo completo de configurar/validar/limpar chave funciona na sidebar
- [ ] Nenhuma chave aparece em log, print ou tela após configurada
- [ ] Revisão com humano antes de prosseguir

---

## Fase 4: Agente — resumo executivo

### Task 14: Orquestrador do agente (contexto)
- [ ] Not started

**Description:** `src/agent/orchestrator.py`: monta contexto para o LLM a partir do
profile resumido (JSON compacto), schema de colunas e amostra pequena de dados
(configurável, nunca o dataset completo). Função `build_context(profile, sample_df) -> dict`
separada da chamada ao provider, para ser testável isoladamente.

**Acceptance criteria:**
- [ ] Contexto gerado nunca inclui mais que `SAMPLE_ROWS_FOR_AGENT` linhas de dado bruto
- [ ] Contexto é serializável em JSON sem erro para todos os tipos de coluna suportados

**Verification:**
- [ ] Tests pass: `pytest tests/test_agent_orchestrator.py`

**Dependencies:** Task 9, Task 10, Task 12

**Files likely touched:**
- `src/agent/orchestrator.py`
- `tests/test_agent_orchestrator.py`

**Estimated scope:** Small: 1-2 files

---

### Task 15: Aba "Agente IA" — resumo executivo
- [ ] Not started

**Description:** Aba mostra estado vazio orientando a configurar a chave quando ausente;
com chave válida, botão gera resumo executivo (características principais, problemas de
qualidade, hipóteses, próximos passos) via `orchestrator` + `provider.generate_summary`.
Tratamento de erro por tipo (chave ausente/inválida, chave revogada, cota esgotada, rate
limit, timeout, modelo indisponível) com mensagens pt-BR sem expor a chave. Aviso de
privacidade (o que é enviado à OpenAI, custo é do dono da chave).

**Acceptance criteria:**
- [ ] Sem chave: estado vazio orientando a configurar na sidebar, resto do app funciona
- [ ] Com chave válida: resumo executivo é gerado e exibido
- [ ] Cada tipo de erro simulado (mock) produz mensagem pt-BR específica, nunca stack trace
  cru nem a chave

**Verification:**
- [ ] Tests pass: `pytest tests/test_agent_orchestrator.py` cobre os cenários de erro via
  provider mockado
- [ ] Manual: gerar resumo com chave real de teste (custo mínimo) no dataset de exemplo

**Dependencies:** Task 13, Task 14

**Files likely touched:**
- `src/ui/tabs/agente_ia.py`
- `app.py`

**Estimated scope:** Medium: 3-5 files

---

## Checkpoint: Fase 4
- [ ] Resumo executivo funciona ponta a ponta com chave real de teste
- [ ] Todos os cenários de erro mockados passam em teste
- [ ] Revisão com humano antes de prosseguir

---

## Fase 5: Agente — chat

### Task 16: Chat com streaming e histórico
- [ ] Not started

**Description:** `provider.chat()` como generator de tokens/chunks; UI de chat na aba
"Agente IA" com `st.chat_message`/`st.chat_input`, histórico em
`session_state["chat_history"]`, botão "Limpar conversa".

**Acceptance criteria:**
- [ ] Resposta aparece incrementalmente (streaming) na UI
- [ ] Histórico persiste entre perguntas na mesma sessão
- [ ] "Limpar conversa" zera o histórico sem afetar a chave configurada

**Verification:**
- [ ] Tests pass: `pytest tests/test_agent_provider.py` (streaming mockado retorna chunks)
- [ ] Manual: conversa de 3+ turnos no app local

**Dependencies:** Task 15

**Files likely touched:**
- `src/agent/provider.py`
- `src/ui/tabs/agente_ia.py`

**Estimated scope:** Small: 1-2 files

---

### Task 17: Truncamento inteligente de contexto
- [ ] Not started

**Description:** Quando profile + histórico excede limite de tokens estimado, truncar
priorizando: alertas de qualidade > estatísticas resumidas > amostra de dados > histórico
antigo de chat. Função isolada e testável.

**Acceptance criteria:**
- [ ] Dataset sintético com 200+ colunas não gera erro de contexto excedido
- [ ] Truncamento preserva os alertas de maior severidade

**Verification:**
- [ ] Tests pass: `pytest tests/test_agent_orchestrator.py::test_truncamento`

**Dependencies:** Task 14, Task 16

**Files likely touched:**
- `src/agent/orchestrator.py`
- `tests/test_agent_orchestrator.py`

**Estimated scope:** Small: 1-2 files

---

## Checkpoint: Fase 5
- [ ] Chat multi-turno com streaming funciona
- [ ] Dataset largo (muitas colunas) não quebra por excesso de contexto
- [ ] Revisão com humano antes de prosseguir

---

## Fase 6: Function calling do agente

### Task 18: Registro de funções seguras
- [ ] Not started

**Description:** `src/agent/tools.py`: allowlist fixa de funções (agregar, filtrar,
agrupar, calcular estatística, gerar gráfico) com schema de argumentos e validação
explícita antes de executar. Sem `exec`/`eval` em nenhum ponto.

**Acceptance criteria:**
- [ ] Argumento fora do schema é rejeitado antes de qualquer execução
- [ ] Nenhuma função aceita string de código arbitrário como argumento

**Verification:**
- [ ] Tests pass: `pytest tests/test_agent_tools.py`

**Dependencies:** Task 9, Task 10

**Files likely touched:**
- `src/agent/tools.py`
- `tests/test_agent_tools.py`

**Estimated scope:** Medium: 3-5 files

---

### Task 19: Integração de function calling no chat
- [ ] Not started

**Description:** `orchestrator`/`provider` passam a oferecer as ferramentas da Task 18 ao
modelo via function calling da OpenAI; resultado da função volta pro modelo compor a
resposta final. Fallback normal se o modelo/conta não suportar function calling.

**Acceptance criteria:**
- [ ] Pergunta que pede agregação simples ("total de vendas por região") dispara a função
  correta e usa o resultado na resposta
- [ ] Sem suporte a function calling, chat continua funcionando no modo texto simples

**Verification:**
- [ ] Tests pass: `pytest tests/test_agent_orchestrator.py::test_function_calling`
- [ ] Manual: testar 2-3 perguntas de agregação com chave real no dataset de exemplo

**Dependencies:** Task 16, Task 18

**Files likely touched:**
- `src/agent/orchestrator.py`
- `src/agent/provider.py`

**Estimated scope:** Medium: 3-5 files

---

## Checkpoint: Fase 6
- [ ] Function calling funciona para os casos de agregação/filtro básicos
- [ ] Nenhum caminho de código executa string vinda do modelo
- [ ] Revisão com humano antes de prosseguir

---

## Fase 7: Exportação

### Task 20: Export do profile em JSON
- [ ] Not started

**Description:** `src/export.py`: serializa o profile completo (overview, tipos,
numérico, categórico, data, qualidade, correlações) em JSON para download via
`st.download_button`.

**Acceptance criteria:**
- [ ] JSON exportado é válido e reflete os dados calculados nas abas
- [ ] Nenhuma chave ou configuração sensível presente no JSON

**Verification:**
- [ ] Tests pass: `pytest tests/test_export.py::test_json`

**Dependencies:** Task 9, Task 10

**Files likely touched:**
- `src/export.py`
- `tests/test_export.py`

**Estimated scope:** Small: 1-2 files

---

### Task 21: Export do relatório em Markdown/HTML
- [ ] Not started

**Description:** Relatório combinando resumo do agente (se gerado) + principais achados do
profile, exportável em Markdown e HTML.

**Acceptance criteria:**
- [ ] Relatório é gerado mesmo sem resumo do agente (usa só o profile determinístico)
- [ ] Nenhuma chave ou configuração sensível presente no relatório

**Verification:**
- [ ] Tests pass: `pytest tests/test_export.py::test_markdown_html`

**Dependencies:** Task 15, Task 20

**Files likely touched:**
- `src/export.py`
- `src/ui/tabs/exportar.py`

**Estimated scope:** Small: 1-2 files

---

### Task 22: Teste de não-vazamento de chave em exports
- [ ] Not started

**Description:** Teste dedicado que gera todos os artefatos de export com uma chave falsa
presente na sessão e garante que a string da chave não aparece em nenhum output.

**Acceptance criteria:**
- [ ] Teste falha propositalmente se alguém colar a chave em um export (validar com bug
  injetado temporariamente durante o desenvolvimento do teste)

**Verification:**
- [ ] Tests pass: `pytest tests/test_export.py::test_no_key_leak`

**Dependencies:** Task 20, Task 21

**Files likely touched:**
- `tests/test_export.py`

**Estimated scope:** Small: 1-2 files

---

## Checkpoint: Fase 7
- [ ] Download de JSON e Markdown/HTML funciona no app
- [ ] Teste de não-vazamento de chave passa
- [ ] Revisão com humano antes de prosseguir

---

## Fase 8: Qualidade, testes e CI final

### Task 23: Suite pytest completa e cenários de falha do agente
- [ ] Not started

**Description:** Completar cobertura: ingestão (encodings/separadores/tamanho), profiling
(todas as funções), agente (chave inválida, cota esgotada, rate limit, timeout, modelo
indisponível, function calling), export. Client OpenAI sempre mockado.

**Acceptance criteria:**
- [ ] Cobertura cobre todos os módulos de `src/`
- [ ] Todos os cenários de erro do agente listados no RF4 têm teste correspondente

**Verification:**
- [ ] Tests pass: `pytest` (suite completa)

**Dependencies:** Tasks 3-22

**Files likely touched:**
- `tests/**`

**Estimated scope:** Medium: 3-5 files

---

### Task 24: Ruff (lint + format)
- [ ] Not started

**Description:** Configurar `ruff` (`pyproject.toml` ou `ruff.toml`) e corrigir app inteiro
para ficar em conformidade. Adicionar type hints onde faltarem nos módulos de `src/`.

**Acceptance criteria:**
- [ ] `ruff check .` sem erros
- [ ] `ruff format --check .` sem alterações pendentes

**Verification:**
- [ ] Build succeeds: `ruff check . && ruff format --check .`

**Dependencies:** Tasks 3-22

**Files likely touched:**
- `pyproject.toml`
- ajustes pontuais em `src/**`

**Estimated scope:** Medium: 3-5 files

---

### Task 25: Checagem de não-vazamento de chave em logs
- [ ] Not started

**Description:** Teste/checagem estática (grep programático ou teste de integração) que
garante que nenhuma exceção não tratada, log ou `print` no código expõe a chave de API.

**Acceptance criteria:**
- [ ] Nenhuma chamada a `print`/`logging` recebe a variável da chave diretamente em
  nenhum módulo (checagem automatizada, não só revisão manual)

**Verification:**
- [ ] Tests pass: `pytest tests/test_security_key_leak.py`

**Dependencies:** Task 13

**Files likely touched:**
- `tests/test_security_key_leak.py`

**Estimated scope:** Small: 1-2 files

---

## Checkpoint: Fase 8
- [ ] `pytest` e `ruff check`/`ruff format --check` verdes localmente e na CI
- [ ] Revisão com humano antes de prosseguir

---

## Fase 9: Documentação e deploy

### Task 26: sample_data/
- [ ] Not started

**Description:** Planilha de exemplo (CSV e/ou Excel) representativa (mistura de tipos:
numérico, categórico, data, texto, algum nulo/outlier proposital) para demo e para os
testes usarem como fixture compartilhada.

**Acceptance criteria:**
- [ ] Arquivo de exemplo cobre todos os tipos de coluna suportados
- [ ] Testes de profiling/ingestão podem referenciar esse arquivo como fixture

**Verification:**
- [ ] Manual: app com esse arquivo mostra as 4 abas de análise preenchidas

**Dependencies:** Task 11

**Files likely touched:**
- `sample_data/exemplo.csv`
- `sample_data/exemplo.xlsx`

**Estimated scope:** Small: 1-2 files

---

### Task 27: README completo
- [ ] Not started

**Description:** Descrição, screenshot/GIF, badge "Open in Streamlit", diagrama Mermaid de
arquitetura, como obter chave OpenAI e adicionar créditos, como rodar local, tutorial de
deploy passo a passo no Streamlit Community Cloud (repo → share.streamlit.io → Create app →
Advanced settings/versão Python → subdomínio → deploy/logs → redeploy automático em push →
reboot → limitações do plano free → troubleshooting), seção de segurança/privacidade,
roadmap e como contribuir — conforme especificado no RF do projeto.

**Acceptance criteria:**
- [ ] Todas as 7 seções pedidas na spec estão presentes
- [ ] Tutorial de deploy é executável passo a passo por alguém sem contexto prévio

**Verification:**
- [ ] Manual: seguir o próprio tutorial do zero para publicar o app

**Dependencies:** Tasks 1-26

**Files likely touched:**
- `README.md`

**Estimated scope:** Medium: 3-5 files (README + imagens/GIF)

---

### Task 28: LICENSE, badge e revisão final
- [ ] Not started

**Description:** Adicionar `LICENSE`, badge "Open in Streamlit" apontando pro deploy real,
revisão final de `.gitignore` e do `requirements.txt` (versões fixadas onde fizer sentido).

**Acceptance criteria:**
- [ ] `LICENSE` presente e referenciada no README
- [ ] Badge aponta para a URL real do app publicado
- [ ] `requirements.txt` sem dependências não usadas

**Verification:**
- [ ] Manual: clicar no badge do README e confirmar que abre o app publicado

**Dependencies:** Task 27, deploy real feito

**Files likely touched:**
- `LICENSE`
- `README.md`
- `requirements.txt`

**Estimated scope:** Small: 1-2 files

---

## Checkpoint: Final
- [ ] Todos os critérios de aceite das fases 0-8 atendidos
- [ ] App publicado no Streamlit Community Cloud seguindo o próprio README
- [ ] Revisão humana final antes de considerar o projeto entregue
