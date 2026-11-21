"""Train the model behind treatment_choice.py from the clinicians' Excel file.

Usage:
    python treatment_choice_train.py "ИСХОДЫ ДО ананмнез ИГХ шейка версия 21.11.2026.xlsx"

Writes data/treatment_choice_model.json (the only file the app needs) and saves
the cross-validated metrics locally in ./treatment_choice_metrics/ (change with
--out-dir): report.txt, metrics.png (report + confusion matrix), feature_association.csv.

Do not commit the Excel file (it contains patient surnames) or the metrics folder.

Excel layout expected:
  * the first two sheets are the surgery group and the observation group;
  * row 1 holds column names, column A holds the surname;
  * the outcome is the fill colour of column A: green = favourable, red = unfavourable.

What the model predicts: the chance of a favourable course. In this data the
outcome depends on the markers, not on the tactic (see README section), so the
app recommends observation when a favourable course is likely and surgery
otherwise.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import LeaveOneOut

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "data" / "treatment_choice_model.json"

N_FEATURES = 4      # inputs the model (and the app's form) uses; 4 pass a Bonferroni-corrected test on this data
THRESHOLD = 0.5     # favourable-course probability at or above which observation is recommended
C_REG = 1.0         # logistic-regression regularisation (smaller = stronger)

CLASS_NAMES = ["Неблагоприятный исход", "Благоприятный исход"]   # y = 0, y = 1

# Same field spelled differently between sheets or file versions -> one name.
ALIASES = {
    "Количество типов ВПЧ по данным мазка с шейки матки методом ПЦР РТ":
        "Количество типов ВПЧ по данным мазка с шейки матки методом ПЦР",
    "Роды в анамнезе": "Количество родов",
    "p16 в эпителии шейки макти, %": "p16 в эпителии шейки матки, %",
}
# Headers that only continue the previous column's name.
CONTINUATIONS = {"продолжительность"}

_THEME_SLOTS = ["lt1", "dk1", "lt2", "dk2", "accent1", "accent2", "accent3",
                "accent4", "accent5", "accent6", "hlink", "folHlink"]


# ── Excel reading ────────────────────────────────────────────────────────────

def _norm(text) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()


def _theme_colours(wb) -> dict[int, str]:
    xml = wb.loaded_theme.decode("utf8") if isinstance(wb.loaded_theme, bytes) else (wb.loaded_theme or "")
    out = {}
    for i, slot in enumerate(_THEME_SLOTS):
        m = re.search(rf"<a:{slot}>.*?(?:srgbClr val|lastClr)=\"([0-9A-Fa-f]{{6}})\"", xml, re.S)
        if m:
            out[i] = m.group(1).upper()
    return out


def _outcome_from_fill(cell, theme: dict[int, str]) -> tuple[int | None, str]:
    """Fill colour -> 1 (green, favourable) / 0 (red, unfavourable) / None (anything else)."""
    fc = cell.fill.fgColor
    if fc.type == "theme":
        rgb = theme.get(fc.theme)
    elif fc.type == "rgb":
        rgb = str(fc.rgb)[-6:].upper()
    else:
        rgb = None
    if not rgb or not re.fullmatch(r"[0-9A-F]{6}", rgb):
        return None, str(rgb)
    r, g, b = (int(rgb[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, sat, _ = colorsys.rgb_to_hsv(r, g, b)
    hue *= 360
    if sat < 0.2:                       # white / grey: no outcome marked
        return None, rgb
    if 70 <= hue <= 170:
        return 1, rgb
    if hue <= 50 or hue >= 330:
        return 0, rgb
    return None, rgb


def _column_names(header_row) -> list[str | None]:
    names = []
    for i, h in enumerate(header_row):
        if h is None or not _norm(h):
            names.append(None)
            continue
        h = _norm(h)
        if h.lower() in CONTINUATIONS and i > 0 and header_row[i - 1] is not None:
            h = f"{_norm(header_row[i - 1])} - {h}"
        names.append(ALIASES.get(h, h))
    return names


def _to_float(v) -> float:
    if v is None:
        return np.nan
    if isinstance(v, str):
        v = v.strip().replace(",", ".")
    try:
        return float(v)
    except (TypeError, ValueError):
        return np.nan


def load_excel(path: Path) -> pd.DataFrame:
    """Both sheets as one table: one row per patient, feature columns + `_y` + `_group`.

    Columns are matched by name, so a different column order between sheets is fine.
    Surnames (column A) are not kept.
    """
    wb = openpyxl.load_workbook(path, data_only=True)
    if len(wb.worksheets) < 2:
        sys.exit("Ожидались два листа: хирургическая и наблюдательная тактика.")
    theme = _theme_colours(wb)

    frames, unknown = [], []
    for ws in wb.worksheets[:2]:
        names = _column_names([c.value for c in ws[1]])
        dup = sorted({n for n in names if n and names.count(n) > 1})
        if dup:
            sys.exit(f"Лист «{ws.title}»: повторяющиеся названия столбцов: {dup}")
        rows = []
        for r in range(2, ws.max_row + 1):
            cells = list(ws[r])
            if cells[0].value is None:
                continue
            y, colour = _outcome_from_fill(cells[0], theme)
            if y is None:
                unknown.append(f"«{ws.title}», строка {r}: цвет {colour}")
                continue
            row = {n: _to_float(cells[j].value) for j, n in enumerate(names) if j > 0 and n}
            row["_y"] = y
            row["_group"] = ws.title
            rows.append(row)
        frames.append(pd.DataFrame(rows))

    if unknown:
        sys.exit("Не удалось определить исход по цвету ячейки (ожидается зелёный или красный):\n  "
                 + "\n  ".join(unknown))

    a, b = (set(f.columns) for f in frames)
    if a != b:
        sys.exit("Названия столбцов на листах не совпадают.\n"
                 f"  Только на первом листе: {sorted(a - b)}\n"
                 f"  Только на втором листе: {sorted(b - a)}\n"
                 "Переименуйте столбцы или добавьте соответствие в ALIASES.")
    return pd.concat(frames, ignore_index=True)[frames[0].columns]


# ── Model ────────────────────────────────────────────────────────────────────

def rank_features(X: pd.DataFrame, y: np.ndarray) -> list[tuple[str, float]]:
    """Features ordered by how well each one alone separates the outcomes (|AUC − 0.5|)."""
    scored = []
    for f in X.columns:
        col = X[f]
        if col.nunique(dropna=True) < 2:
            continue
        auc = roc_auc_score(y, col.fillna(col.median()))
        scored.append((f, float(auc)))
    return sorted(scored, key=lambda t: abs(t[1] - 0.5), reverse=True)


class Model:
    """Median imputation -> standardisation -> logistic regression on the chosen features."""

    def __init__(self, features: list[str]):
        self.features = features

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "Model":
        Z = X[self.features]
        self.median = Z.median()
        Z = Z.fillna(self.median)
        self.mean = Z.mean()
        self.scale = Z.std(ddof=0).replace(0, 1.0)
        self.lr = LogisticRegression(C=C_REG, max_iter=10000).fit((Z - self.mean) / self.scale, y)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        Z = X[self.features].fillna(self.median)
        return self.lr.predict_proba((Z - self.mean) / self.scale)[:, 1]


def cross_validate(X: pd.DataFrame, y: np.ndarray, k: int) -> np.ndarray:
    """Leave-one-out: each patient is predicted by a model that never saw them.
    Feature choice is repeated inside every fold, so it cannot peek at the patient either."""
    oof = np.zeros(len(y))
    for tr, te in LeaveOneOut().split(X, y):
        feats = [f for f, _ in rank_features(X.iloc[tr], y[tr])[:k]]
        oof[te] = Model(feats).fit(X.iloc[tr], y[tr]).predict_proba(X.iloc[te])
    return oof


def _input_kind(col: pd.Series) -> str:
    vals = set(col.dropna().unique())
    if vals <= {0.0, 1.0}:
        return "binary"
    if all(float(v).is_integer() for v in vals) and col.max() - col.min() <= 20:
        return "integer"
    return "continuous"


def save_metrics_png(report_text: str, note: str, cm: np.ndarray, path: Path) -> bool:
    """One picture: classification report on top, confusion matrix below."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен — картинка не сохранена (pip install matplotlib).")
        return False
    # Lay out in inches: measure the two text blocks, then put the matrix under them.
    W, LEFT, GAP = 5.6, 0.25, 0.2
    fig = plt.figure(figsize=(W, 8), dpi=130)
    t_report = fig.text(0, 0, "Classification report:\n" + report_text.rstrip("\n"),
                        family="monospace", fontsize=9, va="top", ha="left")
    t_note = fig.text(0, 0, note, fontsize=8, color="#555", va="top", ha="left")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    h_report = t_report.get_window_extent(renderer).height / fig.dpi
    h_note = t_note.get_window_extent(renderer).height / fig.dpi
    matrix_h = 3.3                                   # height of the matrix itself
    H = GAP + h_report + GAP + h_note + 0.55 + matrix_h + 0.6
    fig.set_figheight(H)
    y = H - GAP
    t_report.set_position((LEFT / W, y / H))
    y -= h_report + GAP
    t_note.set_position((LEFT / W, y / H))
    ax = fig.add_axes([0.8 / W, 0.6 / H, 3.4 / W, matrix_h / H])
    im = ax.imshow(cm, cmap="Greens", vmin=0, aspect="auto")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=13)
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["0", "1"]); ax.set_yticklabels(["0", "1"])
    ax.set_xlabel("Predicted"); ax.set_ylabel("True"); ax.set_title("Confusion matrix")
    fig.colorbar(im, cax=fig.add_axes([4.45 / W, 0.6 / H, 0.17 / W, matrix_h / H]))
    fig.savefig(path, bbox_inches="tight", pad_inches=0.15, facecolor="white")
    plt.close(fig)
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("excel", type=Path, help="Excel-файл с данными пациентов")
    ap.add_argument("--out-dir", type=Path, default=Path("treatment_choice_metrics"),
                    help="папка для метрик (отчёт, матрица ошибок, связь признаков с исходом)")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    def say(text: str = "") -> None:
        print(text)
        lines.append(text)

    df = load_excel(args.excel)
    features = [c for c in df.columns if not c.startswith("_")]
    X, y = df[features], df["_y"].to_numpy()
    trained_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    say(f"Файл: {args.excel.name}")
    say(f"Обучено: {trained_at}")
    say(f"Пациентов: {len(df)}, признаков в файле: {len(features)}")
    by_group = (df.groupby("_group", sort=False)["_y"]
                  .agg(total="size", good="sum").reset_index())
    for _, g in by_group.iterrows():
        say(f"  {g['_group']}: {g['total']} (благоприятный исход {g['good']}, неблагоприятный {g['total'] - g['good']})")

    # Cross-validated quality (what the report and confusion matrix show)
    oof = cross_validate(X, y, N_FEATURES)
    pred = (oof >= THRESHOLD).astype(int)
    report_text = classification_report(y, pred, target_names=[f"Группа {i}" for i in (0, 1)],
                                        digits=2, zero_division=0)
    cm = confusion_matrix(y, pred, labels=[0, 1])
    auc = float(roc_auc_score(y, oof))

    say("\nКросс-валидация (leave-one-out): каждый пациент оценён моделью, которая его не видела.")
    say(f"Группа 0 — {CLASS_NAMES[0].lower()}, Группа 1 — {CLASS_NAMES[1].lower()}.\n")
    say("Classification report:")
    say(report_text)
    say(f"ROC AUC: {auc:.3f}")
    say("\nConfusion matrix (строки — факт, столбцы — прогноз):")
    say(pd.DataFrame(cm, index=["факт 0", "факт 1"], columns=["прогноз 0", "прогноз 1"]).to_string())

    # What the app would have recommended for each patient (cross-validated)
    rec = np.where(pred == 1, "Наблюдение", "Хирургия")
    outcome = pd.Series(np.where(y == 1, "благоприятный", "неблагоприятный"), name="Исход")
    table = pd.crosstab([df["_group"].rename("Тактика"), outcome], pd.Series(rec, name="Рекомендация"))
    say("\nРекомендация программы (по кросс-валидации) в разрезе фактической тактики и исхода:")
    say(table.to_string())

    # Final model on all patients
    ranked = rank_features(X, y)
    chosen = [f for f, _ in ranked[:N_FEATURES]]
    model = Model(chosen).fit(X, y)
    coefs = dict(zip(chosen, model.lr.coef_[0]))

    say(f"\nПризнаки модели (вес > 0 — повышает шанс благоприятного исхода), порог {THRESHOLD:.0%}:")
    for f in chosen:
        say(f"  {coefs[f]:+.2f}  {f}")

    # Metrics stay on this computer; the app gets only the model.
    report_path = args.out_dir / "report.txt"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assoc_path = args.out_dir / "feature_association.csv"
    pd.DataFrame([{
        "Признак": f,
        "Сила связи (AUC)": round(max(a, 1 - a), 3),
        "Чем выше значение": "тем чаще благоприятный исход" if a >= 0.5 else "тем чаще неблагоприятный исход",
        "В модели": "да" if f in chosen else "",
    } for f, a in ranked]).to_csv(assoc_path, index=False, encoding="utf-8-sig")

    bundle = {
        "trained_at": trained_at,
        "source_file": args.excel.name,
        "n_patients": int(len(df)),
        "threshold": THRESHOLD,
        "intercept": float(model.lr.intercept_[0]),
        "features": [{
            "name": f,
            "kind": _input_kind(X[f]),
            "coef": float(coefs[f]),
            "mean": float(model.mean[f]),
            "scale": float(model.scale[f]),
            "median": float(model.median[f]),
            "min": float(X[f].min()),
            "max": float(X[f].max()),
        } for f in chosen],
    }
    MODEL_PATH.parent.mkdir(exist_ok=True)
    MODEL_PATH.write_text(json.dumps(bundle, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\nSaved: {MODEL_PATH}")
    print(f"Saved: {report_path}")
    print(f"Saved: {assoc_path}")
    png_path = args.out_dir / "metrics.png"
    note = (f"Группа 0 — {CLASS_NAMES[0].lower()}, Группа 1 — {CLASS_NAMES[1].lower()}.\n"
            f"Кросс-валидация leave-one-out, {len(df)} пациенток.")
    if save_metrics_png(report_text, note, cm, png_path):
        print(f"Saved: {png_path}")


if __name__ == "__main__":
    main()
