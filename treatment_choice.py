import json
import math
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

# Model file written by treatment_choice_train.py
MODEL_PATH = Path(__file__).resolve().parent / "data" / "treatment_choice_model.json"
BORDERLINE = 0.15   # closer than this to the threshold -> show "borderline" warning

st.set_page_config(
    page_title="ENDOCIN TACTICS",
    page_icon="🏥",
    layout="wide",
)


def load_model() -> dict:
    # Read on every run, not cached: Streamlit Cloud keeps the app process running
    # when a new model file is pushed, and a cache would keep serving the old model.
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def favourable_probability(model: dict, values: dict) -> float:
    """Chance of a favourable course (logistic regression stored as plain numbers)."""
    z = model["intercept"]
    for f in model["features"]:
        z += f["coef"] * (values[f["name"]] - f["mean"]) / f["scale"]
    return 1.0 / (1.0 + math.exp(-z))


def _fmt(x: float) -> str:
    return f"{x:g}"


def feature_input(f: dict):
    name, med = f["name"], f["median"]
    if f["kind"] == "binary":
        return float(st.selectbox(name, [0, 1], index=int(round(med)),
                                  format_func=lambda v: "Да" if v else "Нет", key=name))
    if f["kind"] == "integer":
        return float(st.number_input(name, min_value=0, value=int(round(med)), step=1, key=name))
    step = 1.0 if f["max"] - f["min"] > 50 else 0.1
    return float(st.number_input(name, min_value=0.0, value=float(med), step=step, key=name))


def probability_chart(p: float, threshold: float) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=[p * 100], y=[""], orientation="h",
        marker_color="#4CAF50" if p >= threshold else "#E57373",
        text=[f"{p * 100:.0f}%"], textposition="inside", insidetextanchor="end",
    ))
    fig.add_vline(x=threshold * 100, line_dash="dash", line_color="#555",
                  annotation_text=f"порог {threshold * 100:.0f}%", annotation_position="top")
    fig.update_layout(
        xaxis=dict(range=[0, 100], title="Вероятность благоприятного течения, %"),
        height=170, margin=dict(t=30, b=10, l=10, r=10), showlegend=False,
    )
    return fig


# ── UI ───────────────────────────────────────────────────────────────────────

st.title("ENDOCIN TACTICS", anchor=False)
st.subheader("Система поддержки принятия врачебных решений", anchor=False)
st.markdown("Выбор тактики ведения пациенток с наружным генитальным эндометриозом "
            "в сочетании с цервикальной интраэпителиальной неоплазией лёгкой степени")

if not MODEL_PATH.exists():
    st.error("Модель не найдена. Запустите `python treatment_choice_train.py <файл.xlsx>` и загрузите "
             "`data/treatment_choice_model.json` в репозиторий.")
    st.stop()

model = load_model()
thr = model["threshold"]
feats = model["features"]

st.caption(
    "Программа оценивает вероятность благоприятного течения по данным пациентки. "
    "Если благоприятное течение вероятно — рекомендуется наблюдательная тактика, "
    "если нет — хирургическая."
)

st.subheader("Данные пациентки")
values = {}
sections: dict[str, list[dict]] = {}
for f in feats:
    sections.setdefault(f.get("group", ""), []).append(f)
for section, items in sections.items():
    if section:
        st.markdown(f"#### {section}")
    cols = st.columns(3)
    for i, f in enumerate(items):
        with cols[i % 3]:
            values[f["name"]] = feature_input(f)

if st.button("🔮 Получить рекомендацию", type="primary"):
    p = favourable_probability(model, values)

    if p >= thr:
        st.success("### Рекомендация: **наблюдательная (выжидательная) тактика**")
    else:
        st.error("### Рекомендация: **хирургическая тактика**")
    st.plotly_chart(probability_chart(p, thr), width="stretch")

    if abs(p - thr) < BORDERLINE:
        st.warning("⚠️ Результат пограничный: вероятность близка к порогу. "
                   "Решение — за врачом с учётом всей клинической картины.")
    outside = [f for f in feats if not (f["min"] <= values[f["name"]] <= f["max"])]
    if outside:
        st.warning("Значения вне диапазона обучающих данных, прогноз менее надёжен: "
                   + "; ".join(f"{f['name']} (в данных {_fmt(f['min'])}–{_fmt(f['max'])})"
                               for f in outside))
