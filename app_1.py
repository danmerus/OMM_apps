import streamlit as st
import numpy as np
import joblib

groups = ['Высокий риск рецидива эндометриоза', 'Низкий риск рецидива эндометриоза']

model = joblib.load("model_1.joblib")

st.title("ОММ ENDOMETRIOSIS RECURRENCE")

result_styles = {
    0: "background-color: #ff4d4d; color: white; padding: 15px; border-radius: 10px;",   
    1: "background-color: #66ff66; color: black; padding: 15px; border-radius: 10px;"
}

st.write("Введите значения показателей иммуногистохимии:")

feature_list = ['ER стромы очага (H-score)', 'ER желез очага (H-score)',
       'Bcl-2 стромы очага (H-score)', 'Bcl-2 желез очага (H-score)',
       'AKT стрмы очага %', 'AKT желез  очага %', 'PTEN  стромы очага %',
       'PTEN  желез очага %', 'VGEF стромы очага %', 'VGEF желез очага %',
       'р53 стромы %', 'р53 желез очага %']
boolean_features = [
    'Наличие заболеваний ЖКТ', 'Жалобы на диаррею',
    'Жалобы на запоры', 'Жалобы на вздутие живота',
    'Жалобы на боль в животе'
]

input_values = []
for feature_name in feature_list:
    if feature_name in boolean_features:
        checked = st.checkbox(feature_name, value=False)
        input_values.append(int(checked))
    else:
        numeric_val = st.number_input(feature_name, value=0.0)
        input_values.append(numeric_val)

if st.button("Рассчёт"):
    X_new = np.array([input_values])
    predicted_group = model.predict(X_new)[0]
    style = result_styles.get(predicted_group, "")
    result_html = f'<div style="{style}">{groups[predicted_group]}</div>'
    st.markdown(result_html, unsafe_allow_html=True)
