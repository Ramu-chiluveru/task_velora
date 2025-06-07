# Function to fetch article details (dummy function for now)
import db
import psycopg2
import requests

def fetch_article_details():
    
    url = f"https://pubmed.ncbi.nlm.nih.gov/39946820/"
    
    try:
      print(url)
      response = requests.get(url)
      print(response.text)
      response.raise_for_status()
      data = response.json()
      print(data)
    except requests.exceptions.RequestException as e:
      print(e)

fetch_article_details()