import numpy as np
import streamlit as st

st.set_page_config(
    page_title="ПНИ — Прогноз наступления беременности",
    page_icon="🔬",
    layout="centered",
)

# ── Model ────────────────────────────────────────────────────────────────────
# Логистическая регрессия из описания модели:
#   P = 1 / (1 + e^(-z))
#   z = 72,727·x1 + 14,313·x2 + 308,381·x3 + 3242,545·x4 + 78,335·x5
#       − 189,648·x6 − 38,471·x7 + 161,322
# В исходном тексте последний коэффициент (−38,471) записан при x4; x4 там
# встречается дважды, а x7 не используется, поэтому здесь он отнесён к x7.
INTERCEPT = 161.322
THRESHOLD = 0.5  # условный порог; в описании модели порог не указан

# key, обозначение, подпись, единицы, коэффициент, (min, max, default, step)
PREDICTORS = [
    ("cd34", "x1", "CD34, строма эндометрия", "%", 72.727,
     (0.0, 100.0, 0.0, 0.1)),
    ("p53", "x2", "p53, железы эндометрия", "%", 14.313,
     (0.0, 100.0, 0.0, 0.1)),
    ("pten", "x3", "PTEN, строма эндометрия", "%", 308.381,
     (0.0, 100.0, 0.0, 0.1)),
    ("bcl2", "x4", "Bcl-2, железы эндометрия", "%", 3242.545,
     (0.0, 100.0, 0.0, 0.1)),
    ("cd138", "x5", "CD138, строма эндометрия", "клеток в поле зрения", 78.335,
     (0.0, 500.0, 0.0, 1.0)),
    ("mir135a", "x6", "miR-135a-5p, строма эндометрия", "ΔCt", -189.648,
     (-30.0, 30.0, 0.0, 0.01)),
    ("mir143", "x7", "miR-143-3p, строма эндометрия", "ΔCt", -38.471,
     (-30.0, 30.0, 0.0, 0.01)),
]


def linear_predictor(values):
    return INTERCEPT + sum(coef * values[key]
                           for key, _, _, _, coef, _ in PREDICTORS)


def probability(z):
    # tanh-форма сигмоиды: не переполняется при больших |z|
    return float(0.5 * (1.0 + np.tanh(z / 2.0)))


# ── Page ─────────────────────────────────────────────────────────────────────
st.title("🔬 Прогноз наступления беременности при повторных неудачах имплантации")
st.markdown(
    "Расчёт по математической модели для пациенток с повторными неудачами "
    "имплантации в программах ВРТ. Предикторы — результаты пайпель-биопсии "
    "эндометрия на 6-е сутки после пика ЛГ."
)

# ── Prediction ───────────────────────────────────────────────────────────────
with st.form("patient_form"):
    values = {}

    st.markdown("**Иммуногистохимия**")
    cols = st.columns(2)
    for i, (key, sym, label, unit, _, (mn, mx, default, step)) in enumerate(
            PREDICTORS[:5]):
        values[key] = cols[i % 2].number_input(
            f"{label}, {unit}", min_value=mn, max_value=mx, value=default,
            step=step, key=key)

    st.markdown("**МикроРНК**")
    cols = st.columns(2)
    for i, (key, sym, label, unit, _, (mn, mx, default, step)) in enumerate(
            PREDICTORS[5:]):
        values[key] = cols[i % 2].number_input(
            f"{label}, {unit}", min_value=mn, max_value=mx, value=default,
            step=step, format="%.2f", key=key,
            help="Вводится ΔCt как есть, без смены знака.")

    submitted = st.form_submit_button("🔮 Рассчитать прогноз", type="primary")

if submitted:
    z = linear_predictor(values)
    p = probability(z)

    st.markdown("---")
    if p >= THRESHOLD:
        st.markdown("## ✅ Прогноз: наступление беременности вероятно")
    else:
        st.markdown("## ❌ Прогноз: наступление беременности маловероятно")

st.divider()
