# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="OMM SUPERIMPOSED PREECLAMPSIA PREDICT",
                   page_icon="🩺", layout="centered")

COEFFS = {"X1": 2.45, "X2": -4.63, "X3": 2.64, "X4": 4.22, "X5": -57.11, "X6": 117.62}
INTERCEPT = -3.96

def compute_D(x1, x2, x3, x4, x5, x6):
    return (COEFFS["X1"]*x1 + COEFFS["X2"]*x2 + COEFFS["X3"]*x3 + COEFFS["X4"]*x4
            + COEFFS["X5"]*x5 + COEFFS["X6"]*x6 + INTERCEPT)

def risk_label(D):
    return "Высокий риск" if D > 0 else "Низкий риск"

def parse_float(s: str):
    """Return float value from text (supports comma decimal), or None if blank/invalid."""
    s = (s or "").strip()
    if s == "":
        return None
    try:
        return float(s.replace(",", "."))  # allow comma decimal input
    except ValueError:
        return None

st.title("🩺 OMM SUPERIMPOSED PREEКLAMPSIA PREDICT")
st.caption("Калькулятор оценки риска преэклампсии у пациенток с хронической артериальной гипертензией.")

st.subheader("Ввод признаков")
c1, c2 = st.columns(2)

with c1:
    X1 = 1 if st.checkbox("Гиподинамия", value=False) else 0
    X2 = 1 if st.checkbox("Хроническая АГ в предыдущую беременность", value=False) else 0
    X3 = 1 if st.checkbox("ДАД >100 мм рт. ст. в I триместре", value=False) else 0
    X4 = 1 if st.checkbox("ДАД >100 мм рт. ст. во II триместре", value=False) else 0

with c2:
    X5_text = st.text_input("Уровень экспрессии miR-181a (I триместр)",
                            value="", placeholder="введите число (напр., 0.0123)")
    X6_text = st.text_input("Уровень экспрессии miR-221 (I триместр)",
                            value="", placeholder="введите число (напр., 0.0456)")

st.markdown("---")

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if st.button("Рассчитать"):
    X5 = parse_float(X5_text)
    X6 = parse_float(X6_text)

    # простая валидация
    if X5 is None or X6 is None:
        st.warning("Пожалуйста, заполните корректные числовые значения для X5 и X6.")
    elif X5 < 0 or X6 < 0:
        st.warning("Значения X5 и X6 не должны быть отрицательными.")
    else:
        D = compute_D(X1, X2, X3, X4, X5, X6)
        st.session_state.last_result = {"D": D, "label": risk_label(D)}

# Показываем результат, если он есть
res = st.session_state.last_result
if res is not None:
    if res["D"] > 0:
        st.error(f"**{res['label']}**  \nСчёт D = **{res['D']:.3f}** (порог 0)")
    else:
        st.success(f"**{res['label']}**  \nСчёт D = **{res['D']:.3f}** (порог 0)")
