# app.py
# «OMM SUPERIMPOSED PREECLAMPSIA PREDICT» (single-patient calculator)
# D = 2.45*X1 - 4.63*X2 + 2.64*X3 + 4.22*X4 - 57.11*X5 + 117.62*X6 - 3.96
# Classification: D > 0 → высокий риск; иначе низкий риск

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="OMM SUPERIMPOSED PREECLAMPSIA PREDICT",
    page_icon="🩺",
    layout="centered",
)

# ----------------------- Model constants & helpers -----------------------

COEFFS = {
    "X1": 2.45,     # гиподинамия (1/0)
    "X2": -4.63,    # хроническая АГ в предыдущую беременность (1/0)
    "X3": 2.64,     # ДАД >100 в I триместре (1/0)
    "X4": 4.22,     # ДАД >100 во II триместре (1/0)
    "X5": -57.11,   # экспрессия miR-181a (число)
    "X6": 117.62,   # экспрессия miR-221 (число)
}
INTERCEPT = -3.96

def compute_D(x1, x2, x3, x4, x5, x6):
    return (
        COEFFS["X1"] * x1
        + COEFFS["X2"] * x2
        + COEFFS["X3"] * x3
        + COEFFS["X4"] * x4
        + COEFFS["X5"] * x5
        + COEFFS["X6"] * x6
        + INTERCEPT
    )

def risk_label(D):
    return "Высокий риск" if D > 0 else "Низкий риск"
    
# ----------------------- UI -----------------------

st.title("🩺 OMM SUPERIMPOSED PREECLAMPSIA PREDICT")
st.caption("Калькулятор оценки риска преэклампсии у пациенток с хронической артериальной гипертензией.")

st.subheader("Ввод признаков")
c1, c2 = st.columns(2)

with c1:
    X1 = 1 if st.checkbox("Гиподинамия (да)", value=False) else 0
    X2 = 1 if st.checkbox("Хроническая АГ в предыдущую беременность (да)", value=False) else 0
    X3 = 1 if st.checkbox("ДАД >100 мм рт. ст. в I триместре (да)", value=False) else 0
    X4 = 1 if st.checkbox("ДАД >100 мм рт. ст. во II триместре (да)", value=False) else 0

with c2:
    X5 = st.number_input(
        "Уровень экспрессии miR-181a (I триместр)",
        min_value=0.0, step=0.0001, format="%.6f", value=0.0,
    )
    X6 = st.number_input(
        "Уровень экспрессии miR-221 (I триместр)",
        min_value=0.0, step=0.0001, format="%.6f", value=0.0,
    )

st.markdown("---")

# Keep last result shown until the next calculation
if "last_result" not in st.session_state:
    st.session_state.last_result = None

if st.button("Рассчитать"):
    D = compute_D(X1, X2, X3, X4, X5, X6)
    st.session_state.last_result = {
        "D": D,
        "X": (X1, X2, X3, X4, X5, X6),
        "label": risk_label(D),
    }

# Show result if available
res = st.session_state.last_result
if res is not None:
    D = res["D"]
    lbl = res["label"]
    if D > 0:
        st.error(f"**{lbl}**  \nСчёт D = **{D:.3f}** (порог 0)")
    else:
        st.success(f"**{lbl}**  \nСчёт D = **{D:.3f}** (порог 0)")

