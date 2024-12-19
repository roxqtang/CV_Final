import os
import openai
import user_info
import time
from langchain.llms import OpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
CUR_TIME = time.strftime("%Y-%m-%d %H:%M")  

def process_llm(collected_objects, final_context):
    objects_detected = [obj['label'] for obj in collected_objects]
    object_list = ", ".join(objects_detected) if objects_detected else "no objects detected"
    top_priorities_today = user_info.get_user_top_priorities_today()
    current_time = time.strftime("%Y-%m-%d %H:%M")
    target_date = user_info.get_user_target_date()
    current_state = user_info.get_user_current_state()
    hobbies = user_info.get_user_hobbies()
    preferences = user_info.get_user_preferences()
    schedules = user_info.get_user_schedule()
    
    
    # Pre-designed prompt
    system_message = (
        f"""
        You are a helpful assistant that provides concise suggestions
        basd on user's history and the current scene understanding.
        You response will contain two parts: 1. suggestion 2. proposed update
        For suggestion part, use natural smooth human-like language style.
        For proposed update part,
        If you see a mismatch between current_state and scene context, propose
        an update using the following format. For example:
        [update]: [current_state] walking on street

        Your proposed update should consider only the discrepancy between
        user profile and what we saw the last 5s, not including your own suggestion.
        """
    )
    
    user_message = f"""
User Profile:
[current_state]: {current_state}
[top_priorities_today]: {top_priorities_today}
[preferences]: {preferences}
[schedules]: {schedules}

Here are what we saw the last 5s:
Scene Context: {final_context}
Detected Objects: {object_list}

Given the user state and schedule, provide a suggestion relevant to the user's current situation no longer than 2 sentences.
Keep the suggestion concise.
Pay attention to the current time: {current_time} and the target date: {target_date} and event times:
If you think the user_state should change based on current state, you can append an [update] line as described.
Return only the suggestions and optional [update] line, no other info.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message.strip()}
        ],
        max_tokens=200,
        temperature=0.7
    )
    llm_suggestion = response.choices[0].message.content.strip()
    print(f"llm_suggestion: {llm_suggestion}")
    llm_suggestion = postprocess(llm_suggestion)
    return llm_suggestion


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
        max_tokens=200,
        temperature=0.7
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
