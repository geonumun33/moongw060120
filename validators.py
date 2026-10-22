# validators.py: 사용자 입력 검증 (오류 / 경고)
#
# 오류(errors)  : 예측을 할 수 없는 잘못된 입력 (숫자가 아님, 음수, 하루 24시간 초과)
# 경고(warnings): 예측은 가능하지만 주의가 필요한 입력 (학습 데이터 범위 밖, 수면 부족 등)
#
# 이 파일은 Streamlit이나 머신러닝 모델과 무관한 순수 Python 코드입니다.

import math

# 학습 데이터(가상 데이터)의 범위: 항목 이름 -> (최소, 최대)
# data_generator.py에서 데이터를 만들 때 쓴 범위와 같습니다.
RANGES = {
    "공부 시간": (0, 12),
    "수면 시간": (3, 10),
    "스마트폰 사용 시간": (0, 10),
    "휴식 시간": (0, 5),
}

MAX_TOTAL_HOURS = 24  # 하루는 24시간
LOW_SLEEP_HOURS = 4  # 수면이 이보다 적으면 경고
HIGH_PHONE_HOURS = 8  # 스마트폰이 이 이상이면 경고


def is_number(value):
    """value가 쓸 수 있는 숫자(int 또는 float)이면 True.

    문자열, None, True/False, NaN, 무한대는 숫자로 인정하지 않습니다.
    """
    if isinstance(value, bool):  # True/False는 파이썬에서 숫자로 취급되므로 따로 제외
        return False
    if not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)


def validate_inputs(study, sleep, phone, rest):
    """입력값 4개를 검사해서 (errors, warnings)를 돌려준다.

    errors   : 오류 메시지 문자열 리스트 (하나라도 있으면 예측하면 안 됨)
    warnings : 경고 메시지 문자열 리스트 (예측은 해도 되지만 주의 필요)
    """
    errors = []
    warnings = []

    values = {
        "공부 시간": study,
        "수면 시간": sleep,
        "스마트폰 사용 시간": phone,
        "휴식 시간": rest,
    }

    # 1단계: 각 항목이 숫자인지, 음수는 아닌지 확인 (오류)
    valid_numbers = {}  # 오류가 없는 항목만 모아 둔다
    for name, value in values.items():
        if not is_number(value):
            errors.append(f"{name}은(는) 숫자로 입력해 주세요.")
        elif value < 0:
            errors.append(f"{name}은(는) 0보다 작을 수 없습니다. (입력값: {value})")
        else:
            valid_numbers[name] = value

    # 2단계: 네 항목이 모두 정상 숫자일 때만 하루 합계가 24시간을 넘는지 확인 (오류)
    if len(valid_numbers) == len(values):
        # 컴퓨터의 소수 계산에는 아주 작은 오차가 있다. (예: 0.4+9.0+9.8+4.8 = 24.000000000000004)
        # 앱은 0.1시간 단위로 입력받으므로, 비교하기 전에 소수 첫째 자리로 반올림한다.
        total = round(sum(valid_numbers.values()), 1)
        if total > MAX_TOTAL_HOURS:
            errors.append(
                f"네 항목의 합계가 {total:g}시간입니다. "
                f"하루는 {MAX_TOTAL_HOURS}시간이므로 합계를 줄여 주세요."
            )

    # 3단계: 학습 데이터 범위를 벗어나면 경고 (오류 아님)
    for name, value in valid_numbers.items():
        low, high = RANGES[name]
        if value < low or value > high:
            warnings.append(
                f"{name} {value:g}시간은 학습 데이터 범위({low}~{high}시간) 밖입니다. "
                "예측이 부정확할 수 있습니다."
            )

    # 4단계: 건강 관련 경고 (숫자로 확인된 값만 검사)
    if "수면 시간" in valid_numbers and sleep < LOW_SLEEP_HOURS:
        warnings.append(
            f"수면 시간이 {LOW_SLEEP_HOURS}시간 미만입니다. 수면 부족은 집중도에 나쁜 영향을 줄 수 있습니다."
        )
    if "스마트폰 사용 시간" in valid_numbers and phone >= HIGH_PHONE_HOURS:
        warnings.append(
            f"스마트폰 사용 시간이 {HIGH_PHONE_HOURS}시간 이상입니다. 사용 시간을 줄이는 것을 권합니다."
        )

    return errors, warnings
