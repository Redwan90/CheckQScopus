# app.py — Streamlit app to check Scopus quartiles of citing journals from uploaded CSV

import streamlit as st
import pandas as pd

st.title("Citing Journals Scopus Quartile Checker (CSV-Based)")

# Step 1: Upload CSV file
uploaded_file = st.file_uploader("Upload CSV with columns: DOI, Cited By Journal, Year, Quartile", type=["csv"])

if uploaded_file:
    try:
        # Load the CSV
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
        df.columns = [col.strip().replace("\ufeff", "") for col in df.columns]  # clean BOM

        # Step 2: Paste DOIs
        user_input = st.text_area("Paste DOIs (one per line, with or without 'https://doi.org/'):")
        user_dois = [
            doi.strip().replace("https://doi.org/", "") 
            for doi in user_input.splitlines() if doi.strip()
        ]

        if user_dois:
            # Step 3: Filter data based on DOIs
            filtered_df = df[df['DOI'].isin(user_dois)]

            if not filtered_df.empty:
                st.subheader("Citing Journals and Quartiles")
                st.dataframe(filtered_df)

                # Step 4: Quartile Summary
                citation_counts = filtered_df.groupby("DOI").size().reset_index(name="Citing Scopus Papers")
                quartile_summary = filtered_df.groupby(["DOI", "Quartile"]).size().reset_index(name="Count")
                quartile_pivot = quartile_summary.pivot(index="DOI", columns="Quartile", values="Count").fillna(0).astype(int)
                final_summary = citation_counts.merge(quartile_pivot, on="DOI")

                st.subheader("Quartile Summary per Article")
                st.dataframe(final_summary)

                # Step 5: Download
                st.download_button("Download Summary CSV", final_summary.to_csv(index=False), file_name="quartile_summary.csv")
            else:
                st.warning("None of the provided DOIs were found in the uploaded dataset.")
        else:
            st.info("Please paste at least one DOI to continue.")

    except Exception as e:
        st.error(f"Error reading the uploaded file: {e}")
else:
    st.info("Please upload a CSV file first.")
