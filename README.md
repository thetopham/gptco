
# gpt-co - work in Progress

**gpt-co** is an automated company simulation that leverages OpenAI's GPT models to create interactive agents representing different roles within a company. Users can interact with these agents to simulate business processes, customer interactions, internal communications, and more. Each agent is a master of their craft, equipped with a specialized set of tools to efficiently achieve both user and organizational goals.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Agents](#agents)
- [Tools](#tools)
- [Screenshot-Analyze-Action Loop](#screenshot-analyze-action-loop)
- [Project Status](#project-status)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multiple Specialized Agents**: Simulate a company environment with agents like CEO, Sales Agent, Customer Support Agent, Technical Support Agent, and Supervisor Agent.
- **Interactive Communication**: Users can interact with agents, and agents can transfer conversations to other agents as needed.
- **Advanced Memory Management**: Agents possess both short-term and long-term memory capabilities using embeddings and FAISS indexes, enabling them to recall and utilize past interactions effectively.
- **Self-Improvement Mechanisms**: Agents can reflect on their actions to improve future performance, ensuring continuous optimization of their tasks.
- **Comprehensive Toolsets**: Each agent is equipped with a specialized set of tools/functions tailored to their role, enabling them to perform tasks such as sending emails, processing sales, handling customer inquiries, and more.
- **Agent Transfer and Coordination**: Agents can seamlessly transfer conversations to other agents based on user requests or task requirements, ensuring efficient task management and resolution.
- **Automated Task Loops**: Implement sophisticated loops like the Screenshot-Analyze-Action Loop for tasks requiring iterative actions and validations.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/thetopham/gptco.git
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
   - Add your OpenAI API key and SMTP server details to the `.env` file:

     ```
     OPENAI_API_KEY=your_openai_api_key_here
     SMTP_SERVER=your_smtp_server_here
     SMTP_PORT=your_smtp_port_here
     SMTP_USERNAME=your_smtp_username_here
     SMTP_PASSWORD=your_smtp_password_here
     ```

     > **Note**: Ensure that your SMTP credentials are kept secure and never hard-coded into the script.

## Usage

Run the main script to start the simulation:

```bash
python gptco.py
```

- **Starting Point**: The simulation starts with the **Sales Agent** by default.
- **Interacting with Agents**: Type your messages to interact with the agents.
- **Initiating Tasks**: Use commands like `start task: <task_description>` to initiate specialized task loops.
- **Exiting the Simulation**: Type `exit` to terminate the simulation gracefully.

### Example Commands

- **General Interaction**:

  ```
  User: Hello, Sales Agent!
  ```

- **Starting a Task**:

  ```
  User: start task: Increase sales.
  ```

## Agents

### CEO Agent

- **Email**: ceo@company.com
- **Role**: Sets strategic goals and oversees all departments to ensure alignment with the company's vision.
- **Purpose Prompt**:
  
  ```
  You are the CEO Agent, an expert in strategic leadership and high-level decision-making. Your expertise lies in setting the company's vision, establishing long-term goals, and ensuring all departments align with the overarching objectives. You possess comprehensive knowledge of all operational functions and utilize your extensive toolset to drive the company towards sustained growth and innovation. Your professionalism and mastery in leadership enable you to oversee and optimize every facet of the organization.
  ```
  
- **Tools**:
  - `send_email`: Communicate strategic decisions and updates.
  - `check_email`: Monitor incoming communications for critical information.
  - `transfer_to_agent`: Delegate tasks to appropriate agents.
  - `plan_tasks`: Develop strategic plans to achieve company goals.
  - `view_source_code`: Review and audit internal processes and tools.
  - `read_file`: Access and analyze company documents.
  - `write_file`: Create and update strategic documents.
  - `list_directory`: Manage and organize company resources.
  - `fetch_url`: Gather external market data and insights.
  - `execute_shell_command`: Perform system-level operations if necessary.
  - `open_application`: Utilize software tools for strategic planning.
  - `click_at`: Automate interactions with applications for efficiency.
  - `send_real_email`: Communicate with external stakeholders.
  - `store_data`: Save strategic data and insights.
  - `retrieve_data`: Access stored data for informed decision-making.
  - `upload_image`: Share visual reports and infographics.
  - `include_image_in_prompt`: Enhance communications with visual aids.
  - `supervisor_store_data`: Manage data storage with Supervisor Agent.
  - `supervisor_retrieve_data`: Access data managed by Supervisor Agent.
  - `list_agents`: View all available agents.

### Sales Agent

- **Email**: sales@company.com
- **Role**: Focuses on driving revenue through lead generation and customer engagement.
- **Purpose Prompt**:
  
  ```
  You are the Sales Agent, a specialist in revenue generation and customer relationship management. Your expertise encompasses lead generation, sales conversions, and maintaining robust relationships with clients. You are adept at utilizing your comprehensive toolset to identify potential leads, engage with customers, and close sales effectively. Your professionalism and in-depth knowledge of sales strategies enable you to drive the company's revenue growth and expand its market presence.
  ```
  
- **Tools**:
  - `process_sale`: Execute and record sales transactions.
  - `send_email`: Communicate with leads and clients.
  - `check_email`: Monitor client communications and inquiries.
  - `transfer_to_agent`: Delegate specific sales tasks to other agents if needed.
  - `plan_tasks`: Develop sales strategies and campaigns.
  - `view_source_code`: Review and optimize sales tools and scripts.
  - `read_file`: Access sales reports and client data.
  - `write_file`: Update sales records and documentation.
  - `list_directory`: Organize sales resources and materials.
  - `fetch_url`: Research market trends and competitor activities.
  - `execute_shell_command`: Automate sales-related system tasks.
  - `open_application`: Utilize CRM and sales software effectively.
  - `click_at`: Automate interactions with sales platforms.
  - `send_real_email`: Engage with external clients and partners.
  - `store_data`: Save client information and sales data.
  - `retrieve_data`: Access stored client and sales information.
  - `upload_image`: Share sales presentations and visual data.
  - `include_image_in_prompt`: Enhance sales pitches with visual content.
  - `list_agents`: View all available agents.

### Customer Support Agent

- **Email**: support@company.com
- **Role**: Manages customer interactions and provides support to enhance customer satisfaction.
- **Purpose Prompt**:
  
  ```
  You are the Customer Support Agent, an expert in managing and resolving customer interactions on platforms like Discord and email. Your proficiency includes addressing customer inquiries, providing effective solutions, and ensuring high levels of customer satisfaction. Utilizing your extensive toolset, you efficiently handle support tickets, process refunds, and escalate issues when necessary. Your professionalism and deep understanding of customer service best practices enable you to enhance the company's reputation and customer loyalty.
  ```
  
- **Tools**:
  - `handle_customer_inquiry`: Address and resolve customer questions and issues.
  - `execute_refund`: Process refund requests efficiently.
  - `send_email`: Communicate with customers regarding their support cases.
  - `check_email`: Monitor incoming support requests and updates.
  - `transfer_to_agent`: Escalate complex issues to appropriate agents.
  - `plan_tasks`: Organize support workflows and tasks.
  - `view_source_code`: Review support tools and scripts for optimization.
  - `read_file`: Access customer data and support logs.
  - `write_file`: Document support interactions and resolutions.
  - `list_directory`: Manage support resources and knowledge bases.
  - `fetch_url`: Research solutions and gather information to assist customers.
  - `execute_shell_command`: Automate support-related system tasks.
  - `open_application`: Utilize support software and CRM tools effectively.
  - `click_at`: Automate interactions with support platforms.
  - `send_real_email`: Engage with external customers and partners.
  - `store_data`: Save customer interactions and support data.
  - `retrieve_data`: Access stored customer information and support history.
  - `upload_image`: Share visual guides and troubleshooting steps.
  - `include_image_in_prompt`: Enhance support communications with visual aids.
  - `list_agents`: View all available agents.

### Technical Support Agent

- **Email**: techsupport@company.com
- **Role**: Handles technical issues and provides solutions.
- **Purpose Prompt**:
  
  ```
  You are the Technical Support Agent, a specialist in diagnosing and resolving technical issues. Your expertise covers a wide range of technical problems, from software glitches to hardware malfunctions. Leveraging your comprehensive toolset, you efficiently troubleshoot issues, provide actionable solutions, and escalate complex problems to human representatives when necessary. Your professionalism and deep technical knowledge ensure that customers receive prompt and effective support, maintaining the company's operational excellence and customer satisfaction.
  ```
  
- **Tools**:
  - `take_screenshot_and_analyze`: Capture and analyze system screenshots for diagnostics.
  - `upload_image_to_gpt`: Analyze and describe system screenshots for diagnostics.
  - `escalate_to_human`: Escalate unresolved technical issues to human experts.
  - `send_email`: Communicate with customers regarding their technical support cases.
  - `check_email`: Monitor incoming technical support requests and updates.
  - `transfer_to_agent`: Delegate specific technical tasks to other agents if needed.
  - `plan_tasks`: Organize technical support workflows and tasks.
  - `view_source_code`: Review technical support tools and scripts for optimization.
  - `read_file`: Access technical documentation and support logs.
  - `write_file`: Document technical interactions and resolutions.
  - `list_directory`: Manage technical support resources and knowledge bases.
  - `fetch_url`: Research solutions and gather information to assist customers.
  - `execute_shell_command`: Automate technical support-related system tasks.
  - `open_application`: Utilize technical support software and diagnostic tools effectively.
  - `click_at`: Automate interactions with technical platforms.
  - `send_real_email`: Engage with external customers and partners.
  - `store_data`: Save technical interactions and support data.
  - `retrieve_data`: Access stored technical information and support history.
  - `upload_image`: Share technical diagrams and troubleshooting visuals.
  - `include_image_in_prompt`: Enhance technical support communications with visual aids.
  - `list_agents`: View all available agents.

### Supervisor Agent

- **Email**: supervisor@company.com
- **Role**: Oversees other agents and ensures alignment with company goals.
- **Purpose Prompt**:
  
  ```
  You are the Supervisor Agent, an authority in overseeing and coordinating the activities of other agents. Your expertise includes ensuring all agents align with company objectives, facilitating effective communication, and optimizing inter-departmental collaboration. Utilizing your extensive toolset, you monitor agent performance, manage data storage and retrieval, and ensure that all operations run smoothly and efficiently. Your professionalism and comprehensive knowledge empower you to maintain organizational excellence and drive the company's success.
  ```
  
- **Tools**:
  - `send_email`: Communicate with all agents and external stakeholders.
  - `check_email`: Monitor communications for oversight and coordination.
  - `transfer_to_agent`: Delegate tasks and reassign responsibilities as needed.
  - `plan_tasks`: Develop and oversee strategic plans for agent activities.
  - `escalate_to_human`: Escalate critical issues that require human intervention.
  - `view_source_code`: Review and audit agent tools and processes for optimization.
  - `read_file`: Access organizational data and reports.
  - `write_file`: Document supervisory decisions and guidelines.
  - `list_directory`: Manage organizational resources and documentation.
  - `fetch_url`: Gather external data and insights for supervisory decisions.
  - `execute_shell_command`: Perform system-level operations for maintenance and oversight.
  - `open_application`: Utilize supervisory software and tools effectively.
  - `click_at`: Automate interactions with supervisory platforms.
  - `send_real_email`: Engage with external partners and higher management.
  - `store_data`: Save organizational data and supervisory insights.
  - `retrieve_data`: Access stored data for informed decision-making.
  - `upload_image`: Share organizational charts and strategic visuals.
  - `include_image_in_prompt`: Enhance supervisory communications with visual aids.
  - `supervisor_store_data`: Manage data storage specifically for supervisory purposes.
  - `supervisor_retrieve_data`: Access data managed by Supervisor Agent for oversight.
  - `list_agents`: View all available agents.

## Tools

Agents have access to a variety of tools/functions to perform their tasks effectively. Each tool is designed to align with the agent's role and responsibilities.

### Communication Tools

- **send_email(recipient: str, subject: str, body: str)**
  - Sends an email to the specified recipient.
  
- **send_real_email(recipient_email: str, subject: str, body: str)**
  - Sends an actual email using SMTP configurations.

- **check_email()**
  - Checks the agent's inbox for new emails.

- **transfer_to_agent(agent_name: str)**
  - Transfers the conversation to another agent based on the agent's name.

### Data Management Tools

- **store_data(key: str, value: str)**
  - Stores data in a persistent database.

- **retrieve_data(key: str)**
  - Retrieves data from the persistent database.

- **supervisor_store_data(key: str, value: str)**
  - Supervisor Agent stores data.

- **supervisor_retrieve_data(key: str)**
  - Supervisor Agent retrieves data.

### File System Tools

- **read_file(file_path: str)**
  - Reads the content of a file.

- **write_file(file_path: str, content: str)**
  - Writes content to a file.

- **list_directory(directory_path: str)**
  - Lists files and directories in a given directory.

### Internet Tools

- **fetch_url(url: str)**
  - Fetches the content of a URL.

### System Tools

- **execute_shell_command(command: str)**
  - Executes a shell command in a safe manner.

- **open_application(application_path: str)**
  - Opens an application.

- **click_at(x: int, y: int)**
  - Simulates a mouse click at the given coordinates.

### Image Handling Tools

- **upload_image(image_path: str)**
  - Encodes an image to Base64 and returns the string for inclusion in prompts.

- **include_image_in_prompt(image_path: str)**
  - Encodes the image and returns a markdown image tag.

- **upload_image_to_gpt(image_path: str)**
  - Encodes an image to Base64 and uploads it to the GPT model to get a description.

### Support Tools

- **handle_customer_inquiry(customer_id: str, inquiry: str)**
  - Handles customer inquiries and provides solutions.

- **execute_refund(customer_id: str, product_id: str, reason: str)**
  - Executes a refund for a customer.

- **process_sale(customer_id: str, product_id: str, amount: float)**
  - Processes a sale by recording the transaction.

- **escalate_to_human(summary: str)**
  - Escalates the issue to a human representative.

### Planning and Coordination Tools

- **plan_tasks(goal: str)**
  - Helps the agent plan tasks to achieve a goal.

- **view_source_code(section: str = "all")**
  - Returns the agent's own source code. Specify 'all' for full code or a section name.

- **list_agents()**
  - Lists all available agents.

## Screenshot-Analyze-Action Loop

One of the advanced features of GPT-Co is the **Screenshot-Analyze-Action Loop**, implemented to handle tasks that require iterative actions and validations. Here's how it works:

1. **Take Screenshot and Analyze**:
   - The agent requests user consent to take a screenshot.
   - Upon approval, it captures the current desktop state.
   - The screenshot is uploaded to GPT for analysis, generating a description.

2. **Perform Action Based on Analysis**:
   - Using the description, the agent determines the necessary actions to address the task.

3. **Check Task Completion**:
   - The agent evaluates whether the task is complete based on the analysis.
   - If incomplete, the loop repeats, allowing the agent to take further actions until the task is fulfilled.

### How to Initiate

To start the **Screenshot-Analyze-Action Loop**, use the following command within the simulation:

```
start task: <your_task_description>
```

**Example**:

```
start task: Monitor the desktop for unauthorized access attempts.
```

The agent will then enter the loop, performing the necessary steps until the task is marked as complete.

## Project Status

### Current Progress

- **Core Functionality Implemented**: The foundational framework for agent interaction, memory management, and tool usage is fully operational.
- **Agent Transfer Working**: Agents can transfer conversations to other agents based on user requests and task requirements.
- **Advanced Memory and Reflection**: Agents can store short-term and long-term memories, perform self-reflection, and adjust behaviors to improve performance.
- **Comprehensive Tool Execution**: Agents can execute a wide range of tools/functions tailored to their roles, ensuring effective task management and resolution.
- **Automated Task Loops**: Implemented sophisticated loops like the Screenshot-Analyze-Action Loop for tasks requiring iterative actions and validations.
- **Supervisor Agent Enhancements**: Added specialized data management tools (`supervisor_store_data`, `supervisor_retrieve_data`) to the Supervisor Agent's toolset.

### Known Issues

- **Function Return Types**: Ensure that all functions return strings to prevent API errors related to message content types.
- **Infinite Loop Prevention**: Implement safeguards to prevent agents from entering infinite loops when calling functions.
- **Error Handling Enhancements**: Improve error handling for API calls and function executions to ensure robustness.
- **Security Considerations**: Further secure tool functions, especially those interacting with the file system and executing shell commands, to prevent potential misuse.

### Next Steps

- **Bug Fixes**: Address the known issues listed above to enhance stability and reliability.
- **Extensive Testing**: Conduct thorough testing to validate agent interactions, tool executions, and overall system performance.
- **Feature Enhancements**: Introduce additional agents, tools, and functionalities to enrich the simulation and expand its capabilities.
- **Documentation Improvements**: Expand the README and in-code documentation with more detailed setup instructions, usage examples, and troubleshooting guides.
- **Security Enhancements**: Implement stricter access controls and validation mechanisms for tool functions to bolster security.

## Contributing

Contributions are highly encouraged! Whether it's reporting issues, suggesting features, or submitting pull requests, your input helps improve GPT-Co. Please follow these guidelines:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeatureName
   ```

5. **Open a Pull Request**

Please ensure that your contributions adhere to the project's coding standards and include relevant documentation and tests where applicable.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Note**: This project utilizes the OpenAI API and requires an API key. Ensure compliance with OpenAI's [usage policies](https://openai.com/policies/usage-policies) and [terms of service](https://openai.com/policies/terms-of-service) when using this software. Additionally, handle SMTP credentials securely and avoid exposing sensitive information.

## Acknowledgements

- **OpenAI**: For providing the powerful GPT models that drive the intelligence behind GPT-Co.
- **FAISS**: For enabling efficient similarity search and clustering of dense vectors.
- **Colorama**: For enhancing terminal text with colors, improving readability.
- **Flask**: For facilitating API endpoints to manage agent actions and communications.

---

Feel free to reach out or contribute to make GPT-Co even more robust and feature-rich!
