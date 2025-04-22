import streamlit as st

st.set_page_config(
    page_title="Прогноз преэклампсии",
    layout="centered",
)

tabs = st.tabs(["Риск реализации преэклампсии", "Степень тяжести преэклампсии"])

# --- Tab 1: Риск реализации преэклампсии ---
with tabs[0]:
    st.header("OMM PREECLAMPSIA PREDICT")
    with st.form("risk_form"):
        bmi = st.number_input(
            "Индекс массы тела (кг/м²)",
            min_value=15.0, max_value=60.0, step=0.1,
        )
        fgr = st.checkbox("Задержка роста плода")
        alt = st.number_input("Уровень АЛТ (ед/л)", format="%.2f")
        albumin = st.number_input("Уровень альбумина (г/л)", format="%.2f")
        apoe_option = st.radio(
            "Полиморфизм АроЕ",
            ("CC", "CT", "TT"),
        )
        cetp_option = st.radio(
            "Полиморфизм СЕТР",
            ("GG", "GA", "AA"),
        )
        submit1 = st.form_submit_button("Расчет")
    if submit1:
        apoe_map = {"CC": 0, "CT": 1, "TT": 2}
        cetp_map = {"GG": 0, "GA": 1, "AA": 2}
        X = (
            1.2
            - 0.17 * bmi
            + 3.9 * (1 if fgr else 0)
            - 0.19 * albumin
            + 0.66 * alt
            - 0.93 * apoe_map[apoe_option]
            - 0.32 * cetp_map[cetp_option]
        )
        if X >= 0:
            st.error("ВЫСОКИЙ РИСК\nреализации преэклампсии")
        else:
            st.success("НИЗКИЙ РИСК\nреализации преэклампсии")

# --- Tab 2: Степень тяжести преэклампсии ---
with tabs[1]:
    st.header("Прогноз степени тяжести преэклампсии")
    with st.form("severity_form"):
        apoe = st.checkbox("Наличие вариантного аллеля С гена АроЕ")
        cetp = st.checkbox("Наличие вариантного аллеля А гена СЕТР")
        lpl = st.checkbox("Наличие вариантного аллеля G гена LPL")
        weight_gain = st.number_input(
            "Прибавка массы тела при беременности (кг)", step=0.1
        )
        cholesterol = st.number_input(
            "Уровень холестерина (ммоль/л)", format="%.2f"
        )
        apoA = st.number_input("Уровень ApoA (г/л)", format="%.2f")
        submit2 = st.form_submit_button("Расчет")
    if submit2:
        D = (
            2.438 * (1 if apoe else 0)
            + 5.643 * (1 if cetp else 0)
            + 2.9 * (1 if lpl else 0)
            - 0.14 * weight_gain
            - 0.64 * cholesterol
            - 2.93 * apoA
            + 7.21
        )
        if D <= 0:
            st.error("ТЯЖЕЛАЯ ФОРМА\nПРЕЭКЛАМПСИИ")
        else:
            st.success("УМЕРЕННАЯ ФОРМА\nПРЕЭКЛАМПСИИ")
