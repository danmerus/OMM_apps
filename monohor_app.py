# app.py
# Streamlit app: Прогноз риска летального исхода в неонатальном периоде
# Запуск: streamlit run app.py

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Риск в неонатальном периоде (MCDA, sFGR)",
    page_icon="🍼",
    layout="centered",
)

st.title("Прогноз риска в неонатальном периоде")
st.caption(
    "Метод для недоношенных монохориальных диамниотических близнецов с синдромом селективной задержки роста плода (sFGR). "
    "Расчет диагностического индекса (DI) по заданной формуле и стратификация риска."
)


st.divider()

# --- Ввод данных ---
st.subheader("Ввод клинико-гистологических признаков")

def yes_no_to_int(label: str, key: str):
    choice = st.radio(label, ["Нет", "Есть"], horizontal=True, key=key)
    return 1 if "Есть" in choice else 0

col1, col2 = st.columns(2)
with col1:
    x1 = yes_no_to_int("Внутриутробная гибель моно ди близнеца ", "x1")
    x2 = yes_no_to_int("Преждевременный разрыв оболочек ", "x2")
    x4 = yes_no_to_int("Острая плацентарная недостаточность ", "x4")
with col2:
    x5 = yes_no_to_int("Интервиллузит ", "x5")
    x3 = st.number_input(
        "Оценка по шкале Апгар на 1-й минуте ", min_value=0.0, max_value=10.0, step=0.5, value=7.0
    )

with st.form("calc_form"):
    submitted = st.form_submit_button("Рассчитать")

THRESHOLD = 0.875

def compute_di(x1, x2, x3, x4, x5):
    return 19.5 * x1 + 19.2 * x2 - 2.2 * x3 + 25.0 * x4 + 15.7 * x5 - 0.81

if submitted:
    di = compute_di(x1, x2, x3, x4, x5)

    # Классификация
    if di > THRESHOLD:
        risk_text = "Высокий риск"
        color_block = "error"
    elif di < THRESHOLD:
        risk_text = "Низкий риск"
        color_block = "success"
    else:
        risk_text = "Граничное значение (ровно 0.875)"
        color_block = "warning"

    st.subheader("Результат")

    if color_block == "error":
        st.error(f"🧮 {risk_text}")
    elif color_block == "success":
        st.success(f"🧮 {risk_text}")
    else:
        st.warning(f"🧮 {risk_text}")


st.divider()
