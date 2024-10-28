# chart_by_status.py
import pandas as pd
import plotly.express as px
import streamlit as st

def plot_issues_by_status(issues_df):
    if issues_df.empty:
        st.warning("No issues available for plotting.")
        return

    # Explode the Labels to count by labels and status
    labels_df = issues_df.explode('Labels')

    # Split clients and explode to separate rows for each client
    labels_df['Client'] = labels_df['Client'].str.split(', ')
    clients_df = labels_df.explode('Client')

    # Group by Labels and Status to get the count of issues
    status_counts = clients_df.groupby(['Labels', 'Status']).size().reset_index(name='Count')

    # Create a Plotly bar chart
    fig = px.bar(status_counts, 
                 x='Labels', 
                 y='Count', 
                 color='Status', 
                 title='Number of Issues by Labels and Status',
                 labels={'Count': 'Number of Issues', 'Labels': 'Labels'},
                 text='Count',
                 barmode='stack')

    fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig.update_layout(xaxis_title='Labels', yaxis_title='Number of Issues', xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)