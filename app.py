# app.py — Citation Checker using OpenAlex + Scopus API + SCImago Quartile

import streamlit as st
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import urllib.parse

# Scopus API key (already known to you)
SCOPUS_API_KEY = 'c9187cfd41d4c6496be780048b47904e'
HEADERS_SCOPUS = {'X-ELS-APIKey': SCOPUS_API_KEY}

st.title("OpenAlex Citation Checker with Scopus + SCImago Quartile")
input_doi = st.text_input("Enter the DOI of your article:", placeholder="e.g., https://doi.org/10.xxxx/xxxxx")

def clean_doi(doi):
    return doi.strip().replace("https://doi.org/", "").replace("http://doi.org/", "")

@st.cache_data(show_spinner=False)
def get_openalex_citers(doi):
    openalex_url = f"https://api.openalex.org/works/doi:{doi}"
    r = requests.get(openalex_url)
    if r.status_code != 200:
        return []
    work_id = r.json().get("id")
    if not work_id:
        return []
    cited_url = f"https://api.openalex.org/works?filter=cites:{work_id}&per-page=50"
    r = requests.get(cited_url)
    if r.status_code != 200:
        return []
    citing = r.json().get("results", [])
    return [w.get("doi", "").replace("https://doi.org/", "") for w in citing if w.get("doi")]

@st.cache_data(show_spinner=False)
def get_scopus_journal_name(citing_doi):
    query = f"REF({citing_doi}) OR DOI({citing_doi})"
    url = f"https://api.elsevier.com/content/search/scopus?query={urllib.parse.quote(query)}&field=source-title"
    r = requests.get(url, headers=HEADERS_SCOPUS)
    if r.status_code == 200:
        entries = r.json().get("search-results", {}).get("entry", [])
        if entries:
            return entries[0].get("source-title", "Unknown")
    return None

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

if input_doi:
    base_doi = clean_doi(input_doi)
    with st.spinner("Getting citing DOIs from OpenAlex..."):
        citing_dois = get_openalex_citers(base_doi)
        if citing_dois:
            quartile_summary = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0, "Unknown": 0}
            citing_records = []

            for citing_doi in citing_dois:
                journal = get_scopus_journal_name(citing_doi)
                if journal and journal != "Unknown":
                    quartile = get_quartile_from_scimago(journal)
                    if quartile in quartile_summary:
                        quartile_summary[quartile] += 1
                    else:
                        quartile_summary["Unknown"] += 1
                    citing_records.append({
                        "Citing DOI": citing_doi,
                        "Journal": journal,
                        "SCImago Quartile": quartile
                    })
                else:
                    citing_records.append({
                        "Citing DOI": citing_doi,
                        "Journal": "Not Found",
                        "SCImago Quartile": "Unknown"
                    })
                    quartile_summary["Unknown"] += 1
                time.sleep(1)  # Avoid being blocked

            df = pd.DataFrame(citing_records)
            st.subheader("Citing DOIs with Journal + Quartile")
            st.dataframe(df)

            st.subheader("Citation Quartile Summary")
            q_summary = pd.DataFrame([{"DOI": f"https://doi.org/{base_doi}", "Citations": len(citing_dois), **quartile_summary}])
            st.dataframe(q_summary)

            st.download_button("Download Citing Data", df.to_csv(index=False), file_name="citing_articles.csv")
            st.download_button("Download Quartile Summary", q_summary.to_csv(index=False), file_name="quartile_summary.csv")
        else:
            st.warning("No citing DOIs found via OpenAlex.")
else:
    st.info("Paste a DOI to fetch citing papers and their Scopus/Quartile status.")
