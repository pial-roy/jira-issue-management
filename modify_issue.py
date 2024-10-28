# modify_issue.py
import os
from jira import JIRA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Jira configuration
JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")

# Initialize Jira client
jira = JIRA(server=JIRA_API_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

def modify_issue(issue_key, summary=None, description=None, labels=None, status=None):
    try:
        issue = jira.issue(issue_key)
        # Update fields
        fields_to_update = {}
        if summary is not None:
            fields_to_update['summary'] = summary
        if description is not None:
            fields_to_update['description'] = description
        if labels is not None:
            fields_to_update['labels'] = labels

        if fields_to_update:
            issue.update(fields=fields_to_update)

        # Update status if provided
        if status:
            transition_id = None
            transitions = jira.transitions(issue)
            for transition in transitions:
                if transition['name'] == status:
                    transition_id = transition['id']
                    break
            if transition_id:
                jira.transition_issue(issue, transition_id)

        return {"success": True, "message": f"Issue {issue_key} updated successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}
        
def log_work(issue_key, time_spent, work_description=None):
    try:
        issue = jira.issue(issue_key)
        # Log work hours using camel case for timeSpent
        jira.add_worklog(issue, timeSpent=time_spent, comment=work_description)
        return {"success": True, "message": f"Logged {time_spent} on issue {issue_key}."}
    except Exception as e:
        return {"success": False, "error": str(e)}