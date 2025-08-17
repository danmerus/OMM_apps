# app.py
import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Неонатальный риск (TTTS)", layout="centered")

st.title("Оценка риска летального исхода (неонатальный период)")
st.caption("Для недоношенных монохориальных диамниотических близнецов после фето-фетального трансфузионного синдрома (ФФТС)")

THRESHOLD = 0.4  # порог P

def compute_di(x1:int, x2:int, x3:float, x4:float) -> float:
    # DI = 2.679*X1 - 1.299*X2 + 0.218*X3 + 0.536*X4 - 19.669
    return 2.679 * x1 - 1.299 * x2 + 0.218 * x3 + 0.536 * x4 - 19.669

def logistic(di: float) -> float:
    return 1.0 / (1.0 + math.exp(-di))

def classify(p: float, thr: float) -> str:
    return "Высокий риск" if p > thr else "Низкий риск"

def parse_int(s, name, min_v=None, max_v=None):
    if s is None or s.strip() == "":
        return None, f"Поле «{name}» пустое."
    try:
        v = int(s.strip())
    except Exception:
        return None, f"Поле «{name}» должно быть целым числом."
    if min_v is not None and v < min_v:
        return None, f"«{name}» должно быть ≥ {min_v}."
    if max_v is not None and v > max_v:
        return None, f"«{name}» должно быть ≤ {max_v}."
    return v, None

def parse_float(s, name, min_v=None, max_v=None):
    if s is None or s.strip() == "":
        return None, f"Поле «{name}» пустое."
    try:
        v = float(s.replace(",", "."))
    except Exception:
        return None, f"Поле «{name}» должно быть числом."
    if min_v is not None and v < min_v:
        return None, f"«{name}» должно быть ≥ {min_v}."
    if max_v is not None and v > max_v:
        return None, f"«{name}» должно быть ≤ {max_v}."
    return v, None

st.subheader("Ввод параметров пациента")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        # selectbox с пустым состоянием
        x1_opt = st.selectbox(
            "Признаки материнской мальперфузии",
            options=["— выберите —", "Нет (0)", "Есть (1)"],
            index=0,
        )
        x2_str = st.text_input(
            "Аpgar на 10-й минуте (баллы)",
            value="", placeholder="0–10 (целое)"
        )
    with col2:
        x3_str = st.text_input(
            "Хлор (ммоль/л), 1–6 часов жизни",
            value="", placeholder="например, 100.0"
        )
        x4_str = st.text_input(
            "Лактат (ммоль/л), 1–6 часов жизни",
            value="", placeholder="например, 2.0"
        )

    submitted = st.form_submit_button("Рассчитать риск")

if submitted:
    errors = []

    # X1
    if x1_opt == "— выберите —":
        x1 = None
        errors.append("Выберите значение для «Признаки материнской мальперфузии».")
    else:
        x1 = 1 if "Есть" in x1_opt else 0

    # X2, X3, X4
    x2, err = parse_int(x2_str, "Апгар 10 мин", min_v=0, max_v=10);  errors += [e for e in [err] if e]
    x3, err = parse_float(x3_str, "Хлор (ммоль/л)", min_v=0.0);      errors += [e for e in [err] if e]
    x4, err = parse_float(x4_str, "Лактат (ммоль/л)", min_v=0.0);    errors += [e for e in [err] if e]

    if errors:
        st.error("Проверьте поля:\n\n- " + "\n- ".join(errors))
    else:
        di = compute_di(int(x1), int(x2), float(x3), float(x4))
        p = logistic(di)
        verdict = classify(p, THRESHOLD)

        st.subheader("Результаты")
        c1, c2, c3 = st.columns(3)
        # c1.metric("DI", f"{di:.3f}")
        # c2.metric("P (вероятность)", f"{p:.2%}")
        # c3.metric("Порог", f"{THRESHOLD:.0%}")

        st.progress(min(max(p, 0.0), 1.0))
        st.markdown(
            f"**Итог:** <span style='font-size:1.15rem; font-weight:600;'>{verdict}</span>",
            unsafe_allow_html=True,
        )

        with st.expander("Проверка используемых значений"):
            st.json(
                {
                    "X1 (мальперфузия)": int(x1),
                    "X2 (Apgar 10 мин)": int(x2),
                    "X3 (Хлор, ммоль/л)": float(x3),
                    "X4 (Лактат, ммоль/л)": float(x4),
                    "DI": round(di, 6),
                    "P": round(p, 6),
                }
            )
