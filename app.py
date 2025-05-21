#app.py — Crossref + Scopus + SCImago Citation Quartile Tracker

import streamlit as st import pandas as pd import requests import time from bs4 import BeautifulSoup import urllib.parse

API_KEY = 'c9187cfd41d4c6496be780048b47904e' HEADERS = {'X-ELS-APIKey': API_KEY}

st.title("Citing Journal Quartile Checker (Crossref + Scopus + SCImago)") doi_input = st.text_area("Paste DOIs (https://doi.org/...):", height=200) doi_list = [d.strip().replace("https://doi.org/", "") for d in doi_input.splitlines() if d.strip()]

@st.cache_data(show_spinner=False) def get_crossref_citers(doi): url = f"https://api.crossref.org/works/{doi}/cited-by" r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}) if r.status_code == 200: items = r.json().get("message", {}).get("items", []) return [item.get("DOI") for item in items if item.get("DOI")] return []

@st.cache_data(show_spinner=False) def get_scopus_journal_name(citing_doi): url = f"https://api.elsevier.com/content/search/scopus?query=DOI({citing_doi})&field=source-title" r = requests.get(url, headers=HEADERS) if r.status_code == 200: entries = r.json().get("search-results", {}).get("entry", []) if entries: return entries[0].get("source-title", "Unknown") return None

@st.cache_data(show_spinner=False) def get_quartile_from_scimago(journal_name): query = urllib.parse.quote(journal_name) search_url = f"https://www.scimagojr.com/journalsearch.php?q={query}" try: r = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10) soup = BeautifulSoup(r.text, 'html.parser') link = soup.select_one('a[href*="journalsearch.php?id="]') if not link: return "Unknown" journal_url = "https://www.scimagojr.com/" + link['href'] rj = requests.get(journal_url, headers={"User-Agent": "Mozilla/5.0"}) jsoup = BeautifulSoup(rj.text, 'html.parser') for row in jsoup.select("table.table.table-condensed tr"): cells = row.find_all("td") if len(cells) >= 4: quartile = cells[3].text.strip() if quartile.startswith("Q"): return quartile except: return "Error" return "Unknown"

results = []

if doi_list: with st.spinner("Checking citations via Crossref and Scopus..."): for original_doi in doi_list: citers = get_crossref_citers(original_doi) journal_quartiles = []

for citing_doi in citers:
            journal = get_scopus_journal_name(citing_doi)
            if journal:
                q = get_quartile_from_scimago(journal)
                journal_quartiles.append(q)
                time.sleep(1)

        summary = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0, "Unknown": 0}
        for q in journal_quartiles:
            if q in summary:
                summary[q] += 1
            else:
                summary["Unknown"] += 1

        results.append({
            "DOI": f"https://doi.org/{original_doi}",
            "Citing Scopus Papers": len(journal_quartiles),
            **summary
        })

df = pd.DataFrame(results)
st.subheader("Citation + Quartile Summary")
st.dataframe(df)
st.download_button("Download CSV", df.to_csv(index=False), file_name="citation_quartile_summary.csv")

else: st.info("Paste at least one DOI to begin.")

