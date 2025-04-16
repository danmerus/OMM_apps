import streamlit as st
import math

st.title("Прогнозирование риска развития тазовых и уродинамических дисфункций")

# 1) Radio buttons for question1
question1 = st.radio(
    "У пациентки были первые роды?",
    options=["Да", "Нет"],
    index=0
)
ar_1 = 1 if question1 == "Да" else 0

# 2) Number input for question2
ar_2 = st.number_input(
    "Разность ширины уретры в покое и при натуживании (мм) (от -1 до 1)",
    min_value=-1.0,
    max_value=1.0,
    step=0.1,
    value=0.0,
    format="%.1f"
)

# 3) Number input for question3
ar_3 = st.number_input(
    "Величина давления, оказываемого на влагалищный датчик при сокращении мышц (мм.рт.ст.) (от 55 до 100)",
    min_value=55.0,
    max_value=100.0,
    step=1.0,
    value=70.0,
    format="%.1f"
)

# 4) Radio buttons for question4
question4 = st.radio(
    "Пациентка является носителем генотипа GG гена ESR1:A-351G?",
    options=["Да", "Нет"],
    index=1
)
ar_4 = 1 if question4 == "Да" else 0

# 5) Number input for question5
ar_5 = st.number_input(
    "Величина сухожильного центра промежности (мм) (от 2.0 до 12.0)",
    min_value=2.0,
    max_value=12.0,
    step=0.1,
    value=6.0,
    format="%.1f"
)

# 6) Number input for question6
ar_6 = st.number_input(
    "Величина m. bulbospongiosus (мм) (от 3.0 до 14.0)",
    min_value=3.0,
    max_value=14.0,
    step=0.1,
    value=8.0,
    format="%.1f"
)

# Button to trigger computation
if st.button("Рассчитать риск"):
    # Replicate the logistic formula from the PHP
    numerator = math.exp(
        13.189
        - 1.314  * ar_1
        - 5.4581 * ar_2
        - 0.12576 * ar_3
        + 2.9661 * ar_4
        - 0.27877 * ar_5
        - 0.16889 * ar_6
    )
    denominator = 1 + numerator
    W = numerator / denominator

    # Decide risk level
    if W >= 0.5:
        st.markdown("<h3 style='text-align: center; color: red;'>ВЫСОКИЙ РИСК</h3>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center;'>развития дисфункции тазового дна через 6 месяцев после родов</h5>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center; color: green;'>НИЗКИЙ РИСК</h3>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center;'>развития дисфункции тазового дна через 6 месяцев после родов</h5>", unsafe_allow_html=True)
