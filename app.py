# app.py — Automated Scopus Citing Journal Checker (DOI list as links)

import streamlit as st
import pandas as pd
import requests

# Step 1: Configure Scopus API key
API_KEY = 'c9187cfd41d4c6496be780048b47904e'  # Replace with your Scopus API key from https://dev.elsevier.com
HEADERS = {'X-ELS-APIKey': API_KEY}

# Streamlit UI
st.title("Scopus Citing Journal Quartile Checker")
st.markdown("Paste a list of DOIs (with or without 'https://doi.org/'):")

user_input = st.text_area("DOI List", height=200)
user_dois = [
    doi.strip().replace("https://doi.org/", "").replace("http://doi.org/", "")
    for doi in user_input.splitlines() if doi.strip()
]

@st.cache_data(show_spinner=False)
def get_eid_from_doi(doi):
    url = f"https://api.elsevier.com/content/search/scopus?query=DOI({doi})&field=eid"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        entries = data.get("search-results", {}).get("entry", [])
        if entries:
            return entries[0].get("eid")
    return None

@st.cache_data(show_spinner=False)
def get_citing_document_count(eid):
    url = f"https://api.elsevier.com/content/abstract/citations?scopus_id={eid}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        cites = data.get("abstract-citations-response", {}).get("citeInfoMatrix", {}).get("citeInfo", [])
        return len(cites)
    return 0

# Step 2: Process input DOIs
results = []

if user_dois:
    with st.spinner("Querying Scopus..."):
        for doi in user_dois:
            eid = get_eid_from_doi(doi)
            if eid:
                count = get_citing_document_count(eid)
                results.append({"DOI": doi, "Citing Scopus Papers": count})
            else:
                results.append({"DOI": doi, "Citing Scopus Papers": "Not Found"})

    df = pd.DataFrame(results)
    st.subheader("Scopus Citation Summary")
    st.dataframe(df)

    st.download_button("Download CSV", df.to_csv(index=False), file_name="scopus_citation_summary.csv")
else:
    st.info("Paste at least one DOI to begin.")
