import streamlit as st

# ── helpers ──────────────────────────────────────────────────────────────
def get_float(label, placeholder, *, min_v: float, max_v: float):
    """
    Numeric text box that starts empty.
    Returns float or None after validating range and format.
    """
    raw = st.text_input(
        label,
        value="",               # ◀︎ leave blank
        placeholder=placeholder # ◀︎ grey hint
    )
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


def yes_no(label: str) -> int | None:
    choice = st.selectbox(label, ["— выберите —", "Да", "Нет"], index=0)
    return None if choice.startswith("—") else int(choice == "Да")


# ── UI ───────────────────────────────────────────────────────────────────
st.header("OMM PURE RESPONCE")

with st.form("fertility_form"):
    st.write("### Пожалуйста, введите результаты исследований")

    no2 = get_float(
        "Концентрация эндогенного нитрита NO₂ в сыворотке венозной крови (мкмоль/л)",
        "",
        min_v=0.0,
        max_v=999.999,
    )

    no3 = get_float(
        "Концентрация нитрата NO₃ в сыворотке венозной крови (мкмоль/л)",
        "",
        min_v=0.0,
        max_v=999.999,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        rodi = yes_no("Роды в анамнезе")
    with col2:
        spaechniy = yes_no("Спаечный процесс в малом тазу")
    with col3:
        gisteroskopiya = yes_no("Гистероскопия в анамнезе")

    submitted = st.form_submit_button("Анализ результатов")

# ── logic & result ───────────────────────────────────────────────────────
if submitted:
    if None in (no2, no3, rodi, spaechniy, gisteroskopiya):
        st.warning("Пожалуйста, заполните все поля.")
    else:
        score = (
            0.542 * no2
            + 0.154 * no3
            - 4.125 * rodi
            + 10.337 * spaechniy
            - 8.762 * gisteroskopiya
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
