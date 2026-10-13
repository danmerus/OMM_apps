import numpy as np
import pandas as pd
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


def fmt(x, digits=3):
    return f"{x:,.{digits}f}".replace(",", " ").replace(".", ",").replace("-", "−")


# ── Page ─────────────────────────────────────────────────────────────────────
st.title("🔬 Прогноз наступления беременности при повторных неудачах имплантации")
st.markdown(
    "Расчёт по математической модели для пациенток с повторными неудачами "
    "имплантации в программах ВРТ. Предикторы — результаты пайпель-биопсии "
    "эндометрия на 6-е сутки после пика ЛГ."
)

tab_pred, tab_model = st.tabs(["🎯 Прогноз", "📐 О модели"])

# ── Tab 1: Prediction ────────────────────────────────────────────────────────
with tab_pred:
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

        c1, c2 = st.columns(2)
        c1.metric("Вероятность P", f"{fmt(p * 100, 1)} %")
        c2.metric("Значение z", fmt(z))
        st.progress(p)
        st.caption(
            f"Заключение дано по условному порогу P = {fmt(THRESHOLD, 1)}; "
            "в описании модели порог не указан."
        )

        with st.expander("Вклад предикторов в z", expanded=True):
            rows = [{
                "Предиктор": f"{sym} — {label}",
                "Значение": values[key],
                "Коэффициент": coef,
                "Вклад в z": coef * values[key],
            } for key, sym, label, _, coef, _ in PREDICTORS]
            rows.append({"Предиктор": "Константа", "Значение": None,
                         "Коэффициент": None, "Вклад в z": INTERCEPT})
            rows.append({"Предиктор": "Итого z", "Значение": None,
                         "Коэффициент": None, "Вклад в z": z})
            st.dataframe(
                pd.DataFrame(rows), hide_index=True, width="stretch",
                column_config={
                    "Значение": st.column_config.NumberColumn(format="%.2f"),
                    "Коэффициент": st.column_config.NumberColumn(format="%.3f"),
                    "Вклад в z": st.column_config.NumberColumn(format="%.3f"),
                })

        if abs(z) > 10:
            st.info(
                "Коэффициенты модели велики, поэтому при большинстве значений "
                "P получается практически равной 0 % или 100 %."
            )

# ── Tab 2: Model ─────────────────────────────────────────────────────────────
with tab_model:
    st.markdown("### Формула")
    st.latex(r"P = \frac{1}{1 + e^{-z}}")
    st.latex(
        r"\begin{aligned} z ={}& 72{,}727\,x_1 + 14{,}313\,x_2 + 308{,}381\,x_3"
        r" + 3242{,}545\,x_4 + 78{,}335\,x_5 \\ &- 189{,}648\,x_6"
        r" - 38{,}471\,x_7 + 161{,}322 \end{aligned}"
    )
    st.markdown("где *e* — основание натуральных логарифмов (≈ 2,71828).")

    st.markdown("### Предикторы")
    st.dataframe(
        pd.DataFrame([{
            "Обозначение": sym,
            "Показатель": label,
            "Единицы": unit,
            "Коэффициент": coef,
        } for _, sym, label, unit, coef, _ in PREDICTORS]),
        hide_index=True, width="stretch",
        column_config={
            "Коэффициент": st.column_config.NumberColumn(format="%.3f")},
    )

    st.markdown("### Как получена модель")
    st.markdown(
        "Модель построена методом логистической регрессии с автоматическим "
        "отбором предикторов по информативности (IBM SPSS Statistics 26.0) на "
        "иммуногистохимических данных пациенток 1 группы (n = 30) и группы "
        "сравнения (n = 30); биоптаты эндометрия взяты на 6-е сутки после "
        "пика ЛГ."
    )

st.divider()
st.caption(
    "Исследовательский калькулятор. Не является медицинским изделием и не "
    "заменяет решение врача."
)
