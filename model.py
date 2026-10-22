# model.py: 모델 학습 / 저장 / 불러오기 / 예측
#
# ⚠️ 중요: 이 모델은 실제 학생 데이터가 아니라, 공식으로 만든 "교육용 가상 데이터"로 학습합니다.
#    그래서 R²가 높게 나와도 "실제 학생의 집중도를 정확히 예측한다"는 뜻이 아닙니다.
#    (모델은 현실이 아니라 data_generator.py에 내가 적어 둔 공식을 다시 찾아낸 것뿐입니다.)
#
# 실행: python model.py   (학습 후 models/focus_model.joblib 에 저장)

import os

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from validators import validate_inputs

# 이 파일이 있는 폴더 기준으로 경로를 만든다 (어디서 실행해도 같은 위치를 가리킴)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "study_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "focus_model.joblib")

# 입력 특성(X)의 이름과 순서. 학습할 때와 예측할 때 반드시 똑같아야 한다.
FEATURE_COLUMNS = ["study_hours", "sleep_hours", "phone_hours", "break_hours"]
TARGET_COLUMN = "focus_score"  # 정답(y). 학습에만 쓰고 예측 때는 입력받지 않는다.

TEST_SIZE = 0.2  # 20%는 평가용
RANDOM_STATE = 42  # 항상 같은 방식으로 나누기 위한 고정값


class ModelNotFoundError(FileNotFoundError):
    """저장된 모델 파일이 없을 때 발생하는 오류 (메시지가 한국어로 안내함)."""


def load_data(data_path=DATA_PATH):
    """CSV 파일을 읽어 (X, y)로 나누어 돌려준다."""
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"학습 데이터 파일이 없습니다: {data_path}\n"
            "먼저 'python data_generator.py'를 실행해 가상 데이터를 만들어 주세요."
        )
    df = pd.read_csv(data_path)
    X = df[FEATURE_COLUMNS]  # 입력 4개
    y = df[TARGET_COLUMN]  # 정답
    return X, y


def train_model(data_path=DATA_PATH, model_path=MODEL_PATH, save=True):
    """모델을 학습하고 평가한 뒤(필요하면 저장) 결과를 딕셔너리로 돌려준다.

    돌려주는 값: model, mae, r2, n_train, n_test, model_path
    - MAE: 예측이 정답과 평균 몇 점 차이 나는지 (작을수록 좋음)
    - R² : 모델이 점수 변화를 얼마나 설명하는지 (1에 가까울수록 좋음)
    """
    X, y = load_data(data_path)

    # 학습용 80% / 평가용 20%로 나눈다. random_state를 고정해서 항상 같은 결과가 나온다.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    model = LinearRegression()
    model.fit(X_train, y_train)  # 학습용 데이터로만 학습

    # 학습에 쓰지 않은 평가용 데이터로 성능을 잰다
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    if save:
        save_model(model, model_path)

    return {
        "model": model,
        "mae": float(mae),
        "r2": float(r2),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "model_path": model_path if save else None,
    }


def save_model(model, model_path=MODEL_PATH):
    """학습된 모델을 파일로 저장한다. (폴더가 없으면 만든다)"""
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)


def load_model(model_path=MODEL_PATH):
    """저장된 모델을 불러온다. 파일이 없으면 이해하기 쉬운 오류를 낸다."""
    if not os.path.exists(model_path):
        raise ModelNotFoundError(
            "학습된 모델 파일이 없습니다.\n"
            "먼저 'python model.py'를 실행해 모델을 학습하고 저장해 주세요.\n"
            f"(찾은 위치: {model_path})"
        )
    return joblib.load(model_path)


def predict_focus(study, sleep, phone, rest, model_path=MODEL_PATH):
    """공부·수면·스마트폰·휴식 시간으로 집중도 점수를 예측한다. (집중도는 입력받지 않음)

    - 입력이 잘못되면(숫자 아님, 음수, 합계 24시간 초과) ValueError를 낸다.
      검사는 validators.py의 validate_inputs를 그대로 사용한다.
    - 학습 범위 밖 같은 '경고'는 오류가 아니므로 예측은 진행한다.
    - 결과는 0~100점으로 제한하고 소수 첫째 자리까지 반올림한다.
    """
    errors, _warnings = validate_inputs(study, sleep, phone, rest)
    if errors:
        raise ValueError("입력값에 문제가 있습니다: " + " ".join(errors))

    model = load_model(model_path)

    # 학습 때와 같은 컬럼 이름과 순서로 표를 만든다
    row = pd.DataFrame(
        [[study, sleep, phone, rest]],
        columns=FEATURE_COLUMNS,
    )
    score = float(model.predict(row)[0])

    score = max(0.0, min(100.0, score))  # 0~100점으로 제한
    return round(score, 1)


if __name__ == "__main__":
    result = train_model()
    print("=" * 60)
    print("StudyFit 모델 학습 완료  (※ 교육용 가상 데이터 기반)")
    print("=" * 60)
    print(f"학습용 {result['n_train']}개 / 평가용 {result['n_test']}개")
    print(f"MAE : {result['mae']:.2f}점  -> 평가용 데이터에서 예측이 정답과 평균 이만큼 차이남")
    print(f"R²  : {result['r2']:.3f}   -> 1에 가까울수록 가상 데이터의 점수 변화를 잘 설명함")
    print(f"저장 위치: {result['model_path']}")
    print("주의: 가상 데이터로 학습했으므로 실제 학생의 집중도를 보장하지 않습니다.")
