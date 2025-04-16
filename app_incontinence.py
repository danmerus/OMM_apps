import streamlit as st

def main():
    st.title("Анализ результатов исследований")

    # Create a form so that all input is collected nicely
    with st.form(key="my_form"):
        st.write("Введите данные:")

        dlinaUretri = st.number_input(
            "Длина уретры по данным УЗИ (см)",
            min_value=2.0,
            max_value=4.2,
            step=0.01,
            format="%.2f",
        )

        diffShiriniUretri = st.number_input(
            "Разность ширины уретры в покое и при натуживании (см)",
            min_value=-0.39,
            max_value=0.50,
            step=0.01,
            format="%.2f",
        )

        maxSpeedMochi = st.number_input(
            "Максимальная скорость потока мочи (мл/сек)",
            min_value=16.0,
            max_value=41.0,
            step=0.01,
            format="%.2f",
        )

        avgSpeedMochi = st.number_input(
            "Средняя скорость потока мочи (мл/сек)",
            min_value=8.0,
            max_value=21.0,
            step=0.01,
            format="%.2f",
        )

        ggCOL1A = st.checkbox(
            "Пациент является носителем генотипа GG COL1A1:1546",
            value=False
        )
        ggESR = st.checkbox(
            "Пациент является носителем генотипа GG ESR:-351",
            value=False
        )

        # Button to trigger the calculation
        submit_button = st.form_submit_button(label="Анализ результатов")

    # If user clicked "Analyze"
    if submit_button:
        # Convert booleans to integer (0 or 1) the same way
        val_ggCOL1A = 1 if ggCOL1A else 0
        val_ggESR = 1 if ggESR else 0

        # Calculations based on your JavaScript
        resultSetka = (
            -7.9285 * diffShiriniUretri
            + 0.2587 * avgSpeedMochi
            + 0.4650 * val_ggESR
            - 3.8844
        )
        resultGel = (
            1.390 * dlinaUretri
            - 0.3216 * maxSpeedMochi
            - 0.7385 * val_ggCOL1A
            + 6.184
        )

        # Present the results
        st.write("## Результаты")
        # For Setka
        if resultSetka > 0:
            st.markdown(
                "**Уретропексия свободной синтетической петлёй + передняя кольпоррафия:** "
                ":red[НЕ рекомендовано]"
            )
        else:
            st.markdown(
                "**Уретропексия свободной синтетической петлёй + передняя кольпоррафия:** "
                ":green[РЕКОМЕНДОВАНО]"
            )

        # For Gel
        if resultGel > 0:
            st.markdown(
                "**Парауретральное введение объёмообразующего геля + передняя кольпоррафия:** "
                ":red[НЕ рекомендовано]"
            )
        else:
            st.markdown(
                "**Парауретральное введение объёмообразующего геля + передняя кольпоррафия:** "
                ":green[РЕКОМЕНДОВАНО]"
            )

        # Debug info (remove if not needed)
        # st.write(f"resultSetka = {resultSetka:.4f}")
        # st.write(f"resultGel   = {resultGel:.4f}")

if __name__ == "__main__":
    main()