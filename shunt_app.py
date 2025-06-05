# app.py
import streamlit as st
import numpy as np

st.set_page_config(page_title="Прогноз & нефроамниальный шунт", page_icon="🍼")

st.header("Прогноз и необходимость нефроамниального шунтирования\nу плодов с врождённой обструктивной уропатией")


# ──────────────────────────────────────────────────────────────
# I.  Прогностический индекс WI
# ──────────────────────────────────────────────────────────────
st.header("I этап – прогноз (WI)")

col1, col2 = st.columns(2)
with col1:
    x1 = st.checkbox("Двустороннее поражение почек (Х1)", value=False)
    x2 = st.checkbox("Мужской пол плода (Х2)", value=False)

with col2:
    x3 = st.number_input("Продольный размер почки, мм (Х3)", min_value=0.0, value=35.0)
    x4 = st.number_input("Толщина паренхимы, мм (Х4)", min_value=0.0, value=4.0)
    x5 = st.number_input("Индекс васкуляризации VI (Х5)", min_value=0.0, value=0.35)
    x6 = st.number_input("Индекс потока FI (Х6)", min_value=0.0, value=0.50)

# коэффициенты формулы (примерные – вставьте точные при необходимости)
b = np.array([-1.0,  0.8,  0.02,  0.15,  5.0,  7.0])   # <− замените точными
const_wi = 4.673

X = np.array([int(x1), int(x2), x3, x4, x5, x6])
wi = const_wi + np.dot(b, X)

st.subheader(f"WI = {wi:>.3f}")

if wi < 0:
    st.error("Неблагоприятный прогноз")
else:
    st.success("Благоприятный прогноз – переходим ко 2-му этапу")

# ──────────────────────────────────────────────────────────────
# II.  Диагностический индекс DI
# ──────────────────────────────────────────────────────────────
if wi >= 0:
    st.header("II этап – необходимость шунтирования (DI)")

    col3, col4 = st.columns(2)
    with col3:
        y1 = st.number_input("Продольный размер почки, мм (Y1)", min_value=0.0, value=x3)
        y2 = st.number_input("Толщина паренхимы, мм (Y2)", min_value=0.0, value=x4)
        y3 = st.number_input("Индекс васкуляризации VI (Y3)", min_value=0.0, value=x5)
        y4 = st.number_input("Индекс потока FI (Y4)", min_value=0.0, value=x6)

    with col4:
        y5 = st.checkbox("Почка-киста (Y5)", value=False)
        y6 = st.checkbox("Кистозная дисплазия почки (Y6)", value=False)

    # коэффициенты формулы (примерные – замените)
    a = np.array([0.015, 0.12, 4.2, 6.8, -1.5, -2.0])   # <− замените точными
    const_di = 0.463

    Y = np.array([y1, y2, y3, y4, int(y5), int(y6)])
    di = const_di + np.dot(a, Y)

    st.subheader(f"DI = {di:>.3f}")

    if di < 0:
        st.error("Необходимо проведение нефроамниального шунтирования")
    else:
        st.success("Показаний для шунтирования нет")
