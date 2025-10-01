import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
from clarifier_agent import clarifier_agent
from agents import Runner

# Improve this agent to do the following:
# 1. Clarify the search query to improve search results by making clarifying questions.
# 2. Refactor to be a true agentic system rather than a chain of calls.

load_dotenv(override=True)


async def check_and_clarify(query: str):
    """Check if clarification is needed and return questions if so"""
    result = await Runner.run(clarifier_agent, query)
    questions = result.final_output.questions
    
    if questions:
        return True, questions
    return False, []


async def run_research(query: str, clarifications: str = ""):
    """Run research with optional clarifications"""
    full_query = query
    if clarifications.strip():
        full_query = f"{query}\n\nAdditional context: {clarifications}"
    
    async for chunk in ResearchManager().run(full_query):
        yield chunk


with gr.Blocks() as ui:
    gr.Markdown("# Deep Research")
    
    # Main query input
    query_textbox = gr.Textbox(
        label="What topic would you like to research?",
        placeholder="Enter your research question or topic..."
    )
    
    # Clarification section (initially hidden)
    with gr.Group(visible=False) as clarification_group:
        gr.HTML("""
            <div style="
                background-color: #f8f9fa; 
                border: 2px solid #e9ecef; 
                border-radius: 8px; 
                padding: 16px; 
                margin: 8px 0;
            ">
                <h4 style="color: #495057; margin-top: 0;">
                    🤔 Let's clarify your research topic
                </h4>
            </div>
        """)
        questions_display = gr.Markdown()
        clarifications_textbox = gr.Textbox(
            label="Your answers",
            placeholder="Please answer the questions above to help refine the research...",
            lines=3
        )
        continue_button = gr.Button("Start Research", variant="primary")
    
    # Single run button
    run_button = gr.Button("Start Research", variant="primary")
    
    # Results
    report = gr.Markdown(label="Report")
    
    async def handle_run_research(query):
        """Handle the main research flow with optional clarification"""
        if not query.strip():
            gr.Warning("Please enter a research query first.")
            return gr.update(visible=False), "", "", gr.update(visible=True)
        
        try:
            # Check if clarification is needed
            needs_clarification, questions = await check_and_clarify(query)
            
            if needs_clarification and questions:
                # Show clarification questions, hide run button
                questions_md = "\n".join([f"**{i+1}.** {q}" for i, q in enumerate(questions)])
                return (
                    gr.update(visible=True),  # Show clarification group
                    questions_md,  # Display questions
                    "",  # Clear report
                    gr.update(visible=False)  # Hide run button
                )
            else:
                # Run research directly if no clarification needed
                report_content = ""
                async for chunk in run_research(query):
                    report_content = chunk
                return gr.update(visible=False), "", report_content, gr.update(visible=True)
        except Exception as e:
            gr.Error(f"Error: {str(e)}")
            return gr.update(visible=False), "", "", gr.update(visible=True)
    
    async def handle_continue_research(query, clarifications):
        """Continue research with clarifications"""
        try:
            report_content = ""
            async for chunk in run_research(query, clarifications):
                report_content = chunk
            return gr.update(visible=False), report_content, gr.update(visible=True)
        except Exception as e:
            gr.Error(f"Error: {str(e)}")
            return gr.update(visible=True), "", gr.update(visible=False)
    
    # Event handlers
    run_button.click(
        handle_run_research,
        inputs=[query_textbox],
        outputs=[clarification_group, questions_display, report, run_button]
    )
    
    continue_button.click(
        handle_continue_research,
        inputs=[query_textbox, clarifications_textbox],
        outputs=[clarification_group, report, run_button]
    )
    
    # Enter key starts research
    query_textbox.submit(
        handle_run_research, 
        inputs=[query_textbox], 
        outputs=[clarification_group, questions_display, report, run_button]
    )

ui.launch(inbrowser=True)

