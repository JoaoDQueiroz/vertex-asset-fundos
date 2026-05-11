"""Gráficos do painel de caixa (Plotly)."""

from __future__ import annotations

import plotly.graph_objects as go


CORES = ("#004850", "#99946A", "#3d8b7a", "#2d5a54", "#c9a962", "#6b5b45", "#8aa6a0")


def fig_donut_fundos_por_administrador(contagens: dict[str, int], titulo_centro: str) -> go.Figure:
    if not contagens:
        contagens = {"—": 1}
    labels = list(contagens.keys())
    values = list(contagens.values())
    cores = [CORES[i % len(CORES)] for i in range(len(labels))]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.62,
                marker=dict(colors=cores, line=dict(color="#E6E1D8", width=1)),
                textinfo="percent",
                textposition="outside",
            )
        ]
    )
    total = int(sum(values))
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:11px'>Fundos</span>",
        x=0.5,
        y=0.5,
        font=dict(size=18, color="#004850"),
        showarrow=False,
    )
    fig.update_layout(
        title=dict(text=titulo_centro, font=dict(size=13, color="#004850"), x=0.02, xanchor="left"),
        margin=dict(t=36, b=24, l=24, r=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, font=dict(size=11, color="#333")),
        height=340,
    )
    return fig
