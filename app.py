# app.py — Streamlit app to check Scopus quartiles of citing journals (Paste DOI List)

import streamlit as st
import pandas as pd

# Simulated citation data (expand this as needed)
citation_data = [
    {"DOI": "10.48161/qaj.v4n3a918", "Cited By Journal": "IEEE Access", "Year": 2023, "Quartile": "Q1"},
    {"DOI": "10.48161/qaj.v4n3a773", "Cited By Journal": "Heliyon", "Year": 2022, "Quartile": "Q2"},
    {"DOI": "10.48161/qaj.v4n3a773", "Cited By Journal": "Scientific Reports", "Year": 2023, "Quartile": "Q1"},
    {"DOI": "10.48161/qaj.v4n3a733", "Cited By Journal": "Journal of Cleaner Production", "Year": 2021, "Quartile": "Q1"},
    {"DOI": "10.48161/qaj.v4n3a699", "Cited By Journal": "Mathematics", "Year": 2023, "Quartile": "Q2"},
    {"DOI": "10.48161/qaj.v4n3a699", "Cited By Journal": "Egyptian Informatics Journal", "Year": 2022, "Quartile": "Q3"},
    {"DOI": "10.48161/qaj.v4n3a699", "Cited By Journal": "Asian Journal of Water", "Year": 2023, "Quartile": "Q4"}
]

# Convert to DataFrame
df = pd.DataFrame(citation_data)

# Streamlit UI
st.title("Citing Journals Scopus Quartile Checker (Paste DOI List)")

# Input area
user_input = st.text_area("Paste DOIs (one per line, with or without 'https://doi.org/'):")

# Clean and normalize DOIs
user_dois = [doi.strip().replace("https://doi.org/", "") for doi in user_input.splitlines() if doi.strip()]

# Processing and display
if user_dois:
    filtered_df = df[df['DOI'].isin(user_dois)]

    if not filtered_df.empty:
        st.subheader("Citing Journals and Their Quartiles")
        st.dataframe(filtered_df)

        # Summarize citation counts and quartiles
        citation_counts = filtered_df.groupby("DOI").size().reset_index(name="Citing Scopus Papers")
        quartile_summary = filtered_df.groupby(["DOI", "Quartile"]).size().reset_index(name="Count")
        quartile_pivot = quartile_summary.pivot(index="DOI", columns="Quartile", values="Count").fillna(0).astype(int)
        final_summary = citation_counts.merge(quartile_pivot, on="DOI")

        st.subheader("Quartile Summary per Article")
        st.dataframe(final_summary)

        # Download CSV
        st.download_button("Download Summary CSV", final_summary.to_csv(index=False), file_name="quartile_summary.csv")
    else:
        st.warning("No matching DOIs found in the internal dataset.")
else:
    st.info("Please paste at least one DOI to begin.")
