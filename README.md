# Vertex Asset · Fundos

Painel único para ver **posição de caixa**, **cadastro de fundos**, **assembleias** e **variação de saldo em CC** — com filtros, totais, indicadores por janela de tempo (1M / 3M / 6M) e leitura por administrador. Os dados deste repositório são **sintéticos** (adequado para portfólio e revisão de código).

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
$env:RCAP_DEMO = "1"
python -m streamlit run app.py
```

Abre o URL que o Streamlit indicar (em geral `http://localhost:8501`).

## URL público (Streamlit Cloud)

O link só existe **depois** de publicares uma vez (é gerado pelo Streamlit). Formato típico: `https://NOME-QUE-ESCOLHERES.streamlit.app`

1. Conta em [share.streamlit.io](https://share.streamlit.io) com o mesmo GitHub do repo.  
2. **New app** → escolhe o repositório → **Main file:** `app.py` → **Branch:** `main`.  
3. **Secrets** (recomendado): colar `RCAP_DEMO = "1"` para forçar modo planilhas (sem MySQL).  
4. **Deploy**. No fim copias o URL e colas no email / formulário.

O repo já inclui `pyproject.toml` com `-e .` no `requirements.txt` para o Cloud instalar o pacote `rcap_fundos` sem `PYTHONPATH` manual.

## Docker

```bash
docker compose up --build
```

## Dados de demonstração

Ficheiros em `demo_data/`. Regenerar: `python scripts/build_demo_xlsx.py`.

## Testes

Com dependências instaladas (`pip install -r requirements.txt`):

```powershell
pytest tests/
```

## LGPD

Sem dados pessoais nem operações reais. Não commits com `.env` com segredos nem extracts de produção.

## MySQL (opcional)

Ver `.env.example` — `RCAP_DEMO=0` e variáveis `MYSQL_*` para ambiente privado.

## Estrutura

`app.py` · `src/rcap_fundos/` (UI + núcleo) · `styles/` · `imagens/` · `tests/`
