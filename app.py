# app.py — Scopus Citing Journal Checker (Supports full https://doi.org links)

import streamlit as st
import pandas as pd
import requests

# Scopus API configuration
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your valid Scopus API key
HEADERS = {'X-ELS-APIKey': API_KEY}

st.title("Scopus Citing Papers Checker")
st.markdown("Paste a list of DOIs (e.g., `https://doi.org/10.xxxx`) below:")

# Text input for full DOI links
user_input = st.text_area("Enter DOIs (one per line):", height=200)

# Normalize DOIs by removing 'https://doi.org/' prefix
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
        cites = response.json().get("abstract-citations-response", {}).get("citeInfoMatrix", {}).get("citeInfo", [])
        return len(cites)
    return 0

results = []

if user_dois:
    with st.spinner("Checking citations in Scopus..."):
        for doi in user_dois:
            eid = get_eid_from_doi(doi)
            if eid:
                count = get_citing_document_count(eid)
                results.append({"DOI": f"https://doi.org/{doi}", "Citing Scopus Papers": count})
            else:
                results.append({"DOI": f"https://doi.org/{doi}", "Citing Scopus Papers": "Not found"})

    df = pd.DataFrame(results)
    st.subheader("Scopus Citation Results")
    st.dataframe(df)

    st.download_button("Download Results as CSV", df.to_csv(index=False), file_name="scopus_citations.csv")
else:
    st.info("Paste at least one DOI above to begin.")
