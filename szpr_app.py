import streamlit as st
import numpy as np

st.set_page_config(page_title="OMM – прогноз ССЗРП МХДА", page_icon="🍼")

# ──────────────────────────  HEADER  ──────────────────────────
st.header("OMM ПРОГНОЗ СЗРП МХДА")

st.markdown(
"""
**Цель**  
1. По данным I-го триместра (11 – 13 ⁶/₇ недель) оценить риск синдрома
селективной задержки роста плода (ССЗРП).  
2. При высоком риске уточнить исход беременности по пульсационному
индексу (ПИ) венозного протока.
"""
)

# ──────────────────────────  INPUTS  ──────────────────────────
st.header("Ввод данных (I-й триместр)")

def to_float(txt: str | None) -> float | None:
    """Строка → float, либо None, если пусто/не число."""
    try:
        return float(txt) if txt not in ("", None) else None
    except ValueError:
        return None

c1, c2 = st.columns(2)
with c1:
    ktr1 = st.text_input("КТР 1, мм")
    tvp1 = st.text_input("ТВП 1, мм")
with c2:
    ktr2 = st.text_input("КТР 2, мм")
    tvp2 = st.text_input("ТВП 2, мм")

tkr = st.radio(
    "Патологическая трикуспидальная регургитация (ТКР) у хотя бы одного плода:",
    options=[0, 1],
    format_func=lambda x: "Есть" if x else "Нет",
    horizontal=True,
)

# ────────────────── 1-й ЭТАП ──────────────────
st.subheader("1-й этап → риск ССЗРП")

if st.button("Рассчитать риск ССЗРП"):
    vals = list(map(to_float, (ktr1, ktr2, tvp1, tvp2)))
    if None in vals:                          # не заполнили все поля
        st.warning("⚠️ Введите все четыре числовые величины.")
        st.stop()

    k1, k2, v1, v2 = vals
    Z = 2.75 + 0.20 * (k1 - k2) + 0.71 * (v1 - v2) - 3.75 * min(v1, v2) + 2.27 * tkr
    prob = 1 / (1 + np.exp(-Z))

    st.session_state["prob"] = prob          # сохраняем для второго этапа
    st.session_state["risk_high"] = prob > 0.15

    st.write(f"Вероятность ССЗРП: **{prob:.3f}**")
    if st.session_state["risk_high"]:
        st.error("⚠️ Высокий риск ССЗРП")
    else:
        st.success("Низкий риск ССЗРП")

# ────────────────── 2-й ЭТАП ──────────────────
if st.session_state.get("risk_high"):
    st.subheader("2-й этап → прогноз исхода")

    pi_txt = st.text_input("Максимальный ПИ венозного протока, ед.", key="pi_input")

    if st.button("Рассчитать исход"):
        pi_val = to_float(pi_txt)
        if pi_val is None:
            st.warning("⚠️ Введите числовое значение ПИ.")
            st.stop()

        if pi_val > 1.3:
            st.error(
                "Прогноз: вероятна гибель одного/двух плодов.\n\n"
                "👉 Рассмотрите коагуляцию сосудов пуповины меньшего плода."
            )
        else:
            st.success(
                "Прогноз: оба плода, вероятно, выживут.\n\n"
                "👉 Рекомендуется динамическое наблюдение."
            )
