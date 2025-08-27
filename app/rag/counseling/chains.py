from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from app.rag.counseling.vectorstore import build_counseling_vectorstore
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

counseling_prompt = ChatPromptTemplate.from_template("""
당신은 따뜻하고 친절한 심리 상담사입니다.  
아래 context를 참고하여 사용자의 고민에 공감하고 조언을 해주세요.  
context에 답이 없다면 LLM의 일반 지식으로 보완해도 됩니다.  
단, 전문적인 치료나 의학적 진단은 대신하지 마세요.  

<context>
{context}
</context>

🙋 질문: {input}
""")

llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo-0125", temperature=0.7)

def build_counseling_chain(pdf_path: str):
    vectorstore = build_counseling_vectorstore(pdf_path)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    document_chain = create_stuff_documents_chain(llm, counseling_prompt)
    return create_retrieval_chain(retriever, document_chain)
