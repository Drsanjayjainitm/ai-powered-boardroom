"""Consistent chart presentation for browser and PDF printing."""

def polish_chart(fig, *, legend=True, bottom=90):
    fig.update_layout(
        template="plotly_white",
        font=dict(size=13, color="#10233F"),
        title=dict(font=dict(size=17, color="#10233F"), x=0.02),
        margin=dict(l=55, r=35, t=75, b=bottom),
        height=385,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        showlegend=legend,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(automargin=True, title_standoff=12)
    fig.update_yaxes(automargin=True, title_standoff=12, gridcolor="#E7EEF3")
    return fig
