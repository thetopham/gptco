import os
import json
import time
import inspect
import logging
import subprocess
import requests
import smtplib
import sqlite3
import base64
import sys
from email.mime.text import MIMEText
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import faiss
import numpy as np
from colorama import init, Fore, Style
import pyautogui
from flask import Flask, request, jsonify

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(filename='agent_logs.log', level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

# Global variable to keep track of the current agent
current_agent = None

# Email system simulation
email_storage = {}  # Dictionary to store emails for each agent

# Function to convert Python functions to function schemas compatible with OpenAI API
def function_to_schema(func) -> dict:
    sig = inspect.signature(func)
    parameters = {}
    for name, param in sig.parameters.items():
        param_type = param.annotation if param.annotation != inspect._empty else str
        # Map Python types to JSON Schema types
        type_map = {
            str: 'string',
            int: 'integer',
            float: 'number',
            bool: 'boolean',
            list: 'array',
            dict: 'object',
            type(None): 'null',
        }
        json_type = type_map.get(param_type, 'string')
        parameters[name] = {"type": json_type}

    return {
        "name": func.__name__,
        "description": func.__doc__.strip() if func.__doc__ else "No description provided",
        "parameters": {
            "type": "object",
            "properties": parameters,
            "required": list(parameters.keys()),
        },
    }

# Define additional tool functions

# 1. File System Access
def read_file(file_path: str):
    """Reads the content of a file."""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    except Exception as e:
        return str(e)

def write_file(file_path: str, content: str):
    """Writes content to a file."""
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return f"Content written to '{file_path}'."
    except Exception as e:
        return str(e)

def list_directory(directory_path: str):
    """Lists files and directories in a given directory."""
    try:
        items = os.listdir(directory_path)
        return items
    except FileNotFoundError:
        return f"Directory '{directory_path}' not found."
    except Exception as e:
        return str(e)

# 2. Internet Access
def fetch_url(url: str):
    """Fetches the content of a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return str(e)

# 3. Command Execution
def execute_shell_command(command: str):
    """Executes a shell command in a safe manner."""
    # Define a list of allowed commands for safety
    allowed_commands = ['ls', 'echo', 'pwd', 'whoami']
    cmd = command.split()[0]
    if cmd in allowed_commands:
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5)
            return result.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return f"Error: {e.output.decode('utf-8')}"
        except Exception as e:
            return str(e)
    else:
        return "Command not allowed for safety reasons."

# 4. Interacting with Applications
def open_application(application_path: str):
    """Opens an application."""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(application_path)
        elif os.name == 'posix':  # Unix/Linux/MacOS
            subprocess.Popen(['open', application_path] if sys.platform == 'darwin' else ['xdg-open', application_path])
        else:
            return "Unsupported OS."
        return f"Application '{application_path}' opened."
    except Exception as e:
        return str(e)

def click_at(x: int, y: int):
    """Simulates a mouse click at the given coordinates."""
    try:
        pyautogui.click(x, y)
        return f"Clicked at ({x}, {y})."
    except Exception as e:
        return str(e)

# 5. Real Email Integration
def send_real_email(recipient_email: str, subject: str, body: str):
    """Sends an actual email."""
    try:
        sender_email = current_agent.email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # SMTP server configuration
        smtp_server = os.getenv('SMTP_SERVER')  # e.g., 'smtp.gmail.com'
        smtp_port = os.getenv('SMTP_PORT')      # e.g., 587
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')

        if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
            return "SMTP server details are not fully configured in the .env file."

        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return f"Email sent to {recipient_email}."
    except Exception as e:
        return str(e)

# 6. Enhancing Memory and Learning
def store_data(key: str, value: str):
    """Stores data in a persistent database."""
    try:
        conn = sqlite3.connect('agent_data.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)')
        cursor.execute('REPLACE INTO data (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()
        return f"Data stored under key '{key}'."
    except Exception as e:
        return str(e)

def retrieve_data(key: str):
    """Retrieves data from the persistent database."""
    try:
        conn = sqlite3.connect('agent_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM data WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return f"No data found for key '{key}'."
    except Exception as e:
        return str(e)

# 6a. Supervisor Agent's access to store and retrieve data (Previously Unused)
def supervisor_store_data(key: str, value: str):
    """Supervisor Agent stores data."""
    return store_data(key, value)

def supervisor_retrieve_data(key: str):
    """Supervisor Agent retrieves data."""
    return retrieve_data(key)

# 7. Image Handling
def upload_image(image_path: str):
    """
    Encodes an image to Base64 and returns the string.
    This allows the image to be included in prompts.
    """
    try:
        with open(image_path, 'rb') as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
        return encoded_string
    except FileNotFoundError:
        return f"Image '{image_path}' not found."
    except Exception as e:
        return str(e)

def include_image_in_prompt(image_path: str):
    """
    Encodes the image and returns a markdown image tag.
    """
    encoded_image = upload_image(image_path)
    if "not found" in encoded_image or "Error" in encoded_image:
        return encoded_image
    markdown_image = f"![Screenshot](data:image/jpeg;base64,{encoded_image})"
    return markdown_image

# 8. Image Upload to GPT
def upload_image_to_gpt(image_path: str):
    """
    Encodes an image to Base64 and uploads it to the GPT model to get a description.
    """
    import base64
    import requests

    # OpenAI API Key (ensure it's set in the environment variables)
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "OpenAI API key not found in environment variables."

    # Function to encode the image
    def encode_image(image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            return f"Image '{image_path}' not found."
        except Exception as e:
            return str(e)

    # Getting the base64 string
    base64_image = encode_image(image_path)
    if base64_image.startswith("Image") or "Error" in base64_image:
        return base64_image  # Return the error message

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",  # Corrected model name
        "messages": [
            {
                "role": "user",
                "content": "Describe the contents of this image.",
            },
            {
                "role": "user",
                "content": f"data:image/jpeg;base64,{base64_image}"
            }
        ],
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"

# 9. Screenshot Function with Image Upload
def take_screenshot_and_analyze():
    """
    Takes a screenshot of the current desktop after obtaining explicit user consent,
    saves it, uploads it, and includes the description in the agent's memory.
    """
    consent = input(Fore.YELLOW + "Agent requests to take a screenshot of your desktop. Do you allow this? (yes/no): ").strip().lower()
    if consent == 'yes':
        try:
            screenshot = pyautogui.screenshot()
            screenshot_path = f"screenshot_{int(time.time())}.png"
            screenshot.save(screenshot_path)
            print(Fore.GREEN + f"Screenshot saved as {screenshot_path}.")

            # Upload the image to GPT and get the description
            upload_response = upload_image_to_gpt(screenshot_path)
            if isinstance(upload_response, dict):
                # Assuming the description is needed to be returned
                description = upload_response.get('choices', [{}])[0].get('message', {}).get('content', "No description available.")
                # Add the image description to memory
                current_agent.add_to_memory(f"Screenshot taken: {description}")
                return f"Screenshot taken and description added to memory."
            else:
                # If an error occurred
                return upload_response
        except Exception as e:
            return str(e)
    else:
        print(Fore.RED + "Screenshot denied by user.")
        return "Screenshot denied by user."

# 10. Condition Check Function (Previously Unused)
def is_task_complete(task_description: str) -> bool:
    """
    Evaluates whether a given task is complete based on the description.
    """
    # Placeholder for actual condition evaluation logic
    # For demonstration, we'll assume tasks containing 'complete' are done
    return 'complete' in task_description.lower()

# 11. Plan Tasks Function
def plan_tasks(goal: str):
    """
    Helps the agent plan tasks to achieve a goal.
    """
    tasks = [f"Step 1 for {goal}", f"Step 2 for {goal}", f"Step 3 for {goal}"]
    tasks_str = '\n'.join(tasks)  # Convert the list to a string
    print(Fore.GREEN + f"Planned tasks:\n{tasks_str}")
    return tasks_str

# 12. Condition Check Function (Previously Defined as condition_check, Renamed for Clarity)
def condition_check(condition: str):
    """
    Evaluates a condition and returns 'True' or 'False' as a string.
    """
    result = "True" if condition.lower() == "true" else "False"
    print(Fore.GREEN + f"Condition '{condition}' evaluated to {result}.")
    return result

# 13. View Source Code Function (Improved)
def view_source_code(section: str = "all"):
    """
    Returns the agent's own source code. Specify 'all' for full code or a section name.
    """
    # Limit the amount of code returned to prevent exceeding context length
    max_characters = 1500  # Adjust as needed
    try:
        with open(__file__, 'r') as f:
            code = f.read()
        if section != "all":
            # Extract specific sections if needed
            pattern = rf"def {section}\(.*?\n(?:    .*\n)*"
            import re
            match = re.search(pattern, code)
            if match:
                code = match.group(0)
            else:
                code = f"Section '{section}' not found."
        code = code[:max_characters] + "..." if len(code) > max_characters else code
        return code
    except Exception as e:
        logging.error(f"Failed to read source code. Error: {str(e)}")
        return "Error reading source code."

# 14. Agent Class Definition
class Agent(BaseModel):
    name: str
    email: str
    model: str = "gpt-4o"  # Updated model name
    purpose_prompt: str  # Purpose Prompt: role, goal, next action
    instructions: str  # Inference Prompt will be dynamically generated
    tools: List
    short_term_memory: List[str] = []  # Short-term memory
    long_term_memory_index: Any = None  # FAISS index for long-term memory
    long_term_memory_data: List[str] = []  # Data corresponding to the FAISS index
    reward: float = 0.0  # Accumulated reward

    def add_to_memory(self, content: str):
        """Adds content to both short-term and long-term memory using embeddings."""
        self.short_term_memory.append(content)
        # Limit short-term memory to the last 100 entries
        if len(self.short_term_memory) > 100:
            self.short_term_memory = self.short_term_memory[-100:]
        # Error handling in case embedding retrieval fails
        try:
            response = openai.embeddings.create(  # Corrected method name
                input=content,
                model="text-embedding-ada-002"
            )
            embedding = response['data'][0]['embedding']
            embedding = np.array(embedding, dtype=np.float32)
        except Exception as e:
            logging.error(f"Failed to generate embedding for memory: {content}. Error: {str(e)}")
            return

        if self.long_term_memory_index is None:
            self.long_term_memory_index = faiss.IndexFlatL2(len(embedding))
            self.long_term_memory_data = []

        self.long_term_memory_index.add(np.array([embedding]))
        self.long_term_memory_data.append(content)

    def retrieve_memory(self, query: str):
        """Retrieves relevant memories using FAISS based on a query."""
        if self.long_term_memory_index is None:
            return []

        try:
            response = openai.embeddings.create(  # Corrected method name
                input=query,
                model="text-embedding-ada-002"
            )
            embedding = response['data'][0]['embedding']
            embedding = np.array(embedding, dtype=np.float32)
            D, I = self.long_term_memory_index.search(np.array([embedding]), k=5)
            results = [self.long_term_memory_data[i] for i in I[0] if i < len(self.long_term_memory_data)]
            return results
        except Exception as e:
            logging.error(f"Failed to retrieve memory for query: {query}. Error: {str(e)}")
            return []

    def self_reflect(self):
        """
        Reflect on recent actions to improve future performance.
        """
        recent_memories = self.short_term_memory[-5:]  # Get the last 5 memories
        reflection_prompt = (
            f"As {self.name}, reflect on your recent actions:\n"
            + "\n".join(recent_memories)
            + "\nWhat can you learn to improve future actions?"
        )

        response = openai.chat.completions.create(  # Corrected method name
            model=self.model,
            messages=[{"role": "system", "content": reflection_prompt}],
        )

        insights = response.choices[0].message.content
        print(Fore.BLUE + f"{self.name} reflection: {insights}")
        # Store reflection in memory
        self.add_to_memory(f"Reflection: {insights}")

        # Optionally, update the purpose_prompt
        update_prompt = (
            f"Based on your reflection, update your purpose prompt to better achieve your goals.\n"
            f"Current purpose prompt: {self.purpose_prompt}"
        )
        response = openai.chat.completions.create(  # Corrected method name
            model=self.model,
            messages=[{"role": "system", "content": update_prompt}],
        )
        new_purpose_prompt = response.choices[0].message.content
        print(Fore.BLUE + f"{self.name} updated purpose prompt: {new_purpose_prompt}")
        self.purpose_prompt = new_purpose_prompt

    def adjust_behavior(self):
        """
        Adjust behavior based on accumulated rewards.
        """
        threshold = 1.0  # Define a threshold for reward adjustment
        if self.reward > threshold:
            print(Fore.GREEN + f"{self.name} received positive reward. Reinforcing successful strategies.")
            # Implement positive adjustments
            pass
        elif self.reward < -threshold:
            print(Fore.RED + f"{self.name} received negative reward. Reevaluating strategies.")
            # Implement negative adjustments
            pass
        # Reset reward
        self.reward = 0.0

    def communicate(self, other_agent: 'Agent', message: str):
        """
        Send a message to another agent.
        """
        other_agent.receive_message(self.name, message)

    def receive_message(self, sender_name: str, message: str):
        """
        Receive a message from another agent.
        """
        print(Fore.CYAN + f"{self.name} received a message from {sender_name}: {message}")
        # Process the message
        self.add_to_memory(f"Message from {sender_name}: {message}")

# Function to save agent memory to a file
def save_agent_memory(agent: Agent):
    filename = f"{agent.name.replace(' ', '_').lower()}_memory.json"
    memory_data = {
        'short_term_memory': agent.short_term_memory,
        'long_term_memory_data': agent.long_term_memory_data,
    }
    with open(filename, 'w') as f:
        json.dump(memory_data, f)

# Function to load agent memory from a file
def load_agent_memory(agent: Agent):
    filename = f"{agent.name.replace(' ', '_').lower()}_memory.json"
    try:
        with open(filename, 'r') as f:
            memory_data = json.load(f)
            agent.short_term_memory = memory_data.get('short_term_memory', [])
            agent.long_term_memory_data = memory_data.get('long_term_memory_data', [])
            # Rebuild the FAISS index
            if agent.long_term_memory_data:
                embeddings = []
                for content in agent.long_term_memory_data:
                    response = openai.embeddings.create(  # Corrected method name
                        input=content,
                        model="text-embedding-ada-002"
                    )
                    embedding = response['data'][0]['embedding']
                    embeddings.append(embedding)
                embeddings = np.array(embeddings, dtype=np.float32)
                agent.long_term_memory_index = faiss.IndexFlatL2(len(embeddings[0]))
                agent.long_term_memory_index.add(embeddings)
            else:
                agent.long_term_memory_index = None
    except FileNotFoundError:
        agent.short_term_memory = []
        agent.long_term_memory_index = None
        agent.long_term_memory_data = []

# Email functions (existing)
def send_email(recipient: str, subject: str, body: str):
    """
    Sends an email to the specified recipient.
    """
    sender = current_agent.email
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    email = {
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "timestamp": timestamp,
    }

    # Add the email to the recipient's inbox
    if recipient in email_storage:
        email_storage[recipient].append(email)
    else:
        email_storage[recipient] = [email]

    print(Fore.GREEN + f"Email sent to {recipient} with subject '{subject}'.")
    return f"Email sent to {recipient} with subject '{subject}'."

def check_email():
    """
    Checks the agent's inbox for new emails.
    """
    inbox = email_storage.get(current_agent.email, [])
    if not inbox:
        print(Fore.YELLOW + "Your inbox is empty.")
        return "Your inbox is empty."

    # Display emails
    print(Fore.CYAN + f"Emails for {current_agent.name}:")
    for idx, email in enumerate(inbox, 1):
        print(Fore.MAGENTA + f"Email {idx}:")
        print(Fore.MAGENTA + f"From: {email['sender']}")
        print(Fore.MAGENTA + f"Subject: {email['subject']}")
        print(Fore.MAGENTA + f"Body: {email['body']}")
        print(Fore.MAGENTA + f"Timestamp: {email['timestamp']}")
        print("-" * 40)

    return f"You have {len(inbox)} email(s) in your inbox."

# Other tool functions (existing)
def process_sale(customer_id: str, product_id: str, amount: float):
    """
    Processes a sale by recording the transaction.
    """
    print(Fore.GREEN + f"Processing sale for customer {customer_id} purchasing product {product_id} for ${amount}.")
    return f"Sale processed for customer {customer_id} purchasing product {product_id} for ${amount}."

def handle_customer_inquiry(customer_id: str, inquiry: str):
    """
    Handles customer inquiries and provides solutions.
    """
    print(Fore.GREEN + f"Handling inquiry from customer {customer_id}: {inquiry}")
    return f"Inquiry from customer {customer_id} addressed."

def execute_refund(customer_id: str, product_id: str, reason: str):
    """
    Executes a refund for a customer.
    """
    print(Fore.GREEN + f"Executing refund for customer {customer_id} on product {product_id} due to {reason}.")
    return f"Refund executed for customer {customer_id} on product {product_id}."

def escalate_to_human(summary: str):
    """
    Escalates the issue to a human representative.
    """
    print(Fore.YELLOW + "Escalating to human representative...")
    print(f"Summary: {summary}")
    return "Issue escalated to human representative."

def transfer_to_agent(agent_name: str):
    """
    Transfers the conversation to another agent.
    """
    print(Fore.YELLOW + f"Transfer requested to {agent_name}.")

    # Normalize agent names to lowercase without spaces for comparison
    normalized_agents = {key.lower().replace(' ', ''): agents[key] for key in agents}
    normalized_agent_name = agent_name.lower().replace(' ', '')

    if normalized_agent_name in normalized_agents:
        return normalized_agents[normalized_agent_name]
    else:
        print(Fore.RED + f"Agent '{agent_name}' not found.")
        return None

# List Agents Function
def list_agents():
    """
    Lists all available agents.
    """
    available_agents = ', '.join(agents.keys())  # Join the list into a string
    print(Fore.GREEN + f"Available agents: {available_agents}")
    return available_agents

# Define agents with their Purpose Prompt, tools, and memory

# CEO Agent
ceo_agent = Agent(
    name="CEO Agent",
    email="ceo@company.com",
    purpose_prompt=(
        "You are the CEO Agent, an expert in strategic leadership and high-level decision-making. "
        "Your expertise lies in setting the company's vision, establishing long-term goals, "
        "and ensuring all departments align with the overarching objectives. "
        "You possess comprehensive knowledge of all operational functions and utilize your extensive toolset "
        "to drive the company towards sustained growth and innovation. "
        "Your professionalism and mastery in leadership enable you to oversee and optimize every facet of the organization."
    ),
    instructions="",  # Inference Prompt will be dynamically generated
    tools=[
        send_email,          # Communicate strategic decisions and updates
        check_email,         # Monitor incoming communications for critical information
        transfer_to_agent,   # Delegate tasks to appropriate agents
        plan_tasks,          # Develop strategic plans to achieve company goals
        view_source_code,    # Review and audit internal processes and tools
        read_file,           # Access and analyze company documents
        write_file,          # Create and update strategic documents
        list_directory,      # Manage and organize company resources
        fetch_url,           # Gather external market data and insights
        execute_shell_command,  # Perform system-level operations if necessary
        open_application,    # Utilize software tools for strategic planning
        click_at,            # Automate interactions with applications for efficiency
        send_real_email,     # Communicate with external stakeholders
        store_data,          # Save strategic data and insights
        retrieve_data,       # Access stored data for informed decision-making
        upload_image,        # Share visual reports and infographics
        include_image_in_prompt,  # Enhance communications with visual aids
        supervisor_store_data,    # Manage data storage with Supervisor Agent
        supervisor_retrieve_data  # Access data managed by Supervisor Agent
    ],
)

# Sales Agent
sales_agent = Agent(
    name="Sales Agent",
    email="sales@company.com",
    purpose_prompt=(
        "You are the Sales Agent, a specialist in revenue generation and customer relationship management. "
        "Your expertise encompasses lead generation, sales conversions, and maintaining robust relationships with clients. "
        "You are adept at utilizing your comprehensive toolset to identify potential leads, engage with customers, "
        "and close sales effectively. Your professionalism and in-depth knowledge of sales strategies enable you "
        "to drive the company's revenue growth and expand its market presence."
    ),
    instructions="",  # Inference Prompt will be dynamically generated
    tools=[
        process_sale,        # Execute and record sales transactions
        send_email,          # Communicate with leads and clients
        check_email,         # Monitor client communications and inquiries
        transfer_to_agent,   # Delegate specific sales tasks to other agents if needed
        plan_tasks,          # Develop sales strategies and campaigns
        view_source_code,    # Review and optimize sales tools and scripts
        read_file,           # Access sales reports and client data
        write_file,          # Update sales records and documentation
        list_directory,      # Organize sales resources and materials
        fetch_url,           # Research market trends and competitor activities
        execute_shell_command,  # Automate sales-related system tasks
        open_application,    # Utilize CRM and sales software effectively
        click_at,            # Automate interactions with sales platforms
        send_real_email,     # Engage with external clients and partners
        store_data,          # Save client information and sales data
        retrieve_data,       # Access stored client and sales information
        upload_image,        # Share sales presentations and visual data
        include_image_in_prompt  # Enhance sales pitches with visual content
    ],
)

# Customer Support Agent
customer_support_agent = Agent(
    name="Customer Support Agent",
    email="support@company.com",
    purpose_prompt=(
        "You are the Customer Support Agent, an expert in managing and resolving customer interactions on platforms like Discord and email. "
        "Your proficiency includes addressing customer inquiries, providing effective solutions, and ensuring high levels of customer satisfaction. "
        "Utilizing your extensive toolset, you efficiently handle support tickets, process refunds, and escalate issues when necessary. "
        "Your professionalism and deep understanding of customer service best practices enable you to enhance the company's reputation and customer loyalty."
    ),
    instructions="",  # Inference Prompt will be dynamically generated
    tools=[
        handle_customer_inquiry,  # Address and resolve customer questions and issues
        execute_refund,           # Process refund requests efficiently
        send_email,               # Communicate with customers regarding their support cases
        check_email,              # Monitor incoming support requests and updates
        transfer_to_agent,        # Escalate complex issues to appropriate agents
        plan_tasks,               # Organize support workflows and tasks
        view_source_code,         # Review support tools and scripts for optimization
        read_file,                # Access customer data and support logs
        write_file,               # Document support interactions and resolutions
        list_directory,           # Manage support resources and knowledge bases
        fetch_url,                # Research solutions and gather information to assist customers
        execute_shell_command,    # Automate support-related system tasks
        open_application,         # Utilize support software and CRM tools effectively
        click_at,                 # Automate interactions with support platforms
        send_real_email,          # Engage with external customers and partners
        store_data,               # Save customer interactions and support data
        retrieve_data,            # Access stored customer information and support history
        upload_image,             # Share visual guides and troubleshooting steps
        include_image_in_prompt   # Enhance support communications with visual aids
    ],
)

# Technical Support Agent
technical_support_agent = Agent(
    name="Technical Support Agent",
    email="techsupport@company.com",
    purpose_prompt=(
        "You are the Technical Support Agent, a specialist in diagnosing and resolving technical issues. "
        "Your expertise covers a wide range of technical problems, from software glitches to hardware malfunctions. "
        "Leveraging your comprehensive toolset, you efficiently troubleshoot issues, provide actionable solutions, "
        "and escalate complex problems to human representatives when necessary. "
        "Your professionalism and deep technical knowledge ensure that customers receive prompt and effective support, "
        "maintaining the company's operational excellence and customer satisfaction."
    ),
    instructions="",  # Inference Prompt will be dynamically generated
    tools=[
        take_screenshot_and_analyze,  # Capture and analyze system screenshots for diagnostics
        escalate_to_human,            # Escalate unresolved technical issues to human experts
        send_email,                   # Communicate with customers regarding their technical support cases
        check_email,                  # Monitor incoming technical support requests and updates
        transfer_to_agent,            # Delegate specific technical tasks to other agents if needed
        plan_tasks,                   # Organize technical support workflows and tasks
        view_source_code,             # Review technical support tools and scripts for optimization
        read_file,                    # Access technical documentation and support logs
        write_file,                   # Document technical interactions and resolutions
        list_directory,               # Manage technical support resources and knowledge bases
        fetch_url,                    # Research solutions and gather information to assist customers
        execute_shell_command,        # Automate technical support-related system tasks
        open_application,             # Utilize technical support software and diagnostic tools effectively
        click_at,                     # Automate interactions with technical platforms
        send_real_email,              # Engage with external customers and partners
        store_data,                   # Save technical interactions and support data
        retrieve_data,                # Access stored technical information and support history
        upload_image,                 # Share technical diagrams and troubleshooting visuals
        include_image_in_prompt,      # Enhance technical support communications with visual aids
        upload_image_to_gpt            # Analyze and describe system screenshots for diagnostics
    ],
)

# Supervisor Agent
supervisor_agent = Agent(
    name="Supervisor Agent",
    email="supervisor@company.com",
    purpose_prompt=(
        "You are the Supervisor Agent, an authority in overseeing and coordinating the activities of other agents. "
        "Your expertise includes ensuring all agents align with company objectives, facilitating effective communication, "
        "and optimizing inter-departmental collaboration. "
        "Utilizing your extensive toolset, you monitor agent performance, manage data storage and retrieval, "
        "and ensure that all operations run smoothly and efficiently. "
        "Your professionalism and comprehensive knowledge empower you to maintain organizational excellence and drive the company's success."
    ),
    instructions="",  # Inference Prompt will be dynamically generated
    tools=[
        send_email,                  # Communicate with all agents and external stakeholders
        check_email,                 # Monitor communications for oversight and coordination
        transfer_to_agent,           # Delegate tasks and reassign responsibilities as needed
        plan_tasks,                  # Develop and oversee strategic plans for agent activities
        escalate_to_human,           # Escalate critical issues that require human intervention
        view_source_code,            # Review and audit agent tools and processes for optimization
        read_file,                   # Access organizational data and reports
        write_file,                  # Document supervisory decisions and guidelines
        list_directory,              # Manage organizational resources and documentation
        fetch_url,                   # Gather external data and insights for supervisory decisions
        execute_shell_command,       # Perform system-level operations for maintenance and oversight
        open_application,            # Utilize supervisory software and tools effectively
        click_at,                    # Automate interactions with supervisory platforms
        send_real_email,             # Engage with external partners and higher management
        store_data,                  # Save organizational data and supervisory insights
        retrieve_data,               # Access stored data for informed decision-making
        upload_image,                # Share organizational charts and strategic visuals
        include_image_in_prompt,     # Enhance supervisory communications with visual aids
        supervisor_store_data,       # Manage data storage specifically for supervisory purposes
        supervisor_retrieve_data     # Access data managed by Supervisor Agent for oversight
    ],
)

# Aggregate all agents
agents = {
    "CEO Agent": ceo_agent,
    "Sales Agent": sales_agent,
    "Customer Support Agent": customer_support_agent,
    "Technical Support Agent": technical_support_agent,
    "Supervisor Agent": supervisor_agent,
}

# Add list_agents to each agent's tools
for agent in agents.values():
    agent.tools.append(list_agents)


# Load memory for each agent
for agent in agents.values():
    load_agent_memory(agent)

def execute_tool_call(tool_call, tools_map, agent_name, messages):
    global current_agent
    name = tool_call.name  # Use attribute access
    args = json.loads(tool_call.arguments) if tool_call.arguments else {}
    print(Fore.MAGENTA + f"{agent_name} is executing action: {name}({args})")
    if name in tools_map:
        result = tools_map[name](**args)
    else:
        result = f"Tool '{name}' not found."

    # Log the action
    logging.info(f"{agent_name} executed {name} with arguments {args} and result: {result}")

    # Agent reflects on the action
    reflection = f"Executed {name} with arguments {args} and result: {result}"
    current_agent.add_to_memory(reflection)

    # Handle specific tool responses
    if name == "upload_image_to_gpt":
        # Process the JSON response from the image upload
        if isinstance(result, dict) and 'choices' in result:
            try:
                description = result['choices'][0]['message']['content']
                tool_content = f"Image Description: {description}"
            except (KeyError, IndexError):
                tool_content = "Failed to retrieve image description."
        else:
            tool_content = result  # Error message or other string

    else:
        # Ensure tool_content is a string
        tool_content = str(result) if result is not None else "Action failed."

    result_message = {
        "role": "function",
        "name": tool_call.name,
        "content": tool_content,
    }
    messages.append(result_message)

    # Handle agent transfer
    if isinstance(result, Agent):
        # Agent handoff
        return result  # Return the new agent
    else:
        return None  # No agent transfer

# Response class to hold agent and messages
class Response(BaseModel):
    agent: Optional[Agent]
    messages: List[Dict]

# Helper function to trim messages
def trim_messages(messages: List[Dict], max_messages: int = 50) -> List[Dict]:
    """
    Trims the messages list to retain only the most recent 'max_messages' entries.
    """
    if len(messages) > max_messages:
        return messages[-max_messages:]
    return messages

# Optional: Summarize older messages
def summarize_messages(messages: List[Dict], summary_length: int = 5) -> List[Dict]:
    """
    Summarizes older messages to retain context without exceeding token limits.
    """
    if len(messages) <= 100:
        return messages
    
    # Extract messages to summarize
    messages_to_summarize = messages[:-75]  # Summarize messages older than the last 75
    if not messages_to_summarize:
        return messages

    # Create a summary prompt
    summary_prompt = (
        "Summarize the following conversation to capture the key points and context:\n\n"
        + "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages_to_summarize])
    )
    
    # Get the summary from the model
    try:
        summary_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=500,  # Adjust based on desired summary length
        )
        summary = summary_response.choices[0].message.content.strip()
        
        # Create a summarized message
        summarized_message = {
            "role": "system",
            "content": f"Summary of earlier conversation:\n{summary}"
        }
        
        # Retain the last 75 messages and add the summary
        new_messages = messages[-75:] + [summarized_message]
        return new_messages
    except Exception as e:
        logging.error(f"Failed to summarize messages. Error: {str(e)}")
        # If summarization fails, proceed without it
        return messages

# The main function to run the interaction loop
def run_full_turn(agent: Agent, messages: List[Dict]) -> Response:
    global current_agent
    current_agent = agent
    num_init_messages = len(messages)
    messages = messages.copy()

    # Include agent's memory in the system prompt
    if agent.short_term_memory:
        memory_prompt = "\n".join([f"- {entry}" for entry in agent.short_term_memory[-5:]])
        messages.insert(1, {"role": "system", "content": f"Your memory:\n{memory_prompt}"})

    # Trim or summarize messages to prevent exceeding context length
    if len(messages) > 100:  # Define a threshold based on testing
        messages = summarize_messages(messages, summary_length=5)  # Summarize older messages
    else:
        messages = trim_messages(messages, max_messages=50)  # Trim to the last 50 messages

    # Construct the Inference Prompt
    available_tools = [tool.__name__ for tool in agent.tools]
    next_action = agent.purpose_prompt.split('Your primary goal is to ')[-1]
    inference_prompt = (
        f"You have the following list of available actions/tools: {available_tools}. "
        f"Based on your next action, which is '{next_action}', "
        f"determine the best tool to execute. Provide a brief rationale for your choice."
    )

    # Set the agent's instructions to include both the Purpose Prompt and Inference Prompt
    agent_instructions = f"{agent.purpose_prompt}\n\n{inference_prompt}"

    while True:
        # Convert tools to schemas
        tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
        tools_map = {tool.__name__: tool for tool in current_agent.tools}

        # Get the agent's response
        try:
            response = openai.chat.completions.create(
                model=current_agent.model,  # Use the updated model
                messages=[{"role": "system", "content": agent_instructions}] + messages,
                functions=tool_schemas,
                function_call="auto",
            )
        except Exception as e:
            print(Fore.RED + "An error occurred while communicating with the OpenAI API.")
            print(f"Error: {str(e)}")
            return Response(agent=current_agent, messages=messages)

        # Access the content of the response properly
        message = response.choices[0].message
        if message.content:
            print(Fore.CYAN + f"{current_agent.name}: " + Style.RESET_ALL + message.content)
            # Store the content into memory
            current_agent.add_to_memory(f"{current_agent.name}: {message.content}")

        if message.function_call:
            function_call = message.function_call
            result = execute_tool_call(function_call, tools_map, current_agent.name, messages)

            if result:
                # Agent handoff
                print(Fore.YELLOW + f"Transferring to {result.name}...\n")
                current_agent = result  # Update current agent
                # Inform the agent of the handoff
                messages.append({
                    "role": "system",
                    "content": f"You have been transferred to {current_agent.name}. Adopt the new role immediately."
                })
                break  # Break to start over with the new agent
        else:
            break  # No function calls, end the loop

        # Agent self-reflection and behavior adjustment
        current_agent.self_reflect()
        current_agent.adjust_behavior()

        # Save agent memory after each turn
        save_agent_memory(current_agent)

    return Response(agent=current_agent, messages=messages[num_init_messages:])

# Flask app for Agent APIs (Scaling Communication Between Agents)
app = Flask(__name__)

# Redirect Flask's logs to a separate file to prevent cluttering the main console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Set to ERROR to reduce verbosity

@app.route('/agent_action', methods=['POST'])
def agent_action():
    data = request.get_json()
    action = data.get('action')
    params = data.get('params', {})
    # Execute the action
    result = execute_agent_action(action, params)
    return jsonify({'result': result})

def execute_agent_action(action, params):
    # Map action to function and execute
    action_map = {
        'send_real_email': send_real_email,
        'read_file': read_file,
        'write_file': write_file,
        'list_directory': list_directory,
        'fetch_url': fetch_url,
        'execute_shell_command': execute_shell_command,
        'open_application': open_application,
        'click_at': click_at,
        'store_data': store_data,
        'retrieve_data': retrieve_data,
        'upload_image': upload_image,
        'include_image_in_prompt': include_image_in_prompt,
        'upload_image_to_gpt': upload_image_to_gpt,  # Added the new action
        # Add other actions here
    }
    if action in action_map:
        return action_map[action](**params)
    else:
        return f"Action '{action}' not recognized."

# Start the Flask app in a separate thread if needed
import threading

def start_flask():
    app.run(port=5000)

flask_thread = threading.Thread(target=start_flask, daemon=True)
flask_thread.start()

# Implementing the Screenshot-Analyze-Action Loop
def screenshot_analyze_action_loop(task_description: str):
    """
    Implements the loop: Take screenshot, analyze, perform action, check completion.
    Repeats until the task is complete.
    """
    while True:
        # Take a screenshot and analyze it
        result = take_screenshot_and_analyze()
        print(Fore.GREEN + result)

        # Retrieve the latest description from memory
        if current_agent.long_term_memory_data:
            latest_description = current_agent.long_term_memory_data[-1]
            print(Fore.BLUE + f"Latest Description: {latest_description}")

            # Check if the task is complete
            if is_task_complete(latest_description):
                print(Fore.GREEN + "Task is complete.")
                current_agent.add_to_memory("Task completed successfully.")
                break
            else:
                print(Fore.YELLOW + "Task is not complete. Continuing the loop.")
                current_agent.add_to_memory("Task not complete. Continuing actions.")
        else:
            print(Fore.RED + "No description available to evaluate task completion.")
            break

        # Optional: Wait for a short duration before the next iteration
        time.sleep(2)

# The main loop to run the automated company
def main():
    global current_agent
    # Start with the Sales Agent
    current_agent = sales_agent
    messages = []

    print(Fore.GREEN + "Automated Company Started.")
    print("Type 'exit' to terminate the simulation.\n")

    while True:
        try:
            user_input = input(Fore.YELLOW + "User: " + Style.RESET_ALL)
        except EOFError:
            # Handle unexpected EOF (e.g., Ctrl+D)
            print(Fore.GREEN + "\nTerminating the simulation.")
            break
        if user_input.lower() == "exit":
            print(Fore.GREEN + "Terminating the simulation.")
            break

        messages.append({"role": "user", "content": user_input})

        # Check if the user input is a command to start the screenshot-analyze-action loop
        if user_input.lower().startswith("start task:"):
            task_description = user_input[len("start task:"):].strip()
            print(Fore.BLUE + f"Starting task: {task_description}")
            current_agent.add_to_memory(f"Starting task: {task_description}")
            screenshot_analyze_action_loop(task_description)
            continue  # Skip the normal turn after starting the task

        response = run_full_turn(current_agent, messages)
        messages = response.messages
        current_agent = response.agent

        # Save agent memory after each turn
        save_agent_memory(current_agent)

        # Optional: Handle self-reflection and behavior adjustment after each turn
        current_agent.self_reflect()
        current_agent.adjust_behavior()

if __name__ == "__main__":
    main()
