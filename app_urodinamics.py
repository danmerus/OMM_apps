import streamlit as st
import math

def get_float(label, placeholder, *, min_v, max_v):
    """Return a float or None, after basic validation."""
    txt = st.text_input(label, placeholder=placeholder)
    if txt == "":
        return None                # nothing entered
    try:
        val = float(txt.replace(",", "."))  # allow comma‑decimal
    except ValueError:
        st.error("Введите число, пожалуйста.")
        return None
    if not (min_v <= val <= max_v):
        st.error(f"Значение должно быть в диапазоне {min_v} … {max_v}.")
        return None
    return val

st.subheader("OMM POSTPARTUM PELVIC DYSFUNCTION")
st.header("Прогнозирование риска развития тазовых и уродинамических дисфункций женщин после родов")

# ───────────── Базовые поля ─────────────
question1 = st.selectbox(
    "У пациентки были первые роды?",
    options=["— выберите ответ —", "Да", "Нет"],
    index=0
)
ar_1 = None if question1.startswith("—") else int(question1 == "Да")

ar_2 = get_float(
    "Разность ширины уретры в покое и при натуживании (мм)",
    "от -1 до 1",
    min_v=-1.0, max_v=1.0
)

ar_3 = get_float(
    "Давление на влагалищный датчик при сокращении мышц (мм рт. ст.)",
    "55 … 100",
    min_v=55.0, max_v=100.0
)

question4 = st.selectbox(
    "Пациентка — носитель генотипа GG гена ESR1:A‑351G?",
    options=["— выберите ответ —", "Да", "Нет"],
    index=0
)
ar_4 = None if question4.startswith("—") else int(question4 == "Да")

ar_5 = get_float(
    "Размер сухожильного центра промежности (мм)",
    "2.0 … 12.0",
    min_v=2.0, max_v=12.0
)

ar_6 = get_float(
    "Размер m. bulbospongiosus (мм)",
    "3.0 … 14.0",
    min_v=3.0, max_v=14.0
)

# ───────────── Кнопка расчёта ─────────────
if st.button("Рассчитать риск"):
    # убеждаемся, что все поля заполнены
    if None in (ar_1, ar_2, ar_3, ar_4, ar_5, ar_6):
        st.warning("Пожалуйста, заполните все поля.")
    else:
        num = math.exp(
            13.189
            - 1.314  * ar_1
            - 5.4581 * ar_2
            - 0.12576 * ar_3
            + 2.9661 * ar_4
            - 0.27877 * ar_5
            - 0.16889 * ar_6
        )
        W = num / (1 + num)
        if W >= 0.5:
            st.markdown(
                "<h3 style='text-align:center;color:red;'>ВЫСОКИЙ РИСК</h3>"
                "<h5 style='text-align:center;'>дисфункции тазового дна через 6 месяцев после родов</h5>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<h3 style='text-align:center;color:green;'>НИЗКИЙ РИСК</h3>"
                "<h5 style='text-align:center;'>дисфункции тазового дна через 6 месяцев после родов</h5>",
                unsafe_allow_html=True,
            )
