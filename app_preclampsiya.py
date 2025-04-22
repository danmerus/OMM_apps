import streamlit as st

st.header("OMM PREECLAMPSIA IN GESTATIONAL MELLITUS AFTER ART")

st.markdown("""
Этот калькулятор вычисляет риск преэклампсии при гестационном сахарном диабете после ВРТ.
""")

# 1) Вид программы ВРТ (x1) — неизменяемый выбор
program = st.selectbox(
    "1) Вид программы ВРТ:",
    (
        "Перенос в цикле стимуляции суперовуляции",
        "Перенос размороженного эмбриона (криоперенос)"
    )
)

# 2) ИМТ в I триместре (x2) — числовое поле
x2 = st.number_input(
    "2) Индекс массы тела (ИМТ) в I триместре, кг/м²:",
    min_value=0.0,
    max_value=100.0,
    value=24.0,
    step=0.1
)

# 3) Наличие ССЗ (x3)
cvd = st.selectbox(
    "3) Наличие заболеваний сердечно‑сосудистой системы:",
    ("Нет", "Да")
)

# 4) Полиморфизм гена ApoB (x4)
geno = st.selectbox(
    "4) Полиморфизм гена ApoBPro2739leuGgtA:",
    ("Доминантный вариант", "Гетерозиготный вариант", "Рецессивный вариант")
)

# Button to run calculation
if st.button("Calculate"):
    # map inputs to x1–x4
    x1 = 0 if program.startswith("Перенос эмбриона в цикле стимуляции суперовуляции") else 1
    x3 = 1 if cvd == "Да" else 0
    x4 = {"Доминантный вариант (GG)": 0, "Гетерозиготный вариант (GA)": 1, "Рецессивный вариант (АА)": 2}[geno]

    # compute prognostic index D
    D = -0.287 * x1 + 1.166 * x2 + 3.460 * x3 + 5.860 * x4 - 31.912

    # red background for high risk, green for low
    if D >= 0:
        st.error("⚠️ Высокий риск развития преэклампсии")
    else:
        st.success("✔️ Низкий (отсутствует) риск преэклампсии")
