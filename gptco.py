import os
import json
import time
import inspect
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import faiss
import numpy as np
from colorama import init, Fore, Style

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

# Import pyautogui for desktop interaction (if needed)
import pyautogui

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

# Define the Agent class with memory and self-improvement capabilities
class Agent(BaseModel):
    name: str
    email: str
    model: str = "gpt-4o"
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
        # Error handling in case embedding retrieval fails
        try:
            response = openai.embeddings.create(
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
            response = openai.embeddings.create(
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

        response = openai.chat.completions.create(
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
        response = openai.chat.completions.create(
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
                    response = openai.embeddings.create(
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

# Email functions
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

# Other tool functions
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

def take_screenshot():
    """
    Takes a screenshot of the current desktop after obtaining explicit user consent.
    """
    consent = input(Fore.YELLOW + "Agent requests to take a screenshot of your desktop. Do you allow this? (yes/no): ").strip().lower()
    if consent == 'yes':
        screenshot = pyautogui.screenshot()
        screenshot_path = f"screenshot_{int(time.time())}.png"
        screenshot.save(screenshot_path)
        print(Fore.GREEN + f"Screenshot saved as {screenshot_path}.")
        return f"Screenshot taken and saved as {screenshot_path}."
    else:
        print(Fore.RED + "Screenshot denied by user.")
        return "Screenshot denied by user."

def perform_desktop_action(action_details: str):
    """
    Performs an action on the desktop after obtaining explicit user consent.
    """
    consent = input(Fore.YELLOW + f"Agent requests to perform a desktop action: {action_details}. Do you allow this? (yes/no): ").strip().lower()
    if consent == 'yes':
        # Placeholder implementation
        print(Fore.GREEN + f"Performing desktop action: {action_details}")
        return f"Desktop action '{action_details}' performed."
    else:
        print(Fore.RED + "Desktop action denied by user.")
        return "Desktop action denied by user."

def plan_tasks(goal: str):
    """
    Helps the agent plan tasks to achieve a goal.
    """
    tasks = [f"Step 1 for {goal}", f"Step 2 for {goal}", f"Step 3 for {goal}"]
    tasks_str = '\n'.join(tasks)  # Convert the list to a string
    print(Fore.GREEN + f"Planned tasks:\n{tasks_str}")
    return tasks_str


def condition_check(condition: str):
    """
    Evaluates a condition and returns 'True' or 'False' as a string.
    """
    result = "True" if condition.lower() == "true" else "False"
    print(Fore.GREEN + f"Condition '{condition}' evaluated to {result}.")
    return result


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



# Define agents with their Purpose Prompt, tools, and memory
# CEO Agent
ceo_agent = Agent(
    name="CEO Agent",
    email="ceo@company.com",
    purpose_prompt=(
        "You are CEO Agent, an AI responsible for setting strategic goals, making high-level decisions, "
        "and overseeing all departments to ensure alignment with the company's vision. "
        "Your primary goal is to lead the company towards growth and innovation. "
        
    ),
    instructions="",  # Inference Prompt will be dynamically generated
    tools=[send_email, check_email, transfer_to_agent, plan_tasks, view_source_code],
)

# Sales Agent
sales_agent = Agent(
    name="Sales Agent",
    email="sales@company.com",
    purpose_prompt=(
        "You are Sales Agent, an AI focused on driving revenue through lead generation and customer engagement. "
        "Your primary goal is to convert leads into sales and maintain strong relationships with clients. "
        "You have access to a tool called 'list_agents' which lists all available agents. "
        
    ),
    instructions="",
    tools=[
        process_sale,
        send_email,
        check_email,
        transfer_to_agent,
        plan_tasks,
        view_source_code,
        # We'll add list_agents later
    ],
)

# Customer Support Agent
customer_support_agent = Agent(
    name="Customer Support Agent",
    email="support@company.com",
    purpose_prompt=(
        "You are Customer Support Agent, an AI agent responsible for managing customer interactions on Discord and via email. "
        "Your primary goal is to provide timely and effective support to enhance customer satisfaction. "
        
    ),
    instructions="",  # Inference Prompt will be dynamically generated
    tools=[handle_customer_inquiry, execute_refund, send_email, check_email, transfer_to_agent, plan_tasks, view_source_code],
)

# Technical Support Agent
technical_support_agent = Agent(
    name="Technical Support Agent",
    email="techsupport@company.com",
    purpose_prompt=(
        "You are Technical Support Agent, an AI responsible for handling technical issues and providing solutions. "
        "Your primary goal is to assist customers with technical problems and escalate to human representatives if necessary. "
        
    ),
    instructions="",  # Inference Prompt will be dynamically generated
    tools=[take_screenshot, perform_desktop_action, escalate_to_human, send_email, check_email, transfer_to_agent, plan_tasks, view_source_code],
)

# Supervisor Agent
supervisor_agent = Agent(
    name="Supervisor Agent",
    email="supervisor@company.com",
    purpose_prompt=(
        "You are Supervisor Agent, responsible for overseeing other agents, ensuring alignment with company goals, "
        "and facilitating communication and collaboration among agents."
    ),
    instructions="",  # Inference Prompt will be dynamically generated
    tools=[send_email, check_email, transfer_to_agent, plan_tasks, escalate_to_human, view_source_code],
)

# Aggregate all agents
agents = {
    "CEO Agent": ceo_agent,
    "Sales Agent": sales_agent,
    "Customer Support Agent": customer_support_agent,
    "Technical Support Agent": technical_support_agent,
    "Supervisor Agent": supervisor_agent,
}

def list_agents():
    """
    Lists all available agents.
    """
    available_agents = ', '.join(agents.keys())  # Join the list into a string
    print(Fore.GREEN + f"Available agents: {available_agents}")
    return available_agents


# Update agents' tools to include list_agents
sales_agent.tools.append(list_agents)
# Optionally, add to other agents
customer_support_agent.tools.append(list_agents)
technical_support_agent.tools.append(list_agents)
supervisor_agent.tools.append(list_agents)
ceo_agent.tools.append(list_agents)

# Load memory for each agent
for agent in agents.values():
    load_agent_memory(agent)

def execute_tool_call(tool_call, tools_map, agent_name, messages):
    global current_agent
    name = tool_call.name
    args = json.loads(tool_call.arguments) if tool_call.arguments else {}
    print(Fore.MAGENTA + f"{agent_name} is executing action: {name}({args})")
    result = tools_map[name](**args)

    # Log the action
    logging.info(f"{agent_name} executed {name} with arguments {args} and result: {result}")

    # Agent reflects on the action
    reflection = f"Executed {name} with arguments {args} and result: {result}"
    current_agent.add_to_memory(reflection)

    # Ensure tool_content is a string
    tool_content = str(result) if result is not None else "Action failed."
    result_message = {
        "role": "function",
        "name": tool_call.name,  # Changed from function_call to tool_call
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

    # Construct the Inference Prompt
    available_tools = [tool.__name__ for tool in agent.tools]
    next_action = agent.purpose_prompt.split('Your next action should be to ')[-1]
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
                model=current_agent.model,
                messages=[{"role": "system", "content": agent_instructions}] + messages,
                functions=tool_schemas,
                function_call="auto",
            )
        except Exception as e:
            print(Fore.RED + "An error occurred while communicating with the OpenAI API.")
            print(f"Error code: {e}")
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



# Main loop to run the automated company
def main():
    global current_agent
    # Start with the Sales Agent
    current_agent = sales_agent
    messages = []

    print(Fore.GREEN + "Automated Company Simulation Started.")
    print("Type 'exit' to terminate the simulation.\n")

    while True:
        user_input = input(Fore.YELLOW + "User: " + Style.RESET_ALL)
        if user_input.lower() == "exit":
            print(Fore.GREEN + "Terminating the simulation.")
            break

        messages.append({"role": "user", "content": user_input})

        response = run_full_turn(current_agent, messages)
        messages = response.messages
        current_agent = response.agent

if __name__ == "__main__":
    main()
