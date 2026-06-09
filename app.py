import streamlit as st
from google import genai
from google.genai import types

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="급식실 자리 챗봇",
    page_icon="🍽️",
)

st.title("🍽️ 급식실 자리 추천 챗봇")

# -----------------------------
# API 키 확인
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "GEMINI_API_KEY가 설정되지 않았습니다.\n\n"
        "Streamlit Secrets에 API 키를 등록해주세요."
    )
    st.stop()

# -----------------------------
# Gemini 클라이언트 생성
# -----------------------------
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini 클라이언트 생성 실패: {e}")
    st.stop()

# -----------------------------
# 시스템 프롬프트
# -----------------------------
SYSTEM_PROMPT = """
당신은 학교 급식실 자리 추천 챗봇이다.

역할:
- 학생이 원하는 조건에 맞는 자리를 추천한다.
- 예시 조건:
  - 조용한 자리
  - 친구들과 이야기하기 좋은 자리
  - 창가 자리
  - 배식대와 가까운 자리
  - 출입구와 먼 자리
  - 혼밥하기 좋은 자리

답변 규칙:
- 친절하고 간결하게 답변한다.
- 추천 이유를 함께 설명한다.
- 실제 좌석 정보를 모를 경우 일반적인 급식실 기준으로 안내한다.
"""

# -----------------------------
# 채팅 기록 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! 🍽️ 원하는 급식실 자리 조건을 말해 주세요."
        }
    ]

# -----------------------------
# 이전 메시지 출력
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# 사용자 입력
# -----------------------------
user_input = st.chat_input("예: 조용한 자리 추천해줘")

if user_input:
    # 사용자 메시지 저장
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # 대화 기록 구성
        conversation_text = SYSTEM_PROMPT + "\n\n"

        for msg in st.session_state.messages:
            role = "사용자" if msg["role"] == "user" else "챗봇"
            conversation_text += f"{role}: {msg['content']}\n"

        # Gemini 호출
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=conversation_text,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=500,
            ),
        )

        answer = response.text

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except Exception as e:
        error_msg = f"오류가 발생했습니다: {str(e)}"

        with st.chat_message("assistant"):
            st.error(error_msg)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_msg
            }
        )
