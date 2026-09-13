import streamlit as st
import sqlite3
import os
import subprocess
from dotenv import load_dotenv
from smolagents import CodeAgent, InferenceClientModel

from setup_db import createDb

if not os.path.exists('company.db') :
    createDb()
# load_dotenv()

HF_API_KEY = st.secrets.get("HF_API_KEY") or os.getenv("HF_API_KEY")

if not HF_API_KEY :
    st.error("Hugging Face API Key not found. Please configure it in your secrets.")

st.set_page_config(page_title = "Text2SQL AI Assistant", page_icon = "📊")
st.title("Talk to you SQL Database")

@st.cache_resource
def getAgent () :
    model = InferenceClientModel("Qwen/Qwen3.8-27B")
    return CodeAgent(tools = [], model = model)

agent = getAgent()

def getDBSchema () :
    conn = sqlite3.connect('company.db')
    cursor = conn.cursor()

    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schemas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return "\n".join(schemas)

user_query = st.text_input("Ask a question about your data:", "Who is the newest employee ?")

if st.button("Generate & Run Query") :
    if user_query :
        schema = getDBSchema()
        print(f"SCHEMA : {schema}")
        prompt = f"""
            You are a strict SQL assistant. Given the following SQLite database schema:
        {schema}
        
        Convert this user request into a valid SQL query: "{user_query}"
        Respond ONLY with the raw SQL query wrapper. Do not include markdown code blocks like ```sql. Just text.
        """

        with st.spinner("AI is thinking ...") :
            try :
                generated_sql = agent.model(messages = [{"role" : "user", "content" : prompt}])

                # if generated_sql.startswith("```"):
                #     generated_sql = generated_sql.split("\n")[1:-1]
                #     generated_sql = "\n".join(generated_sql)

                st.subheader("Generated SQL Query:")
                st.code(generated_sql.content, language="sql")
                
                # Execute against local SQLite database
                conn = sqlite3.connect('company.db')
                cursor = conn.cursor()
                cursor.execute(generated_sql.content)
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                conn.close()
                
                # Display results
                st.subheader("Results:")
                if results:
                    st.dataframe([dict(zip(columns, row)) for row in results])
                else:
                    st.info("Query executed successfully, but returned 0 rows.")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")