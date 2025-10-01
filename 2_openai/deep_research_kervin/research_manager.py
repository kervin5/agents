from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from evaluator_agent import evaluator_agent, ResearchEvaluation
import asyncio

class ResearchManager:

    async def run(self, query: str):
        """ Run the autonomous deep research process, yielding status updates and the final report"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            
            print("Starting autonomous research...")
            yield "Starting autonomous research..."
            
            # Autonomous research loop with max 3 cycles
            all_search_results = []
            cycle = 1
            max_cycles = 3
            evaluation = None
            
            while cycle <= max_cycles:
                print(f"Research cycle {cycle}/{max_cycles}")
                yield f"Research cycle {cycle}/{max_cycles}"
                
                # Plan searches for this cycle
                if cycle == 1:
                    # Initial planning based on original query
                    search_plan = await self.plan_searches(query)
                else:
                    # Plan additional searches based on evaluation gaps
                    if evaluation and evaluation.suggested_searches:
                        search_plan = await self.plan_additional_searches(query, evaluation.suggested_searches)
                    else:
                        break  # No more searches suggested
                
                yield f"Planned {len(search_plan.searches)} searches for cycle {cycle}"
                
                # Perform searches
                cycle_results = await self.perform_searches(search_plan)
                all_search_results.extend(cycle_results)
                
                yield f"Completed {len(cycle_results)} searches. Total results: {len(all_search_results)}"
                
                # Evaluate research completeness
                evaluation = await self.evaluate_research(query, all_search_results)
                
                print(f"Research evaluation - Complete: {evaluation.is_complete}, Score: {evaluation.completeness_score}")
                yield f"Research evaluation - Completeness: {evaluation.completeness_score:.1%}"
                
                if evaluation.is_complete or cycle == max_cycles:
                    if evaluation.is_complete:
                        yield f"Research complete after {cycle} cycles! Writing report..."
                    else:
                        yield f"Max cycles reached. Writing report with current findings..."
                    break
                else:
                    yield f"Gaps identified: {', '.join(evaluation.gaps_identified[:2])}{'...' if len(evaluation.gaps_identified) > 2 else ''}"
                    yield f"Planning additional searches for cycle {cycle + 1}..."
                
                cycle += 1
            
            # Write report and send email
            report = await self.write_report(query, all_search_results)
            yield "Report written, sending email..."
            await self.send_email(report)
            yield "Email sent, research complete"
            yield report.markdown_report

    async def evaluate_research(self, query: str, search_results: list[str]) -> ResearchEvaluation:
        """ Evaluate if current research is complete or needs more searches """
        print("Evaluating research completeness...")
        
        # Summarize results for evaluation
        results_summary = "\n\n".join([f"Result {i+1}: {result[:500]}..." 
                                     for i, result in enumerate(search_results)])
        
        input_text = f"""Original Query: {query}

Current Search Results Summary:
{results_summary}

Total number of search results: {len(search_results)}"""
        
        result = await Runner.run(evaluator_agent, input_text)
        evaluation = result.final_output_as(ResearchEvaluation)
        
        print(f"Evaluation: {evaluation.reasoning}")
        return evaluation

    async def plan_additional_searches(self, original_query: str, suggested_searches: list[str]) -> WebSearchPlan:
        """ Plan additional searches based on evaluator suggestions """
        print("Planning additional searches...")
        
        # Convert suggested searches into WebSearchItems
        search_items = []
        for i, search_query in enumerate(suggested_searches[:3]):  # Max 3 additional searches
            search_items.append(WebSearchItem(
                query=search_query,
                reason=f"Fill research gap identified in cycle evaluation"
            ))
        
        return WebSearchPlan(searches=search_items)
        

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """ Plan the searches to perform for the query """
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """ Perform the searches to perform for the query """
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """ Perform a search for the query """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """ Write the report for the query """
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing report")
        return result.final_output_as(ReportData)
    
    async def send_email(self, report: ReportData) -> None:
        print("Writing email...")
        result = await Runner.run(
            email_agent,
            report.markdown_report,
        )
        print("Email sent")