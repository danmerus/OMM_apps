# OMM apps
To run locally: `streamlit run %appname%.py`

## treatment_choice.py — выбор тактики лечения

The app reads only `data/treatment_choice_model.json`. To retrain on a new Excel file from the clinicians:

```
pip install streamlit scikit-learn openpyxl matplotlib
python treatment_choice_train.py "ИСХОДЫ ДО ананмнез ИГХ шейка версия 21.11.2026.xlsx"
```

This rewrites `data/treatment_choice_model.json` and saves the cross-validated metrics locally in
`treatment_choice_metrics/` (`report.txt` with the classification report, `metrics.png` with the report and confusion matrix,
`feature_association.csv`); `--out-dir` picks another folder. The app shows only the recommendation.
Commit only the JSON: **never commit the Excel file, it contains surnames.**

Expected Excel layout: first sheet = surgery group, second = observation group; row 1 = column names;
column A = surname, its fill colour = outcome (green favourable, red unfavourable). Columns are matched
by name, so their order may differ between sheets; if a column is renamed in only one sheet, training
stops and lists the mismatch (add the old→new name to `ALIASES`).

How it decides: one model (logistic regression on the 4 features most associated with the outcome)
estimates the chance of a favourable course. At ≥ 50 % the app recommends observation, otherwise surgery.
In the 21.11.2026 data the outcome depends on p16 / Ki-67 in the cervical epithelium and not on the
tactic, so the data cannot say which tactic is better for a given patient — only how risky her course is.
