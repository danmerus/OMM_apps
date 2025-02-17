import streamlit as st
import numpy as np
import joblib

groups = ['Высокий риск рецидива эндометриоза', 'Низкий риск рецидива эндометриоза']

model = joblib.load("model.joblib")

st.title("ОММ ENDOMETRIOSIS RECURRENCE")

result_styles = {
    0: "background-color: #ff4d4d; color: white; padding: 15px; border-radius: 10px;",   
    1: "background-color: #66ff66; color: black; padding: 15px; border-radius: 10px;"
}

st.write("Введите значения:")

feature_list = [
    'Возраст', 'Рост ', 'Вес',
    'Наличие заболеваний ЖКТ', 'Жалобы на диаррею', 'Жалобы на запоры',
    'Жалобы на вздутие живота', 'Жалобы на боль в животе',
    'Длительность с момента последней операции, лет',
    'Общая бактериальная масса, Lg (ГЭ/Г)', 'Доля нормальной микробиоты, %',
    'Разнообразие, количество таксонов, шт.',
    'Bifidobacterium spp, Lg (ГЭ/Г)', 'Lactobacillaceae, Lg (ГЭ/Г)',
    'Firmicutes/Bacteroidetes, соотношение', 'Дрожжевые грибы,  Lg (ГЭ/Г)',
    'Условно-патогенная микробиота, %', 'Патогенные представители, Lg (ГЭ/Г)',
    'Общая бактериальная масса вагинальной микробиоты, Lg (ГЭ/Г)',
    'Lactobacillus spp, количество, Lg (ГЭ/Г)',
    'Сем. Enterobacteriaceae, Lg (ГЭ/Г)', 'Streptococcus spp, Lg (ГЭ/Г)',
    'Staphylococcus spp, Lg (ГЭ/Г)',
    'Gardnerella vaginalis + Prevotella bivia + Porphyromonas spp, Lg (ГЭ/Г)',
    'Eubacterium spp, Lg (ГЭ/Г)',
    'Megasphaera spp + Veilbnella spp + Dialister spp, Lg (ГЭ/Г)',
    'Lachnobacterium spp + Clostridium spp, Lg (ГЭ/Г)',
    'Mobiluncus spp + Corynebacterium spp, Lg (ГЭ/Г)',
    'Atopobium vaginae, Lg (ГЭ/Г)',
    'Ureaplasma (urealiticum + parvum), Lg (ГЭ/Г)'
]

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
