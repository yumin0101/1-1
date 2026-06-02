import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 타이틀
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💌", layout="centered")
st.title("💌 달콤살벌 연애상담소")
st.caption("연애 고민, 썸, 이별... 혼자 끙끙 앓지 말고 Gemini에게 물어보세요!")

# 2. Streamlit Secrets에서 API 키 불러오기 및 설정
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 관관리자 설정을 확인해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! 당신의 연애 고민을 들어드릴 연애 카운셀러입니다. 무슨 고민이 있으신가요? (예: 썸남/썸녀 심리가 궁금해요, 권태기 같아요 등)"
        }
    ]

# 4. 기존 채팅 기록 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("고민을 이야기해주세요..."):
    # 사용자 메시지를 화면에 표시 및 세션에 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 6. Gemini 모델을 통한 답변 생성 (오류 처리 포함)
    with st.chat_message("assistant"):
        with st.spinner("답변을 고민하고 있어요... ☕"):
            try:
                # 대화 맥락을 유지하기 위해 프롬프트 구성 (역할 부여)
                system_instruction = (
                    "너는 친절하고 공감 능력이 뛰어나며, 때로는 뼈 때리는 조언도 아끼지 않는 전문 연애 카운셀러야. "
                    "상황을 분석하고 따뜻하면서도 현실적인 해결책을 제시해줘. 말투는 다정하고 친근하게 해줘."
                )
                
                # gemini-2.5-flash-lite 모델 로드
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash-lite",
                    system_instruction=system_instruction
                )
                
                # Gemini가 인식할 수 있는 형태로 이전 대화 기록 변환
                # (Gemini API의 chat history 구조에 맞게 변환하거나, 간단하게 텍스트로 합쳐 보낼 수 있습니다)
                chat = model.start_chat(history=[])
                
                # 대화 기록 학습시키기 (최근 대화 맥락 전달)
                # 단순화를 위해 전체 메시지를 대화 내역으로 주입
                formatted_history = []
                for msg in st.session_state.messages[:-1]: # 방금 넣은 user_input 제외
                    role = "user" if msg["role"] == "user" else "model"
                    formatted_history.append({"role": role, "parts": [msg["content"]]})
                
                chat.history = formatted_history
                
                # 답변 생성
                response = chat.send_message(user_input)
                ai_response = response.text
                
                # 결과 출력 및 저장
                st.write(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                # API 오류나 네트워크 문제가 발생했을 때의 예외 처리
                error_message = f"죄송합니다. 답변을 생성하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요. 😢\n\n*(오류 내용: {str(e)})*"
                st.error(error_message)
