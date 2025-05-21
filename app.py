import streamlit as st
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import urllib.parse

# Your Scopus API Key
API_KEY = 'c9187cfd41d4c6496be780048b47904e'
HEADERS = {'X-ELS-APIKey': API_KEY}

st.title("Scopus Citing Journal Quartile Checker (Live)")
user_input = st.text_area("Paste DOIs (e.g., https://doi.org/...):", height=200)
doi_list = [d.strip().replace("https://doi.org/", "").replace("http://doi.org/", "") for d in user_input.splitlines() if d.strip()]

@st.cache_data(show_spinner=False)
def get_citing_articles_from_scopus(doi):
    url = f"https://api.elsevier.com/content/search/scopus?query=ref({doi})&field=dc:title,prism:doi,source-title"
    res = requests.get(url, headers=HEADERS)
    journals = []
    if res.status_code == 200:
        entries = res.json().get("search-results", {}).get("entry", [])
        for entry in entries:
            journal = entry.get("source-title", "").strip()
            if journal:
                journals.append(journal)
    return journals

@st.cache_data(show_spinner=False)
def get_quartile_from_scimago(journal_name):
    query = urllib.parse.quote(journal_name)
    search_url = f"https://www.scimagojr.com/journalsearch.php?q={query}"
    try:
        r = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        link = soup.select_one('a[href*="journalsearch.php?id="]')
        if not link:
            return "Unknown"
        journal_url = "https://www.scimagojr.com/" + link['href']
        rj = requests.get(journal_url, headers={"User-Agent": "Mozilla/5.0"})
        jsoup = BeautifulSoup(rj.text, 'html.parser')
        for row in jsoup.select("table.table.table-condensed tr"):
            cells = row.find_all("td")
            if len(cells) >= 4:
                quartile = cells[3].text.strip()
                if quartile.startswith("Q"):
                    return quartile
    except:
        return "Error"
    return "Unknown"

results = []

if doi_list:
    with st.spinner("Querying Scopus and SCImago..."):
        for doi in doi_list:
            citing_journals = get_citing_articles_from_scopus(doi)
            quartile_summary = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0, "Unknown": 0}

            for journal in citing_journals:
                q = get_quartile_from_scimago(journal)
                time.sleep(1)  # Respect SCImago
                if q in quartile_summary:
                    quartile_summary[q] += 1
                else:
                    quartile_summary["Unknown"] += 1

            results.append({
                "DOI": f"https://doi.org/{doi}",
                "Citing Scopus Papers": len(citing_journals),
                **quartile_summary
            })

    df = pd.DataFrame(results)
    st.subheader("Citation + SCImago Quartile Summary")
    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False), file_name="quartile_summary.csv")
else:
    st.info("Paste at least one DOI to begin.")
