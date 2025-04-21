import streamlit as st

st.set_page_config(
    page_title="ГСД — риск ЗРП",
    page_icon="🩺",
    layout="centered",
)

st.header("OMM FETAL GROWTH RETARDATION IN GESTATIONAL MELLITUS")

with st.form("risk_form"):
    x1 = st.selectbox(
        "Нарушение маточно‑плацентарного кровотока по УЗИ",
        ("Нет", "Есть"),
        help="Выберите «Есть», если кровоток нарушен"
    )
    x2 = st.number_input(
        "Концентрация VEGF‑A (мЕ/мл)",
        min_value=0.0,
        step=0.1,
        format="%.2f"
    )
    x3 = st.selectbox(
        "Гетерозиготный генотип eNOS:G894T G>T",
        ("Нет", "Есть"),
        help="«Есть» = обнаружен генотип G/T"
    )

    submitted = st.form_submit_button("Рассчитать риск")

if submitted:
    # map selections to 0 / 1
    x1_val = 1 if x1 == "Есть" else 0
    x3_val = 1 if x3 == "Есть" else 0

    P = 27.4 * x1_val - 0.31 * x2 + 0.48 * x3_val + 1.6
    st.markdown(f"### Индекс **P** = `{P:.2f}`")

    if P > 0.49:
        st.error("Высокий риск задержки роста плода")
    else:
        st.success("Низкий риск задержки роста плода")

    # st.caption(
    #     "При расчёте используются значения из публикации: "
    #     "Aspartaminotransferase — ЛПВП — генотип PPARG P12A — поддержка гестагенами."
    # )
