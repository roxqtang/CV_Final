import os
import openai
import user_info
import time
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.schema.runnable import RunnableSequence


from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

#openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"
llm = ChatOpenAI(model="gpt-4", temperature=0.7, max_tokens=200, api_key=openai.api_key)
def process_llm(collected_objects, final_context):
    # Initialize LLMs with specific parameters
    scene_llm = ChatOpenAI(
        temperature=0.3,
        max_tokens=150,
        model="gpt-4",
        api_key=openai.api_key
    )
    
    schedule_llm = ChatOpenAI(
        temperature=0.2,
        max_tokens=200,
        model="gpt-4",
        api_key=openai.api_key
    )
    
    recommendation_llm = ChatOpenAI(
        temperature=0.7,
        max_tokens=200,
        model="gpt-4",
        api_key=openai.api_key
    )
        # Get all necessary user information
    current_time_str, current_datetime = user_info.get_current_time()
    next_events = user_info.get_next_events()  # This includes location, activity, interruptions, solutions
    current_state = user_info.get_user_current_state()
    conservative_goals = user_info.get_user_conservative_goals()
    ambitious_goals = user_info.get_user_ambitious_goals()
    attitude = user_info.get_attitude_for_today()
    most_expected = user_info.get_most_expected_event()
    
    # Get historical data for pattern analysis
    history_today = user_info.get_user_history_today()
    history_past_day = user_info.get_user_history_past_day()
    history_past_week = user_info.get_user_history_past_week()
    history_past_month = user_info.get_user_history_past_month()
    
    # 1. Scene Analysis Chain with enhanced context
    scene_template = """
    As an AI assistant with expertise in Psychology and Human Behavior, analyze the current scene:
    
    Current Context:
    - Time: {current_time}
    - Location: {current_state}
    - Scene Details: {final_context}
    - Detected Objects: {object_list}
    - User's Attitude Today: {attitude}
    - Most Desired Activity: {most_expected}
        Think through this step-by-step:
    1. What is the user currently doing based on the scene and objects?
    2. How does this align with their current location and planned activities?
    3. Are there signs of procrastination (e.g., presence of {most_expected} related items)?
    4. What's the likely psychological state based on:
        - Detected objects
        - Current activity
        - Stated attitude ("{attitude}")
    5. Are there environmental factors helping or hindering focus?
        Provide a concise analysis focusing on:
    - Current activity and psychological state
    - Environmental factors affecting productivity
    - Potential barriers to planned activities
    """
        # 2. Schedule and Goals Analysis Chain with detailed context
    schedule_template = """
    As a Time Management and Project Management expert, analyze the schedule:
    
    Scene Analysis: {scene_analysis}
    Current Situation:
    - Time: {current_time}
    - Next Events: {next_events}
    - Conservative Goals: {conservative_goals}
    
    Historical Context:
    - Today's Progress: {history_today}
    - Past Day Pattern: {history_past_day}
    - Weekly Pattern: {history_past_week}
    
    Think through this step-by-step:
    1. Schedule Analysis:
        - Current time vs next event timing
        - Potential interruptions from event data
        - Available solutions from event data
    
    2. Goal Progress:
        - Conservative goals status
        - Completion patterns from history
        - Risk assessment for remaining tasks
    
    3. Time Management:
        - Buffer time availability
        - Task prioritization needs
        - Interruption mitigation strategies
        Provide structured analysis of:
    - Immediate schedule concerns
    - Goal achievement risks
    - Time management recommendations
    """
        # 3. Flow State and Recommendation Chain with psychological focus
    recommendation_template = """
    As a Psychology and Flow State expert, provide strategic recommendations:
    
    Current Analysis:
    - Scene Assessment: {scene_analysis}
    - Schedule Status: {schedule_analysis}
    
    User Context:
    - Conservative Goals: {conservative_goals}
    - Ambitious Goals: {ambitious_goals}
    - Current State: {current_state}
    - Attitude Today: {attitude}
    - Completion History: {history_patterns}
        Think through this step-by-step:
    1. Flow State Assessment:
        - Current psychological barriers
        - Environmental obstacles
        - Focus enablers/disablers
    
    2. Goal Alignment:
        - Conservative vs ambitious goals
        - Priority adjustments needed
        - Psychological readiness
    
    3. Action Planning:
        - Immediate next steps
        - Environment modifications
        - Psychological preparation
        Provide concise and clear suggestions with max 20 words:
    1. Primary Recommendation: Clear, actionable 2-sentence suggestion
    2. Implementation Steps: How to start, what specific action to take.
    3. If needed, add [update] for current_state
        Format:
    Suggestion: [Primary recommendation]
    Steps: [1. First step 2. Second step 3. Third step]
    [update]: [if needed]
    """
        # Create chains with error handling

    scene_chain = LLMChain(
        llm=scene_llm,
        prompt=PromptTemplate(
            input_variables=["current_time", "current_state", "final_context",
                            "object_list", "attitude", "most_expected"],
            template=scene_template
        ),
        output_key="scene_analysis"
    )
    schedule_chain = LLMChain(
        llm=schedule_llm,
        prompt=PromptTemplate(
            input_variables=["scene_analysis", "current_time", "next_events",
                            "conservative_goals", "history_today",
                            "history_past_day", "history_past_week"],
            template=schedule_template
        ),
        output_key="schedule_analysis",
        verbose=False
    )
    recommendation_chain = LLMChain(
        llm=recommendation_llm,
        prompt=PromptTemplate(
            input_variables=["scene_analysis", "schedule_analysis",
                            "conservative_goals", "ambitious_goals",
                            "current_state", "attitude", "history_patterns"],
            template=recommendation_template
        ),
        output_key="final_recommendation",
        verbose=False
    )
    # Combine chains
    overall_chain = SequentialChain(
        chains=[scene_chain, schedule_chain, recommendation_chain],
        input_variables=["current_time", "current_state", "final_context",
                        "object_list", "attitude", "most_expected", "next_events",
                        "conservative_goals", "ambitious_goals", "history_today",
                        "history_past_day", "history_past_week", "history_patterns"],
        output_variables=["scene_analysis", "schedule_analysis", "final_recommendation"],
        verbose=False
    )
    # Execute chain with comprehensive input
    result = overall_chain({
        "current_time": current_time_str,
        "current_state": current_state,
        "final_context": final_context,
        "object_list": ", ".join([obj['label'] for obj in collected_objects]),
        "attitude": attitude,
        "most_expected": most_expected,
        "next_events": next_events,
        "conservative_goals": conservative_goals,
        "ambitious_goals": ambitious_goals,
        "history_today": history_today,
        "history_past_day": history_past_day,
        "history_past_week": history_past_week,
        "history_patterns": {
            "today": history_today,
            "past_day": history_past_day,
            "past_week": history_past_week,
            "past_month": history_past_month
        }
    })
    return postprocess(result["final_recommendation"])


def preprocess(contexts):
    all_context = "\n".join(contexts)
    system_message = (
        "You are a helpful assistant that summarizes the given context into a concise statement."
    )
    user_message = f"""
Here are the context collected from past 5s, each for 1s:

{all_context}

Please summarize the above context into one concise paragraph no longer than 100 words. Be brief and clear.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message.strip()}
        ],
        max_tokens=100,
        temperature=0.3
    )

    summary = response.choices[0].message.content.strip()
    return summary

def postprocess(llm_output):

    lines = llm_output.split("\n")
    suggestion_lines = []
    update_line = None

    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("[update]:"):
            update_line = line_stripped
            # no need to add to suggestion_lines
        else:
            suggestion_lines.append(line)

    # update if found
    if update_line:
        update_info = update_line.replace("[update]:", "").strip()
        if update_info.startswith("[") and "]" in update_info:
            closing_bracket_idx = update_info.index("]")
            field = update_info[1:closing_bracket_idx]
            new_value = update_info[closing_bracket_idx+1:].strip()

            # check "current_state" field
            if field == "current_state":
                user_info.update_user_state(new_value)
            # possible more fields

    suggestion_text = "\n".join(suggestion_lines).strip()
    return suggestion_text
