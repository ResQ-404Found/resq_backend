import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

vectorstore = None  

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 카테고리 분류 프롬프트
category_prompt = ChatPromptTemplate.from_template("""
당신은 사용자의 질문을 hospital / shelter / disaster / guideline / other 중 하나로 분류합니다.
출력은 반드시 카테고리 이름 하나만 쓰세요.

질문: {input}
""")

category_llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0)

def classify_question(question: str) -> str:
    result = category_llm.invoke(category_prompt.format_messages(input=question))
    return result.content.strip().lower()


# 답변 프롬프트
answer_prompt = ChatPromptTemplate.from_template("""
당신은 재난 대응 전문가 챗봇입니다.

context에 있는 정보를 기반으로 답변하세요.
만약 context에 정보가 부족하거나 없을 경우 "데이터에 없습니다."라고만 말하지 말고,
재난 대응 전문가로서 알고 있는 일반적인 대처 방법을 대신 알려주세요.

출력 형식은 질문 주제에 따라 다음과 같이 해주세요:

[병원 정보]
- 이름: ...
- 주소: ...
- 전화번호: ...
- 응급실: ...
- 주말진료: ...
- 운영시간: ...

[대피소 정보]
- 이름: ...
- 주소: ...
- 유형: ...

[재난 정보]
- 재난 종류: ...
- 단계: ...
- 발생 지역: ...
- 내용: ...

[대처 방법]
- 상황: ...
- 행동 지침:
1. ...
2. ...
3. ...
- 참고: ...

<context>
{context}
</context>

질문: {input}
""")

answer_llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=0)
document_chain = create_stuff_documents_chain(answer_llm, answer_prompt)


def init_vectorstore(vs):
    """main.py에서 vectorstore를 초기화할 때 호출"""
    global vectorstore
    vectorstore = vs


def rag_answer(question: str):
    if vectorstore is None:
        return {"answer": "⚠️ 벡터스토어가 아직 초기화되지 않았습니다."}

    category = classify_question(question)
    print(f"[DEBUG] 분류된 카테고리: {category}")

    if category == "hospital":
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3, "filter": {"category": "hospital"}})
    elif category == "shelter":
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3, "filter": {"category": "shelter"}})
    elif category == "disaster":
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3, "filter": {"category": "disaster"}})
    elif category == "guideline":
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    else:
        return {"answer": "저는 재난 대응 전문 챗봇입니다. 해당 주제는 답변해드릴 수 없습니다."}

    rag_chain = create_retrieval_chain(retriever, document_chain)
    return rag_chain.invoke({"input": question})
