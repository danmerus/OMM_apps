import json
import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Model file written by treatment_choice_train.py
MODEL_PATH = Path(__file__).resolve().parent / "data" / "treatment_choice_model.json"
BORDERLINE = 0.15   # closer than this to the threshold -> show "borderline" warning

st.set_page_config(
    page_title="Выбор тактики лечения",
    page_icon="🏥",
    layout="wide",
)


@st.cache_data
def load_model() -> dict:
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


def confusion_chart(cm: list[list[int]]) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=cm, x=["0", "1"], y=["0", "1"], colorscale="Greens", zmin=0,
        text=cm, texttemplate="%{text}", textfont=dict(size=22),
        hovertemplate="Истина: %{y}<br>Прогноз: %{x}<br>Пациентов: %{z}<extra></extra>",
    ))
    fig.update_layout(
        title="Confusion matrix",
        xaxis=dict(title="Predicted", type="category"),
        yaxis=dict(title="True", type="category", autorange="reversed"),
        height=380, width=440, margin=dict(t=50, b=10),
    )
    return fig


# ── UI ───────────────────────────────────────────────────────────────────────

st.title("🏥 Система поддержки выбора тактики лечения")

if not MODEL_PATH.exists():
    st.error("Модель не найдена. Запустите `python treatment_choice_train.py <файл.xlsx>` и загрузите "
             "`data/treatment_choice_model.json` в репозиторий.")
    st.stop()

model = load_model()
thr = model["threshold"]
feats = model["features"]

st.caption(
    "Программа оценивает вероятность благоприятного течения по маркерам пациентки. "
    "Если благоприятное течение вероятно — рекомендуется наблюдательная тактика, "
    "если нет — хирургическая."
)

tab_pred, tab_metrics, tab_about = st.tabs(["🔍 Рекомендация", "📊 Метрики модели", "📈 Признаки и данные"])

# ── Tab 1: recommendation ────────────────────────────────────────────────────
with tab_pred:
    st.subheader("Данные пациентки")
    values = {}
    cols = st.columns(2)
    for i, f in enumerate(feats):
        with cols[i % 2]:
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

    st.caption(f"Модель обучена на данных {model['n_patients']} пациенток. "
               "Рекомендация не заменяет клиническое решение врача.")

# ── Tab 2: metrics ───────────────────────────────────────────────────────────
with tab_metrics:
    m = model["metrics"]
    st.subheader("Качество модели на кросс-валидации")
    st.write(
        f"Проверка методом leave-one-out: каждая из {model['n_patients']} пациенток оценена моделью, "
        "обученной на остальных, — то есть на пациентке, которую модель не видела. "
        "Отбор признаков тоже повторялся внутри каждой проверки."
    )
    st.markdown("**Группа 0** — неблагоприятный исход, **Группа 1** — благоприятный исход.")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.code("Classification report:\n" + m["report_text"], language=None)
        st.metric("ROC AUC", f"{m['auc']:.2f}")
    with c2:
        st.plotly_chart(confusion_chart(m["confusion"]), width="content")

    st.subheader("Что программа рекомендовала бы пациенткам из выборки")
    rec = pd.DataFrame(m["recommendations"]).rename(columns={
        "group": "Фактическая тактика", "outcome": "Исход",
        "observation": "Рекомендовано наблюдение", "surgery": "Рекомендована операция",
    })
    st.dataframe(rec, hide_index=True, width="stretch")

    st.info(
        "Почему метрики такие высокие: в этих данных p16 и Ki-67 в эпителии шейки матки полностью "
        "разделяют исходы — у всех пациенток с низкими значениями исход благоприятный, с высокими — "
        "неблагоприятный, в обеих группах лечения. Выборка небольшая, поэтому точность нужно "
        "подтвердить на новых пациентках."
    )

# ── Tab 3: features and data ─────────────────────────────────────────────────
with tab_about:
    st.subheader("Признаки, которые использует модель")
    st.dataframe(pd.DataFrame([{
        "Признак": f["name"],
        "Влияние": "↓ снижает шанс благоприятного исхода" if f["coef"] < 0 else "↑ повышает шанс благоприятного исхода",
        "Вес": round(f["coef"], 2),
        "Диапазон в данных": f"{_fmt(f['min'])}–{_fmt(f['max'])}",
        "Медиана": _fmt(round(f["median"], 2)),
    } for f in feats]), hide_index=True, width="stretch")
    st.caption("Вес — коэффициент логистической регрессии на стандартизованных значениях: "
               "чем больше по модулю, тем сильнее признак влияет на прогноз.")

    st.subheader("Связь каждого признака из таблицы с исходом")
    st.caption("Сила связи — AUC одного признака: 0,5 — связи нет, 1 — признак сам по себе полностью "
               f"разделяет исходы. В модель вошли {len(feats)} самых сильных.")
    st.dataframe(pd.DataFrame([{
        "Признак": r["name"],
        "Сила связи (AUC)": round(max(r["auc"], 1 - r["auc"]), 3),
        "Чем выше значение": "тем чаще благоприятный исход" if r["auc"] >= 0.5 else "тем чаще неблагоприятный исход",
    } for r in model["univariate_auc"]]), hide_index=True, width="stretch", height=400)

    st.subheader("Данные")
    st.write(f"Файл: `{model['source_file']}` · обучено {model['trained_at']}")
    st.dataframe(pd.DataFrame([{
        "Группа": g["name"], "Пациенток": g["total"],
        "Благоприятный исход": g["good"], "Неблагоприятный исход": g["total"] - g["good"],
    } for g in model["groups"]]), hide_index=True)
