# gptco

# GPT-Co: Automated Company Simulation

**GPT-Co** is an automated company simulation that leverages OpenAI's GPT models to create interactive agents representing different roles within a company. Users can interact with these agents to simulate business processes, customer interactions, and internal communications.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Agents](#agents)
- [Tools](#tools)
- [Project Status](#project-status)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multiple Agents**: Simulate a company environment with agents like CEO, Sales Agent, Customer Support Agent, Technical Support Agent, and Supervisor Agent.
- **Interactive Communication**: Users can interact with agents, and agents can transfer conversations to other agents as needed.
- **Agent Memory**: Agents have short-term and long-term memory capabilities using embeddings and FAISS indexes.
- **Self-Improvement**: Agents can reflect on their actions to improve future performance.
- **Tool Functions**: Agents have access to various tools/functions to perform tasks like sending emails, processing sales, and more.
- **Agent Transfer**: Agents can transfer conversations to other agents based on user requests.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/gptco.git
   cd gptco
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   - Create a `.env` file in the project root directory.
   - Add your OpenAI API key to the `.env` file:

     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Usage

Run the main script to start the simulation:

```bash
python gptco6.py
```

- The simulation starts with the Sales Agent.
- Type your messages to interact with the agents.
- Type `'exit'` to terminate the simulation.

## Agents

### CEO Agent

- **Email**: ceo@company.com
- **Role**: Sets strategic goals and oversees all departments.
- **Tools**: `send_email`, `check_email`, `transfer_to_agent`, `plan_tasks`, `view_source_code`, `list_agents`

### Sales Agent

- **Email**: sales@company.com
- **Role**: Focuses on driving revenue through lead generation and customer engagement.
- **Tools**: `process_sale`, `send_email`, `check_email`, `transfer_to_agent`, `plan_tasks`, `view_source_code`, `list_agents`

### Customer Support Agent

- **Email**: support@company.com
- **Role**: Manages customer interactions and provides support to enhance customer satisfaction.
- **Tools**: `handle_customer_inquiry`, `execute_refund`, `send_email`, `check_email`, `transfer_to_agent`, `plan_tasks`, `view_source_code`, `list_agents`

### Technical Support Agent

- **Email**: techsupport@company.com
- **Role**: Handles technical issues and provides solutions.
- **Tools**: `take_screenshot`, `perform_desktop_action`, `escalate_to_human`, `send_email`, `check_email`, `transfer_to_agent`, `plan_tasks`, `view_source_code`, `list_agents`

### Supervisor Agent

- **Email**: supervisor@company.com
- **Role**: Oversees other agents and ensures alignment with company goals.
- **Tools**: `send_email`, `check_email`, `transfer_to_agent`, `plan_tasks`, `escalate_to_human`, `view_source_code`, `list_agents`

## Tools

Agents have access to various tools/functions to perform tasks:

- `send_email(recipient: str, subject: str, body: str)`
- `check_email()`
- `process_sale(customer_id: str, product_id: str, amount: float)`
- `handle_customer_inquiry(customer_id: str, inquiry: str)`
- `execute_refund(customer_id: str, product_id: str, reason: str)`
- `escalate_to_human(summary: str)`
- `transfer_to_agent(agent_name: str)`
- `take_screenshot()`
- `perform_desktop_action(action_details: str)`
- `plan_tasks(goal: str)`
- `view_source_code(section: str = "all")`
- `list_agents()`

## Project Status

**Current Progress**

- **Core Functionality Implemented**: The basic framework for agent interaction, memory management, and tool usage is in place.
- **Agent Transfer Working**: Agents can transfer conversations to other agents based on user requests.
- **Memory and Reflection**: Agents can store short-term and long-term memories and perform self-reflection to improve future actions.
- **Function Execution and Messaging**: Agents can execute functions/tools and appropriately respond to users.

**Known Issues**

- **API Method Corrections Needed**: Some OpenAI API method calls need to be updated to the correct methods (e.g., `openai.Embedding.create` instead of `openai.embeddings.create`).
- **Model Name Correction**: Ensure that the model names used (e.g., `"gpt-4o"`) are valid OpenAI model names like `"gpt-3.5-turbo"` or `"gpt-4"`.
- **Function Return Types**: Functions should return strings to avoid API errors related to message content types.
- **Infinite Loop Prevention**: Adjustments are needed to prevent agents from entering infinite loops when calling functions.
- **Error Handling**: Improve error handling for API calls and function executions.

**Next Steps**

- **Bug Fixes**: Address the known issues listed above to ensure smooth operation.
- **Testing**: Perform thorough testing to validate agent interactions and functionality.
- **Enhancements**: Consider adding more agents, tools, and features to enrich the simulation.
- **Documentation**: Expand the README with more detailed setup instructions and examples.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests to help improve the project.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Note**: This project uses the OpenAI API and requires an API key. Please ensure you comply with OpenAI's usage policies and terms of service when using this software.
