import streamlit as st

# ─────────────── helpers ────────────────
def num_input(label, *, key, placeholder=""):
    """Numeric field that stays blank until user types something."""
    raw = st.text_input(label, key=key, value="", placeholder=placeholder)
    if raw == "":
        return None
    # Accept comma decimals; reject anything else that isn't a valid float
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        st.warning(f"«{raw}» не является числом")
        return None


def stage_badge(text, bad=True):
    color = "#dc3545" if bad else "#198754"
    return f"<div style='text-align:center; font-weight:600; color:{color};'>{text}</div>"


# ─────────────── UI / logic ─────────────
st.header("OMM LUNG MATURITY PREDICT")

col1, col2, col3 = st.columns(3)

# ————— Model 1 ————————————————————————————
with col1:
    with st.form("model1"):
        st.subheader("Модель 1")
        v_leuk = num_input(
            "Уровень цитокина TNF (пг/мл):", key="m1_tnf", placeholder=""
        )
        v_na = num_input(
            "Уровень Na⁺ в газах крови (первый час жизни):",
            key="m1_na",
            placeholder="",
        )

        submitted1 = st.form_submit_button("Расчёт")
        if submitted1:
            if None in (v_leuk, v_na):
                st.warning("Пожалуйста, заполните все поля.")
            else:
                z = -3.287 + 0.215 * v_leuk + 0.0321 * v_na  # ← придуманный coef‑ы
                st.markdown("---")
                st.markdown(
                    stage_badge(
                        "Каналикулярная стадия" if z >= 0.5 else "Саккулярная стадия",
                        bad=z >= 0.5,
                    ),
                    unsafe_allow_html=True,
                )

# ————— Model 2 ————————————————————————————
with col2:
    with st.form("model2"):
        st.subheader("Модель 2")
        v353 = num_input(
            "Уровень цитокина TNF (пг/мл):",
            key="m2_tnf",
            placeholder="",
        )
        v172 = num_input(
            "Уровень Na⁺ в газах крови (первый час жизни):",
            key="m2_na",
            placeholder="",
        )
        v210 = num_input(
            "Уровень гематокрита (первый анализ):",
            key="m2_hct",
            placeholder="",
        )
        v344 = num_input(
            "MAX плотность лёгочной ткани (латеральная точка 6-го МР):",
            key="m2_density",
            placeholder="",
        )

        submitted2 = st.form_submit_button("Расчёт")
        if submitted2:
            if None in (v353, v172, v210, v344):
                st.warning("Пожалуйста, заполните все поля.")
            else:
                Z = (
                    -30.649
                    + 0.1969 * v172
                    - 0.0258 * v210
                    + 0.0242 * v344
                    + 0.2189 * v353
                )
                st.markdown("---")
                st.markdown(
                    stage_badge(
                        "Каналикулярная стадия" if Z >= 0.68 else "Саккулярная стадия",
                        bad=Z >= 0.68,
                    ),
                    unsafe_allow_html=True,
                )

# ————— Model 3 ————————————————————————————
with col3:
    with st.form("model3"):
        st.subheader("Модель 3")
        v_tnf = num_input(
            "Уровень цитокина TNF (пг/мл):",
            key="m3_tnf",
            placeholder="",
        )
        v_nse = num_input(
            "Уровень цитокина NSE (мкг/л):",
            key="m3_nse",
            placeholder="",
        )
        v_pkt = num_input(
            "Уровень ПКТ (нг/мл):",
            key="m3_pkt",
            placeholder="",
        )

        submitted3 = st.form_submit_button("Расчёт")
        if submitted3:
            if None in (v_tnf, v_nse, v_pkt):
                st.warning("Пожалуйста, заполните все поля.")
            else:
                z3 = -12.345 + 0.11 * v_tnf + 0.33 * v_nse + 0.42 * v_pkt  # demo coefs
                st.markdown("---")
                st.markdown(
                    stage_badge(
                        "Каналикулярная стадия" if z3 >= 0.6 else "Саккулярная стадия",
                        bad=z3 >= 0.6,
                    ),
                    unsafe_allow_html=True,
                )
