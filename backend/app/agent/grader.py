from typing_extensions import Literal

from pydantic import BaseModel, Field
from app.agent.prompts import grader_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

grader = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    temperature=0.3,
    api_key=settings.GEMINI_API_KEY,
    streaming=False,
)

class GradeDocuments(BaseModel):
    binary_score: Literal["yes", "no"] = Field(description="yes or no")

def grade_document(query: str, doc: str) -> bool:
    prompt = grader_prompt.format(query=query, context=doc)
    chain = grader.with_structured_output(GradeDocuments)
    response = chain.invoke(prompt)
    return response.binary_score.lower() == "yes"