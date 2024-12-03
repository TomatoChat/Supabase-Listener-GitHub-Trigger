# Supabase Listener GitHub Trigger

This repository contains a Python script that listens for new entries in a Supabase database and triggers a specified GitHub Actions workflow when new entries are detected.

## Overview

The `newEntryTrigger.py` script periodically checks a specified Supabase table for new entries. If a new entry is found since the last check, it triggers a GitHub Actions workflow using the GitHub API.

This repository is created to leverage the advantages of running this listener for free using GitHub Actions, as it is hosted in a public repository. Sensitive information, such as access tokens and API keys, are securely stored as GitHub Secrets to ensure security and privacy.

## Technologies Used

- Python: The primary programming language for the listener.
- Supabase: A backend-as-a-service that provides a PostgreSQL database.
- GitHub Actions: A feature of GitHub that allows continuous integration and continuous delivery (CI/CD).
- `asyncio`: An asynchronous I/O framework for Python.

## Getting Started

To set up the project locally, follow these instructions:

### Prerequisites

- Python 3.10 or higher
- Git
- A GitHub account
- A Supabase account

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/TomatoChat/Supabase-Listener-GitHub-Trigger.git
   cd Supabase-Listener-GitHub-Trigger
   ```

2. **Create a virtual environment and activate it** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file based on the provided `.env.template`, and fill in the respective values:
   ```bash
   cp .env.template .env
   # Edit .env with your own values
   ```

## Configuration

Before running the script, ensure the following environment variables are set in your `.env` file:

- `SUPABASE_URL`: Your Supabase project URL.
- `SUPABASE_KEY`: Your Supabase API key.
- `SUPABASE_TABLE`: The name of the table to monitor in Supabase.
- `GH_KEY`: Your GitHub personal access token for authentication.
- `GH_ACTION`: The name of the GitHub Actions workflow to trigger.
- `GH_PROFILE`: Your GitHub username or organization name.
- `GH_REPO`: The name of the GitHub repository containing the workflow.

## Running the Listener

Once everything is set up, you can run the listener script:

```bash
python newEntryTrigger.py
```

The script will continuously check the specified Supabase table for new entries and trigger the GitHub action when new entries are detected.

## GitHub Actions Workflow

The workflow is defined in the `.github/workflows/listenerTrigger.yml`. It can be triggered manually through the GitHub interface, and it installs the necessary dependencies before running the listener.

## License

This project is licensed under the MIT License.