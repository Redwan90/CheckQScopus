#app.py — Automated Scopus Citing Journal Checker (DOI list as links)

import streamlit as st import pandas as pd import requests

API Configuration

API_KEY = 'c9187cfd41d4c6496be780048b47904e'  # Replace this with your actual Elsevier Scopus API key HEADERS = {'X-ELS-APIKey': API_KEY}

Streamlit UI

st.title("Scopus Citing Journal Quartile Checker") st.markdown("Paste a list of DOIs (with or without https://doi.org/) below:")

user_input = st.text_area("DOI List", height=200)

Clean DOIs and normalize

user_dois = [doi.strip().replace("https://doi.org/", "") for doi in user_input.splitlines() if doi.strip()]

@st.cache_data(show_spinner=False) def get_eid_from_doi(doi): url = f"https://api.elsevier.com/content/search/scopus?query=DOI({doi})&field=eid" res = requests.get(url, headers=HEADERS) if res.status_code == 200: data = res.json() entries = data.get("search-results", {}).get("entry", []) if entries: return entries[0].get("eid") return None

@st.cache_data(show_spinner=False) def get_citing_journals(eid): url = f"https://api.elsevier.com/content/abstract/citations?scopus_id={eid}" res = requests.get(url, headers=HEADERS) if res.status_code == 200: return res.json() return {}

results = []

if user_dois: with st.spinner("Fetching citation data from Scopus..."): for doi in user_dois: eid = get_eid_from_doi(doi) if not eid: results.append({"DOI": doi, "Error": "EID not found"}) continue

citing_data = get_citing_journals(eid)
        citing_docs = citing_data.get("abstract-citations-response", {}).get("citeInfoMatrix", {}).get("citeInfo", [])

        if citing_docs:
            count = len(citing_docs)
            results.append({"DOI": doi, "Citing Scopus Papers": count})
        else:
            results.append({"DOI": doi, "Citing Scopus Papers": 0})

df_results = pd.DataFrame(results)
st.subheader("Scopus Citation Summary")
st.dataframe(df_results)
st.download_button("Download CSV", df_results.to_csv(index=False), file_name="scopus_citation_summary.csv")

else: st.info("Paste at least one DOI to begin.")

