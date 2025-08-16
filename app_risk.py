# app.py

import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Неонатальный риск (TTTS)", layout="centered")

st.title("Оценка риска летального исхода (неонатальный период)")
st.caption("Для недоношенных монохориальных диамниотических близнецов после фето-фетального трансфузионного синдрома (ФФТС)")

with st.expander("ℹ️ О методе и формулах"):
    st.markdown(
        r"""
**Диагностический индекс (DI):**
\[
DI = 2.679 \cdot X_1 \;-\; 1.299 \cdot X_2 \;+\; 0.218 \cdot X_3 \;+\; 0.536 \cdot X_4 \;-\; 19.669
\]
где  
- \(X_1\) — признаки материнской мальперфузии: есть = 1, нет = 0;  
- \(X_2\) — Апгар на 10-й минуте (баллы);  
- \(X_3\) — хлор в капиллярной крови (ммоль/л) в первые 1–6 часов жизни;  
- \(X_4\) — лактат в капиллярной крови (ммоль/л) в первые 1–6 часов жизни.

**Вероятность (стандартная логистическая функция):**
\[
P = \frac{1}{1 + e^{-DI}}
\]

Порог интерпретации: если \(P > 0.4\) — высокий риск, иначе — низкий риск.

> Примечание: в описании встречается запись \(P = 1/(1+e-D)\), что, вероятно, опечатка. Здесь по умолчанию используется стандарт \(1/(1+e^{-DI})\). При необходимости можно переключить вариант ниже.
""",
        unsafe_allow_html=False,
    )

with st.sidebar:
    st.header("Настройки")
    threshold = st.slider("Порог вероятности (P)", min_value=0.0, max_value=1.0, value=0.4, step=0.01)
    logistic_variant = st.radio(
        "Формула логистики",
        options=("P = 1 / (1 + exp(-DI)) [рекомендуется]", "P = 1 / (1 + exp(+DI))"),
        index=0,
    )
    st.markdown("---")
    st.markdown("**Дисклеймер:** инструмент не предназначен для постановки клинических диагнозов или решения о лечении.")

st.subheader("Ввод параметров пациента")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        x1_label = "Признаки материнской мальперфузии"
        x1_opt = st.selectbox(x1_label, options=["Нет (0)", "Есть (1)"])
        x1 = 1 if "Есть" in x1_opt else 0

        x2 = st.number_input(
            "Аpgar на 10-й минуте (баллы)",
            min_value=0, max_value=10, value=7, step=1,
            help="Целое число от 0 до 10",
        )
    with col2:
        x3 = st.number_input(
            "Хлор (ммоль/л), 1–6 часов жизни",
            min_value=50.0, max_value=140.0, value=100.0, step=0.1,
            help="Типичные значения в пределах ~95–110 ммоль/л",
        )
        x4 = st.number_input(
            "Лактат (ммоль/л), 1–6 часов жизни",
            min_value=0.0, max_value=20.0, value=2.0, step=0.1,
            help="Ед. изм.: ммоль/л",
        )

    submitted = st.form_submit_button("Рассчитать риск")

def compute_di(x1:int, x2:int, x3:float, x4:float) -> float:
    # DI = 2.679*X1 - 1.299*X2 + 0.218*X3 + 0.536*X4 - 19.669
    return 2.679 * x1 - 1.299 * x2 + 0.218 * x3 + 0.536 * x4 - 19.669

def logistic(di: float, variant: str) -> float:
    if "exp(+DI)" in variant:
        # Non-standard; provided only as a toggle in case исходный источник имел иной знак
        return 1.0 / (1.0 + math.exp(di))
    # Default (standard)
    return 1.0 / (1.0 + math.exp(-di))

def classify(p: float, thr: float) -> str:
    return "Высокий риск" if p > thr else "Низкий риск"

if submitted:
    di = compute_di(x1, int(x2), float(x3), float(x4))
    p = logistic(di, logistic_variant)
    verdict = classify(p, threshold)

    st.subheader("Результаты")
    c1, c2, c3 = st.columns(3)
    c1.metric("DI", f"{di:.3f}")
    c2.metric("P (вероятность)", f"{p:.2%}")
    c3.metric("Порог", f"{threshold:.0%}")

    # Visual hint
    st.progress(min(max(p, 0.0), 1.0))
    st.markdown(
        f"**Итог:** <span style='font-size:1.15rem; font-weight:600;'>{verdict}</span>",
        unsafe_allow_html=True,
    )

    with st.expander("Проверка используемых значений"):
        st.json(
            {
                "X1 (мальперфузия)": x1,
                "X2 (Apgar 10 мин)": int(x2),
                "X3 (Хлор, ммоль/л)": float(x3),
                "X4 (Лактат, ммоль/л)": float(x4),
                "DI": round(di, 6),
                "P": round(p, 6),
                "Порог": threshold,
                "Формула": logistic_variant,
            }
        )

st.markdown("---")
st.caption(
    "© Исследовательский инструмент. Не заменяет клиническое мышление и не является медицинским изделием. "
    "Решения о лечении принимаются специалистами с учётом полной клинической картины."
)

# Optional: simple batch mode via CSV
with st.expander("Загрузка CSV (пакетная оценка)"):
    st.write("Загрузите CSV со столбцами: malperf (0/1), apgar10 (0–10), chloride, lactate")
    file = st.file_uploader("CSV", type=["csv"])
    if file is not None:
        try:
            df = pd.read_csv(file)
            req = {"malperf", "apgar10", "chloride", "lactate"}
            if not req.issubset(df.columns):
                st.error(f"Отсутствуют обязательные столбцы: {sorted(list(req - set(df.columns)))}")
            else:
                df["DI"] = (
                    2.679 * df["malperf"].astype(float)
                    - 1.299 * df["apgar10"].astype(float)
                    + 0.218 * df["chloride"].astype(float)
                    + 0.536 * df["lactate"].astype(float)
                    - 19.669
                )
                if "exp(+DI)" in logistic_variant:
                    df["P"] = 1.0 / (1.0 + (df["DI"]).apply(math.exp))
                else:
                    df["P"] = 1.0 / (1.0 + (-df["DI"]).apply(math.exp))
                df["Class"] = df["P"].apply(lambda v: "Высокий риск" if v > threshold else "Низкий риск")
                st.dataframe(df.head(20))
                st.download_button(
                    "Скачать результаты (CSV)",
                    df.to_csv(index=False).encode("utf-8"),
                    file_name="risk_results.csv",
                    mime="text/csv",
                )
        except Exception as e:
            st.error(f"Ошибка чтения/обработки файла: {e}")
