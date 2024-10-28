# jira_issue_creation.py
import os
import requests
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Jira configuration
JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_PROJECT_NAME = os.getenv("JIRA_PROJECT_NAME")

def create_issue(summary, description, issue_type, labels):
    # Jira API endpoint for creating an issue
    url = f"{JIRA_API_URL}/rest/api/3/issue"

    # Jira API headers and authentication
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

    # Format the description with client and description in ADF
    description_adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": f"{description}"}
                ]
            }
        ]
    }

    # Issue data including labels
    issue_data = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_NAME
            },
            "summary": summary,
            "description": description_adf,
            "issuetype": {
                "name": issue_type
            },
            "labels": labels
        }
    }

    # Make the POST request to create the issue
    response = requests.post(url, headers=headers, auth=auth, data=json.dumps(issue_data))

    # Check response status
    if response.status_code == 201:
        print("Issue created successfully.")
        return {"success": True, "issue_key": response.json().get("key")}
    else:
        print(f"Failed to create issue: {response.status_code}")
        print(response.json())
        return {"success": False, "error": response.json().get("errors", response.text)}