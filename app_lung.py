import streamlit as st

# ─────────────── helpers ────────────────
def num_input(label, *, key):
    raw = st.text_input(label, key=key, value="", placeholder="")
    if raw == "":
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        st.warning(f"«{raw}» не является числом")
        return None


def stage_badge(text, bad=True):
    color = "#dc3545" if bad else "#198754"
    return f"<div style='text-align:center;font-weight:600;color:{color};'>{text}</div>"


# hide both possible versions of the grey hint
st.markdown(
    """
    <style>
    div[data-testid="stFormSubmitPrompt"],
    div[data-testid="stFormSubmitRegPrompt"] {display:none;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.header("OMM LUNG MATURITY PREDICT")

col1, col2, col3 = st.columns(3)

# ───────────── Model 1 ─────────────
with col1:
    st.subheader("Модель 1")

    with st.form("model1"):
        v_leuk = num_input("TNF (пг/мл):", key="m1_tnf")
        v_na   = num_input("Na⁺ (первый час):", key="m1_na")

        btn_box = st.empty()                       # ← reserve slot for the button
        submitted1 = btn_box.form_submit_button("Расчёт")

    # after the form: replace button with result
    if submitted1:
        if None in (v_leuk, v_na):
            btn_box.warning("Пожалуйста, заполните все поля.")
        else:
            score = -3.287 + 0.215 * v_leuk + 0.0321 * v_na
            btn_box.markdown(
                stage_badge(
                    "Каналикулярная стадия" if score >= 0.5 else "Саккулярная стадия",
                    bad=score >= 0.5,
                ),
                unsafe_allow_html=True,
            )

# ───────────── copy the same btn_box pattern to Model 2 & 3 ─────────────
