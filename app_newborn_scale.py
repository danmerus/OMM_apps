import streamlit as st

st.set_page_config(
    page_title="ОММ.MedNeo — оценка тяжести состояния новорожденных",
    layout="centered",
)

st.header("Программа оценки тяжести состояния и органной дисфункции у новорожденных")
st.subheader("Шкала ОММ.MedNeo")

# ---------- helpers ---------------------------------------------------------
SECTION = """
<style>
.big-box {{
    width: 100%;
    border-radius: 0.6rem;
    padding: 1.4rem;
    font-weight: 700;
    font-size: 1.2rem;
    text-align: center;
}}
.good  {{background:#19b16b;color:#fff;}}
.ok    {{background:#ff6788;color:#fff;}}
.bad   {{background:#f82222;color:#fff;}}
</style>
"""

st.markdown(SECTION, unsafe_allow_html=True)

# ---------- inputs ----------------------------------------------------------
with st.form("neo_form"):
    st.markdown("### Дыхательная система")
    resp = st.radio(
        "", ["ИВЛ", "СРАР / O₂-маска", "Без респираторной терапии"],
        format_func=lambda s: s,
        horizontal=False,
    )
    resp_score = {"ИВЛ": 2, "СРАР / O₂-маска": 1, "Без респ. терапии": 0}.get(resp, 0)

    st.markdown("### FiO₂ (фракция кислорода во вдыхаемой смеси)")
    fio2 = st.radio(
        "", ["≥ 50 %", "30 – 49 %", "≤ 29 %"], horizontal=False
    )
    fio2_score = {"≥ 50 %": 1, "30 – 49 %": 2, "≤ 29 %": 0}[fio2]

    st.markdown("### Центральная нервная система")
    cns = st.radio(
        "", ["Атония / арефлексия", "Гипотонус / гипорефлексия", "Норма"],
        horizontal=False,
    )
    cns_score = {"Атония / арефлексия": 2, "Гипотонус / гипорефлексия": 1, "Норма": 0}[cns]

    st.markdown("### Гемодинамическая стабильность")
    hemo = st.radio(
        "",
        [
            "Допамин > 5 мкг/кг/мин и/или Добутамин > 5 мкг/кг/мин\n"
            "Адреналин ≥ 0,1 мкг/кг/мин\nНорадреналин ≥ 0,1 мкг/кг/мин",
            "Допамин < 5 мкг/кг/мин или Добутамин < 5 мкг/кг/мин",
            "Не требует",
        ],
        horizontal=False,
    )
    hemo_score = {
        "Допамин > 5 мкг/кг/мин и/или Добутамин > 5 мкг/кг/мин\n"
        "Адреналин ≥ 0,1 мкг/кг/мин\nНорадреналин ≥ 0,1 мкг/кг/мин": 2,
        "Допамин < 5 мкг/кг/мин или Добутамин < 5 мкг/кг/мин": 1,
        "Не требует": 0,
    }[hemo]

    st.markdown("### Температура тела")
    temp = st.radio("", ["≥ 37 .6 °C", "≤ 36 .4 °C", "36 .5 – 37 .5 °C"])
    temp_score = {"≥ 37 .6 °C": 2, "≤ 36 .4 °C": 2, "36 .5 – 37 .5 °C": 0}[temp]

    st.markdown("### Дефицит оснований (ВЕ)")
    be = st.radio("", ["< −13 ммоль/л", "−8 … −12 .9 ммоль/л", "> −8 ммоль/л"])
    be_score = {"< −13 ммоль/л": 2, "−8 … −12 .9 ммоль/л": 1, "> −8 ммоль/л": 0}[be]

    st.markdown("### Лактат")
    lact = st.radio("", ["≥ 6 .9 ммоль/л", "4 .1 – 6 .8 ммоль/л", "≤ 4 ммоль/л"])
    lact_score = {"≥ 6 .9 ммоль/л": 2, "4 .1 – 6 .8 ммоль/л": 1, "≤ 4 ммоль/л": 0}[lact]

    submitted = st.form_submit_button("Рассчитать оценку")

# ---------- result ----------------------------------------------------------
if submitted:
    score = sum(
        [
            resp_score,
            fio2_score,
            cns_score,
            hemo_score,
            temp_score,
            be_score,
            lact_score,
        ]
    )

    if score <= 2:
        st.markdown(f'<div class="big-box good">Состояние средней степени тяжести — прогноз благоприятный (сумма баллов {score})</div>', unsafe_allow_html=True)
    elif score <= 8:
        st.markdown(f'<div class="big-box ok">Состояние тяжёлое — прогноз благоприятный (сумма баллов {score})</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="big-box bad">Состояние крайне тяжёлое — прогноз неблагоприятный (сумма баллов {score})</div>', unsafe_allow_html=True)
