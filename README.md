# Autonomous PR Reviewer with LangGraph

## Author Information

- Developer: Srihari Swain
- Email: srihariswain2001@gmail.com
- GitHub: https://github.com/srihari-swain

## Project Overview

This project implements an autonomous PR (Pull Request) review system using LangGraph and LangChain. It automates the process of reviewing GitHub pull requests by analyzing code changes, identifying potential issues, and generating review comments using AI-powered analysis.

## Key Features

- **RESTful API**: Built with FastAPI for high-performance and easy integration
- **Automated PR Analysis**: Fetches and analyzes pull requests from GitHub MCP
- **AI-Powered Code Review**: Uses GPT-4o to analyze code changes and identify potential issues
- **Structured Workflow**: Implements a state machine using LangGraph for managing the review process
- **Intelligent Decision Making**: Provides merge recommendations based on code quality and review findings
- **Detailed Reporting**: Generates comprehensive review summaries with actionable feedback
- **Asynchronous Processing**: Handles multiple PR reviews concurrently with async/await

## Project Structure

```
autonomous-pr-reviewer/
├── src/
│   ├── agents/                     # Agent implementations
│   │   ├── code_analyzer_agent/     # Analyzes code changes using AI
│   │   ├── decision_maker_agent/    # Makes merge decisions using ReAct
│   │   ├── pr_retriever_agent/      # Fetches PR metadata
│   │   └── pr_reviewer_agent/       # Generates review comments
│   │
│   ├── comms/server/             # API server implementation
│   │   └── rest_api/               # REST API endpoints
│   │       ├── api.py              # FastAPI application and routes
│   │
│   ├── orchestrator/              # Workflow orchestration
│   │   └── agent_orchestrator.py    # Main workflow definition using LangGraph
│   │
│   ├── schema/                   # Data models and schemas
│   ├── tools/                     # Utility tools
│   │   ├── github_mcp_tool.py     # GitHub API integration
│   │   └── react_tool.py          # ReAct agent utilities
│   │
│   └── main.py                   # Application entry point
│
├── .env                         # Environment variables
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Core Features

### PR Analysis
- Fetches PR metadata including title, description, and author information
- Retrieves detailed file changes with additions and deletions
- Analyzes commit history for better context understanding

### Code Review
- AI-powered code analysis using GPT-4o
- Identifies potential bugs and security vulnerabilities
- Detects code smells and anti-patterns
- Provides actionable improvement suggestions

### Workflow
- State-based workflow orchestration using LangGraph
- Conditional execution paths based on PR content
- Detailed logging and progress tracking
- Configurable review thresholds and rules

### Decision Making
- ReAct-based decision making for merge recommendations
- Risk assessment of code changes
- Clear justification for review decisions
- Configurable approval criteria

## Agent Architecture

The system is built using a LangGraph-based workflow with specialized agents that work together to review pull requests:

### 1. PR Retriever Agent
- **Location**: `src/agents/pr_retriever_agent/`
- **Responsibility**: Fetches PR metadata and changes from GitHub
- **Key Features**:
  - Retrieves PR metadata (title, description, author)
  - Fetches changed files with detailed diff information
  - Collects commit history and related metadata
  - Handles GitHub API rate limiting and pagination

### 2. Code Analyzer Agent
- **Location**: `src/agents/code_analyzer_agent/`
- **Responsibility**: Performs in-depth analysis of code changes
- **Key Features**:
  - Uses GPT-4o for intelligent code analysis
  - Identifies potential bugs and security vulnerabilities
  - Detects code smells and anti-patterns
  - Provides specific improvement suggestions
  - Categorizes issues by severity (High/Medium/Low)

### 3. PR Reviewer Agent
- **Location**: `src/agents/pr_reviewer_agent/`
- **Responsibility**: Generates actionable review comments
- **Key Features**:
  - Creates detailed, context-aware review comments
  - Suggests specific code improvements
  - Asks clarifying questions when needed
  - Formats feedback for clear communication

### 4. Decision Maker Agent
- **Location**: `src/agents/decision_maker_agent/`
- **Responsibility**: Makes final merge decisions
- **Key Features**:
  - Implements ReAct (Reasoning and Acting) pattern
  - Considers code quality metrics and review feedback
  - Provides clear justification for decisions
  - Can be configured with project-specific rules
  - Handles edge cases and ambiguous situations

## Workflow

The workflow is implemented as a state machine in `agent_orchestrator.py` and follows these steps:

1. **Initialization**
   - Load environment variables and configuration
   - Initialize all required agents and tools
   - Set up the LangGraph workflow

2. **PR Data Retrieval**
   - Fetch PR metadata from GitHub
   - Retrieve file changes and diffs
   - Collect commit history and related information

3. **Code Analysis**
   - Analyze each changed file using AI
   - Identify potential issues and improvements
   - Categorize findings by severity

4. **Review Generation**
   - Generate actionable review comments
   - Provide specific improvement suggestions
   - Ask clarifying questions when needed

5. **Decision Making**
   - Evaluate the PR based on analysis and reviews
   - Make a merge/reject decision
   - Provide clear justification for the decision

6. **Reporting**
   - Generate a comprehensive review summary
   - Format output for readability
   - Provide final recommendations

## Setup and Installation

### Core Dependencies

- Python 3.8+
- Go 1.16+ (for MCP server)
- FastAPI: Modern, fast web framework for building APIs
- Uvicorn: ASGI server for FastAPI
- LangChain: Framework for building LLM applications
- LangGraph: For workflow orchestration
- python-dotenv: Environment variable management
- PyGithub: GitHub API client
- OpenAI: For GPT-4o integration
- Pydantic: Data validation and settings management
- GitHub MCP Server: For GitHub API interactions

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account with access to the target repositories
- An OpenAI API key with access to GPT-4o

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/srihari-swain/autonomous-pr-reviewer-agent.git
   cd autonomous-pr-reviewer-agent
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root with the following variables:
   ```bash
   # Required
   GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
   OPENAI_API_KEY=your_openai_api_key
   
   # Optional
   # LOG_LEVEL=INFO  # Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   # MAX_CONCURRENT_REQUESTS=5  # Limit concurrent API requests
   ```

5. **Verify installation**:
   ```bash
   python -c "import langchain; print(f'LangChain version: {langchain.__version__}')
   ```
## Configuration

### GitHub Integration

1. **Generate a GitHub Personal Access Token**:
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with the following scopes:
     - `repo` (full control of private repositories)
     - `read:org` (read organization and team membership)
     - `read:user` (read user profile data)

2. **Configure Target Repository**:
   - Update the following variables in `src/orchestrator/agent_orchestrator.py`:
     ```python
     REPO_OWNER = "your-username"  # Repository owner
     REPO_NAME = "your-repo"       # Repository name
     # PR number will be automatically fetched or can be specified
     ```
## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Go 1.16+ (for MCP server)
- Git
- A GitHub account with access to the target repositories
- An OpenAI API key with access to GPT-4o

### MCP Server Setup

The project uses GitHub's MCP (Model Context Protocol) server for GitHub API interactions:

1. **Clone and build the MCP server**:
   ```bash
   git clone https://github.com/github/github-mcp-server.git
   cd github-mcp-server/cmd/github-mcp-server
   go build -o github-mcp-server
   ```

2. **Configure the MCP server path** in `src/tools/github_tools.py`:
   ```python
   mcp_path: str = Field(
       default="/path/to/github-mcp-server/cmd/github-mcp-server/github-mcp-server",
       description="Path to GitHub MCP server executable"
   )
   ```
   Update the path to point to your MCP server executable.

3. **Set your GitHub token**:
   ```bash
   export GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
   ```

### Environment Variables

Create a `.env` file in the project root with the following variables:
```bash
# Required
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key

```

## Running the Application

### Option 1: Run with FastAPI (Recommended)

1. **Set PYTHONPATH** to include the project root:
   ```bash
   export PYTHONPATH=$(pwd)
   ```

2. **Start the FastAPI server**:
   ```bash
   python3 src/main.py
   ```
   The server will start on http://0.0.0.0:8000 by default.

3. **Access the API documentation**:
   - Interactive API docs (Swagger UI): http://localhost:8000/docs
   - Alternative API docs (ReDoc): http://localhost:8000/redoc

4. **Test the API**:
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/review-pr/' \
     -H 'Content-Type: application/json' \
     -d '{"pr_url": "https://github.com/owner/repo/pull/123"}'
   ```

   Or use the test script:
   ```bash
   python src/utils/api_test.py --repo-url https://github.com/owner/repo --pr-number 123
   ```
## Support

For questions or support, please open an issue in the repository or contact the maintainer.