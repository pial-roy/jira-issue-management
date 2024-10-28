import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from jira_data_collection import collect_data
from jira_issue_creation import create_issue
from modify_issue import modify_issue, log_work
from chart_by_status import plot_issues_by_status
from chart_by_labels import plot_issues_by_labels

# Set the page layout to be wider
st.set_page_config(layout="wide")

# Load environment variables
load_dotenv()
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_URL = os.getenv("JIRA_API_URL")
JIRA_PROJECT_NAME = os.getenv("JIRA_PROJECT_NAME")
LABEL_OPTIONS = os.getenv("LABELS", "").split(", ")
CLIENT_OPTIONS = os.getenv("CLIENT", "").split(", ")

st.title("Jira Issue Management")
st.write(f"API URL: {JIRA_API_URL}")
st.write(f"Email: {JIRA_EMAIL}")

# Tabs setup
tabs = st.tabs(["Analyze Issues", "Create New Issue", "Modify Issues"])
timezone = pytz.timezone("UTC")

# Analyze Issues Tab
with tabs[0]:
    st.sidebar.title("Jira Issue Analysis")
    time_frame = st.sidebar.selectbox("Select Time Frame:", ["Last Week", "Last Month", "Custom Date Range"])

    if time_frame == "Last Week":
        end_date = datetime.now(timezone)
        start_date = end_date - timedelta(weeks=1)
    elif time_frame == "Last Month":
        end_date = datetime.now(timezone)
        start_date = end_date - timedelta(weeks=4)
    else:
        start_date = st.sidebar.date_input("Start Date", value=(datetime.now() - timedelta(weeks=1)).date(), key="start_date_custom")
        end_date = st.sidebar.date_input("End Date", value=datetime.now().date(), key="end_date_custom")

    if st.sidebar.button("Fetch Issues"):
        issues_df = collect_data(start_date=start_date, end_date=end_date, max_results=2000)
        if not issues_df.empty:
            st.subheader("Issues Found")
            # Create a new DataFrame for display without the URL column
            issues_display_df = issues_df.copy()
            issues_display_df['Key'] = issues_display_df.apply(lambda row: f'<a href="{row["URL"]}">{row["Key"]}</a>', axis=1)

            # Drop the original URL column for cleaner display
            issues_display_df = issues_display_df.drop(columns=['URL'])

            # Display the DataFrame as HTML to allow hyperlinks
            st.markdown(issues_display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

            # Plot the charts
            st.subheader("Analysis Charts")
            plot_issues_by_status(issues_df)
            plot_issues_by_labels(issues_df)
        else:
            st.warning("No issues found for the selected date range.")

# Create New Issue Tab
with tabs[1]:
    st.subheader("Create a New Jira Issue")
    issue_summary = st.text_input("Summary")
    issue_description = st.text_area("Description")
    issue_type = st.selectbox("Issue Type", ["Bug", "Task", "Story"])
    
    client_name = st.selectbox("Select Client", CLIENT_OPTIONS, index=0)
    labels_input = st.multiselect("Select Labels", LABEL_OPTIONS, default=[])

    if st.button("Create Issue"):
        if issue_summary and client_name:
            combined_description = f"client: {client_name}\ndescription: {issue_description}"
            response = create_issue(
                summary=issue_summary,
                description=combined_description,
                client=client_name,
                issue_type=issue_type,
                labels=labels_input
            )
            if response.get("success"):
                st.success(f"Issue created successfully! Issue Key: {response.get('issue_key')}")
            else:
                st.error(f"Failed to create issue: {response.get('error')}")
        else:
            st.warning("Please provide both a summary and a client name.")

# Modify Issues Tab
with tabs[2]:
    st.subheader("Modify Existing Issues")

    time_frame = st.selectbox("Select Time Frame:", ["Last Week", "Last Month", "Custom Date Range"], key="time_frame_modify")
    end_date = datetime.now(timezone)
    start_date = end_date - timedelta(weeks=1 if time_frame == "Last Week" else 4)

    if time_frame == "Custom Date Range":
        start_date = st.date_input("Start Date", value=(datetime.now() - timedelta(weeks=1)).date(), key="modify_start_date")
        end_date = st.date_input("End Date", value=datetime.now().date(), key="modify_end_date")

    issues_df = collect_data(start_date=start_date, end_date=end_date, max_results=2000)

    if not issues_df.empty:
        if 'Description' not in issues_df.columns:
            issues_df['Description'] = ''  # Ensure the Description column exists

        issues_df["Labels"] = issues_df["Labels"].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')

        headers = ["Issue Key", "Summary", "Status", "Client(s)", "Labels", "Description", "Log Work", "Actions"]
        columns = st.columns(len(headers))
        for col, header in zip(columns, headers):
            col.write(f"**{header}**")

        for index, row in issues_df.iterrows():
            columns = st.columns(len(headers))
            columns[0].write(f"<a href='{row['URL']}'>{row['Key']}</a>", unsafe_allow_html=True)
            summary = columns[1].text_input(f"Summary_{row['Key']}", value=row['Summary'], key=f"summary_{row['Key']}")
            status = columns[2].selectbox(f"Status_{row['Key']}", ["To Do", "In Progress", "Done"], index=["To Do", "In Progress", "Done"].index(row["Status"]), key=f"status_{row['Key']}")

            default_clients = [client.strip() for client in (row.get("Client") or "").split(", ") if client.strip() in CLIENT_OPTIONS]
            clients = columns[3].multiselect(f"Client_{row['Key']}", options=CLIENT_OPTIONS, default=default_clients, key=f"client_{row['Key']}")

            default_labels = [label.strip() for label in (row.get("Labels") or "").split(", ") if label.strip() in LABEL_OPTIONS]
            labels = columns[4].multiselect(f"Labels_{row['Key']}", options=LABEL_OPTIONS, default=default_labels, key=f"labels_{row['Key']}")

            description = columns[5].text_area(f"Description_{row['Key']}", value=row["Description"], key=f"description_{row['Key']}")

            time_spent = columns[6].text_input(f"Time Spent (e.g., 2h 30m) for {row['Key']}", key=f"time_spent_{row['Key']}")
            work_description = columns[6].text_area(f"Work Description for {row['Key']}", key=f"work_desc_{row['Key']}")

            if columns[7].button(f"Update {row['Key']}", key=f"update_{row['Key']}"):
                updated_fields = {
                    "summary": summary,
                    "status": status,
                    "labels": labels,
                    "description": f"client: {', '.join(clients)}\ndescription: {description}" if description else None
                }

                response = modify_issue(row["Key"], **updated_fields)
                if response["success"]:
                    st.success(f"Issue {row['Key']} updated successfully!")
                    
                    if time_spent:
                        log_response = log_work(row["Key"], time_spent, work_description)
                        if log_response["success"]:
                            st.success(log_response["message"])
                        else:
                            st.error(f"Failed to log work on issue {row['Key']}: {log_response['error']}")
                else:
                    st.error(f"Failed to update issue {row['Key']}: {response['error']}")
    else:
        st.warning("No issues found for modification.")