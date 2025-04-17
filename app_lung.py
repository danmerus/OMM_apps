import streamlit as st

# ───────────────── helpers ──────────────────
def num_input(label, *, key, placeholder=""):
    """Numeric field that stays blank until user types something."""
    raw = st.text_input(label, key=key, value="", placeholder=placeholder)
    if raw == "":
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        st.warning(f"«{raw}» не является числом")
        return None


def stage_badge(text, bad=True):
    color = "#dc3545" if bad else "#198754"
    return f"<div style='text-align:center; font-weight:600; color:{color};'>{text}</div>"


def model_block(title, inputs, formula, threshold):
    """
    Render one model column.

    inputs   – list of (label, key) pairs
    formula  – lambda returning score from the collected floats
    threshold– cutoff above which stage = 'Каналикулярная'
    """
    st.subheader(title)
    result = st.empty()  # placeholder on top

    with st.form(key=title):
        vals = [num_input(lbl, key=key) for lbl, key in inputs]
        submitted = st.form_submit_button("Расчёт")

    if submitted:
        if any(v is None for v in vals):
            result.warning("Пожалуйста, заполните все поля.")
        else:
            score = formula(*vals)
            result.markdown(
                stage_badge(
                    "Каналикулярная стадия" if score >= threshold else "Саккулярная стадия",
                    bad=score >= threshold,
                ),
                unsafe_allow_html=True,
            )


# ──────────────── layout / CSS ───────────────
st.markdown(
    """
    <style>
    /* hide grey "Press Enter to submit" helper inside st.form() */
    div[data-testid="stFormSubmitPrompt"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.header("OMM LUNG MATURITY PREDICT")
col1, col2, col3 = st.columns(3)

# ─────────────── Models ──────────────────────
with col1:
    model_block(
        "Модель 1",
        [
            ("Уровень цитокина TNF (пг/мл):", "m1_tnf"),
            ("Уровень Na⁺ в газах крови (первый час жизни):", "m1_na"),
        ],
        lambda tnf, na: -3.287 + 0.215 * tnf + 0.0321 * na,
        threshold=0.5,
    )

with col2:
    model_block(
        "Модель 2",
        [
            ("Уровень цитокина TNF (пг/мл):", "m2_tnf"),
            ("Уровень Na⁺ в газах крови (первый час жизни):", "m2_na"),
            ("Уровень гематокрита (первый анализ):", "m2_hct"),
            ("MAX плотность лёгочной ткани (лат. точка 6‑го МР):", "m2_density"),
        ],
        lambda tnf, na, hct, dens: (
            -30.649 + 0.1969 * na - 0.0258 * hct + 0.0242 * dens + 0.2189 * tnf
        ),
        threshold=0.68,
    )

with col3:
    model_block(
        "Модель 3",
        [
            ("Уровень цитокина TNF (пг/мл):", "m3_tnf"),
            ("Уровень цитокина NSE (мкг/л):", "m3_nse"),
            ("Уровень ПКТ (нг/мл):", "m3_pkt"),
        ],
        lambda tnf, nse, pkt: -12.345 + 0.11 * tnf + 0.33 * nse + 0.42 * pkt,
        threshold=0.6,
    )
