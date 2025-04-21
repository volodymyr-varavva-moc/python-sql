import streamlit as st
import pandas as pd
import requests
import json
from typing import Dict, Any, List

# API URL
API_URL = "http://localhost:8000/api/v1/query/process"

st.set_page_config(
    page_title="NL2SQL App",
    page_icon="🔍",
    layout="wide"
)

def process_query(query: str) -> Dict[str, Any]:
    """
    Send the query to the backend API and get the response
    """
    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error: {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def display_results(response: Dict[str, Any]) -> None:
    """
    Display the results of the query
    """
    if "error" in response:
        st.error(response["error"])
        if "details" in response:
            st.error(response["details"])
        return
        
    # Display explanation
    st.markdown("### Query Interpretation")
    st.write(response["explanation"])
    
    # Display SQL
    st.markdown("### Generated SQL")
    st.code(response["sql_query"], language="sql")
    
    # Display parameters
    if response["parameters"]:
        st.markdown("### Extracted Parameters")
        params_df = pd.DataFrame(response["parameters"])
        st.dataframe(params_df)
    
    # Display results
    st.markdown("### Results")
    results = response["results"]
    
    if "rows" in results and results["rows"]:
        df = pd.DataFrame(results["rows"])
        st.dataframe(df, use_container_width=True)
        st.write(f"Total rows: {results['row_count']}")
    elif "affected_rows" in results:
        st.success(results["message"])
    else:
        st.info("No results returned")

def main():
    st.title("Natural Language to SQL Query")
    
    st.markdown("""
    This application translates your questions about customers and orders into SQL queries
    and shows you the results directly from the database.
    
    ### Example queries:
    - Show me all customers
    - What are the total sales for each customer?
    - Show me orders with total amount greater than $100
    - Find the most recent order for each customer
    """)
    
    # Query input
    query = st.text_area("Enter your question:", height=100)
    
    # Process button
    if st.button("Run Query"):
        if not query:
            st.warning("Please enter a query")
        else:
            with st.spinner("Processing..."):
                response = process_query(query)
                display_results(response)
    
    # Show sample database schema
    with st.expander("Database Schema"):
        st.markdown("""
        ### Customers Table
        - id (INTEGER): Primary key
        - name (STRING): Customer's full name
        - email (STRING): Customer's email address
        - phone (STRING): Customer's phone number
        - address (STRING): Customer's address
        
        ### Orders Table
        - id (INTEGER): Primary key
        - customer_id (INTEGER): Foreign key to customers table
        - order_date (DATE): Date when the order was placed
        - total_amount (FLOAT): Total amount of the order
        - status (STRING): Order status (pending, processing, shipped, delivered)
        - notes (TEXT): Additional notes about the order
        """)

if __name__ == "__main__":
    main()
