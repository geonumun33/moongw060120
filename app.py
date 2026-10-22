# app.py: StudyFit Streamlit 웹앱 (홈 / 학습 습관 입력 / 분석 결과)
#
# 실행: streamlit run app.py
#
# ⚠️ 이 앱은 실제 학생 데이터가 아니라 공식으로 만든 "교육용 가상 데이터"로 학습한 모델을 사용합니다.
#    예측 결과는 참고용이며 실제 집중도를 보장하지 않습니다.

import pandas as pd
import streamlit as st

from advice import generate_advice
from model import ModelNotFoundError, predict_focus
from validators import validate_inputs

APP_TITLE = "StudyFit — AI 학습 습관 분석기"

# 화면 이름 (사이드바 라디오 버튼에 표시됨)
PAGE_HOME = "홈"
PAGE_INPUT = "학습 습관 입력"
PAGE_RESULT = "분석 결과"
PAGES = [PAGE_HOME, PAGE_INPUT, PAGE_RESULT]

# 모델 평가 수치: 이번에 새로 계산한 값이 아니라 4단계(python model.py) 실행 기록에서 가져온 값
MODEL_MAE = 3.78
MODEL_R2 = 0.841

DUMMY_DATA_NOTICE = (
    "이 결과는 실제 학생 데이터가 아닌 교육용 가상 데이터로 학습한 모델의 예측이며, "
    "실제 집중도를 보장하지 않습니다."
)

# 입력칸 기본값
DEFAULT_INPUTS = {"study": 4.0, "sleep": 7.0, "phone": 3.0, "rest": 1.5}


# ---------------------------------------------------------------
# 도우미 함수
# ---------------------------------------------------------------
def get_grade(score):
    """점수를 등급 이름으로 바꾼다: 70 이상 높음 / 40 이상 보통 / 40 미만 낮음"""
    if score >= 70:
        return "높음"
    if score >= 40:
        return "보통"
    return "낮음"


def init_session_state():
    """session_state에 저장 공간을 처음 한 번만 만든다."""
    if "inputs" not in st.session_state:
        st.session_state["inputs"] = dict(DEFAULT_INPUTS)  # 입력값
    if "result" not in st.session_state:
        st.session_state["result"] = None  # 분석 결과 (분석 전에는 None)
    if "page" not in st.session_state:
        st.session_state["page"] = PAGE_HOME  # 현재 화면


def go_to_result():
    """'결과 보기' 버튼을 눌렀을 때 화면을 결과 화면으로 바꾼다."""
    st.session_state["page"] = PAGE_RESULT


def run_analysis(study, sleep, phone, rest):
    """검증 -> 예측 -> 조언 순서로 실행하고 결과를 session_state에 저장한다.

    성공하면 True, 실패하면 False를 돌려준다. (오류는 화면에 메시지로 보여주고 앱은 멈추지 않는다)
    """
    st.session_state["result"] = None  # 이전 결과가 남아 헷갈리지 않게 먼저 지운다

    # 1) 입력 검증 (validators.py)
    errors, warnings = validate_inputs(study, sleep, phone, rest)
    if errors:
        for message in errors:
            st.error(message)
        return False  # 오류가 있으면 예측하지 않는다
    for message in warnings:
        st.warning(message)  # 경고는 보여주되 분석은 계속한다

    # 2) 집중도 예측 (model.py) - 파일이 없거나 문제가 생겨도 앱이 멈추지 않게 처리
    try:
        score = predict_focus(study, sleep, phone, rest)
    except ModelNotFoundError:
        st.error(
            "학습된 모델 파일을 찾을 수 없습니다. "
            "터미널에서 `python model.py`를 실행해 모델을 만든 뒤 다시 시도해 주세요."
        )
        return False
    except ValueError as e:
        st.error(f"입력값을 확인해 주세요. ({e})")
        return False
    except Exception:
        st.error("예측 중 예상하지 못한 문제가 발생했습니다. 모델 파일을 다시 만들어 보세요. (`python model.py`)")
        return False

    # 3) 맞춤형 조언 (advice.py)
    advice = generate_advice(study, sleep, phone, rest, score)

    # 4) 결과 저장: 화면을 이동해도 유지된다
    st.session_state["result"] = {
        "inputs": {"study": study, "sleep": sleep, "phone": phone, "rest": rest},
        "score": score,
        "grade": get_grade(score),
        "advice": advice,
        "warnings": warnings,
    }
    return True


# ---------------------------------------------------------------
# 화면 1: 홈
# ---------------------------------------------------------------
def show_home():
    st.title(APP_TITLE)
    st.write(
        "공부 시간, 수면 시간, 스마트폰 사용 시간, 휴식 시간을 입력하면 "
        "머신러닝 모델이 **집중도 점수를 예측**하고, 습관을 개선할 수 있는 조언을 알려 드려요."
    )

    st.warning(
        "📌 **교육용 가상 데이터 기반 앱입니다.**\n\n"
        "이 앱의 모델은 실제 학생 데이터가 아니라, 공식으로 만든 가상 데이터로 학습했습니다. "
        "따라서 예측 결과는 참고용이며 실제 집중도를 보장하지 않습니다."
    )

    st.subheader("사용 방법")
    st.markdown(
        "1. 왼쪽 사이드바에서 **학습 습관 입력**을 선택해요.\n"
        "2. 하루 평균 공부·수면·스마트폰·휴식 시간을 입력하고 **분석하기**를 눌러요.\n"
        "3. **분석 결과**에서 예측 점수와 맞춤형 조언을 확인해요."
    )


# ---------------------------------------------------------------
# 화면 2: 학습 습관 입력
# ---------------------------------------------------------------
def show_input():
    st.title("학습 습관 입력")
    st.write("하루 평균 시간을 입력해 주세요. (소수 첫째 자리까지, 0~24시간)")

    saved = st.session_state["inputs"]  # 이전에 입력한 값 (화면을 이동해도 유지)

    # 입력칸 4개: min/max는 UI 범위(0~24), 학습 데이터 범위를 벗어나면 경고가 나온다
    study = st.number_input("공부 시간 (시간)", 0.0, 24.0, saved["study"], 0.1, format="%.1f")
    sleep = st.number_input("수면 시간 (시간)", 0.0, 24.0, saved["sleep"], 0.1, format="%.1f")
    phone = st.number_input("스마트폰 사용 시간 (시간)", 0.0, 24.0, saved["phone"], 0.1, format="%.1f")
    rest = st.number_input("휴식 시간 (시간)", 0.0, 24.0, saved["rest"], 0.1, format="%.1f")

    # 현재 입력값을 저장해 둔다 (다른 화면에 갔다 와도 입력칸 값이 유지됨)
    study, sleep, phone, rest = (round(v, 1) for v in (study, sleep, phone, rest))
    st.session_state["inputs"] = {"study": study, "sleep": sleep, "phone": phone, "rest": rest}

    st.caption(f"네 항목의 합계: {study + sleep + phone + rest:.1f}시간 (하루는 24시간)")
    st.caption("참고: 학습 데이터 범위는 공부 0~12, 수면 3~10, 스마트폰 0~10, 휴식 0~5시간입니다.")

    if st.button("분석하기", type="primary"):
        if run_analysis(study, sleep, phone, rest):
            st.success("분석이 완료되었어요!")
            st.button("결과 보기 →", on_click=go_to_result)


# ---------------------------------------------------------------
# 화면 3: 분석 결과
# ---------------------------------------------------------------
def show_result():
    st.title("분석 결과")

    result = st.session_state["result"]
    if result is None:
        st.info("먼저 학습 습관을 입력하고 분석해 주세요.")
        return

    # 가상 데이터 안내 (결과 화면에서 가장 먼저 보이게)
    st.warning(DUMMY_DATA_NOTICE)

    # 점수와 등급
    col1, col2 = st.columns(2)
    col1.metric("집중도 예측 점수", f"{result['score']:.1f}점")
    col2.metric("점수 등급", result["grade"])
    st.caption("등급 기준: 70점 이상 높음 / 40점 이상 70점 미만 보통 / 40점 미만 낮음")

    # 입력 경고가 있었다면 결과 화면에서도 다시 알려준다
    for message in result["warnings"]:
        st.warning(message)

    # 학습 습관 막대그래프
    st.subheader("입력한 학습 습관")
    inputs = result["inputs"]
    chart_data = pd.DataFrame(
        {"시간": [inputs["study"], inputs["sleep"], inputs["phone"], inputs["rest"]]},
        index=["공부", "수면", "스마트폰", "휴식"],
    )
    st.bar_chart(chart_data, y_label="시간(h)")

    # 맞춤형 조언
    st.subheader("맞춤형 학습 조언")
    for text in result["advice"]:
        st.markdown(f"- {text}")
    st.caption("조언은 머신러닝이 아니라 입력값에 따라 문구를 고르는 규칙 기반 기능이며, 의료적 진단이 아닙니다.")

    # 모델 성능
    st.subheader("모델 평가 결과")
    col3, col4 = st.columns(2)
    col3.metric("MAE (평균 오차)", f"{MODEL_MAE}점")
    col4.metric("R²", f"{MODEL_R2}")
    st.info(
        "이 수치는 **가상 평가 데이터**에서 얻은 값이며, 실제 학생에 대한 정확도가 아닙니다. "
        "가상 데이터는 직선 공식으로 만들었기 때문에 선형 모델이 잘 맞는 것이 당연합니다.\n\n"
        "- **MAE**: 가상 평가 데이터에서 예측이 정답과 평균 약 3.78점 차이 났다는 뜻이에요.\n"
        "- **R²**: 가상 데이터 점수 변화의 약 84%를 모델이 설명했다는 뜻이에요."
    )
    st.caption("※ 이 수치는 이번 실행에서 새로 계산한 것이 아니라, 모델 학습(python model.py) 때 기록된 값입니다.")


# ---------------------------------------------------------------
# 앱 시작: 화면 설정 -> 사이드바 -> 선택한 화면 표시
# ---------------------------------------------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="📚")
init_session_state()

st.sidebar.title("📚 StudyFit")
st.sidebar.radio("화면 선택", PAGES, key="page")  # 선택값이 session_state['page']에 저장됨
st.sidebar.caption("교육용 가상 데이터 기반 프로젝트")

page = st.session_state["page"]
if page == PAGE_HOME:
    show_home()
elif page == PAGE_INPUT:
    show_input()
else:
    show_result()
