# advice.py: 개선 조언 문구 생성
#
# ⚠️ 이 파일은 머신러닝 모델이 만든 조언이 아닙니다.
#    입력값과 예측 점수가 정해 둔 조건에 맞는지 if문으로 확인해서,
#    미리 써 둔 문구를 골라 보여주는 "규칙 기반" 기능입니다.
#    (머신러닝은 model.py의 점수 예측에서만 사용합니다.)
#
# 조언은 가상 데이터로 학습한 모델의 예측과 일반적인 생활 습관 상식에 기반한 참고용 문구이며,
# 의료적 진단이나 실제 집중도에 대한 확정적인 판단이 아닙니다.

# 조건을 나누는 기준값 (숫자를 바꾸고 싶으면 여기만 고치면 됨)
LOW_SLEEP_HOURS = 6  # 수면이 이보다 적으면 수면 조언
HIGH_PHONE_HOURS = 5  # 스마트폰이 이 이상이면 스마트폰 조언
LOW_STUDY_HOURS = 2  # 공부가 이보다 적으면 공부 시간 조언
LOW_BREAK_HOURS = 1  # 휴식이 이보다 적으면 휴식 조언
LOW_SCORE = 40  # 예측 점수가 이보다 낮으면 전반 점검 조언
HIGH_SCORE = 70  # 예측 점수가 이 이상이면 격려 문구

DEFAULT_ADVICE = (
    "눈에 띄는 문제는 없어 보여요. 지금의 생활 리듬을 꾸준히 유지해 보세요."
)


def generate_advice(study, sleep, phone, rest, focus_score):
    """생활 습관 4개와 예측 집중도 점수로 조언 문구 리스트를 만든다.

    규칙 기반이므로 같은 입력이면 항상 같은 조언이 나온다.
    조언이 하나도 해당되지 않으면 기본 조언 1개를 돌려준다.
    """
    advice = []

    # 습관별 조언: 조건에 맞으면 문구를 하나씩 추가한다
    if sleep < LOW_SLEEP_HOURS:
        advice.append(
            f"수면 시간이 {LOW_SLEEP_HOURS}시간보다 적어요. "
            "잠이 부족하면 집중하기 어려울 수 있으니 수면 시간을 조금 늘려 보세요."
        )
    if phone >= HIGH_PHONE_HOURS:
        advice.append(
            f"스마트폰을 {HIGH_PHONE_HOURS}시간 이상 사용하고 있어요. "
            "공부할 때는 알림을 끄거나 폰을 멀리 두는 것부터 시작해 보세요."
        )
    if study < LOW_STUDY_HOURS:
        advice.append(
            f"공부 시간이 {LOW_STUDY_HOURS}시간보다 적어요. "
            "하루 중 정해진 시간에 짧게라도 규칙적으로 공부해 보세요."
        )
    if rest < LOW_BREAK_HOURS:
        advice.append(
            f"휴식 시간이 {LOW_BREAK_HOURS}시간보다 적어요. "
            "공부 중간에 짧은 휴식을 넣으면 집중을 이어가는 데 도움이 될 수 있어요."
        )

    # 예측 점수에 따른 조언 (낮은 점수와 높은 점수는 동시에 해당될 수 없음)
    if focus_score < LOW_SCORE:
        advice.append(
            "예측 집중도가 낮게 나왔어요. 수면, 스마트폰, 공부, 휴식 습관을 "
            "전반적으로 한번 점검해 보세요."
        )
    elif focus_score >= HIGH_SCORE:
        advice.append(
            "예측 집중도가 높게 나왔어요. 지금의 좋은 습관을 계속 이어가 보세요. 잘하고 있어요!"
        )

    # 아무 조건에도 해당하지 않으면 기본 조언을 제공한다
    if not advice:
        advice.append(DEFAULT_ADVICE)

    return advice
