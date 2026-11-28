import math

import streamlit as st

# Formula from the clinicians (ФОРМУЛА.docx): P = 1 / (1 + e^-z),
# z = intercept + sum(coef * x). Ranges = min/max in their database (20 patients).
INTERCEPT = 146.786
THRESHOLD = 0.5
FEATURES = [
    # key, label, coef, min, max
    ("cd138", "Экспрессия CD138 в строме эндометрия", -50.608, 0, 1),
    ("cd34", "Экспрессия CD34 в железах эндометрия, %", 4.679, 27.1, 71.1),
    ("p53", "Экспрессия p53 в строме эндометрия, %", 36.007, 2.0, 6.7),
    ("pten", "Экспрессия PTEN в железах эндометрия, %", 0.740, 6.7, 72.9),
    ("mir135", "Экспрессия miR-135a-5p в строме эндометрия, ΔCt", -86.710, 3.32, 8.71),
    ("mir143", "Экспрессия miR-143-3p в строме эндометрия, ΔCt", -13.899, -1.0, 4.41),
]
N_PATIENTS = 20


def pregnancy_probability(values: dict) -> float:
    """Chance of pregnancy in the cryo cycle by the clinicians' formula."""
    z = INTERCEPT + sum(coef * values[key] for key, _, coef, _, _ in FEATURES)
    # Stable form: math.exp overflows for z below about -709
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def _fmt(x: float) -> str:
    return f"{x:g}".replace(".", ",")


def _fmt_probability(p: float) -> str:
    if p > 0.99:
        return "> 99 %"
    if p < 0.01:
        return "< 1 %"
    return f"{p * 100:.0f} %"


# ── UI ───────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="PREDICT Crio Implantation", page_icon="🧬", layout="wide")

st.title("PREDICT Crio Implantation", anchor=False)
st.subheader("Прогнозирование наступления беременности в криопротоколе программ ВРТ "
             "у пациенток с повторными неудачами имплантации", anchor=False)
st.caption("Модель прогнозирования основана на результатах пайпель-биопсии эндометрия "
           "на 6+ЛГ день менструального цикла, предшествующего программе криопереноса.")

st.markdown("#### Данные пациентки")
values: dict[str, float | None] = {}
cols = st.columns(3)
for i, (key, label, _, lo, hi) in enumerate(FEATURES):
    with cols[i % 3]:
        if key == "cd138":
            choice = st.selectbox(label, ["Нет", "Есть"], index=None, placeholder="Выберите",
                                  key=key, help="В базе записана как 0 (нет) / 1 (есть).")
            values[key] = None if choice is None else float(choice == "Есть")
        else:
            values[key] = st.number_input(label, value=None, step=0.1, format="%.2f", key=key,
                                          placeholder="Введите значение",
                                          help=f"В базе: от {_fmt(lo)} до {_fmt(hi)}.")

if st.button("🔮 Рассчитать прогноз", type="primary"):
    missing = [label for key, label, _, _, _ in FEATURES if values[key] is None]
    if missing:
        st.warning("Заполните все поля: " + "; ".join(missing))
    else:
        p = pregnancy_probability(values)
        if p >= THRESHOLD:
            st.success("### Прогноз: беременность **вероятна**")
        else:
            st.error("### Прогноз: беременность **маловероятна**")
        st.markdown(f"Вероятность наступления беременности: **{_fmt_probability(p)}**")

        outside = [(label, lo, hi) for key, label, _, lo, hi in FEATURES
                   if not (lo <= values[key] <= hi)]
        if outside:
            st.warning("Значения вне диапазона базы, на которой построена модель, "
                       "прогноз менее надёжен: "
                       + "; ".join(f"{label} (в базе {_fmt(lo)}–{_fmt(hi)})"
                                   for label, lo, hi in outside))

st.divider()
st.caption(f"Модель построена на данных {N_PATIENTS} пациенток. Результат носит вспомогательный "
           "характер, решение принимает врач.")
