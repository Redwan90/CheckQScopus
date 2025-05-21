import streamlit as st
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import urllib.parse

API_KEY = 'c9187cfd41d4c6496be780048b47904e'  # Replace with your Scopus API Key
HEADERS = {'X-ELS-APIKey': API_KEY}

st.title("Scopus Citing Journal Quartile Checker")
doi_input = st.text_area("Paste DOIs (e.g., https://doi.org/...):", height=200)
doi_list = [d.strip().replace("https://doi.org/", "").replace("http://doi.org/", "") for d in doi_input.splitlines() if d.strip()]

@st.cache_data(show_spinner=False)
def get_eid_from_doi(doi):
    url = f"https://api.elsevier.com/content/search/scopus?query=DOI({doi})&field=eid"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        entries = res.json().get("search-results", {}).get("entry", [])
        if entries:
            return entries[0].get("eid")
    return None

@st.cache_data(show_spinner=False)
def get_citing_journals(eid):
    url = f"https://api.elsevier.com/content/abstract/citations?scopus_id={eid}"
    res = requests.get(url, headers=HEADERS)
    journals = []
    if res.status_code == 200:
        info = res.json().get("abstract-citations-response", {}).get("citeInfoMatrix", {}).get("citeInfo", [])
        for entry in info:
            journal = entry.get("sourceTitle", "").strip()
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
    with st.spinner("Checking citations and quartiles..."):
        for doi in doi_list:
            eid = get_eid_from_doi(doi)
            if not eid:
                results.append({"DOI": f"https://doi.org/{doi}", "Citing Scopus Papers": "Not found"})
                continue

            journals = get_citing_journals(eid)
            summary = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0, "Unknown": 0}

            for journal in journals:
                q = get_quartile_from_scimago(journal)
                time.sleep(1)
                if q in summary:
                    summary[q] += 1
                else:
                    summary["Unknown"] += 1

            results.append({
                "DOI": f"https://doi.org/{doi}",
                "Citing Scopus Papers": len(journals),
                **summary
            })

    df = pd.DataFrame(results)
    st.subheader("Citation + SCImago Quartile Summary")
    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False), file_name="quartile_summary.csv")
else:
    st.info("Paste at least one DOI to begin.")
