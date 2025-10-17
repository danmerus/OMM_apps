# app.py
# Streamlit app: Прогноз риска летального исхода в неонатальном периоде
# Запуск: streamlit run app.py

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Риск в неонатальном периоде (MCDA, sFGR)",
    page_icon="🍼",
    layout="centered",
)

st.title("🍼 Прогноз риска в неонатальном периоде")
st.caption(
    "Метод для недоношенных монохориальных диамниотических близнецов с синдромом селективной задержки роста плода (sFGR). "
    "Расчет диагностического индекса (DI) по заданной формуле и стратификация риска."
)

with st.expander("Описание модели / формула"):
    st.markdown(
        """
**Формула DI:**

\\[
\\text{DI} = 19.5 \\cdot X_1 + 19.2 \\cdot X_2 - 2.2 \\cdot X_3 + 25.0 \\cdot X_4 + 15.7 \\cdot X_5 - 0.81
\\]

**Где:**
- **X₁** — внутриутробная гибель моноди близнеца из пары: есть = 1, нет = 0  
- **X₂** — преждевременный разрыв плодных оболочек: есть = 1, нет = 0  
- **X₃** — оценка по шкале Апгар на 1-й минуте жизни (0–10)  
- **X₄** — острая плацентарная недостаточность (по гистологии): есть = 1, нет = 0  
- **X₅** — интервиллузит (по гистологии): есть = 1, нет = 0  
- **–0.81** — постоянная

**Порог:**
- DI **> 0.875** → **высокий риск**  
- DI **< 0.875** → **низкий риск**  
- DI **= 0.875** → на пороге (граничное значение)
        """
    )

st.divider()

# --- Ввод данных ---
st.subheader("Ввод клинико-гистологических признаков")

def yes_no_to_int(label: str, key: str):
    choice = st.radio(label, ["Нет (0)", "Есть (1)"], horizontal=True, key=key)
    return 1 if "Есть" in choice else 0

col1, col2 = st.columns(2)
with col1:
    x1 = yes_no_to_int("Внутриутробная гибель моноди близнеца (X₁)", "x1")
    x2 = yes_no_to_int("Преждевременный разрыв оболочек (X₂)", "x2")
    x4 = yes_no_to_int("Острая плацентарная недостаточность (X₄)", "x4")
with col2:
    x5 = yes_no_to_int("Интервиллузит (X₅)", "x5")
    x3 = st.number_input(
        "Оценка по шкале Апгар на 1-й минуте (X₃)", min_value=0.0, max_value=10.0, step=0.5, value=7.0
    )

with st.form("calc_form"):
    submitted = st.form_submit_button("Рассчитать DI")

THRESHOLD = 0.875

def compute_di(x1, x2, x3, x4, x5):
    return 19.5 * x1 + 19.2 * x2 - 2.2 * x3 + 25.0 * x4 + 15.7 * x5 - 0.81

if submitted:
    di = compute_di(x1, x2, x3, x4, x5)

    # Классификация
    if di > THRESHOLD:
        risk_text = "Высокий риск"
        color_block = "error"
    elif di < THRESHOLD:
        risk_text = "Низкий риск"
        color_block = "success"
    else:
        risk_text = "Граничное значение (ровно 0.875)"
        color_block = "warning"

    st.subheader("Результат")
    st.metric("DI", f"{di:.3f}", help="Диагностический индекс согласно формуле")

    if color_block == "error":
        st.error(f"🧮 {risk_text} (порог = {THRESHOLD})")
    elif color_block == "success":
        st.success(f"🧮 {risk_text} (порог = {THRESHOLD})")
    else:
        st.warning(f"🧮 {risk_text} (порог = {THRESHOLD})")

    # Вклад факторов (таблица)
    contrib = {
        "Фактор": [
            "X₁: Внутриутробная гибель моноди близнеца",
            "X₂: Преждевременный разрыв оболочек",
            "X₃: Апгар (1 мин)",
            "X₄: Острая плацентарная недостаточность",
            "X₅: Интервиллузит",
            "Константа",
        ],
        "Значение": [x1, x2, x3, x4, x5, -0.81],
        "Коэффициент": [19.5, 19.2, -2.2, 25.0, 15.7, 1.0],
        "Вклад в DI": [
            19.5 * x1,
            19.2 * x2,
            -2.2 * x3,
            25.0 * x4,
            15.7 * x5,
            -0.81,
        ],
    }
    df = pd.DataFrame(contrib)

    with st.expander("Показать вклад факторов"):
        st.dataframe(df.style.format({"Значение": "{:.2f}", "Коэффициент": "{:.2f}", "Вклад в DI": "{:.3f}"}), use_container_width=True)

st.divider()
st.caption(
    "⚠️ Дисклеймер: результат носит вспомогательный характер и не заменяет клиническое решение врача. "
    "Используйте в сочетании с клинической оценкой и локальными протоколами."
)
