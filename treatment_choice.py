import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

MODELS_PATH = "data/models.pkl"
TOP_N_FEATURES = 20


@st.cache_resource
def load_models():
    return joblib.load(MODELS_PATH)


def make_prediction(models, feature_values: dict):
    """Return (p_surg, p_wait) given dict {feature_name: value}."""
    names = models["feature_names"]
    x = np.array([feature_values.get(n, 0.0) for n in names]).reshape(1, -1)
    p_surg = models["clf_surg"].predict_proba(x)[0][1]
    p_wait = models["clf_wait"].predict_proba(x)[0][1]
    return p_surg, p_wait


def prob_bar_chart(p_surg, p_wait):
    fig = go.Figure()
    colors = ["#2196F3", "#4CAF50"]
    labels = ["Хирургическое лечение", "Выжидательная тактика"]
    values = [p_surg, p_wait]
    for i, (lbl, val, col) in enumerate(zip(labels, values, colors)):
        fig.add_trace(go.Bar(
            x=[lbl], y=[val * 100],
            marker_color=col,
            text=[f"{val*100:.1f}%"],
            textposition="outside",
            name=lbl,
        ))
    fig.update_layout(
        yaxis=dict(range=[0, 110], title="Вероятность успешного исхода (%)"),
        xaxis_title="Метод лечения",
        showlegend=False,
        height=350,
        margin=dict(t=20, b=20),
    )
    return fig


def importance_chart(models):
    top = models["top_features"]
    imp_s = [models["imp_surg"][f] for f in top]
    imp_w = [models["imp_wait"][f] for f in top]
    short = [str(f)[:40] for f in top]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Хирургия", x=short, y=imp_s, marker_color="#2196F3"))
    fig.add_trace(go.Bar(name="Выжидание", x=short, y=imp_w, marker_color="#4CAF50"))
    fig.update_layout(
        barmode="group",
        xaxis_tickangle=-45,
        yaxis_title="Важность признака",
        height=400,
        margin=dict(t=10, b=160),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


# ── Streamlit UI ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Выбор тактики лечения",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Система поддержки выбора тактики лечения")
st.caption("Алгоритм рекомендует метод лечения на основе признаков пациента (HPV, микробиом, цитология, ИГХ)")

with st.spinner("Загрузка моделей..."):
    models = load_models()


tabs = st.tabs(["🔍 Прогноз для пациента", "📈 Важность признаков"])

# ── Tab 1: Prediction ────────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("Введите данные пациента")
    st.info(
        f"Показаны {TOP_N_FEATURES} наиболее значимых признаков. "
        "Для остальных признаков используются нулевые значения."
    )

    top_feats = models["top_features"]
    # Determine feature range hints from training data
    surg_df_feat = pd.DataFrame(models["X_surg"], columns=models["feature_names"])
    wait_df_feat = pd.DataFrame(models["X_wait"], columns=models["feature_names"])
    combined_df = pd.concat([surg_df_feat, wait_df_feat])

    input_vals = {}
    cols_per_row = 4
    feat_groups = [top_feats[i:i+cols_per_row] for i in range(0, len(top_feats), cols_per_row)]

    for group in feat_groups:
        cols = st.columns(len(group))
        for col_widget, feat in zip(cols, group):
            feat_data = combined_df[feat].dropna()
            mn, mx = float(feat_data.min()), float(feat_data.max())
            med = float(feat_data.median())
            unique_vals = sorted(feat_data.unique())
            label = str(feat)[:35]

            with col_widget:
                if set(unique_vals).issubset({0.0, 1.0}):
                    # Binary feature → selectbox
                    choice = st.selectbox(label, options=[0, 1],
                                          format_func=lambda v: "Нет (0)" if v == 0 else "Да (1)",
                                          key=feat)
                    input_vals[feat] = float(choice)
                elif mx - mn <= 10 and len(unique_vals) <= 10:
                    # Few discrete values
                    choice = st.selectbox(label, options=[float(v) for v in unique_vals], key=feat)
                    input_vals[feat] = choice
                else:
                    # Continuous
                    val = st.number_input(label, min_value=float(mn), max_value=float(mx),
                                          value=float(med), step=float(max((mx-mn)/100, 0.1)),
                                          key=feat)
                    input_vals[feat] = val

    st.divider()

    if st.button("🔮 Получить рекомендацию", type="primary", use_container_width=True):
        full_input = {feat: input_vals.get(feat, 0.0) for feat in models["feature_names"]}
        p_surg, p_wait = make_prediction(models, full_input)

        st.subheader("Результат")
        res_col1, res_col2 = st.columns([2, 1])

        with res_col1:
            st.plotly_chart(prob_bar_chart(p_surg, p_wait), use_container_width=True)

        with res_col2:
            diff = abs(p_surg - p_wait)
            if p_surg >= p_wait:
                st.success("### ✅ Рекомендация: **Хирургическое лечение**")
                better, worse = "хирургического", "выжидательной тактики"
                bp, wp = p_surg, p_wait
            else:
                st.success("### ✅ Рекомендация: **Выжидательная тактика**")
                better, worse = "выжидательной тактики", "хирургического"
                bp, wp = p_wait, p_surg

            confidence = "высокая" if diff > 0.3 else "умеренная" if diff > 0.15 else "низкая"
            st.write(f"**Уверенность:** {confidence}")
            st.write(f"Вероятность успеха при {better}: **{bp*100:.1f}%**")
            st.write(f"Вероятность успеха при {worse}: **{wp*100:.1f}%**")

            if diff < 0.1:
                st.warning("⚠️ Разница невелика. Рекомендуется дополнительная клиническая оценка.")

            st.caption("*Рекомендация основана на данных 46 пациентов. "
                       "Не заменяет клиническое решение врача.*")

# ── Tab 2: Feature importance ────────────────────────────────────────────────
with tabs[1]:
    st.subheader(f"Топ-{TOP_N_FEATURES} важных признаков")
    st.plotly_chart(importance_chart(models), use_container_width=True)

    st.subheader("Все важности признаков")
    imp_df = pd.DataFrame({
        "Признак": models["feature_names"],
        "Важность (хирургия)": models["imp_surg"].values,
        "Важность (выжидание)": models["imp_wait"].values,
    }).sort_values("Важность (хирургия)", ascending=False).reset_index(drop=True)
    st.dataframe(imp_df, use_container_width=True, height=400)
