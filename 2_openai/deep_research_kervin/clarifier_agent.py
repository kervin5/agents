from pydantic import BaseModel, Field
from agents import Agent

INSTRUCTIONS = f"You are a helpful research assistant. Give a query, come up with a set of clarifying questions \
to ask the user to better understand their intent. Output 3 questions to ask the user. If the query is already clear, \
respond with no questions."


class ClarifyingQuestions(BaseModel):
    questions: list[str] = Field(description="A list of clarifying questions to ask the user.")

clarifier_agent = Agent(
    name="ClarifierAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ClarifyingQuestions,
)