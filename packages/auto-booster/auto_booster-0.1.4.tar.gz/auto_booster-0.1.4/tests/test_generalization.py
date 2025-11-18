import pandas as pd

from auto_boost.cli import AutoBoost, infer_problem_type


def make_autoboost():
    return AutoBoost(
        estimator=object(),
        model_type="classification",
        metric="accuracy",
        folds=2,
        random_state=0,
        early_stopping_rounds=0,
        verbose=0,
    )


def test_infer_problem_type_classification():
    series = pd.Series(["cat", "dog", "cat", "bird"])
    assert infer_problem_type(series) == "classification"


def test_infer_problem_type_regression():
    series = pd.Series([0.1, 0.2, 0.35, 0.4])
    assert infer_problem_type(series) == "regression"


def test_fill_missing_keeps_high_cardinality_strings():
    df = pd.DataFrame(
        {
            "high_card": ["a", "b", "c", None],
            "numeric": [1.0, None, 3.0, 4.0],
        }
    )
    model = make_autoboost()
    filled = model.fill_missing_values(df)
    assert "high_card" in filled.columns
    assert filled["high_card"].isna().sum() == 0
    assert filled["numeric"].isna().sum() == 0
