# app.py
# Streamlit app: Placenta accreta risk index (D) calculator
# Run: streamlit run app.py

import math
import streamlit as st

st.set_page_config(page_title="Индекс D: риск приращения плаценты", layout="centered")

st.title("Прогноз риска приращения плаценты (индекс D)")

st.subheader("Данные пациентки")

col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Возраст (лет)", min_value=12, max_value=60, value=30, step=1)
    height_cm = st.number_input("Рост (см)", min_value=120.0, max_value=210.0, value=165.0, step=1.0)
    weight_kg = st.number_input("Вес (кг)", min_value=30.0, max_value=200.0, value=65.0, step=0.5)

with col2:
    births = st.number_input("Роды в анамнезе (кол-во)", min_value=0, max_value=20, value=1, step=1)
    threat = st.selectbox("Угроза прерывания беременности", ["Нет", "Да"], index=0)
    previa = st.selectbox("Предлежание плаценты", ["Нет", "Да"], index=0)

st.subheader("Матка и рубцы")
scar_count = st.selectbox("Количество рубцов на матке", ["0", "1", "2", "3+"], index=0)

st.subheader("Расположение плаценты")
placenta_location = st.selectbox(
    "Расположение плаценты относительно стенки матки",
    ["Передняя стенка", "Задняя стенка", "Другое/не указано"],
    index=2,
)

st.subheader("Шейка матки")
# В формуле x7 входит с коэффициентом -0.106. Единицы в описании не указаны.
# Здесь просим в миллиметрах (как часто в УЗИ). Если у вас сантиметры — умножьте на 10.
cervix_len_mm = st.number_input("Длина шейки матки (мм)", min_value=0.0, max_value=80.0, value=35.0, step=0.5)

st.divider()

# ---- Feature engineering / mapping ----
# BMI -> overweight
height_m = height_cm / 100.0
bmi = weight_kg / (height_m ** 2) if height_m > 0 else float("nan")

# Interpretation choice (documented):
# x1 = overweight (BMI >= 25)
x1 = 1.0 if (not math.isnan(bmi) and bmi >= 25.0) else 0.0

x2 = 1.0 if age < 30 else 0.0
x3 = 1.0 if age > 40 else 0.0
x4 = 1.0 if births > 3 else 0.0
x5 = 1.0 if threat == "Да" else 0.0
x6 = 1.0 if previa == "Да" else 0.0
x7 = float(cervix_len_mm)

x8 = 1.0 if placenta_location == "Передняя стенка" else 0.0
x9 = 1.0 if placenta_location == "Задняя стенка" else 0.0

scars = scar_count
x10 = 0.0
x11 = 0.0
if scars in {"1", "2", "3+"}:
    x10 = 1.0
if scars == "2":
    x11 = 1.0

# x12: "средний возраст пациентки" is ambiguous for an individual.
# Here we use patient's age (years) as a practical interpretation.
x12 = float(age)

# ---- Compute D ----
d = (
    0.161 * x1
    - 6.55 * x2
    + 5.383 * x3
    + 1.339 * x4
    + 1.195 * x5
    - 2.158 * x6
    - 0.106 * x7
    + 2.163 * x8
    - 2.305 * x9
    + 4.064 * x10
    + 2.092 * x11
    - 0.617 * x12
    + 24.423
)

# ---- Output ----
st.subheader("Результат")

if d > 0:
    st.error(f"Неблагоприятный прогноз (высокий риск). Индекс D = **{d:.3f}**")
else:
    st.success(f"Благоприятный прогноз (низкий риск). Индекс D = **{d:.3f}**")
