import os, json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125",
    api_key=OPENAI_API_KEY,
    temperature=0.7
)

quiz_prompt = ChatPromptTemplate.from_template("""
당신은 재난 안전 교육 전문가입니다.
{category} 상황과 관련된 객관식 퀴즈 {n_questions}문제를 만들어주세요.
특히 주제는 "{topic}" 입니다.

출력은 반드시 JSON 배열로 반환하세요:
[
    {{
    "question_text": "질문 내용",
    "choices": {{"A": "보기1", "B": "보기2", "C": "보기3", "D": "보기4"}},
    "correct_answer": "A",
    "difficulty": "쉬움"
    }},
    ...
]
""")

def generate_quiz(category: str, topic: str, n_questions: int):
    chain = quiz_prompt | llm
    raw = chain.invoke({"category": category, "topic": topic, "n_questions": n_questions})
    try:
        data = json.loads(raw.content if hasattr(raw, "content") else raw)
        return data
    except Exception as e:
        raise ValueError(f"퀴즈 JSON 파싱 실패: {e}")
