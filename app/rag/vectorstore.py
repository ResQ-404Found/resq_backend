import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.loader import (
    load_shelters_as_docs,
    load_hospitals_with_hours_as_docs,
    load_disasters_as_docs,
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",   # 필요시 "text-embedding-3-large"로 교체 가능
    api_key=OPENAI_API_KEY
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,     # 문서 크기에 따라 300~800 정도 조정 가능
    chunk_overlap=100
)

def build_vectorstore(persist_dir: str = "./chroma_db"):
    # 1. DB → Document 불러오기
    docs = []
    docs.extend(load_shelters_as_docs())
    docs.extend(load_hospitals_with_hours_as_docs())
    docs.extend(load_disasters_as_docs())

    # 2. 문서 chunking 적용
    splits = text_splitter.split_documents(docs)

    # 3. 기존 VectorStore 불러오기 (있으면 재사용)
    if os.path.exists(persist_dir):
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_dir
        )
    else:
        # 4. 새로 생성할 경우, 배치 단위로 추가
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_dir
        )
        for i in range(0, len(splits), 100):   # 100개씩 잘라서 추가
            batch = splits[i:i+100]
            vectorstore.add_documents(batch)
        vectorstore.persist()  # 디스크에 저장

    return vectorstore
