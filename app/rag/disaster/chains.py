import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 전역 vectorstore (초기엔 None)
vectorstore = None
hospital_retriever = None
shelter_retriever = None
disaster_retriever = None

def init_vectorstore(vs):
    global vectorstore, hospital_retriever, shelter_retriever, disaster_retriever
    vectorstore = vs
    print("[chains] vectorstore 주입 완료")

    # retriever 세팅
    hospital_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3, "filter": {"category": "hospital"}}
    )
    shelter_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3, "filter": {"category": "shelter"}}
    )
    disaster_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3, "filter": {"category": "disaster"}}
    )

# -----------------------
# 분류 & 답변 부분 (그대로)
# -----------------------
category_prompt = ChatPromptTemplate.from_template("""
당신은 사용자의 질문을 hospital / shelter / disaster / guideline / other 중 하나로 분류합니다.
출력은 반드시 카테고리 이름 하나만 쓰세요.

질문: {input}
""")
category_llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0)

def classify_question(question: str) -> str:
    result = category_llm.invoke(category_prompt.format_messages(input=question))
    return result.content.strip().lower()

answer_prompt = ChatPromptTemplate.from_template("""
당신은 재난 대응 전문가 챗봇입니다.
context에 있는 정보를 기반으로 답변하세요.
만약 context에 정보가 부족하거나 없을 경우 "데이터에 없습니다."라고만 말하지 말고,
재난 대응 전문가로서 알고 있는 일반적인 대처 방법을 대신 알려주세요.

<context>
{context}
</context>

질문: {input}
""")

answer_llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=0)
document_chain = create_stuff_documents_chain(answer_llm, answer_prompt)

def rag_answer(question: str):
    if not vectorstore:
        return {"answer": "vectorstore가 초기화되지 않았습니다."}

    category = classify_question(question)
    print(f"[DEBUG] 분류된 카테고리: {category}")

    if category == "hospital":
        retriever = hospital_retriever
    elif category == "shelter":
        retriever = shelter_retriever
    elif category == "disaster":
        retriever = disaster_retriever
    elif category == "guideline":
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    else:
        return {"answer": "저는 재난 대응 전문 챗봇입니다. 해당 주제는 답변해드릴 수 없습니다."}

    rag_chain = create_retrieval_chain(retriever, document_chain)
    return rag_chain.invoke({"input": question})
