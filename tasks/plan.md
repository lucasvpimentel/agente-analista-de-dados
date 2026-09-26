# Plano de Implementação: DataLens (Agente IA Analista de Dados)

## Visão Geral

App Streamlit: upload de CSV/Excel → profile estatístico determinístico (pandas/numpy/scipy,
sem libs pesadas de auto-profiling) → camada de Agente IA (OpenAI SDK) que resume o profile
e responde perguntas em chat. Chave de API do usuário fica só em `session_state`, injetada
por parâmetro no cliente do provedor — nunca em cache, disco, log ou export. Deploy no
Streamlit Community Cloud via GitHub, sem secrets no servidor.

## Decisões de Arquitetura

- **Camadas separadas**: `ingestion` (leitura de arquivo) → `profiling` (estatística pura,
  testável sem Streamlit) → `agent` (provider LLM injetado por parâmetro) → `ui` (Streamlit:
  sidebar + abas) → `export`. `app.py` na raiz só orquestra chamadas às camadas.
- **Provider LLM atrás de interface**: `LLMProvider` abstrata com `generate_summary(profile)`
  e `chat(messages, profile) -> Iterator[str]` (streaming). `OpenAIProvider` implementa;
  recebe `api_key` e `model` no construtor — nunca lê de estado global ou `st.secrets`.
  Facilita trocar de provedor depois e mockar em teste.
- **Config único**: `src/config.py` concentra `MODELS`, `DEFAULT_MODEL`, limites de tamanho
  (`MAX_FILE_SIZE_MB`, `MAX_ROWS_FULL_PROFILE`, `SAMPLE_ROWS_FOR_AGENT`), thresholds
  (outlier, categoria rara, correlação). Nenhum nome de modelo ou limite hardcoded fora daqui.
- **Chave de API**: só em `st.session_state["openai_api_key"]`. Nenhuma função de
  profiling/export toca nessa chave. Nenhum `st.cache_data`/`st.cache_resource` envolve a
  chave ou o cliente OpenAI instanciado com ela — cache do profile é cacheado só pelos
  bytes/hash do arquivo de dados.
- **Sem exec/eval**: function calling (Fase 2, opcional) chama só funções Python
  pré-registradas com validação de argumentos; nunca executa código gerado pelo modelo.
- **Amostragem grande**: acima de `MAX_ROWS_FULL_PROFILE`, profile roda em amostra
  configurável para caber nos ~1GB RAM do Streamlit Cloud free.

## Grafo de Dependências

```
config.py
    │
    ├── ingestion (leitura CSV/Excel)
    │       │
    │       └── profiling (overview, tipos, numérico, categórico, data, qualidade, correlação)
    │               │
    │               ├── ui/tabs (Visão Geral, Colunas, Qualidade, Correlações)
    │               │
    │               └── agent/orchestrator (recebe profile resumido)
    │                       │
    ├── agent/provider (interface + OpenAIProvider)
    │       │
    │       └── agent/orchestrator ──┴──> ui/tabs (Agente IA)
    │                                          │
    ├── ui/sidebar (config de chave, usa agent/provider p/ validar)
    │                                          │
    └── export (usa profiling + agent) ────────┴──> ui/tabs (Exportar)
```

Ordem de implementação segue bottom-up com fatiamento vertical: cada fase entrega algo
visível e testável no app, não uma camada horizontal isolada.

## Lista de Tarefas

Tarefas detalhadas (descrição, critérios de aceite, verificação, dependências, arquivos)
estão em `tasks/todo.md`. Índice por fase:

### Fase 0 — Scaffold
- Tarefa 1: Estrutura de pastas, config.py, requirements, .gitignore, tema Streamlit
- Tarefa 2: CI (GitHub Actions: ruff + pytest, sem chave real)

### Checkpoint: Fase 0
- Estrutura roda `streamlit run app.py` mostrando página vazia sem erro; CI verde.

### Fase 1 — Ingestão (fatia vertical: upload → preview)
- Tarefa 3: Módulo de ingestão (CSV: sep/encoding auto; Excel: seleção de aba; limites)
- Tarefa 4: UI de upload + preview na página principal

### Checkpoint: Fase 1
- Usuário sobe CSV com `;` e Excel multi-aba local e vê preview correto; testes de
  ingestão passam.

### Fase 2 — Profile determinístico (fatia vertical: dados → abas de análise)
- Tarefa 5: Inferência de tipo por coluna + overview geral
- Tarefa 6: Estatísticas numéricas + outliers (IQR e z-score) + histograma/boxplot
- Tarefa 7: Estatísticas categóricas + alerta de categoria rara
- Tarefa 8: Estatísticas de data/hora + série temporal
- Tarefa 9: Qualidade de dados (nulos, constantes, quase-únicas, duplicatas, alertas)
- Tarefa 10: Correlações (Pearson/Spearman + Cramér's V opcional) com destaque de pares
- Tarefa 11: Abas Streamlit (Visão Geral, Colunas, Qualidade, Correlações) com gráficos Plotly
  e cache do profile via `st.cache_data` (chave = hash dos dados, não da API key)

### Checkpoint: Fase 2
- App funciona 100% sem chave de API: todas as 4 abas de análise mostram dados reais de
  um dataset de exemplo; testes de profiling (incluindo correção manual de tipo) passam.

### Fase 3 — Configuração da chave de API (sidebar)
- Tarefa 12: Interface `LLMProvider` + `OpenAIProvider` (sem chamada de chat ainda, só
  validação leve de chave)
- Tarefa 13: Sidebar — campo de senha, seletor de modelo, botão validar, botão limpar,
  link OpenAI, texto de aviso; estado não configurada/válida/inválida/sem créditos

### Checkpoint: Fase 3
- Chave inválida mostra erro amigável; chave válida muda o indicador; "Limpar chave"
  reseta estado; nenhuma chave aparece em log/print/export nesta fase (checagem manual).

### Fase 4 — Agente: resumo executivo
- Tarefa 14: `agent/orchestrator.py` monta contexto (profile resumido + schema + amostra
  pequena, nunca dataset completo) e chama `generate_summary`
- Tarefa 15: Aba "Agente IA" — estado vazio sem chave; botão de resumo executivo com
  tratamento de erro (chave ausente/inválida/cota/rate limit/timeout) em pt-BR

### Checkpoint: Fase 4
- Com chave válida, botão gera resumo executivo coerente sobre dataset de exemplo; com
  chave inválida/sem créditos, mensagem amigável sem stack trace nem chave exposta.

### Fase 5 — Agente: chat
- Tarefa 16: Chat com streaming (`chat()` como generator), histórico em `session_state`,
  botão limpar conversa
- Tarefa 17: Truncamento inteligente de contexto quando profile é grande demais

### Checkpoint: Fase 5
- Conversa multi-turno funciona com streaming visível; truncamento evita erro de
  contexto excedido em dataset largo (muitas colunas).

### Fase 6 — Function calling do agente
- Tarefa 18: Registro de funções seguras (agregar, filtrar, agrupar, estatística, gráfico)
  com validação de argumentos, sem exec/eval
- Tarefa 19: Integração de function calling no chat com fallback se modelo não suportar

### Checkpoint: Fase 6
- Perguntas que pedem agregação/filtro disparam função correta; argumentos inválidos são
  rejeitados sem executar.

### Fase 7 — Exportação
- Tarefa 20: Export do profile em JSON
- Tarefa 21: Export do relatório (resumo do agente) em Markdown/HTML
- Tarefa 22: Teste/checagem garantindo ausência da chave em qualquer arquivo exportado

### Checkpoint: Fase 7
- Download de JSON e Markdown/HTML funciona; teste de "sem vazamento de chave" passa.

### Fase 8 — Qualidade, testes e CI final
- Tarefa 23: Suite pytest completa (ingestão, profiling, agente com client OpenAI
  mockado incluindo chave inválida/cota esgotada/rate limit/function calling)
- Tarefa 24: Ruff (lint + format) configurado e app 100% conforme
- Tarefa 25: Checagem de não-vazamento de chave em logs (teste dedicado)

### Checkpoint: Fase 8
- `pytest` e `ruff check` verdes localmente e na CI.

### Fase 9 — Documentação e deploy
- Tarefa 26: `sample_data/` com planilha de exemplo + dados de teste
- Tarefa 27: README completo (descrição, arquitetura Mermaid, como obter/usar chave,
  rodar local, tutorial de deploy passo a passo no Streamlit Cloud, segurança/privacidade,
  roadmap)
- Tarefa 28: `LICENSE`, badge "Open in Streamlit", revisão final de `.gitignore`

### Checkpoint: Final
- Todos os critérios de aceite atendidos; app publicável no Streamlit Community Cloud
  seguindo o próprio README; revisão humana antes de merge/deploy.

## Riscos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| RAM do plano free (~1GB) estoura com dataset grande | Alto | Amostragem configurável acima de `MAX_ROWS_FULL_PROFILE`; limite de tamanho de upload |
| Vazamento da chave de API (log, cache, export) | Alto | Chave só em `session_state`, nunca em `st.cache_*`; teste dedicado de não-vazamento (Tarefa 23) |
| Matriz de correlação cara em datasets com muitas colunas numéricas | Médio | Cap de nº de colunas na matriz + amostragem de linhas |
| Function calling (Fase 6) executar ação não intencional | Alto | Allowlist fixa de funções + validação de schema de argumentos antes de rodar; nunca exec/eval |
| Rate limit / cota esgotada da OpenAI durante demo | Médio | Tratamento de erro específico por tipo de falha, mensagens em pt-BR, sem expor chave |
| Custo de build/deploy no Streamlit Cloud com dependências pesadas | Baixo | Evitar `ydata-profiling`; manter requirements enxuto (pandas/numpy/scipy/plotly/openai/streamlit) |

## Decisões Confirmadas

- Modelo padrão: `gpt-4o-mini` (`config.DEFAULT_MODEL`), demais opções em `config.MODELS`
  a definir na Tarefa 12.
- Excel: só `.xlsx` (dependência `openpyxl`). `.xls` legado fora de escopo.
