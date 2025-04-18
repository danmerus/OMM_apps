import streamlit as st

st.header("OMM PREECLAMPSIA IN GESTATIONAL MELLITUS AFTER ART")

st.markdown("""
Этот калькулятор вычисляет риск преэклампсии при ГСД и ВРТ.
""")

# 1. Выбор программы ВРТ (x1) с пустым placeholder
program = st.selectbox(
    "1) Вид программы ВРТ:",
    ("", "Перенос в цикле стимуляции суперовуляции", "Перенос размороженного эмбриона (криоперенос)")
)

# 2. BMI в I триместре (x2) как текстовое поле с placeholder
x2_str = st.text_input(
    "2) Индекс массы тела (ИМТ) в I триместре, кг/м²:",
    placeholder="Например, 24.0"
)

# 3. Наличие ССЗ (x3) с пустым placeholder
cvd = st.selectbox(
    "3) Наличие заболеваний сердечно‑сосудистой системы:",
    ("", "Нет", "Да")
)

# 4. Полиморфизм гена ApoB (x4) с пустым placeholder
geno = st.selectbox(
    "4) Полиморфизм гена ApoBPro2739leuGgtA:",
    ("", "Доминантный вариант", "Гетерозиготный вариант", "Рецессивный вариант")
)

# Только при заполненных полях считаем D
if program and x2_str and cvd and geno:
    x1 = 0 if program.startswith("Перенос в цикле стимуляции") else 1
    try:
        x2 = float(x2_str)
    except ValueError:
        st.error("Пожалуйста, введите корректное число для ИМТ.")
        st.stop()
    x3 = 1 if cvd == "Да" else 0
    x4 = {"Доминантный вариант": 0, "Гетерозиготный вариант": 1, "Рецессивный вариант": 2}[geno]

    # Compute D
    D = -0.287 * x1 + 1.166 * x2 + 3.460 * x3 + 5.860 * x4 - 31.912

    st.markdown("---")
    st.write(f"### Прогностический индекс D = **{D:.3f}**")

    # Risk interpretation
    if D >= 0:
        st.success("⚠️ Высокий риск развития преэклампсии")
    else:
        st.info("✔️ Низкий (отсутствует) риск преэклампсии")
else:
    st.info("Пожалуйста, заполните все поля выше для вычисления риска.")
