from app.rag.disaster.chains import rag_chain

def ask_disaster_bot(question: str) -> str:
    response = rag_chain.invoke({"input": question})
    return response["answer"]