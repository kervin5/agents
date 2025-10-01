from pydantic import BaseModel, Field
from agents import Agent, function_tool, Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from evaluator_agent import evaluator_agent, ResearchEvaluation
import asyncio

# Tool functions that the agent can choose to use
@function_tool
async def search_web(query: str, reason: str = "") -> str:
    """Search the web for information on a specific query"""
    print(f"🔍 TOOL: Searching web for: '{query}' (Reason: {reason})")
    try:
        result = await Runner.run(
            search_agent,
            f"Search term: {query}\nReason for searching: {reason}",
        )
        search_result = str(result.final_output)
        print(f"✅ Search completed - found {len(search_result)} characters of content")
        return search_result
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        print(f"❌ Search failed: {str(e)}")
        return error_msg

@function_tool
async def plan_research_searches(query: str) -> str:
    """Plan a comprehensive set of searches for a research query"""
    print(f"📋 TOOL: Planning research searches for: '{query}'")
    try:
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        plan = result.final_output_as(WebSearchPlan)
        searches = [f"- {item.query} (Reason: {item.reason})" for item in plan.searches]
        plan_result = f"Planned {len(searches)} searches:\n" + "\n".join(searches)
        print(f"✅ Planning completed - {len(plan.searches)} searches planned")
        return plan_result
    except Exception as e:
        error_msg = f"Planning failed: {str(e)}"
        print(f"❌ Planning failed: {str(e)}")
        return error_msg

@function_tool
async def evaluate_research_quality(original_query: str, search_results: str) -> str:
    """Evaluate if current research is complete or needs more investigation"""
    print(f"🔬 TOOL: Evaluating research quality for: '{original_query}'")
    try:
        input_text = f"""Original Query: {original_query}

Current Search Results:
{search_results}"""
        
        result = await Runner.run(evaluator_agent, input_text)
        evaluation = result.final_output_as(ResearchEvaluation)
        
        status = "COMPLETE" if evaluation.is_complete else "INCOMPLETE"
        gaps = ", ".join(evaluation.gaps_identified) if evaluation.gaps_identified else "None"
        suggestions = ", ".join(evaluation.suggested_searches) if evaluation.suggested_searches else "None"
        
        print(f"✅ Evaluation completed - Status: {status}, Score: {evaluation.completeness_score:.2f}")
        if not evaluation.is_complete:
            print(f"📝 Gaps identified: {gaps}")
            print(f"💡 Suggested searches: {suggestions}")
        
        return f"""Research Status: {status}
Completeness Score: {evaluation.completeness_score:.2f}
Identified Gaps: {gaps}
Suggested Additional Searches: {suggestions}
Reasoning: {evaluation.reasoning}"""
    except Exception as e:
        error_msg = f"Evaluation failed: {str(e)}"
        print(f"❌ Evaluation failed: {str(e)}")
        return error_msg

@function_tool
async def write_research_report(query: str, search_results: str) -> str:
    """Write a comprehensive research report based on findings"""
    print(f"📝 TOOL: Writing research report for: '{query}'")
    try:
        result = await Runner.run(
            writer_agent,
            f"Original query: {query}\nSummarized search results: {search_results}",
        )
        report = result.final_output_as(ReportData)
        print(f"✅ Report completed - {len(report.markdown_report)} characters written")
        return report.markdown_report
    except Exception as e:
        error_msg = f"Report writing failed: {str(e)}"
        print(f"❌ Report writing failed: {str(e)}")
        return error_msg

AGENT_INSTRUCTIONS = """You are an autonomous research agent. Your goal is to conduct thorough research on any given topic and produce a comprehensive report.

You have access to several tools:
- search_web: Search for specific information
- plan_research_searches: Create a research strategy  
- evaluate_research_quality: Check if research is complete
- write_research_report: Create the final report

Your workflow should be:
1. Start by planning your research approach using plan_research_searches
2. Conduct multiple searches based on your plan using search_web
3. Evaluate if you have enough information using evaluate_research_quality (aim for completeness score > 0.5)
4. If incomplete AND you haven't done 2 evaluation cycles yet, conduct additional targeted searches
5. After 2 evaluation cycles OR if score >= 0.5, ALWAYS proceed to write the report
6. Hand off the report to the Email agent for delivery

CRITICAL AUTONOMY RULES:
- You are AUTONOMOUS - never ask the user for permission or confirmation
- Make your own decisions about when to search more or proceed to writing
- After 2 evaluation cycles, ALWAYS proceed to writing regardless of score
- If you have any information at all, you can write a useful report
- Don't ask "Would you like me to..." - just do what's needed

Be decisive and autonomous. Track your progress and be efficient. Don't repeat unnecessary searches.

Remember: You're aiming for practical, useful research within 2 evaluation cycles maximum.
After completing the report, hand off to the Email agent to send it."""

# Create the autonomous research agent with email handoff
research_agent = Agent(
    name="AutonomousResearcher",
    instructions=AGENT_INSTRUCTIONS,
    model="gpt-4o",
    tools=[
        search_web,
        plan_research_searches, 
        evaluate_research_quality,
        write_research_report,
        # Removed send_email_report tool - will use handoff instead
    ],
    handoffs=[email_agent],  # Hand off to email agent for final step
)

class AutonomousResearchManager:
    """An autonomous research manager that uses tools + single handoff for email delivery"""
    
    async def run(self, query: str):
        """Run autonomous research using the agent with tools"""
        trace_id = gen_trace_id()
        with trace("Autonomous Research", trace_id=trace_id):
            print(f"🚀 Starting autonomous research for: {query}")
            print(f"🔗 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"🚀 Starting autonomous research for: {query}"
            yield f"🔗 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            
            try:
                print("🤖 Handing control to autonomous agent...")
                yield "🤖 Agent is analyzing the query and deciding on research strategy..."
                
                # Let the agent autonomously decide how to research
                result = await Runner.run(
                    research_agent,
                    f"Conduct comprehensive research on: {query}",
                )
                
                # The agent will have used its tools to complete the research
                final_output = str(result.final_output)
                
                print("✅ Autonomous research completed!")
                yield "✅ Research completed by autonomous agent"
                yield final_output
                
            except Exception as e:
                error_msg = f"❌ Research failed: {str(e)}"
                print(error_msg)
                yield error_msg