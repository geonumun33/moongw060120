# test_advice.py: advice.py 자동화 테스트
# 실행: python -m pytest tests/test_advice.py -q

import os
import sys

# tests 폴더 밖(StudyFit 폴더)에 있는 advice.py를 불러올 수 있게 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from advice import DEFAULT_ADVICE, generate_advice


def has(advice, keyword):
    """조언 리스트 중 keyword가 들어간 문장이 있는지 확인"""
    return any(keyword in a for a in advice)


# 기준에 걸리지 않는 '평범한' 입력: 공부 5, 수면 7, 스마트폰 3, 휴식 2, 점수 55
def test_return_is_list_of_strings():
    advice = generate_advice(5, 7, 3, 2, 55)
    assert isinstance(advice, list)
    assert all(isinstance(a, str) and a for a in advice)


def test_low_sleep_advice():
    advice = generate_advice(5, 5.5, 3, 2, 55)
    assert has(advice, "수면")


def test_sleep_exactly_6_has_no_sleep_advice():
    assert not has(generate_advice(5, 6, 3, 2, 55), "수면")


def test_high_phone_advice():
    advice = generate_advice(5, 7, 5, 2, 55)  # 정확히 5시간도 해당
    assert has(advice, "스마트폰")


def test_phone_below_5_has_no_phone_advice():
    assert not has(generate_advice(5, 7, 4.9, 2, 55), "스마트폰")


def test_low_study_advice():
    advice = generate_advice(1, 7, 3, 2, 55)
    assert has(advice, "공부 시간")


def test_low_break_advice():
    advice = generate_advice(5, 7, 3, 0.5, 55)
    assert has(advice, "휴식")


def test_low_score_advice():
    advice = generate_advice(5, 7, 3, 2, 39.9)
    assert has(advice, "전반적으로")


def test_score_exactly_40_has_no_low_score_advice():
    assert not has(generate_advice(5, 7, 3, 2, 40), "전반적으로")


def test_high_score_encouragement():
    advice = generate_advice(5, 8, 2, 2, 70)  # 정확히 70점도 해당
    assert has(advice, "잘하고 있어요")


def test_high_score_not_shown_for_low_score():
    assert not has(generate_advice(5, 7, 3, 2, 30), "잘하고 있어요")


def test_default_advice_when_nothing_applies():
    advice = generate_advice(5, 7, 3, 2, 55)
    assert advice == [DEFAULT_ADVICE]


def test_default_advice_not_added_when_other_advice_exists():
    advice = generate_advice(5, 5, 3, 2, 55)
    assert DEFAULT_ADVICE not in advice


def test_multiple_advice_at_once():
    advice = generate_advice(1, 4, 8, 0, 20)
    assert len(advice) == 5  # 수면, 스마트폰, 공부, 휴식, 낮은 점수
    assert has(advice, "수면") and has(advice, "스마트폰")
    assert has(advice, "공부 시간") and has(advice, "휴식")
    assert has(advice, "전반적으로")


def test_always_at_least_one_advice():
    for score in (0, 39.9, 40, 55, 69.9, 70, 100):
        assert len(generate_advice(5, 7, 3, 2, score)) >= 1


def test_advice_avoids_definitive_or_medical_wording():
    advice = generate_advice(1, 4, 8, 0, 20) + generate_advice(5, 8, 2, 2, 80)
    for banned in ("진단", "치료", "반드시", "확실히"):
        assert not has(advice, banned)
