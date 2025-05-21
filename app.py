import streamlit as st
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import urllib.parse

API_KEY = 'c9187cfd41d4c6496be780048b47904e'
HEADERS = {'X-ELS-APIKey': API_KEY}

st.title("Citing DOIs → Scopus Journal + SCImago Quartile Checker")

# User input
user_input = st.text_area("Paste Citing DOIs (from Google Scholar, Lens, etc.):", height=200)
doi_list = [d.strip().replace("https://doi.org/", "").replace("http://doi.org/", "") for d in user_input.splitlines() if d.strip()]

# Scopus search (robust)
@st.cache_data(show_spinner=False)
def get_scopus_journal(doi):
    query = f"REF({doi}) OR DOI({doi})"
    url = f"https://api.elsevier.com/content/search/scopus?query={urllib.parse.quote(query)}&field=source-title"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        entries = r.json().get("search-results", {}).get("entry", [])
        if entries:
            return entries[0].get("source-title", "Unknown")
    return None

# SCImago quartile scraping
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

# Main processing
results = []

if doi_list:
    with st.spinner("Looking up citing articles..."):
        for doi in doi_list:
            journal = get_scopus_journal(doi)
            if journal and journal != "Unknown":
                quartile = get_quartile_from_scimago(journal)
                time.sleep(1)  # be polite to SCImago
                results.append({
                    "Citing DOI": f"https://doi.org/{doi}",
                    "Journal": journal,
                    "Scopus Indexed": "Yes",
                    "SCImago Quartile": quartile
                })
            else:
                results.append({
                    "Citing DOI": f"https://doi.org/{doi}",
                    "Journal": "Not Found",
                    "Scopus Indexed": "No",
                    "SCImago Quartile": "-"
                })

    df = pd.DataFrame(results)
    st.subheader("Citing DOIs with Journal & Quartile Status")
    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False), file_name="citing_dois_scopus_quartile.csv")
else:
    st.info("Paste DOIs that cite your paper to begin.")
