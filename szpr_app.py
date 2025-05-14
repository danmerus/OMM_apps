import streamlit as st
import numpy as np

st.set_page_config(page_title="OMM – прогноз ССЗРП МХДА", page_icon="🍼")

# ──────────────────────────  HEADER  ──────────────────────────
st.header("OMM ПРОГНОЗ СЗРП МХДА")

st.markdown(
"""
**Цель**  
1. На основании данных I-го триместра (11 – 13 ⁶/₇ недель) оценить риск
синдрома селективной задержки роста плода (ССЗРП).  
2. При высоком риске уточнить исход (гибель одного / двух плодов) по
пульсационному индексу (ПИ) венозного протока.
"""
)

# ──────────────────────────  INPUTS  ──────────────────────────
st.header("Ввод данных (I-й триместр)")

def to_float(val: str | None) -> float | None:
    """Преобразует строку в float или возвращает None, если пусто/не число."""
    try:
        return float(val) if val not in ("", None) else None
    except ValueError:
        return None

col1, col2 = st.columns(2)
with col1:
    ktr1 = to_float(st.text_input("КТР 1 (мм):"))
    tvp1 = to_float(st.text_input("ТВП 1 (мм):"))
with col2:
    ktr2 = to_float(st.text_input("КТР 2 (мм):"))
    tvp2 = to_float(st.text_input("ТВП 2 (мм):"))

tkr = st.radio(
    "Патологическая трикуспидальная регургитация (ТКР) хотя бы у одного плода:",
    options=[0, 1],
    format_func=lambda x: "Есть" if x == 1 else "Нет",
    horizontal=True,
)

all_entered = None not in (ktr1, ktr2, tvp1, tvp2)

# ──────────────────────────  STAGE 1  ──────────────────────────
st.subheader("1-й этап → риск ССЗРП")

if all_entered:
    Z = (
        2.75
        + 0.20 * (ktr1 - ktr2)
        + 0.71 * (tvp1 - tvp2)
        - 3.75 * min(tvp1, tvp2)
        + 2.27 * tkr
    )
    prob = 1 / (1 + np.exp(-Z))

    # вывод без процентного виджета
    st.write(f"Вероятность ССЗРП: **{prob:.3f}**")

    if prob > 0.15:
        st.error("⚠️ Высокий риск ССЗРП")
    else:
        st.success("Низкий риск ССЗРП")
else:
    st.info("Введите все четыре числовых показателя выше, чтобы рассчитать риск.")

# ──────────────────────────  STAGE 2  ──────────────────────────
st.subheader("2-й этап → прогноз исхода (только если риск высок)")

if all_entered and (1 / (1 + np.exp(-(2.75 + 0.20 * (ktr1 - ktr2)
        + 0.71 * (tvp1 - tvp2) - 3.75 * min(tvp1, tvp2) + 2.27 * tkr))) > 0.15):
    pi_val = to_float(
        st.text_input("Максимальный ПИ в венозном протоке (у плодов):")
    )
    if pi_val is not None:
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
else:
    st.info("Заполните ПИ, если риск ССЗРП оказался высоким.")
