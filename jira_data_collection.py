# jira_data_collection.py
import os
import pandas as pd
from jira import JIRA
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Jira configuration
JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_PROJECT_NAME = os.getenv("JIRA_PROJECT_NAME")

# Initialize Jira client
jira = JIRA(server=JIRA_API_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

# Function to fetch issues from Jira
def fetch_issues(project_name, start_date, end_date, max_results=3000):
    query = f'project = "{project_name}" AND created >= "{start_date.strftime("%Y-%m-%d")}" AND created <= "{end_date.strftime("%Y-%m-%d")}"'
    issues = jira.search_issues(query, maxResults=max_results)  # Use max_results parameter
    return issues

# jira_data_collection.py
# ... [other imports and code] ...

def collect_data(start_date, end_date, max_results=3000):
    # Fetch issues
    issues = fetch_issues(JIRA_PROJECT_NAME, start_date, end_date, max_results)

    # Collecting data in a DataFrame
    data = []
    for issue in issues:
        # Initialize client with a default value
        client = None

        # Check for "client:" in description lines
        try:
            description_lines = issue.fields.description.split("\n")
            if description_lines[0].startswith("client:"):
                client = description_lines[0][7:].strip()  # Extract text after "client:"
        except:
            print(issue.key, "Description empty, or client not specified!")

        data.append({
            "Key": issue.key,
            "Summary": issue.fields.summary,
            "Status": issue.fields.status.name,
            "Created": issue.fields.created,
            "Labels": issue.fields.labels,
            "Client": client,  # Add client data even if None
            "URL": f"{JIRA_API_URL}/browse/{issue.key}"  # Add the issue URL
        })

    # Create DataFrame
    issues_df = pd.DataFrame(data)
    return issues_df