import streamlit as st

# ---------- helpers ---------- #
def get_float(label, placeholder, *, min_v, max_v):
    """
    Text‑based numeric input:
    • Returns float or None
    • Shows an error if value is not a number or out of range
    """
    raw = st.text_input(label, placeholder=placeholder)
    if raw == "":
        return None
    try:
        val = float(raw.replace(",", "."))   # allow comma decimals
    except ValueError:
        st.error("Введите число, пожалуйста.")
        return None
    if not (min_v <= val <= max_v):
        st.error(f"Значение должно быть в диапазоне {min_v}…{max_v}.")
        return None
    return val

def yes_no(label):
    """Selectbox with a placeholder so the field can start unselected."""
    choice = st.selectbox(label, ["— выберите ответ —", "Да", "Нет"], index=0)
    return None if choice.startswith("—") else int(choice == "Да")

# ---------- main app ---------- #
def main():
    st.header("OMM INCONTINENCE")

    with st.form("my_form"):
        st.write("Введите данные:")

        dlina_uretri = get_float(
            "Длина уретры по данным УЗИ (см)",
            "2.0 … 4.2",
            min_v=2.0, max_v=4.2
        )

        diff_shirini = get_float(
            "Разность ширины уретры в покое и при натуживании (см)",
            "-0.39 … 0.50",
            min_v=-0.39, max_v=0.50
        )

        max_speed = get_float(
            "Максимальная скорость потока мочи (мл/сек)",
            "16.0 … 41.0",
            min_v=16.0, max_v=41.0
        )

        avg_speed = get_float(
            "Средняя скорость потока мочи (мл/сек)",
            "8.0 … 21.0",
            min_v=8.0, max_v=21.0
        )

        gg_col1a = yes_no("Пациент является носителем генотипа GG COL1A1:1546?")
        gg_esr   = yes_no("Пациент является носителем генотипа GG ESR:-351?")

        submit = st.form_submit_button("Анализ результатов")

    # ----------- calculation ----------- #
    if submit:
        if None in (
            dlina_uretri, diff_shirini, max_speed,
            avg_speed, gg_col1a, gg_esr
        ):
            st.warning("Пожалуйста, заполните все поля корретно.")
            return

        result_setka = (
            -7.9285 * diff_shirini
            + 0.2587 * avg_speed
            + 0.4650 * gg_esr
            - 3.8844
        )
        result_gel = (
            1.390  * dlina_uretri
            - 0.3216 * max_speed
            - 0.7385 * gg_col1a
            + 6.184
        )

        st.write("## Результаты")
        # Setka recommendation
        if result_setka > 0:
            st.markdown(
                "**Уретропексия свободной синтетической петлёй + передняя кольпоррафия:** "
                ":red[НЕ рекомендовано]"
            )
        else:
            st.markdown(
                "**Уретропексия свободной синтетической петлёй + передняя кольпоррафия:** "
                ":green[РЕКОМЕНДОВАНО]"
            )

        # Gel recommendation
        if result_gel > 0:
            st.markdown(
                "**Парауретральное введение объёмообразующего геля + передняя кольпоррафия:** "
                ":red[НЕ рекомендовано]"
            )
        else:
            st.markdown(
                "**Парауретральное введение объёмообразующего геля + передняя кольпоррафия:** "
                ":green[РЕКОМЕНДОВАНО]"
            )

if __name__ == "__main__":
    main()
