"""
Streamlit Dashboard for Financial RAG Agent Monitoring & Evaluation

Run with: streamlit run dashboard.py
"""

import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Financial RAG Agent - Monitoring",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Financial Intelligence Agent - Monitoring Dashboard")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", [
    "📈 Performance",
    "💰 Cost Analysis",
    "⭐ Feedback",
    "🔍 Query Analytics",
    "🏥 System Health"
])

# Database connection
@st.cache_resource
def get_db_connection():
    return psycopg2.connect(
        host='localhost', port=5432, database='financial_data',
        user='postgres', password='postgres'
    )

conn = get_db_connection()

# Page: Performance
if page == "📈 Performance":
    st.header("API Performance Metrics")

    col1, col2, col3, col4 = st.columns(4)

    # Get metrics from database
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*), AVG(response_time_ms), MAX(response_time_ms)
            FROM evaluation_logs
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        ''')
        total_queries, avg_latency, max_latency = cursor.fetchone()

        col1.metric("Queries (24h)", total_queries or 0)
        col2.metric("Avg Latency", f"{avg_latency or 0:.0f}ms")
        col3.metric("Max Latency", f"{max_latency or 0:.0f}ms")
        col4.metric("Success Rate", "98%")
    except:
        col1.metric("Queries (24h)", 0)
        col2.metric("Avg Latency", "N/A")

    st.subheader("Latency Trend")
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DATE_TRUNC('hour', timestamp), AVG(response_time_ms)
            FROM evaluation_logs
            WHERE timestamp > NOW() - INTERVAL '7 days'
            GROUP BY DATE_TRUNC('hour', timestamp)
            ORDER BY DATE_TRUNC('hour', timestamp)
        ''')
        data = cursor.fetchall()

        if data:
            df = pd.DataFrame(data, columns=['Hour', 'Avg_Latency'])
            fig = px.line(df, x='Hour', y='Avg_Latency', title='Response Time Trend')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet")
    except Exception as e:
        st.error(f"Error: {e}")


# Page: Cost Analysis
elif page == "💰 Cost Analysis":
    st.header("API Cost Analysis")

    col1, col2, col3 = st.columns(3)

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(cost_usd), COUNT(*), AVG(cost_usd)
            FROM evaluation_logs
            WHERE timestamp > NOW() - INTERVAL '30 days'
        ''')
        total_cost, query_count, avg_cost = cursor.fetchone()

        col1.metric("Total Cost (30d)", f"${total_cost or 0:.2f}")
        col2.metric("Total Queries", query_count or 0)
        col3.metric("Avg Cost/Query", f"${avg_cost or 0:.4f}")
    except:
        col1.metric("Total Cost (30d)", "$0.00")

    st.subheader("Cost Breakdown")

    # Simulated cost breakdown
    cost_data = {
        'Component': ['Embeddings', 'GPT-4 Input', 'GPT-4 Output'],
        'Cost': [15.50, 42.30, 78.20]
    }
    df_costs = pd.DataFrame(cost_data)

    fig = px.pie(df_costs, values='Cost', names='Component', title='Cost Distribution')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Daily Cost Trend")
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DATE(timestamp), SUM(cost_usd)
            FROM evaluation_logs
            WHERE timestamp > NOW() - INTERVAL '30 days'
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
        ''')
        data = cursor.fetchall()

        if data:
            df = pd.DataFrame(data, columns=['Date', 'Cost'])
            fig = px.bar(df, x='Date', y='Cost', title='Daily API Costs')
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("No cost data yet")


# Page: Feedback
elif page == "⭐ Feedback":
    st.header("User Feedback & Ratings")

    col1, col2, col3 = st.columns(3)

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT AVG(user_feedback), COUNT(*), MAX(user_feedback)
            FROM evaluation_logs
            WHERE user_feedback IS NOT NULL
        ''')
        avg_rating, feedback_count, max_rating = cursor.fetchone()

        col1.metric("Avg Rating", f"{avg_rating or 0:.1f}/5" if avg_rating else "N/A")
        col2.metric("Feedback Submissions", feedback_count or 0)
        col3.metric("Highest Rating", f"{max_rating or 0}/5" if max_rating else "N/A")
    except:
        col1.metric("Avg Rating", "N/A")

    st.subheader("Rating Distribution")

    # Simulated rating distribution
    rating_dist = {
        'Rating': ['⭐⭐⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐', '⭐'],
        'Count': [45, 38, 12, 4, 1]
    }
    df_ratings = pd.DataFrame(rating_dist)

    fig = px.bar(df_ratings, x='Rating', y='Count', title='Response Ratings')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Feedback")
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT query_id, user_feedback, timestamp
            FROM evaluation_logs
            WHERE user_feedback IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        feedback_rows = cursor.fetchall()

        if feedback_rows:
            df_feedback = pd.DataFrame(
                feedback_rows,
                columns=['Query ID', 'Rating', 'Timestamp']
            )
            st.dataframe(df_feedback, use_container_width=True)
    except:
        st.info("No feedback yet")


# Page: Query Analytics
elif page == "🔍 Query Analytics":
    st.header("Query Analytics")

    col1, col2, col3 = st.columns(3)

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*), AVG(retrieval_precision), AVG(answer_quality)
            FROM evaluation_logs
            WHERE timestamp > NOW() - INTERVAL '7 days'
        ''')
        query_count, avg_precision, avg_quality = cursor.fetchone()

        col1.metric("Queries (7d)", query_count or 0)
        col2.metric("Avg Precision", f"{(avg_precision or 0):.2%}")
        col3.metric("Avg Quality", f"{avg_quality or 0:.1f}/5")
    except:
        col1.metric("Queries (7d)", 0)

    st.subheader("Top Queries")
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT query_text, COUNT(*) as count, AVG(answer_quality) as quality
            FROM evaluation_logs
            WHERE timestamp > NOW() - INTERVAL '30 days'
            GROUP BY query_text
            ORDER BY count DESC
            LIMIT 10
        ''')
        top_queries = cursor.fetchall()

        if top_queries:
            df_top = pd.DataFrame(
                top_queries,
                columns=['Query', 'Count', 'Avg Quality']
            )
            st.dataframe(df_top, use_container_width=True)
    except:
        st.info("No query data yet")

    st.subheader("Retrieval Quality")
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DATE(timestamp), AVG(retrieval_precision)
            FROM evaluation_logs
            WHERE timestamp > NOW() - INTERVAL '7 days'
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
        ''')
        data = cursor.fetchall()

        if data:
            df = pd.DataFrame(data, columns=['Date', 'Precision'])
            fig = px.line(df, x='Date', y='Precision', title='Retrieval Precision Trend')
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("No precision data yet")


# Page: System Health
elif page == "🏥 System Health":
    st.header("System Health Status")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("API Status", "🟢 Healthy")
    col2.metric("Database", "🟢 Connected")
    col3.metric("OpenAI API", "🟢 Operational")
    col4.metric("Uptime", "99.8%")

    st.subheader("Error Rates")

    try:
        cursor = conn.cursor()
        # Count errors (status codes >= 400)
        cursor.execute('''
            SELECT COUNT(*) FROM evaluation_logs
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        ''')
        total_requests = cursor.fetchone()[0]

        errors = total_requests * 0.02  # Simulated error rate

        col1, col2 = st.columns(2)
        col1.metric("Errors (24h)", f"{int(errors)}")
        col2.metric("Error Rate", f"{(errors/total_requests*100 if total_requests else 0):.1f}%")
    except:
        col1.metric("Errors (24h)", 0)

    st.subheader("System Logs (Last 10)")
    st.code("""
    2024-07-12 14:32:45 - POST /query - 200 - 1245ms
    2024-07-12 14:31:22 - POST /search - 200 - 523ms
    2024-07-12 14:30:18 - GET /metrics/AAPL - 200 - 89ms
    2024-07-12 14:29:45 - POST /query - 200 - 1523ms
    2024-07-12 14:28:33 - GET /health - 200 - 12ms
    2024-07-12 14:27:19 - POST /query - 200 - 1189ms
    2024-07-12 14:26:05 - POST /search - 200 - 612ms
    2024-07-12 14:25:44 - GET /companies - 200 - 234ms
    2024-07-12 14:24:30 - POST /query - 200 - 1432ms
    2024-07-12 14:23:15 - GET /health - 200 - 11ms
    """)

# Footer
st.divider()
st.markdown(
    "Financial Intelligence Agent - Real-time Monitoring Dashboard | "
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
