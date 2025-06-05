# app.py  (Streamlit 1.33+)

import streamlit as st
import numpy as np
import datetime as dt

st.set_page_config(page_title="Прогноз & Шунтирование", page_icon="🍼")

st.header("СПОСОБ ОПРЕДЕЛЕНИЯ ПРОГНОЗА И НЕОБХОДИМОСТИ ВНУТРИУТРОБНОГО НЕФРОАМНИАЛЬНОГО ШУНТИРОВАНИЯ У ПЛОДОВ С ВРОЖДЕННЫМИ ОБСТРУКТИВНЫМИ УРОПАТИЯМИ")

# ─────────────────────────────────────────────
# вспом-функция: безопасный ввод float / int
# ─────────────────────────────────────────────
def num_or_none(value: str, cast=float):
    value = value.replace(",", ".").strip()
    return cast(value) if value else None


# ============== I. ПРОГНОЗ (WI) ==============

st.header("I этап. Определение прогноза врожденной обструктивной уропатии у плода.")

col1, col2 = st.columns(2)
with col1:
    x1 = st.checkbox("Двустороннее поражение почек (Х1)", value=False)
    x2 = st.checkbox("Мужской пол (Х2)", value=False)

with col2:
    x3 = st.text_input("Продольный размер почки, мм (Х3)", key="x3")
    x4 = st.text_input("Толщина паренхимы, мм (Х4)", key="x4")
    x5 = st.text_input("Индекс васкуляризации VI (Х5)", key="x5")
    x6 = st.text_input("Индекс потока FI (Х6)", key="x6")

if st.button("Рассчитать индекс"):
    # превращаем в значения или None
    vals = [
        int(x1),
        int(x2),
        num_or_none(x3),
        num_or_none(x4),
        num_or_none(x5),
        num_or_none(x6),
    ]
    if None in vals[2:]:
        st.warning("Пожалуйста, заполните все числовые поля.")
    else:
        b = np.array([-0.292, -1.551, -0.054, 0.221, 0.065, 0.416])
        const_wi = 4.673
        wi = np.dot(b, vals) - const_wi
        st.subheader(f"WI = {wi:.3f}")
        if wi < 0:
            st.error("Неблагоприятный прогноз")
        else:
            st.success("Благоприятный прогноз – можно перейти ко 2-му этапу")

            st.session_state["prognosis_ok"] = True  # флаг для шага II
else:
    st.session_state["prognosis_ok"] = False

# ============= II. ШУНТИРОВАНИЕ (DI) =============
if st.session_state.get("prognosis_ok"):
    st.header("II этап – Способ определения необходимости нефроамниального шунтирования у плодов с обструктивными уропатиями.")

    c1, c2 = st.columns(2)
    with c1:
        y1 = st.text_input("Продольный размер почки, мм (Y1)", key="y1")
        y2 = st.text_input("Толщина паренхимы, мм (Y2)", key="y2")
        y3 = st.text_input("Индекс васкуляризации VI (Y3)", key="y3")
        y4 = st.text_input("Индекс потока FI (Y4)", key="y4")

    with c2:
        y5 = st.checkbox("Почка-киста (Y5)", value=False)
        y6 = st.checkbox("Кистозная дисплазия почки (Y6)", value=False)

    if st.button("Рассчитать DI"):
        vals2 = [
            num_or_none(y1),
            num_or_none(y2),
            num_or_none(y3),
            num_or_none(y4),
            int(y5),
            int(y6),
        ]
        if None in vals2[:4]:
            st.warning("Пожалуйста, заполните все числовые поля.")
        else:
            a = np.array([0.017, 0.222, 0.565, -0.388, 5.589, 7.005])
            const_di = 0.463
            di = np.dot(a, vals2) - const_di
            st.subheader(f"DI = {di:.3f}")
            if di < 0:
                st.error("Необходимо проведение нефроамниального шунтирования")
            else:
                st.success("Показаний для шунтирования нет")
