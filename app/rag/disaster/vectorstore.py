import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.disaster.loader import (
    load_shelters_as_docs,
    load_hospitals_with_hours_as_docs,
    load_disasters_as_docs,
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

def build_vectorstore():
    shelters = load_shelters_as_docs()
    print(f"[Loader] 대피소 문서 개수: {len(shelters)}")

    hospitals = load_hospitals_with_hours_as_docs()
    print(f"[Loader] 병원 문서 개수: {len(hospitals)}")

    disasters = load_disasters_as_docs()
    print(f"[Loader] 재난 문서 개수: {len(disasters)}")

    docs = shelters + hospitals + disasters
    print(f"[Vectorstore] 원본 문서 총 개수: {len(docs)}")

    splits = text_splitter.split_documents(docs)
    print(f"[Vectorstore] 청크된 문서 총 개수: {len(splits)}")

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=None
    )

    print("[Vectorstore] in-memory 생성 완료")
    print(f"[Vectorstore] 최종 문서 개수: {len(splits)}")

    return vectorstore
