import streamlit as st

"""
Fetal Macrosomia Risk Predictor (after ART & GDM)
------------------------------------------------
A small Streamlit app that implements the scoring model described in the Russian
patent/formula.  Enter the patient’s laboratory values and clinical parameters to
get the predicted risk of fetal macrosomia.
Run with:
    streamlit run risk_prediction_app.py
"""

# ── Model constants ────────────────────────────────────────────────────────────
COEF_AST = 0.168        # x1  Aspartate aminotransferase (AST)  (U/L)
COEF_HDL = -3.944       # x2  HDL cholesterol (mmol/L)
COEF_P12A = 2.917       # x3  PPARG P12A genotype
COEF_SUPPORT = 13.215   # x4  Luteal support duration (>12w = 1)
INTERCEPT = -10.050     # Const

# ── Helper functions ──────────────────────────────────────────────────────────

def compute_index(ast: float, hdl: float, genotype_code: int, support_code: int) -> float:
    """Return the prognostic index M using the published equation."""
    return (
        COEF_AST * ast
        + COEF_HDL * hdl
        + COEF_P12A * genotype_code
        + COEF_SUPPORT * support_code
        + INTERCEPT
    )


def classify_risk(m_value: float) -> str:
    """Convert M to a clinical interpretation."""
    return (
        "Высокий риск макросомии (M > 0)" if m_value > 0 else
        "Риск макросомии не выявлен (M ≤ 0)"
    )

# ── UI ─────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Macrosomia Risk Predictor", layout="centered")
st.title("🍼 Macrosomia Risk after ART & GDM – Calculator")

st.markdown(
    "Введите значения лабораторных показателей и клинических параметров пациентки."
)

# Input widgets
ast = st.number_input(
    "Аспартатаминотрансфераза (AST), ЕД/л",
    min_value=0.0,
    max_value=1000.0,
    value=25.0,
    step=0.1,
)

hdl = st.number_input(
    "Липопротеины высокой плотности (ЛПВП), ммоль/л",
    min_value=0.0,
    max_value=5.0,
    value=1.2,
    step=0.01,
)

genotype = st.selectbox(
    "Генотип гена PPARG P12A",
    options=[
        (0, "Доминантный гомозиготный (C/C)"),
        (1, "Гетерозиготный (C/G)"),
        (2, "Рецессивный гомозиготный (G/G)")
    ],
    format_func=lambda x: x[1]
)[0]

support = st.selectbox(
    "Длительность лютеиновой поддержки",
    options=[(0, "До 12 недель"), (1, "Свыше 12 недель")],
    format_func=lambda x: x[1]
)[0]

# Calculation
if st.button("Рассчитать риск"):
    m_value = compute_index(ast, hdl, genotype, support)
    risk_text = classify_risk(m_value)

    st.subheader("Результат")
    # st.metric(label="Индекс M", value=f"{m_value:.3f}")
    st.write(f"**{risk_text}**")

    # with st.expander("Подробнее о формуле"):
    #     st.code(
    #         "M = 0.168·AST − 3.944·HDL + 2.917·Genotype + 13.215·Support − 10.050",
    #         language="text",
    #     )
    #     st.write(
    #         "- **AST** — аспартатаминотрансфераза, ЕД/л;\n"
    #         "- **HDL** — липопротеины высокой плотности, ммоль/л;\n"
    #         "- **Genotype**: 0=C/C, 1=C/G, 2=G/G;\n"
    #         "- **Support**: 0 — ≤12 недель, 1 — >12 недель." )

