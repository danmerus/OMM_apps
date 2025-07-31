# app.py
# Streamlit app: «OMM SUPERIMPOSED PREECLAMPSIA PREDICT»
# D = 2.45*X1 - 4.63*X2 + 2.64*X3 + 4.22*X4 - 57.11*X5 + 117.62*X6 - 3.96
# Threshold: D > 0 → высокий риск, иначе низкий риск

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="OMM SUPERIMPOSED PREECLAMPSIA PREDICT",
    page_icon="🩺",
    layout="centered",
)

# ----------------------- Helpers -----------------------

COEFFS = {
    "X1": 2.45,     # гиподинамия (1/0)
    "X2": -4.63,    # хроническая АГ в предыдущую беременность (1/0)
    "X3": 2.64,     # ДАД >100 в I триместре (1/0)
    "X4": 4.22,     # ДАД >100 во II триместре (1/0)
    "X5": -57.11,   # экспрессия miR-181a (число)
    "X6": 117.62,   # экспрессия miR-221 (число)
}
INTERCEPT = -3.96

def compute_D(x1, x2, x3, x4, x5, x6):
    """Compute linear score D."""
    return (
        COEFFS["X1"] * x1
        + COEFFS["X2"] * x2
        + COEFFS["X3"] * x3
        + COEFFS["X4"] * x4
        + COEFFS["X5"] * x5
        + COEFFS["X6"] * x6
        + INTERCEPT
    )

def risk_label(D):
    return "Высокий риск" if D > 0 else "Низкий риск"

def contribution_table(x1, x2, x3, x4, x5, x6):
    vals = {"X1": x1, "X2": x2, "X3": x3, "X4": x4, "X5": x5, "X6": x6}
    rows = []
    for k, v in vals.items():
        rows.append(
            {
                "Признак": k,
                "Коэффициент": COEFFS[k],
                "Значение": v,
                "Вклад": COEFFS[k] * v,
            }
        )
    df = pd.DataFrame(rows)
    df.loc[len(df)] = ["Смещение (intercept)", "", "", INTERCEPT]
    df["Вклад (накоп.)"] = df["Вклад"].cumsum()
    return df

def standardize_boolean_col(s):
    """Convert a series with values like 1/0/True/False/да/нет/yes/no to 1/0."""
    mapping = {
        "да": 1, "дa": 1, "yes": 1, "y": 1, "true": 1, "истина": 1,
        "нет": 0, "no": 0, "n": 0, "false": 0, "ложь": 0
    }
    def convert(v):
        if pd.isna(v):
            return np.nan
        if isinstance(v, (int, float)) and v in (0, 1):
            return int(v)
        if isinstance(v, bool):
            return int(v)
        s = str(v).strip().lower()
        return mapping.get(s, np.nan)
    return s.apply(convert)

def prepare_batch_df(df):
    """
    Accepts either columns named X1..X6 or the verbose Russian names below.
    Returns a clean DataFrame with X1..X6 as numeric (1/0 for booleans).
    """
    # Try to map Russian column names if present:
    rename_map = {
        "гиподинамия": "X1",
        "х1": "X1",
        "х2": "X2",
        "х3": "X3",
        "х4": "X4",
        "х5": "X5",
        "х6": "X6",
        "хроническая аг в предыдущую беременность": "X2",
        "диастолическое ад >100 мм рт. ст. в i триместре": "X3",
        "диастолическое ад >100 мм рт. ст. во ii триместре": "X4",
        "уровень экспрессии микрорнк 181а": "X5",
        "уровень экспрессии микрорнк 221": "X6",
        "miR181a": "X5",
        "miR-181a": "X5",
        "miR221": "X6",
        "miR-221": "X6",
    }
    # Normalize column names (strip and lower) for mapping
    lower_cols = {c: c for c in df.columns}
    df2 = df.copy()
    for c in df.columns:
        cl = c.strip().lower()
        if cl in rename_map:
            df2.rename(columns={c: rename_map[cl]}, inplace=True)

    # If still not present, leave as is (maybe user already named X1..X6)
    missing = [c for c in ["X1", "X2", "X3", "X4", "X5", "X6"] if c not in df2.columns]
    if missing:
        raise ValueError(
            f"Не найдены необходимые колонки: {missing}. Ожидаются X1..X6 или соответствующие русские названия."
        )

    # Standardize boolean columns X1..X4
    for c in ["X1", "X2", "X3", "X4"]:
        df2[c] = standardize_boolean_col(df2[c])

    # Numeric for X5, X6
    for c in ["X5", "X6"]:
        df2[c] = pd.to_numeric(df2[c], errors="coerce")

    # Final check
    if df2[["X1", "X2", "X3", "X4", "X5", "X6"]].isna().any().any():
        raise ValueError("Обнаружены пропуски/некорректные значения в X1..X6 после преобразования.")

    return df2[["X1", "X2", "X3", "X4", "X5", "X6"]]

# ----------------------- UI -----------------------

st.title("🩺 OMM SUPERIMPOSED PREECLAMPSIA PREDICT")
st.caption("Программа для прогнозирования риска развития преэклампсии у пациенток с хронической артериальной гипертензией.")
with st.expander("Описание модели"):
    st.markdown(
        """
**Скоринговая формула:**

\\[
D = 2{,}45\\cdot X_1 - 4{,}63\\cdot X_2 + 2{,}64\\cdot X_3 + 4{,}22\\cdot X_4 - 57{,}11\\cdot X_5 + 117{,}62\\cdot X_6 - 3{,}96.
\\]

- **X1** — гиподинамия (да/нет → 1/0)  
- **X2** — хроническая АГ в предыдущую беременность (да/нет → 1/0)  
- **X3** — ДАД > 100 мм рт. ст. в I триместре данной беременности (да/нет → 1/0)  
- **X4** — ДАД > 100 мм рт. ст. во II триместре данной беременности (да/нет → 1/0)  
- **X5** — уровень экспрессии микроРНК 181а в I триместре (число)  
- **X6** — уровень экспрессии микроРНК 221 в I триместре (число)  

**Правило классификации:**  
- Если **D > 0** → **высокий риск**  
- Если **D ≤ 0** → **низкий риск**  

> ⚠️ *Данное приложение не заменяет медицинское заключение. Используйте результаты только как вспомогательную информацию и консультируйтесь с врачом.*
        """
    )

tab1, tab2 = st.tabs(["🧮 Калькулятор (1 пациентка)", "📄 Пакетная обработка (CSV)"])

with tab1:
    st.subheader("Ввод признаков")
    c1, c2 = st.columns(2)
    with c1:
        X1 = 1 if st.checkbox("X1: Гиподинамия (да)", value=False) else 0
        X2 = 1 if st.checkbox("X2: Хроническая АГ в предыдущую беременность (да)", value=False) else 0
        X3 = 1 if st.checkbox("X3: ДАД >100 мм рт. ст. в I триместре (да)", value=False) else 0
        X4 = 1 if st.checkbox("X4: ДАД >100 мм рт. ст. во II триместре (да)", value=False) else 0
    with c2:
        X5 = st.number_input(
            "X5: Уровень экспрессии miR-181a (I триместр)",
            min_value=0.0, step=0.0001, format="%.6f", value=0.0,
            help="Введите измеренное значение; единицы измерения согласно вашему лабораторному протоколу."
        )
        X6 = st.number_input(
            "X6: Уровень экспрессии miR-221 (I триместр)",
            min_value=0.0, step=0.0001, format="%.6f", value=0.0,
            help="Введите измеренное значение; единицы измерения согласно вашему лабораторному протоколу."
        )

    D = compute_D(X1, X2, X3, X4, X5, X6)
    lbl = risk_label(D)

    st.markdown("---")
    st.subheader("Результат")
    if D > 0:
        st.error(f"**{lbl}**  \nСчёт D = **{D:.3f}** (порог 0)")
    else:
        st.success(f"**{lbl}**  \nСчёт D = **{D:.3f}** (порог 0)")

    with st.expander("Показать вклад каждого признака"):
        dfc = contribution_table(X1, X2, X3, X4, X5, X6)
        st.dataframe(dfc, use_container_width=True)
