from app.rag.counseling.chains import build_counseling_chain

# PDF 경로 (배포 시에는 settings.py 같은 데서 주입)
COUNSELING_PDF = "./data/counseling_manual.pdf"

counseling_chain = build_counseling_chain(COUNSELING_PDF)

def ask_counseling_bot(user_message: str) -> str:
    response = counseling_chain.invoke({"input": user_message})
    return response["answer"]