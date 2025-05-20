# app.py — Streamlit app to check Scopus quartiles of citing journals (Simulated)

import streamlit as st
import pandas as pd

# Simulated dummy data (replace with Scopus API or scraping later)
dummy_data = [
    {"DOI": "10.48161/qaj.v4n4a970", "Cited By Journal": "IEEE Access", "Year": 2023, "Quartile": "Q1"},
    {"DOI": "10.48161/qaj.v4n4a970", "Cited By Journal": "Heliyon", "Year": 2022, "Quartile": "Q2"},
    {"DOI": "10.48161/qaj.v4n4a1220", "Cited By Journal": "Sustainability", "Year": 2023, "Quartile": "Q2"},
    {"DOI": "10.48161/qaj.v4n4a1220", "Cited By Journal": "Scientific Reports", "Year": 2023, "Quartile": "Q1"},
    {"DOI": "10.48161/qaj.v4n4a264", "Cited By Journal": "Journal of Cleaner Production", "Year": 2021, "Quartile": "Q1"},
    {"DOI": "10.48161/qaj.v4n4a931", "Cited By Journal": "Egyptian Informatics Journal", "Year": 2022, "Quartile": "Q3"},
    {"DOI": "10.48161/qaj.v4n4a1423", "Cited By Journal": "International Journal of Environmental Research", "Year": 2023, "Quartile": "Q2"},
    {"DOI": "10.48161/qaj.v4n4a1024", "Cited By Journal": "Mathematics", "Year": 2023, "Quartile": "Q2"}
]

# Convert to DataFrame
df = pd.DataFrame(dummy_data)

# Streamlit UI
st.title("Citing Journals Scopus Quartile Checker (Simulated)")

user_dois = st.text_area("Paste your DOIs (one per line):", """10.48161/qaj.v4n4a970
10.48161/qaj.v4n4a1220
10.48161/qaj.v4n4a264
10.48161/qaj.v4n4a931
10.48161/qaj.v4n4a1423
10.48161/qaj.v4n4a1024""")

# Process DOIs
doi_list = [doi.strip() for doi in user_dois.splitlines() if doi.strip()]
filtered_df = df[df['DOI'].isin(doi_list)]

# Show Results
if not filtered_df.empty:
    st.subheader("Citing Journals and Quartiles")
    st.dataframe(filtered_df)

    # Quartile Summary
    quartile_summary = filtered_df.groupby('Quartile').size().reset_index(name='Count')
    st.subheader("Quartile Distribution")
    st.bar_chart(quartile_summary.set_index('Quartile'))

    # Download option
    st.download_button("Download as CSV", filtered_df.to_csv(index=False), file_name="citing_quartiles.csv")
else:
    st.warning("No data found for the given DOIs in the simulated dataset.")
