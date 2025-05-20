app.py — Streamlit app to check Scopus quartiles of citing journals from uploaded CSV

import streamlit as st import pandas as pd

st.title("Citing Journals Scopus Quartile Checker (CSV-Based)")

Upload CSV file containing DOI, Cited By Journal, Year, and Quartile

uploaded_file = st.file_uploader("Upload a CSV file with citation data", type=["csv"])

if uploaded_file: try: df = pd.read_csv(uploaded_file, encoding="ISO-8859-1") df.columns = [col.strip().replace("\ufeff", "") for col in df.columns]

# Let user paste DOI list
    user_input = st.text_area("Paste DOIs (one per line, with or without https://doi.org/)")
    user_dois = [doi.strip().replace("https://doi.org/", "") for doi in user_input.splitlines() if doi.strip()]

    # Filter based on input DOIs
    filtered_df = df[df['DOI'].isin(user_dois)]

    if not filtered_df.empty:
        st.subheader("Citing Journals and Quartiles")
        st.dataframe(filtered_df)

        # Quartile Summary
        citation_counts = filtered_df.groupby("DOI").size().reset_index(name="Citing Scopus Papers")
        quartile_summary = filtered_df.groupby(["DOI", "Quartile"]).size().reset_index(name="Count")
        quartile_pivot = quartile_summary.pivot(index="DOI", columns="Quartile", values="Count").fillna(0).astype(int)
        final_summary = citation_counts.merge(quartile_pivot, on="DOI")

        st.subheader("Summary: Citing Quartiles per Article")
        st.dataframe(final_summary)
        st.download_button("Download Summary as CSV", final_summary.to_csv(index=False), file_name="quartile_summary.csv")
    else:
        st.warning("None of the provided DOIs were found in the uploaded dataset.")

except Exception as e:
    st.error(f"Error reading the uploaded file: {e}")

else: st.info("Please upload a CSV file with citation data (columns: DOI, Cited By Journal, Year, Quartile).")

