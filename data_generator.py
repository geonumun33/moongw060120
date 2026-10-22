# data_generator.py: 교육용 가상 학습 데이터 생성
#
# ※ 중요: 이 파일이 만드는 데이터는 실제 학생의 데이터가 아닙니다.
#    수업(머신러닝 프로젝트)에서 모델을 연습하기 위해 "내가 정한 공식"으로
#    만든 교육용 가상 데이터입니다. 이 데이터로 학습한 예측은 현실을 보장하지 않습니다.

import os

import numpy as np
import pandas as pd

# ---------------------------------------------------------------
# 설정값 (숫자를 바꾸고 싶으면 여기만 고치면 됩니다)
# ---------------------------------------------------------------
NUM_STUDENTS = 500   # 만들 학생 수
RANDOM_SEED = 42     # 난수 시드: 고정하면 실행할 때마다 같은 데이터가 나옴
NOISE_STD = 5.0      # 무작위 오차의 크기 (점수 단위, 표준편차)

# 각 항목의 (최소, 최대) 시간
STUDY_RANGE = (0, 12)
SLEEP_RANGE = (3, 10)
PHONE_RANGE = (0, 10)
BREAK_RANGE = (0, 5)

# 저장 위치: 이 파일이 있는 폴더 안의 data/study_data.csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "study_data.csv")


def calculate_focus_score(study, sleep, phone, rest):
    """집중도 점수의 '기본값'을 공식으로 계산한다 (무작위 오차는 아직 없음).

    공식:
        집중도 = 40
                 + 3.0 x 수면 시간      (잘 잘수록 올라감)
                 - 2.5 x 스마트폰 시간  (많이 쓸수록 내려감)
                 + 1.5 x 공부 시간      (공부할수록 조금 올라감)
                 + 2.0 x 휴식 시간      (쉬면 올라감)
    """
    return 40 + 3.0 * sleep - 2.5 * phone + 1.5 * study + 2.0 * rest


def generate_data(num_students=NUM_STUDENTS, seed=RANDOM_SEED):
    """가상 학생 데이터를 만들어 DataFrame(표)으로 돌려준다."""
    # 같은 시드를 쓰면 항상 같은 난수가 나온다
    rng = np.random.default_rng(seed)

    rows = []  # 조건을 통과한 학생들을 여기에 모은다

    # 500명이 모일 때까지 반복
    while len(rows) < num_students:
        # 각 시간을 범위 안에서 무작위로 뽑고, 소수 첫째 자리까지 반올림
        study = round(rng.uniform(*STUDY_RANGE), 1)
        sleep = round(rng.uniform(*SLEEP_RANGE), 1)
        phone = round(rng.uniform(*PHONE_RANGE), 1)
        rest = round(rng.uniform(*BREAK_RANGE), 1)

        # 하루는 24시간이므로, 합계가 24시간을 넘으면 버리고 다시 뽑는다
        if study + sleep + phone + rest > 24:
            continue

        # 공식으로 기본 점수를 계산하고, 무작위 오차(정규분포)를 더한다
        # (현실에서는 같은 습관이어도 사람마다 집중도가 조금씩 다르기 때문)
        score = calculate_focus_score(study, sleep, phone, rest)
        score = score + rng.normal(0, NOISE_STD)

        # 점수는 0~100 안으로 자르고, 소수 첫째 자리까지 반올림
        score = round(min(max(score, 0), 100), 1)

        rows.append([study, sleep, phone, rest, score])

    # 표(DataFrame)로 만들면서 컬럼 이름을 붙인다
    columns = ["study_hours", "sleep_hours", "phone_hours", "break_hours", "focus_score"]
    return pd.DataFrame(rows, columns=columns)


def save_data(df, path=CSV_PATH):
    """DataFrame을 CSV 파일로 저장한다. data 폴더가 없으면 만든다."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


if __name__ == "__main__":
    # "python data_generator.py"로 직접 실행했을 때만 아래가 동작한다
    print("※ 이 데이터는 실제 학생 데이터가 아닌 교육용 가상 데이터입니다.")
    data = generate_data()
    save_data(data)
    print(f"{len(data)}명의 가상 데이터를 저장했습니다: {CSV_PATH}")
