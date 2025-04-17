import streamlit as st

# ── helpers ──────────────────────────────────────────────────────────────
def get_float(label, placeholder, *, min_v: float, max_v: float):
    """
    Numeric text box that can start empty.
    Returns float or None after validating range and format.
    """
    raw = st.text_input(label, placeholder)
    if raw == "":
        return None
    try:
        value = float(raw.replace(",", "."))
    except ValueError:
        st.error("Введите число в формате 0.000")
        return None
    if not (min_v <= value <= max_v):
        st.error(f"Значение должно быть в диапазоне {min_v} – {max_v}")
        return None
    return value


# ── UI ───────────────────────────────────────────────────────────────────
st.header("OMM PURE RESPONCE")

with st.form("fertility_form"):
    st.write("### Пожалуйста, введите результаты исследований")

    no2 = get_float(
        "Концентрация эндогенного нитрита NO₂ в сыворотке венозной крови (мкмоль/л)",
        "например 12.345",
        min_v=0.0,
        max_v=999.999,
    )

    no3 = get_float(
        "Концентрация нитрата NO₃ в сыворотке венозной крови (мкмоль/л)",
        "например 34.567",
        min_v=0.0,
        max_v=999.999,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        rodi = st.checkbox("Роды в анамнезе")
    with col2:
        spaechniy = st.checkbox("Спаечный процесс в малом тазу")
    with col3:
        gisteroskopiya = st.checkbox("Гистероскопия в анамнезе")

    submitted = st.form_submit_button("Анализ результатов")

# ── logic & result ───────────────────────────────────────────────────────
if submitted:
    if None in (no2, no3):
        st.warning("Пожалуйста, заполните все числовые поля.")
    else:
        x1 = no2
        x2 = no3
        x3 = int(rodi)
        x4 = int(spaechniy)
        x5 = int(gisteroskopiya)

        score = (
            0.542 * x1
            + 0.154 * x2
            - 4.125 * x3
            + 10.337 * x4
            - 8.762 * x5
            - 4.637
        )

        st.markdown("---")
        if score < 0:
            st.markdown(
                "<h4 style='color:#dc3545'>Прогнозируется НЕВОЗМОЖНОСТЬ наступления беременности</h4>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<h4 style='color:#198754'>Прогнозируется наступление беременности</h4>",
                unsafe_allow_html=True,
            )
