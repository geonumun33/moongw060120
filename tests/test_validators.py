# test_validators.py: validators.py 자동화 테스트
# 실행: python -m pytest tests/test_validators.py -q

import os
import sys

# tests 폴더 밖(StudyFit 폴더)에 있는 validators.py를 불러올 수 있게 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators import validate_inputs


def test_normal_input_has_no_errors_or_warnings():
    errors, warnings = validate_inputs(5, 7, 3, 2)
    assert errors == []
    assert warnings == []


def test_return_value_is_two_lists_of_strings():
    errors, warnings = validate_inputs("abc", 2, 9, 1)
    assert isinstance(errors, list) and isinstance(warnings, list)
    assert all(isinstance(m, str) for m in errors + warnings)


def test_text_input_is_error():
    errors, _ = validate_inputs("abc", 7, 3, 2)
    assert len(errors) == 1
    assert "공부 시간" in errors[0] and "숫자" in errors[0]


def test_none_and_bool_are_errors():
    errors, _ = validate_inputs(None, True, 3, 2)
    assert len(errors) == 2


def test_nan_is_error():
    errors, _ = validate_inputs(float("nan"), 7, 3, 2)
    assert len(errors) == 1


def test_negative_is_error():
    errors, _ = validate_inputs(5, 7, -1, 2)
    assert len(errors) == 1
    assert "스마트폰 사용 시간" in errors[0] and "0보다" in errors[0]


def test_total_over_24_is_error():
    # 합계 12 + 10 + 10 + 5 = 37시간 (각 항목은 범위 안)
    errors, _ = validate_inputs(12, 10, 10, 5)
    assert len(errors) == 1
    assert "합계" in errors[0]


def test_total_exactly_24_is_ok():
    errors, _ = validate_inputs(8, 8, 4, 4)
    assert errors == []


def test_out_of_training_range_is_warning_not_error():
    # 공부 13시간: 학습 범위(0~12) 밖, 합계는 24 이하
    errors, warnings = validate_inputs(13, 5, 3, 1)
    assert errors == []
    assert any("공부 시간" in w and "범위" in w for w in warnings)


def test_low_sleep_is_warning():
    errors, warnings = validate_inputs(5, 3.5, 3, 2)
    assert errors == []
    assert any("수면 시간이 4시간 미만" in w for w in warnings)


def test_sleep_exactly_4_has_no_sleep_warning():
    _, warnings = validate_inputs(5, 4, 3, 2)
    assert warnings == []


def test_high_phone_use_is_warning():
    errors, warnings = validate_inputs(3, 7, 8, 1)
    assert errors == []
    assert any("스마트폰 사용 시간이 8시간 이상" in w for w in warnings)


def test_negative_is_error_without_range_warning():
    # 음수는 오류로만 처리하고 범위 경고는 따로 만들지 않는다
    errors, warnings = validate_inputs(5, 7, -1, 2)
    assert len(errors) == 1
    assert warnings == []


# ---- 회귀 테스트: 소수점 계산 오차 ----
# 컴퓨터는 0.4 + 9.0 + 9.8 + 4.8 을 24.000000000000004 로 계산해서,
# 정확히 24.0시간인 입력이 '24시간 초과' 오류로 잘못 처리되던 문제를 막는다.
def test_total_exactly_24_with_decimals_is_ok():
    errors, _ = validate_inputs(0.4, 9.0, 9.8, 4.8)
    assert errors == []


def test_total_24_point_1_with_decimals_is_error():
    errors, _ = validate_inputs(0.5, 9.0, 9.8, 4.8)
    assert len(errors) == 1
    assert "합계" in errors[0] and "24.1" in errors[0]
