#app.py — Streamlit app to check Scopus quartiles of citing journals (NO CSV required)

import streamlit as st import pandas as pd

Simulated citation data

citation_data = [ {"DOI": "10.48161/qaj.v4n3a918", "Cited By Journal": "IEEE Access", "Year": 2023, "Quartile": "Q1"}, {"DOI": "10.48161/qaj.v4n3a773", "Cited By Journal": "Heliyon", "Year": 2022, "Quartile": "Q2"}, {"DOI": "10.48161/qaj.v4n3a773", "Cited By Journal": "Scientific Reports", "Year": 2023, "Quartile": "Q1"}, {"DOI": "10.48161/qaj.v4n3a733", "Cited By Journal": "Journal of Cleaner Production", "Year": 2021, "Quartile": "Q1"}, {"DOI": "10.48161/qaj.v4n3a699", "Cited By Journal": "Mathematics", "Year": 2023, "Quartile": "Q2"}, {"DOI": "10.48161/qaj.v4n3a699", "Cited By Journal": "Egyptian Informatics Journal", "Year": 2022, "Quartile": "Q3"}, {"DOI": "10.48161/qaj.v4n3a699", "Cited By Journal": "Asian Journal of Water", "Year": 2023, "Quartile": "Q4"} ]

Convert to DataFrame

df = pd.DataFrame(citation_data)

Streamlit UI

st.title("Citing Journals Scopus Quartile Checker (Paste DOI List)")

user_input = st.text_area("Paste DOIs (one per line, with or without 'https://doi.org/'):") user_dois = [doi.strip().replace("https://doi.org/", "") for doi in user_input.splitlines() if doi.strip()]

Filter and process

if user_dois: filtered_df = df[df['DOI'].isin(user_dois)]

if not filtered_df.empty:
    st.subheader("Citing Journals and Quartiles")
    st.dataframe(filtered_df)

    # Summary
    citation_counts = filtered_df.groupby("DOI").size().reset_index(name="Citing Scopus Papers")
    quartile_summary = filtered_df.groupby(["DOI", "Quartile"]).size().reset_index(name="Count")
    quartile_pivot = quartile_summary.pivot(index="DOI", columns="Quartile", values="Count").fillna(0).astype(int)
    final_summary = citation_counts.merge(quartile_pivot, on="DOI")

    st.subheader("Quartile Summary per Article")
    st.dataframe(final_summary)

    st.download_button("Download Summary CSV", final_summary.to_csv(index=False), file_name="quartile_summary.csv")
else:
    st.warning("No matching DOIs found in the internal dataset.")

else: st.info("Paste at least one DOI to begin.")

