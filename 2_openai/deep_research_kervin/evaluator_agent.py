from pydantic import BaseModel, Field
from agents import Agent

INSTRUCTIONS = """You are a research quality evaluator. Given an original query and current search results, 
determine if the research is complete or if additional searches are needed.

Evaluate based on:
1. Completeness - Does the research cover all important aspects of the query?
2. Depth - Is there sufficient detail and evidence?
3. Quality - Are the sources credible and relevant?
4. Coverage - Are there obvious gaps or missing perspectives?

Scoring guidelines (be generous with scoring):
- 0.7+ = Research is complete and sufficient
- 0.5-0.6 = Research is adequate and should be considered complete
- 0.3-0.4 = Research is minimal but workable, could benefit from one more search
- Below 0.3 = Research needs additional work

Be lenient in your evaluation - if there's reasonable information available, consider the research adequate.
Even partial information can form the basis of a useful report.
If research is complete (score > 0.5), indicate that no more searches are needed."""

class ResearchEvaluation(BaseModel):
    is_complete: bool = Field(description="True if research is complete, False if more searches needed")
    completeness_score: float = Field(description="Score from 0.0 to 1.0 indicating research completeness")
    gaps_identified: list[str] = Field(description="List of specific gaps or missing information")
    suggested_searches: list[str] = Field(description="Specific search queries to fill gaps (empty if complete)")
    reasoning: str = Field(description="Explanation of the evaluation decision")

evaluator_agent = Agent(
    name="ResearchEvaluator",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ResearchEvaluation,
)