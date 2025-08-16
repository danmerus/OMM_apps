# app.py

import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Неонатальный риск (TTTS)", layout="centered")

st.title("Оценка риска летального исхода (неонатальный период)")
st.caption("Для недоношенных монохориальных диамниотических близнецов после фето-фетального трансфузионного синдрома (ФФТС)")


st.subheader("Ввод параметров пациента")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        x1_label = "Признаки материнской мальперфузии"
        x1_opt = st.selectbox(x1_label, options=["Нет (0)", "Есть (1)"])
        x1 = 1 if "Есть" in x1_opt else 0

        x2 = st.number_input(
            "Аpgar на 10-й минуте (баллы)",
            min_value=0, max_value=10, value=7, step=1,
            help="Целое число от 0 до 10",
        )
    with col2:
        x3 = st.number_input(
            "Хлор (ммоль/л), 1–6 часов жизни",
            min_value=50.0, max_value=140.0, value=100.0, step=0.1,
            help="Типичные значения в пределах ~95–110 ммоль/л",
        )
        x4 = st.number_input(
            "Лактат (ммоль/л), 1–6 часов жизни",
            min_value=0.0, max_value=20.0, value=2.0, step=0.1,
            help="Ед. изм.: ммоль/л",
        )

    submitted = st.form_submit_button("Рассчитать риск")

def compute_di(x1:int, x2:int, x3:float, x4:float) -> float:
    # DI = 2.679*X1 - 1.299*X2 + 0.218*X3 + 0.536*X4 - 19.669
    return 2.679 * x1 - 1.299 * x2 + 0.218 * x3 + 0.536 * x4 - 19.669

def logistic(di: float) -> float:
    return 1.0 / (1.0 + math.exp(-di))

def classify(p: float, thr: float) -> str:
    return "Высокий риск" if p > thr else "Низкий риск"

if submitted:
    di = compute_di(x1, int(x2), float(x3), float(x4))
    p = logistic(di)
    verdict = classify(p, 0.4)

    st.subheader("Результаты")
    c1, c2, c3 = st.columns(3)
    # c1.metric("DI", f"{di:.3f}")
    # c2.metric("P (вероятность)", f"{p:.2%}")
    # c3.metric("Порог", f"{threshold:.0%}")

    # Visual hint
    st.progress(min(max(p, 0.0), 1.0))
    st.markdown(
        f"**Итог:** <span style='font-size:1.15rem; font-weight:600;'>{verdict}</span>",
        unsafe_allow_html=True,
    )

    with st.expander("Проверка используемых значений"):
        st.json(
            {
                "X1 (мальперфузия)": x1,
                "X2 (Apgar 10 мин)": int(x2),
                "X3 (Хлор, ммоль/л)": float(x3),
                "X4 (Лактат, ммоль/л)": float(x4),
                "DI": round(di, 6),
                "P": round(p, 6),
            }
        )

