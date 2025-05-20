app.py — Streamlit app to check Scopus quartiles of citing journals (Now includes Q1–Q4)

import streamlit as st import pandas as pd

Simulated dummy data (replace with real Scopus export CSV)

dummy_data = [ {"DOI": "10.48161/qaj.v4n4a970", "Cited By Journal": "IEEE Access", "Year": 2023, "Quartile": "Q1"}, {"DOI": "10.48161/qaj.v4n4a970", "Cited By Journal": "Heliyon", "Year": 2022, "Quartile": "Q2"}, {"DOI": "10.48161/qaj.v4n4a1220", "Cited By Journal": "Sustainability", "Year": 2023, "Quartile": "Q2"}, {"DOI": "10.48161/qaj.v4n4a1220", "Cited By Journal": "Scientific Reports", "Year": 2023, "Quartile": "Q1"}, {"DOI": "10.48161/qaj.v4n4a264", "Cited By Journal": "Journal of Cleaner Production", "Year": 2021, "Quartile": "Q1"}, {"DOI": "10.48161/qaj.v4n4a931", "Cited By Journal": "Egyptian Informatics Journal", "Year": 2022, "Quartile": "Q3"}, {"DOI": "10.48161/qaj.v4n4a1423", "Cited By Journal": "International Journal of Environmental Research", "Year": 2023, "Quartile": "Q2"}, {"DOI": "10.48161/qaj.v4n4a1024", "Cited By Journal": "Mathematics", "Year": 2023, "Quartile": "Q2"}, {"DOI": "10.48161/qaj.v4n4a931", "Cited By Journal": "Asian Journal of Water", "Year": 2023, "Quartile": "Q4"} ]

Convert to DataFrame

df = pd.DataFrame(dummy_data)

Streamlit UI

st.title("Citing Journals Scopus Quartile Checker (Q1–Q4)")

user_dois = st.text_area("Paste your DOIs (one per line):", """10.48161/qaj.v4n4a970 10.48161/qaj.v4n4a1220 10.48161/qaj.v4n4a264 10.48161/qaj.v4n4a931 10.48161/qaj.v4n4a1423 10.48161/qaj.v4n4a1024""")

Process DOIs

doi_list = [doi.strip() for doi in user_dois.splitlines() if doi.strip()] filtered_df = df[df['DOI'].isin(doi_list)]

Show Results

if not filtered_df.empty: st.subheader("Citing Journals and Quartiles") st.dataframe(filtered_df)

# Quartile Summary by DOI
citation_counts = filtered_df.groupby("DOI").size().reset_index(name="Citing Scopus Papers")
quartile_summary = filtered_df.groupby(["DOI", "Quartile"]).size().reset_index(name="Count")
quartile_pivot = quartile_summary.pivot(index="DOI", columns="Quartile", values="Count").fillna(0).astype(int)
final_summary = citation_counts.merge(quartile_pivot, on="DOI")

st.subheader("Summary: Citing Quartiles by Article")
st.dataframe(final_summary)

st.download_button("Download Summary CSV", final_summary.to_csv(index=False), file_name="quartile_summary.csv")

else: st.warning("No citing journal data found for the provided DOIs in this dataset.")

