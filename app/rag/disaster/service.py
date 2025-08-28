from app.rag.disaster.chains import rag_answer

def ask_disaster_bot(question: str) -> str:
    result = rag_answer(question)
    return result["answer"]
