import requests
import openai
import speech_recognition as sr
import pyttsx3
from flask import Flask, request, jsonify
import logging
import os
import threading
import concurrent.futures
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_httpauth import HTTPTokenAuth

# Initialize Flask application
app = Flask(__name__)

# Set up rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

# Set up HTTP token authentication
auth = HTTPTokenAuth(scheme='Bearer')

# Authorized tokens (example)
AUTHORIZED_TOKENS = {
    "example_token_1": "user1",
    "example_token_2": "user2"
}

@auth.verify_token
def verify_token(token):
    return AUTHORIZED_TOKENS.get(token)

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Set up logging for tracking events
logging.basicConfig(filename='company_log.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

def speak_text(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# Function to perform a web search
def web_search(query):
    headers = {
        "Ocp-Apim-Subscription-Key": os.getenv('BING_API_KEY')
    }
    search_url = f"https://api.bing.microsoft.com/v7.0/search?q={query}"
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        results = response.json()
        snippets = [entry['snippet'] for entry in results.get("webPages", {}).get("value", [])]
        return "\n".join(snippets[:3])
    except requests.RequestException as e:
        logging.error(f"Web search failed: {e}")
        return "No relevant web search results found."

# Function for role-based GPT interaction
def round_table_discussion(goal, roles):
    discussions = {}
    context = ""
    lock = threading.Lock()

    def get_role_input(role):
        nonlocal context
        search_query = f"{role} advice on achieving goal: {goal}"
        web_context = web_search(search_query)

        prompt = f"You are a {role} GPT. The current context is: '{context}'. The goal is: '{goal}'. Here is additional context from the web: '{web_context}'. Provide your input on how to achieve this goal."
        response = openai.Completion.create(
            engine="gpt-4o",
            prompt=prompt,
            max_tokens=200
        )
        response_text = response.choices[0].text.strip()
        with lock:
            discussions[role] = response_text
            context += f"\n{role}: {response_text}"
            logging.info(f"{role} GPT provided input: {response_text}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_role_input, role) for role in roles]
        concurrent.futures.wait(futures)

    return discussions

# Functions for different types of GPT inputs
def vision_gpt(goal):
    prompt = f"You are a vision GPT. You have received visual information related to the goal: '{goal}'. Describe the relevant visual context to support decision making."
    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

def text_input_gpt(text_input):
    prompt = f"You are a text input GPT. You have received the following information: '{text_input}'. Send it to decision making."
    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

def voice_input_gpt(voice_input_text):
    prompt = f"You are a voice input GPT. You have received the following spoken information: '{voice_input_text}'. Summarize and Send it to decision making."
    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Function for the central brain GPT to process inputs
def brain_gpt(goal, vision_input, text_input, voice_input):
    prompt = f"You are the central brain GPT. The goal is: '{goal}'. Here is input from vision: '{vision_input}', text: '{text_input}', and voice: '{voice_input}'. Make a strategic decision based on this combined information."
    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=prompt,
        max_tokens=300
    )
    return response.choices[0].text.strip()

# Function to gather inputs and make a decision
def gather_inputs_and_decide(goal, text_input, voice_input_text):
    vision_input = vision_gpt(goal)
    processed_text_input = text_input_gpt(text_input)
    processed_voice_input = voice_input_gpt(voice_input_text)

    decision = brain_gpt(goal, vision_input, processed_text_input, processed_voice_input)
    logging.info(f"Brain GPT made a decision: {decision}")

    output_type_prompt = f"You are an output coordinator GPT. The decision is: '{decision}'. Should the output be delivered as text, voice, or a visual representation using DALL-E? Provide a reason for your choice."
    output_response = openai.Completion.create(
        engine="gpt-4o",
        prompt=output_type_prompt,
        max_tokens=100
    )
    output_decision = output_response.choices[0].text.strip().lower()
    logging.info(f"Output coordinator decided on output type: {output_decision}")

    try:
        if "voice" in output_decision:
            speak_text(decision)
            output_result = "Voice output delivered."
        elif "visual" in output_decision or "dall-e" in output_decision:
            dalle_prompt = f"Create an image that represents the following decision: '{decision}'"
            dalle_response = openai.Image.create(
                prompt=dalle_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = dalle_response['data'][0]['url']
            output_result = f"Visual representation created: {image_url}"
        else:
            output_result = f"Text output: {decision}"
    except openai.error.OpenAIError as e:
        logging.error(f"Failed to generate output: {e}")
        output_result = "Failed to generate output."

    logging.info(f"Output result: {output_result}")

    return output_result

# Flask routes to handle API requests
@app.route('/gather_inputs_and_decide', methods=['POST'])
@auth.login_required
@limiter.limit("10 per minute")
def api_gather_inputs_and_decide():
    data = request.get_json()
    goal = data.get('goal')
    text_input = data.get('text_input', '')
    voice_input_text = data.get('voice_input_text', '')

    result = gather_inputs_and_decide(goal, text_input, voice_input_text)

    return jsonify({"result": result}), 200

@app.route('/round_table', methods=['POST'])
@auth.login_required
@limiter.limit("10 per minute")
def api_round_table():
    data = request.get_json()
    goal = data.get('goal')
    roles = data.get('roles', ['Sales', 'Marketing', 'Finance'])

    discussions = round_table_discussion(goal, roles)

    return jsonify({"round_table_discussion": discussions}), 200

if __name__ == '__main__':
    app.run(debug=True)
