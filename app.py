import streamlit as st
import pandas as pd
import requests
import urllib.parse
import time
from bs4 import BeautifulSoup

# Configure Scopus API
API_KEY = 'YOUR_SCOPUS_API_KEY'  # Replace with your valid Scopus API key
HEADERS = {'X-ELS-APIKey': API_KEY}

# Streamlit UI
st.title("Scopus Citing Journals with Real-Time SCImago Quartiles")
st.markdown("Paste a list of DOIs (e.g., https://doi.org/10.xxxx):")

user_input = st.text_area("Enter DOIs below:", height=200)
user_dois = [doi.strip().replace("https://doi.org/", "").replace("http://doi.org/", "") for doi in user_input.splitlines() if doi.strip()]

@st.cache_data(show_spinner=False)
def get_eid_from_doi(doi):
    url = f"https://api.elsevier.com/content/search/scopus?query=DOI({doi})&field=eid"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        entries = r.json().get("search-results", {}).get("entry", [])
        if entries:
            return entries[0].get("eid")
    return None

@st.cache_data(show_spinner=False)
def get_citing_journals(eid):
    url = f"https://api.elsevier.com/content/abstract/citations?scopus_id={eid}"
    r = requests.get(url, headers=HEADERS)
    journals = []
    if r.status_code == 200:
        cite_info = r.json().get("abstract-citations-response", {}).get("citeInfoMatrix", {}).get("citeInfo", [])
        for item in cite_info:
            journal = item.get("sourceTitle", "").strip()
            if journal:
                journals.append(journal)
    return journals

@st.cache_data(show_spinner=False)
def get_quartile_live(journal_name):
    base_url = "https://www.scimagojr.com/journalsearch.php?q="
    query = urllib.parse.quote(journal_name.strip())
    full_url = f"{base_url}{query}"
    try:
        response = requests.get(full_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            link = soup.select_one('a[href*="journalsearch.php?id="]')
            if not link:
                return "Unknown"
            journal_url = "https://www.scimagojr.com/" + link['href']
            journal_page = requests.get(journal_url, headers={"User-Agent": "Mozilla/5.0"})
            if journal_page.status_code == 200:
                jsoup = BeautifulSoup(journal_page.text, 'html.parser')
                for row in jsoup.select("table.table.table-condensed tr"):
                    cells = row.find_all("td")
                    if len(cells) >= 4:
                        quartile = cells[3].text.strip()
                        if quartile.startswith("Q"):
                            return quartile
        return "Unknown"
    except Exception:
        return "Error"

results = []

if user_dois:
    with st.spinner("Fetching data from Scopus and SCImago..."):
        for doi in user_dois:
            eid = get_eid_from_doi(doi)
            if not eid:
                results.append({"DOI": f"https://doi.org/{doi}", "Citing Scopus Papers": "Not found"})
                continue

            citing_journals = get_citing_journals(eid)
            quartile_summary = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0, "Unknown": 0}
            for journal in citing_journals:
                q = get_quartile_live(journal)
                time.sleep(1)  # Be respectful to SCImago
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
    st.subheader("Citation + Real-Time Quartile Summary")
    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False), file_name="scopus_scimago_summary.csv")
else:
    st.info("Paste at least one DOI above to begin.")
