import requests

def fetch_pmids(drug_name):
    """
    Fetches PMIDs of articles related to the given drug from PubMed using Entrez API.
    
    Parameters:
    drug_name (str): The name of the drug to search for.

    Returns:
    list: A list of PMIDs.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",  # Searching in PubMed database
        "term": drug_name,  # Search query (drug name)
        "retmode": "json",  # JSON response format
        "retmax": 1000  # Maximum number of PMIDs to fetch
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])
        return pmids
    else:
        print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
        return []

# Example usage
drug = "paracetamol"
pmid_list = fetch_pmids(drug)

# Store PMIDs in a file
with open("pmids.txt", "w") as file:
    file.write("\n".join(pmid_list))

print(f"Fetched {len(pmid_list)} PMIDs for {drug}.")
