from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from app.rag.vectorstore import build_vectorstore
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

prompt = ChatPromptTemplate.from_template("""
당신은 재난 대응 전문가 챗봇입니다.
아래 context를 기반으로 대답하세요.
만약 context에 해당 정보가 없다면 "데이터에 없습니다."라고만 말하지 말고, 
재난 대응 전문가로서 알고 있는 **일반적인 대처 방법**을 대신 알려주세요.

출력 형식은 질문 주제에 따라 다음과 같이 해주세요:

병원 관련 질문:
[병원 정보]
- 이름: (기관명)
- 주소: (도로명 주소)
- 전화번호: (응급실 전화)
- 응급실: (있음 / 없음)
- 주말진료: (예 / 아니오)
- 운영시간:
- 월요일: HH:MM ~ HH:MM
- 화요일: HH:MM ~ HH:MM
...

대피소 관련 질문:
[대피소 정보]
- 이름: (시설명)
- 주소: (도로명 주소)
- 유형: (대피소 유형명)
- 위도/경도: (위도, 경도)

재난 상황 관련 질문:
[재난 상황]
- 재난 종류: (예: 태풍, 폭우, 한파 등)
- 단계: (예: 주의보 / 경보)
- 발생 지역: (지역명)
- 내용: (메시지 요약)
- 시작 시각: YYYY-MM-DD HH:MM
- 종료 시각: YYYY-MM-DD HH:MM

대처 방법 관련 질문:
[대처 방법]
- 상황: (예: 태풍, 폭우, 지진, 화재 등)
- 행동 지침:
1. (첫 번째 대처 방법)
2. (두 번째 대처 방법)
3. (세 번째 대처 방법)
- 참고: (필요시 추가 주의사항)

<context>
{context}
</context>

질문: {input}
""")

llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo-0125", temperature=0)

vectorstore = build_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

document_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, document_chain)
