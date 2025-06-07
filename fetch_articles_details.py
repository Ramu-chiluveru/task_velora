# import db
# import psycopg2
# import requests
# from bs4 import BeautifulSoup  
# import json
# import ollama

# def clean_the_text(html_text):
#     """Extracts and returns title and abstract from the HTML in JSON format."""
#     soup = BeautifulSoup(html_text, "html.parser")

#     # Extract title
#     title_tag = soup.find("h1", class_="heading-title")
#     title = title_tag.get_text(strip=True) if title_tag else "Title not found"

#     # Extract abstract
#     abstract_tag = soup.find(id="abstract")
#     abstract = abstract_tag.get_text(strip=True) if abstract_tag else "Abstract not found"

#     # Return data as JSON
#     return json.dumps({
#         "title": title,
#         "abstract": summarize_with_llama(abstract),
#     })

# def summarize_with_llama(abstract):
#     """Uses the locally installed Llama 3.2 model in Ollama to generate a summary."""
#     if abstract in ["Abstract not found", "N/A"]:
#         return "N/A"
    
#     response = ollama.chat(
#         model="llama3.2",
#         messages=[
#             {"role": "system", "content": "You are an expert summarizer. Summarize the given text in under 100 words."},
#             {"role": "user", "content": abstract}
#         ]
#     )

#     return response['message']['content']

# def fetch_article_details(conn):
#     """Fetches unprocessed articles from the database, extracts details, and updates status."""
#     article_ids = []
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT pubmed_id FROM articles_details WHERE info_extracted = FALSE")
#             result = cur.fetchall()
#             article_ids = [row[0] for row in result]  
#     except psycopg2.Error as e:
#         return f"Database operation error: {e}"

#     if not article_ids:
#         return "No unprocessed articles found."

#     article_details = []

#     for pubmed_id in article_ids:
#         url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}"

#         try:
#             response = requests.get(url)
#             response.raise_for_status()

#             # Clean the fetched text using BeautifulSoup
#             processed_text = clean_the_text(response.text)

#             # Convert JSON string to dictionary
#             processed_data = json.loads(processed_text)

#             # Append the cleaned article data
#             article_details.append({"pubmed_id": pubmed_id, "title": processed_data["title"], "summary": processed_data["abstract"]})

#             # Mark info_extracted as TRUE in the database
#             try:
#                 with conn.cursor() as cur:
#                     cur.execute("""UPDATE articles_details SET info_extracted = TRUE, summary = %s, title = %s WHERE pubmed_id = %s;""",
#                                 (processed_data["abstract"], processed_data["title"], pubmed_id))

#                 conn.commit()
#             except psycopg2.Error as e:
#                 print(f"Database update error for PubMed ID {pubmed_id}: {e}")

#         except requests.exceptions.RequestException as e:
#             print(f"Error fetching PubMed ID {pubmed_id}: {e}")

#     return article_details

import db
import psycopg2
import requests
from bs4 import BeautifulSoup  
import json
import ollama

def clean_the_text(html_text):
    """Extracts and returns title and abstract from the HTML in JSON format."""
    soup = BeautifulSoup(html_text, "html.parser")

    # Extract title
    title_tag = soup.find("h1", class_="heading-title")
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"

    # Extract abstract
    abstract_tag = soup.find(id="abstract")
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else "Abstract not found"

    # Return data as JSON
    return json.dumps({
        "title": title,
        "abstract": summarize_with_llama(abstract),
    })

def summarize_with_llama(abstract):
    """Uses the locally installed Llama 3.2 model in Ollama to generate a summary."""
    if abstract in ["Abstract not found", "N/A"]:
        return "N/A"
    
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": "You are an expert summarizer. Summarize the given text in under 100 words."},
            {"role": "user", "content": abstract}
        ]
    )

    return response['message']['content']

def fetch_article_details(conn):
    """Fetches unprocessed articles from the database, extracts details, and updates status."""
    article_ids = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pubmed_id FROM articles_details WHERE info_extracted = FALSE")
            result = cur.fetchall()
            article_ids = [row[0] for row in result]  
    except psycopg2.Error as e:
        return f"Database operation error: {e}"

    if not article_ids:
        return "No unprocessed articles found."

    article_details = []

    for pubmed_id in article_ids:
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            # Clean the fetched text using BeautifulSoup
            processed_text = clean_the_text(response.text)

            # Convert JSON string to dictionary
            processed_data = json.loads(processed_text)

            # Append the cleaned article data
            article_details.append({"pubmed_id": pubmed_id, "title": processed_data["title"], "summary": processed_data["abstract"]})

            # Mark info_extracted as TRUE in the database
            try:
                with conn.cursor() as cur:
                    cur.execute("""UPDATE articles_details SET info_extracted = TRUE, summary = %s, title = %s WHERE pubmed_id = %s;""",
                                (processed_data["abstract"], processed_data["title"], pubmed_id))

                conn.commit()
            except psycopg2.Error as e:
                print(f"Database update error for PubMed ID {pubmed_id}: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching PubMed ID {pubmed_id}: {e}")

    return article_details
