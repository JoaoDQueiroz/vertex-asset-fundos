# Vertex Asset · Fundos (Streamlit)

Painel interno para acompanhar posição de caixa por fundo, cadastro, assembleias e variação de saldo em CC em janelas de data. Pensado para operações que precisam cruzar saldo, rubricas de despesa e cadastro sem sair de um único fluxo.

Contexto do envio: processo na **Amazon Transportes** (base na Vila Maria, São Paulo — transporte/logística, não varejo nem AWS).

![Esquema das áreas do painel](docs/readme_assets/overview.svg)

**O que entra no repo**

| Área | Função |
|------|--------|
| Disponibilidade de caixa | Data + fundos; janela 1M/3M/6M com métricas e donut por administrador; abas de relatório e despesa. |
| Assembleias | Eventos deserializados de JSON, com filtros e leitura por status. |
| Cadastro de fundos | Grade com filtros; segunda aba só com colunas de taxas. |
| Saldo em conta corrente | Duas datas mais recentes, diferença por fundo, exportação Excel. |

**Stack**

Streamlit + Pandas + Plotly (donut). A vaga cita Angular/Node: o case prioriza dados e leitura de negócio; em entrevista cruzas com JS se fizer sentido.

## Publicar para revisão

- **Git**: push para GitHub/GitLab (público ou privado com convite) + link no email/candidatura.
- **Streamlit Community Cloud**: liga o repo, `requirements.txt`, sem secrets se mantiveres só `RCAP_DEMO=1` e `demo_data/` no repositório.
- **Docker**: `docker compose up --build` numa máquina acessível na rede da empresa ou exposta com o controlo de segurança que eles exigirem.
- **Zip**: anexar o mesmo conteúdo do repo com instruções do README.
- **Reunião**: `run.bat` ou `streamlit run` + partilha de ecrã.

`pytest` e Docker não são obrigatórios para abrir o app no dia a dia; convém mantê-los no envio se a avaliação incluir código e reprodutibilidade.

---

## Execução local (Windows)

`run.bat` — cria `.venv` se precisar, instala dependências, `RCAP_DEMO=1`, arranca o Streamlit com `demo_data/`.

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "$PWD\src"
$env:RCAP_DEMO = "1"
python -m streamlit run app.py
```

## Docker (opcional)

```bash
docker compose up --build
```

Serviço em `http://localhost:8501`. Variável `RCAP_DEMO=1` já vem no compose.

## Dados

Planilhas em `demo_data/` com nomes fixos. Regenerar: `python scripts/build_demo_xlsx.py`.

## Testes

```powershell
$env:PYTHONPATH = "$PWD\src"
pytest tests/
```

## LGPD

Dados sintéticos; não há titulares identificáveis nem operações reais. Não versionar `.env` com credenciais nem extracts de produção.

## MySQL (opcional)

`.env.example` → `.env` com `MYSQL_*` e `RCAP_DEMO=0` se quiseres apontar a uma base privada.

## Árvore relevante

- `app.py` — entrada
- `src/rcap_fundos/ui/` — ecrãs e sidebar
- `src/rcap_fundos/core/` — cálculos, demo, MySQL opcional
- `tests/` — pytest sobre lógica de caixa
- `styles/`, `imagens/`

Substituir o SVG por captura real: gravar `docs/readme_assets/dashboard.png` e trocar a linha do `![...]` no topo deste ficheiro.
