# chart_by_labels.py
import pandas as pd
import plotly.express as px
import streamlit as st

def plot_issues_by_labels(issues_df, exclude_none=True):
    if issues_df.empty:
        st.warning("No issues available for plotting.")
        return

    # Explode the Labels to count by client and labels
    labels_df = issues_df.explode('Labels')

    # Split clients and explode to separate rows for each client
    labels_df['Client'] = labels_df['Client'].str.split(', ')
    clients_df = labels_df.explode('Client')

    # Optionally exclude clients with the label 'None'
    if exclude_none:
        clients_df = clients_df[clients_df['Client'] != 'None']

    # Group by Client and Labels to get the count of issues
    label_counts = clients_df.groupby(['Client', 'Labels']).size().reset_index(name='Count')

    # Create a Plotly bar chart
    fig = px.bar(label_counts, 
                 x='Client', 
                 y='Count', 
                 color='Labels', 
                 title='Number of Issues by Labels per Client',
                 labels={'Count': 'Number of Issues', 'Client': 'Client'},
                 text='Count',
                 barmode='stack')

    fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig.update_layout(xaxis_title='Client', yaxis_title='Number of Issues', xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)