import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.express as px

st.set_page_config(
    page_title="ВПЧ — Прогноз исходов",
    page_icon="🔬",
    layout="wide",
)

# ── Load artefacts ───────────────────────────────────────────────────────────
@st.cache_resource
def load_all_models():
    models = {
        "surg": joblib.load("model_surg.pkl"),
        "obs":  joblib.load("model_obs.pkl"),
    }
    with open("feature_cols.json", encoding="utf-8") as f:
        cols = json.load(f)
    with open("feature_importances.json", encoding="utf-8") as f:
        fi = json.load(f)
    return models, cols, fi


ALL_MODELS, feature_cols, fi_data = load_all_models()

# ── Feature metadata ─────────────────────────────────────────────────────────
HPV_HR = ["ВПЧ ВКР 16 ", "ВПЧ 18", "ВПЧ 31", "ВПЧ 33", "ВПЧ 35",
          "ВПЧ 39", "ВПЧ 45", "ВПЧ 51", "ВПЧ 52", "ВПЧ 53",
          "ВПЧ 56", "ВПЧ 58", "ВПЧ 59", "ВПЧ 68", "ВПЧ 66"]
HPV_COUNT = ["кол-во типов у 1-ой пациентки"]
HPV_LR = ["ВПЧ НКР 6", " ВПЧ 11", "ВПЧ 42", "ВПЧ 43", "ВПЧ 44", "ВПЧ 73"]
MICROBIOME = [
    "Lactobacillus spp.", "Сем. Enterobacteriaceae", "Streptococcus spp.",
    "Staphylococcus spp.",
    "Gardnerella vaginalis+Prevotella bivia+Porphyromonas spp.",
    "Eubacterium spp.", "Sneathia spp.+Leptotrichia spp.+Fusobacterium spp.",
    "Megasphaera spp.+Veillonella spp.+Dialister spp.",
    "Lachnobacterium spp.+Clostridium spp.",
    "Mobiluncus spp.+Corynebacterium spp.", "Peptostreptococcus spp.",
    "Atobium vaginae", "Candida spp.", "Mycoplasma hominis",
    "Ureaplasma (urealyticum+parvum)", "Mycoplasma genitalium",
]
LACTOBAC = ["Lactobac. spp. % (относительный)", "Lactobac. spp. Снижено"]
CYTOLOGY = [
    "NILM",
    "LSIL Перинуклеарная зона просветления \"гало\"",
    "Амфофилия цитоплазмы", "Двуядерность", "Койлоциты",
    "Ядра обычного размера или слегка увеличены",
    "LSIL ЯЦО увеличено (легк дисп)", "Размер ядра > 3 (легк дисп)",
    "Контур ядерной мембраны неровный (легк дисп)",
    "Хроматин грубый, неравномерно распределен (легк дисп)",
    "ASCUS (ЯЦО увеличено)",
    "Контур ядерной мембраны ровный или неровный",
    "Хроматин распределен равномерно или неравномерно",
]
COLPOSCOPY = [
    "Гиперхромные ядра", "Многоядерность", "НКК",
    "Тонкий АЦЭ", "Нежная мозаика", "Нежная пунктация",
    "Плотный АЦЭ", "Быстрое побеление", "АЦЭ плотный обод",
    "Грубая мозаика", "Грубая пунктация", "Внутри поражения - кон",
    "Признак бугристости", "Лейкоплакия", "Эрозия",
    "Окрашивание Люголем ",
]
CONTINUOUS = {
    "кол-во типов у 1-ой пациентки": (0, 16, 1),
    "Lactobac. spp. % (относительный)": (0.0, 100.0, 80.0),
    "Возраст": (18, 60, 30),
    "ИМТ": (15.0, 45.0, 24.0),
    "возраст начала половой жизни": (12, 30, 17),
    "Возраст Менархе": (9, 18, 13),
    "Пролжительность менструации": (1, 14, 6),
}
for b in MICROBIOME:
    CONTINUOUS[b] = (0.0, 12.0, 0.0)

DEMO_BINARY = [
    "Забол.ЖКТ", "геморрой", "Забол.МВС", "рецидивирующий цистит",
    "фиброаденома МЖ", "анемия", "Курение",
    "Болезненность", "обильные", "КОК в анамнезе", "ВМС",
]
DEMO_LABELS = {
    "Забол.ЖКТ": "Заболевание ЖКТ",
    "геморрой": "Геморрой",
    "Забол.МВС": "Заболевание МВС",
    "рецидивирующий цистит": "Рецидивирующий цистит",
    "фиброаденома МЖ": "Фиброаденома МЖ",
    "анемия": "Анемия",
    "Курение": "Курение",
    "Болезненность": "Болезненные менструации",
    "обильные": "Обильные менструации",
    "КОК в анамнезе": "КОК в анамнезе",
    "ВМС": "ВМС",
}

GROUP_LABEL = {"surg": "Хирургическая", "obs": "Наблюдательная"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def collect_inputs():
    values = {}

    with st.expander("🦠 ВПЧ высокого риска (ВКР)", expanded=True):
        cols = st.columns(5)
        for i, c in enumerate(HPV_HR):
            values[c] = int(cols[i % 5].checkbox(c.strip(), key=f"hpv_{i}"))

    with st.expander("🦠 ВПЧ низкого риска (НКР) + количество типов"):
        cols = st.columns(3)
        values[HPV_COUNT[0]] = cols[0].number_input(
            "Кол-во типов ВПЧ", min_value=0, max_value=16, value=1, step=1)
        for i, c in enumerate(HPV_LR):
            values[c] = int(cols[(i + 1) % 3].checkbox(c.strip(), key=f"lr_{i}"))

    with st.expander("🔬 Микробиом влагалища (log₁₀ концентрация)"):
        cols = st.columns(3)
        for i, c in enumerate(MICROBIOME):
            short = c.split("+")[0].split(".")[0][:30]
            mn, mx, default = CONTINUOUS[c]
            values[c] = cols[i % 3].number_input(
                short, min_value=float(mn), max_value=float(mx),
                value=float(default), step=0.1, key=f"mb_{i}")

    with st.expander("🔬 Лактобациллы"):
        c1, c2 = st.columns(2)
        mn, mx, default = CONTINUOUS[LACTOBAC[0]]
        values[LACTOBAC[0]] = c1.number_input(
            "Lactobac. spp. % (относительный)",
            min_value=float(mn), max_value=float(mx),
            value=float(default), step=0.1)
        values[LACTOBAC[1]] = int(c2.checkbox("Lactobac. spp. Снижено"))

    with st.expander("🔬 Цитология"):
        cols = st.columns(3)
        for i, c in enumerate(CYTOLOGY):
            values[c] = int(cols[i % 3].checkbox(c[:40], key=f"cy_{i}"))

    with st.expander("🔬 Кольпоскопия"):
        cols = st.columns(4)
        for i, c in enumerate(COLPOSCOPY):
            values[c] = int(cols[i % 4].checkbox(c.strip()[:35], key=f"co_{i}"))

    with st.expander("👤 Демография и анамнез", expanded=True):
        c1, c2 = st.columns(2)
        values["Возраст"] = c1.number_input("Возраст (лет)", 18, 60, 30)
        values["ИМТ"] = c2.number_input("ИМТ", 15.0, 45.0, 24.0, step=0.1)
        values["возраст начала половой жизни"] = c1.number_input(
            "Возраст начала половой жизни", 12, 30, 17)
        values["Возраст Менархе"] = c2.number_input("Возраст менархе", 9, 18, 13)
        values["Пролжительность менструации"] = c1.number_input(
            "Длительность менструации (дни)", 1, 14, 6)

        st.markdown("**Сопутствующие заболевания и анамнез**")
        cols = st.columns(3)
        for i, c in enumerate(DEMO_BINARY):
            values[c] = int(cols[i % 3].checkbox(DEMO_LABELS[c], key=f"dm_{i}"))

    return values


def fi_chart(fi_key, title=""):
    fi = fi_data[fi_key]
    fi_df = (
        pd.DataFrame({"Признак": list(fi.keys()), "Важность": list(fi.values())})
        .sort_values("Важность", ascending=False)
        .head(20)
    )
    fig = px.bar(
        fi_df[::-1], x="Важность", y="Признак", orientation="h",
        title=title, color="Важность", color_continuous_scale="Blues",
    )
    fig.update_layout(
        height=550, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=40, b=10), yaxis_title="",
    )
    return fig


# ── Page ─────────────────────────────────────────────────────────────────────
st.title("🔬 Прогноз исходов лечения ВПЧ-ассоциированных поражений шейки матки")

# Group selector lives outside the form so the rest of the UI can react to it
group_key = st.radio(
    "**Тактика ведения пациентки**",
    options=["surg", "obs"],
    format_func=lambda k: GROUP_LABEL[k],
    horizontal=True,
)
st.markdown(f"*Используются модели, обученные на группе: **{GROUP_LABEL[group_key]}***")
st.divider()

tab_pred, tab_fi = st.tabs(["🎯 Прогноз", "📊 Важность признаков"])

# ── Tab 1: Prediction ────────────────────────────────────────────────────────
with tab_pred:
    with st.form("patient_form"):
        inputs = collect_inputs()
        submitted = st.form_submit_button("🔮 Рассчитать прогноз", type="primary")

    if submitted:
        bundle  = ALL_MODELS[group_key]
        row     = pd.DataFrame([{c: inputs.get(c, 0) for c in feature_cols}])[feature_cols]
        row_imp = bundle["imputer"].transform(row.values)  # numpy → no column-name check
        p       = bundle["rf"].predict_proba(row_imp)[0][1]

        st.markdown("---")
        label = "✅ Положительный исход" if p >= 0.5 else "❌ Отрицательный исход"
        st.markdown(f"## {label}")

# ── Tab 2: Feature Importance ────────────────────────────────────────────────
with tab_fi:
    st.markdown(f"### Топ-20 важных признаков — группа: {GROUP_LABEL[group_key]}")
    st.plotly_chart(fi_chart(group_key, GROUP_LABEL[group_key]), use_container_width=True)

