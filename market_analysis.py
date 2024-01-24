import openai
import requests
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

openai.api_key = '<out your API key here>'


def remove_prefixes(text: str) -> str:
    pattern = r'^[0-9]+\.'  # Pattern for "numbers followed by a dot" at the beginning
    text = re.sub(pattern, '', text)  # Remove the pattern
    pattern = r'^-'  # Pattern for "hyphen" at the beginning
    text = re.sub(pattern, '', text)  # Remove the pattern
    return text.strip()  # Strip leading/trailing whitespace


def get_market_categories(market_name: str) -> list[str]:
    prompt = "Frage: In welche Kategorien lässt sich der " + market_name + " in Deutschland einteilen?" + \
             " Antworte in Stichpunkten, gebe nur die Namen der Marktsegmente aus, sonst nichts.\n\nAntwort:"
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=500,
        temperature=0
    )
    m = response.choices[0].text.strip().replace("\n\n", "\n")
    m = m.split(sep="\n")
    m = [remove_prefixes(i) for i in m]
    m = [i if i.lower().__contains__("markt") else i + "markt" for i in m]
    m.append(market_name)
    print(prompt + "\n")
    for i in m:
        print(i)
    return m


def answer_query_from_text(query: str, text: str) -> str:
    prompt = "Nachfolgend erhältst du ein Dokument und eine Frage. Beantworte die Frage anhand des Dokuments. " + \
             "Dokument: " + text + ". Frage: " + query + "Antwort: "

    response = openai.chat.completions.create(
        model="gpt-4-0613",
        messages=[{
            'role': 'user',
            'content': prompt
        }]
    )
    return response.choices[0].message.content


def perform_bing_search(query: str) -> list[str]:
    azure_api_key = '<your API key here>'
    endpoint = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": azure_api_key}
    params = {
        "q": query,  # Search query
        "count": 10,  # Number of results to return
        "offset": 0,  # Offset for results (for pagination)
        "mkt": "de-DE",  # Market for the search
        "safesearch": "Moderate"  # Safe search settings
    }
    all_results = []
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        bing_search_results = response.json()
        for result in bing_search_results.get("webPages", {}).get("value", []):
            url = result['url']
            all_results.append(url)
    else:
        print(f"Error: {response.status_code}, {response.text}")
    return all_results


def get_queries_for_bing_search(search_categories: list[str]) -> list[str]:
    queries = []
    current_year = datetime.now().year
    year_before = current_year - 1
    query_templates = ["Wie hoch sind die Übernachtungszahlen im deutschen",
                       "Wie hoch ist der Umsatz pro Besucher im deutschen",
                       "Aus welchen Ländern kommen die Besucher im deutschen"]
    for year in [current_year, year_before]:
        for m in search_categories:
            for q in query_templates:
                queries.append(q + " " + m + " im Jahr " + str(year) + "?")
    return queries


def get_text_from_website(url: str) -> str:
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:

        # Parse the response content (HTML) with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text from the parsed HTML
        text = soup.get_text(separator=' ', strip=True)
        return text
    else:
        print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
        return "Kein Kontext"


market_name = "Markt für Inlandstourismus"
market_categories = get_market_categories(market_name)
search_queries = get_queries_for_bing_search(market_categories)
query_to_urls = {}
for q in search_queries:
    print("Query" + q)
    time.sleep(1)
    query_to_urls[q] = perform_bing_search(q)
    for url in query_to_urls[q]:
        context = get_text_from_website(url)
        answer = answer_query_from_text(q, context)
        print(answer)
