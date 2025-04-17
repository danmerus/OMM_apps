import streamlit as st

# ───────────────── helpers ──────────────────
def num_input(label, *, key):
    """Numeric text box that starts blank and returns float or None."""
    raw = st.text_input(label, key=key, value="", placeholder="")
    if raw == "":
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        st.warning(f"«{raw}» не является числом")
        return None


def stage_badge(text, bad=True):
    """Return coloured HTML badge."""
    color = "#dc3545" if bad else "#198754"
    return f"<div style='text-align:center;font-weight:600;color:{color};'>{text}</div>"


# ───────────────── CSS ──────────────────────
st.markdown(
    """
    <style>
    /* hide both variants of Streamlit’s “Press Enter to submit” notice */
    div[data-testid="stFormSubmitPrompt"],
    div[data-testid="stFormSubmitRegPrompt"] {display:none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ───────────────── layout ───────────────────
st.header("OMM LUNG MATURITY PREDICT")
col1, col2, col3 = st.columns(3)

# ───────────── Model 1 ─────────────
with col1:
    st.subheader("Модель 1")
    result1 = st.empty()  # placeholder for button / result

    with st.form("model1"):
        v_leuk = num_input("Уровень цитокина TNF (пг/мл):", key="m1_tnf")
        v_na   = num_input("Уровень Na⁺ в газах крови (первый час):", key="m1_na")
        submitted1 = result1.form_submit_button("Расчёт")  # button inside placeholder

    if submitted1:
        if None in (v_leuk, v_na):
            result1.warning("Пожалуйста, заполните все поля.")
        else:
            score = -3.287 + 0.215 * v_leuk + 0.0321 * v_na
            result1.markdown(
                stage_badge(
                    "Каналикулярная стадия" if score >= 0.5 else "Саккулярная стадия",
                    bad=score >= 0.5,
                ),
                unsafe_allow_html=True,
            )

# ───────────── Model 2 ─────────────
with col2:
    st.subheader("Модель 2")
    result2 = st.empty()

    with st.form("model2"):
        v353 = num_input("Уровень цитокина TNF (пг/мл):", key="m2_tnf")
        v172 = num_input("Уровень Na⁺ в газах крови (первый час):", key="m2_na")
        v210 = num_input("Уровень гематокрита (первый анализ):", key="m2_hct")
        v344 = num_input("MAX плотность лёгочной ткани (латер. точка 6‑го МР):", key="m2_den")
        submitted2 = result2.form_submit_button("Расчёт")

    if submitted2:
        if None in (v353, v172, v210, v344):
            result2.warning("Пожалуйста, заполните все поля.")
        else:
            score = -30.649 + 0.1969 * v172 - 0.0258 * v210 + 0.0242 * v344 + 0.2189 * v353
            result2.markdown(
                stage_badge(
                    "Каналикулярная стадия" if score >= 0.68 else "Саккулярная стадия",
                    bad=score >= 0.68,
                ),
                unsafe_allow_html=True,
            )

# ───────────── Model 3 ─────────────
with col3:
    st.subheader("Модель 3")
    result3 = st.empty()

    with st.form("model3"):
        v_tnf = num_input("Уровень цитокина TNF (пг/мл):", key="m3_tnf")
        v_nse = num_input("Уровень цитокина NSE (мкг/л):", key="m3_nse")
        v_pkt = num_input("Уровень ПКТ (нг/мл):", key="m3_pkt")
        submitted3 = result3.form_submit_button("Расчёт")

    if submitted3:
        if None in (v_tnf, v_nse, v_pkt):
            result3.warning("Пожалуйста, заполните все поля.")
        else:
            score = -12.345 + 0.11 * v_tnf + 0.33 * v_nse + 0.42 * v_pkt
            result3.markdown(
                stage_badge(
                    "Каналикулярная стадия" if score >= 0.6 else "Саккулярная стадия",
                    bad=score >= 0.6,
                ),
                unsafe_allow_html=True,
            )
