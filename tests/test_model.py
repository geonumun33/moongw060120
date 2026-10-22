# test_model.py: model.py 자동화 테스트
# 실행: python -m pytest tests/test_model.py -q
#
# 테스트용 모델은 임시 폴더에 따로 만들어 쓰므로 models/focus_model.joblib을 건드리지 않는다.

import inspect
import os
import sys

import pytest

# tests 폴더 밖(StudyFit 폴더)에 있는 model.py를 불러올 수 있게 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import model as m


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    """임시 폴더에 모델을 학습/저장하고 (결과, 모델 경로)를 돌려준다."""
    path = str(tmp_path_factory.mktemp("models") / "test_model.joblib")
    result = m.train_model(model_path=path)
    return result, path


def test_data_loads_500_rows_with_correct_columns():
    X, y = m.load_data()
    assert len(X) == 500 and len(y) == 500
    assert list(X.columns) == m.FEATURE_COLUMNS
    assert y.name == "focus_score"


def test_train_split_is_80_20(trained):
    result, _ = trained
    assert result["n_train"] == 400
    assert result["n_test"] == 100


def test_train_returns_valid_metrics(trained):
    result, _ = trained
    assert result["mae"] >= 0
    assert result["r2"] <= 1
    # 가상 데이터는 직선 공식으로 만들었으므로 성능이 좋아야 정상
    assert result["r2"] > 0.8


def test_training_is_reproducible(tmp_path):
    a = m.train_model(model_path=str(tmp_path / "a.joblib"))
    b = m.train_model(model_path=str(tmp_path / "b.joblib"))
    assert a["mae"] == b["mae"] and a["r2"] == b["r2"]


def test_model_uses_same_column_names_and_order(trained):
    result, _ = trained
    assert list(result["model"].feature_names_in_) == m.FEATURE_COLUMNS


def test_save_and_load_model_gives_same_prediction(trained):
    result, path = trained
    assert os.path.exists(path)
    loaded = m.load_model(path)
    import pandas as pd

    row = pd.DataFrame([[5, 7, 3, 2]], columns=m.FEATURE_COLUMNS)
    assert loaded.predict(row)[0] == result["model"].predict(row)[0]


def test_train_without_save_creates_no_file(tmp_path):
    path = tmp_path / "none.joblib"
    m.train_model(model_path=str(path), save=False)
    assert not path.exists()


def test_predict_returns_float_in_0_100_with_one_decimal(trained):
    _, path = trained
    score = m.predict_focus(5, 7, 3, 2, model_path=path)
    assert isinstance(score, float)
    assert 0 <= score <= 100
    assert score == round(score, 1)


def test_predict_is_clipped_to_0_100(trained):
    _, path = trained
    # 학습 범위 밖 극단값(경고 대상)이라도 결과는 0~100 안이어야 한다
    low = m.predict_focus(0, 0, 24, 0, model_path=path)
    high = m.predict_focus(0, 24, 0, 0, model_path=path)
    assert low == 0.0
    assert high == 100.0


def test_more_sleep_raises_and_more_phone_lowers_score(trained):
    _, path = trained
    base = m.predict_focus(5, 6, 3, 2, model_path=path)
    assert m.predict_focus(5, 8, 3, 2, model_path=path) > base
    assert m.predict_focus(5, 6, 6, 2, model_path=path) < base


def test_predict_does_not_accept_focus_score():
    params = list(inspect.signature(m.predict_focus).parameters)
    assert params[:4] == ["study", "sleep", "phone", "rest"]
    assert not any("focus" in p or "score" in p for p in params)


@pytest.mark.parametrize(
    "args",
    [
        ("abc", 7, 3, 2),  # 문자 입력
        (5, 7, -1, 2),  # 음수
        (12, 10, 10, 5),  # 합계 24시간 초과
    ],
)
def test_invalid_input_raises_value_error(trained, args):
    _, path = trained
    with pytest.raises(ValueError):
        m.predict_focus(*args, model_path=path)


def test_missing_model_file_gives_friendly_error(tmp_path):
    missing = str(tmp_path / "no_model.joblib")
    with pytest.raises(m.ModelNotFoundError) as info:
        m.predict_focus(5, 7, 3, 2, model_path=missing)
    assert "python model.py" in str(info.value)


def test_missing_data_file_gives_friendly_error(tmp_path):
    with pytest.raises(FileNotFoundError) as info:
        m.load_data(str(tmp_path / "no_data.csv"))
    assert "data_generator.py" in str(info.value)
