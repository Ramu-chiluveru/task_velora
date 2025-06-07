# Function to generate abstracts (dummy summarization)
def generate_abstracts(article_details):
    return [f"Summary: {detail[:100]}..." for detail in article_details]  # Placeholder