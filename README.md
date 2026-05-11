# Vertex Asset · Fundos

Painel único para ver **posição de caixa**, **cadastro de fundos**, **assembleias** e **variação de saldo em CC** — com filtros, totais, indicadores por janela de tempo (1M / 3M / 6M) e leitura por administrador. Os dados deste repositório são **sintéticos** (adequado para portfólio e revisão de código).

![Visão geral das áreas](docs/readme_assets/overview.svg)

*Opcional: substituir por captura real em `docs/readme_assets/dashboard.png`.*

---

## O que o repositório mostra

| Módulo | Utilidade |
|--------|-----------|
| Disponibilidade de caixa | Referência por data e fundos; métricas agregadas; donut por administrador; relatórios e despesa detalhada. |
| Assembleias | Linha de eventos a partir de JSON, com filtros por status e prazos. |
| Cadastro de fundos | Grade consultável e aba de taxas. |
| Saldo em CC | Comparação entre as duas datas mais recentes e exportação Excel. |

**Tecnologia:** Python, Streamlit, Pandas e Plotly (gráfico circular).

---

## Como executar (depois de clonar)

**Windows:** duplo clique em `run.bat` (cria `.venv` se precisar, instala dependências, usa `demo_data/`).

**PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "$PWD\src"
$env:RCAP_DEMO = "1"
python -m streamlit run app.py
```

Abre o URL que o Streamlit indicar (em geral `http://localhost:8501`).

## Docker

```bash
docker compose up --build
```

## Dados de demonstração

Ficheiros em `demo_data/`. Regenerar: `python scripts/build_demo_xlsx.py`.

## Testes

```powershell
$env:PYTHONPATH = "$PWD\src"
pytest tests/
```

## LGPD

Sem dados pessoais nem operações reais. Não commits com `.env` com segredos nem extracts de produção.

## MySQL (opcional)

Ver `.env.example` — `RCAP_DEMO=0` e variáveis `MYSQL_*` para ambiente privado.

## Estrutura

`app.py` · `src/rcap_fundos/` (UI + núcleo) · `styles/` · `imagens/` · `tests/`

## Partilhar o projeto

GitHub/GitLab (link no email), **Streamlit Cloud** com este repo e `requirements.txt`, ou **Docker** numa máquina com acesso controlado.
