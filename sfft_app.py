# app.py
import math
import streamlit as st

st.set_page_config(page_title="СФФТ: калькулятор риска", page_icon="🧮", layout="centered")

st.title("🧮 Прогноз СФФТ по УЗ-признакам (логистическая регрессия)")
st.caption(
    "Модель: F = 2.07*ПХ + 0.08*(КТР1-КТР2) + 4.45*ПИ_2 + 2.12*(ТВП>3) - 7.52; "
    "P = 1 / (1 + e^{-F}); порог: 0.25"
)

st.markdown("---")

with st.form("inputs"):
    st.subheader("Ввод признаков")

    ph = st.selectbox("ПХ — предлежание хориона", options=[0, 1], format_func=lambda x: "Есть (1)" if x == 1 else "Нет (0)")

    ktr1 = st.number_input("КТР1 (мм)", min_value=0.0, value=50.0, step=0.1)
    ktr2 = st.number_input("КТР2 (мм)", min_value=0.0, value=50.0, step=0.1)
    ktr_diff = ktr1 - ktr2

    pi2 = st.selectbox("ПИ 2-го плода более 95%", options=[0, 1], format_func=lambda x: "Да" if x == 1 else "Нет")

    tvp_gt3 = st.selectbox("ТВП 1 или 2 плода > 3 мм", options=[0, 1], format_func=lambda x: "Да" if x == 1 else "Нет")

    submitted = st.form_submit_button("Рассчитать")

if submitted:
    # Coefficients from the description
    F = 2.07 * ph + 0.08 * ktr_diff + 4.45 * pi2 + 2.12 * tvp_gt3 - 7.52
    P = 1.0 / (1.0 + math.exp(-F))

    st.markdown("---")
    st.subheader("Результат")

    col1, col2 = st.columns(2)
    col1.metric("Линейный предиктор F", f"{F:.3f}")
    col2.metric("Вероятность P", f"{P:.3f}")

    if P < 0.25:
        st.success("Классификация: **не СФФТ** ")
    else:
        st.error("Классификация: **СФФТ** ")

