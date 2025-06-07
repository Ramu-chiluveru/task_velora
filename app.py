import streamlit as st
import requests
import psycopg2
from datetime import datetime
import pandas as pd

import db
import generate_abstract as g_abstract
import generate_pdf as g_pdf
import fetch_articles_details as f_articles

# Streamlit UI Configuration
st.set_page_config(page_title="PubMed Research Finder", page_icon="🔬", layout="centered")

st.title("🔬 PubMed Research Finder")
st.markdown("Search for PubMed articles by drug name & date range.")

# Input Fields
drug_name = st.text_input("Enter Drug Name", placeholder="e.g., Paracetamol")
start_date = st.date_input("Select Start Date", datetime.today())
end_date = st.date_input("Select End Date", datetime.today())

# Database connection
conn = db.connect_db()

def fetch_pubmed_articles(drug_name, start_date, end_date):
    """Fetch article IDs from PubMed."""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": f"{drug_name}[Title]",
        "datetype": "pdat",
        "mindate": start_date.strftime("%Y/%m/%d"),
        "maxdate": end_date.strftime("%Y/%m/%d"),
        "retmax": 50,
        "sort": "date",
        "retmode": "json"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return []

def insert_article(pubmed_id):
    """Insert PubMed ID into the database if it doesn't exist."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM articles_details WHERE pubmed_id = %s;", (pubmed_id,))
            if cur.fetchone():
                return False
            cur.execute(
                "INSERT INTO articles_details (pubmed_id, info_extracted) VALUES (%s, %s);",
                (pubmed_id, False)
            )
            conn.commit()
            return True
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        return None

if(st.button("Articles")):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pubmed_id,summary,title FROM articles_details WHERE info_extracted = True")
            articles = cur.fetchall()
        st.session_state["articles_page"] = True
        df = pd.DataFrame(articles,columns=["Pubmed id","Summary","Title"])
        st.table(df)

        if(st.button("EXIT")):
            st.session_state["articles_page"] = False
    
    except Exception as e:
        st.error(f"Database error: {e}")



# Step 1: Search Articles
if st.button("Search"):
    if not drug_name:
        st.warning("Please enter a drug name!")
    elif start_date > end_date:
        st.warning("Start date cannot be after end date.")
    else:
        st.info("Fetching PubMed articles...")
        article_ids = fetch_pubmed_articles(drug_name, start_date, end_date)
        
        if not article_ids:
            st.warning("No articles found.")
        else:
            st.success(f"Found {len(article_ids)} articles!")
            for article_id in article_ids:
                if insert_article(article_id):
                    st.markdown(f"🆕 **PubMed ID:** [{article_id}](https://pubmed.ncbi.nlm.nih.gov/{article_id}) ✅ Added to DB")
                else:
                    st.markdown(f"📄 **PubMed ID:** [{article_id}](https://pubmed.ncbi.nlm.nih.gov/{article_id}) ⚠️ Already in DB")
            st.session_state["fetch_articles_enabled"] = True

# Step 2: Fetch Articles
if st.session_state.get("fetch_articles_enabled", False):
    if st.button("Fetch Articles"):
        st.info("Fetching article details...")
        article_details = f_articles.fetch_article_details(conn)
        st.success(article_details)
        if article_details:
            st.session_state["generate_abstract_enabled"] = True

# Step 3: Generate Abstracts
if st.session_state.get("generate_abstract_enabled", False):
    if st.button("Generate Abstract"):
        st.info("Generating abstracts...")
        abstracts = g_abstract.generate_abstracts(article_details)
        if abstracts:
            st.session_state["download_pdf_enabled"] = True

# Step 4: Download PDF
if st.session_state.get("download_pdf_enabled", False):
    if st.button("Download PDF"):
        pdf_filename = g_pdf.generate_pdf(drug_name, abstracts)
        st.success("PDF generated successfully! 🎉")
        with open(pdf_filename, "rb") as f:
            st.download_button("Download PDF", f, file_name=pdf_filename, mime="application/pdf")
