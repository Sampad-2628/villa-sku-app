import streamlit as st
import json
from utils import connect_to_gsheet, read_sheet_as_df, append_row, generate_sku_code, get_existing_sku_codes

# Set up config
st.set_page_config("Villa Mart SKU Generator", layout="wide")

# ✅ Your Google Sheet name
SHEET_NAME = "villa_sku_data"

# Load config data
with open("data/categories.json") as f:
    categories = json.load(f)

with open("data/weighing_methods.json") as f:
    weighing_methods = json.load(f)

with open("data/partners.json") as f:
    partners = json.load(f)

# Connect to Google Sheet
sheet = connect_to_gsheet(SHEET_NAME)

# UI
tab1, tab2 = st.tabs(["📦 SKU Code Generator", "⚙️ Backend"])

with tab1:
    st.title("📦 Villa Mart SKU Code Generator")

    with st.form("sku_form"):
        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox("Select Category", list(categories.keys()))
            sku_name = st.text_input("Enter SKU Name")
            weighing = st.selectbox("Select Weighing Method", list(weighing_methods.keys()))

        with col2:
            quantity = st.text_input("Enter Quantity (e.g. 500gm or 2 bundles)")
            selected_partners = st.multiselect("Select Partners", list(partners.keys()))

        submitted = st.form_submit_button("Generate SKU Code")

    if submitted:
        if not sku_name.strip():
            st.error("❌ SKU Name cannot be empty.")
        else:
            existing_codes = get_existing_sku_codes(sheet)
            sku_code, conflict_code = generate_sku_code(sku_name, existing_codes)

            if not sku_code:
                st.error(f"❌ SKU Code '{conflict_code}' already exists!")
            else:
                category_code = categories[category]
                variant_code = "01"
                final_code = f"V-{category_code}-{sku_code}-{variant_code}"

                st.success(f"✅ Final Code: {final_code}")

                row = {
                    "SKU Name": sku_name,
                    "SKU Name Code": sku_code,
                    "Category": category,
                    "Weighing Method": weighing,
                    "Quantity": quantity,
                    "Partners": ", ".join(selected_partners),
                    "Final Code": final_code
                }

                append_row(sheet, row)

    df = read_sheet_as_df(sheet)
    if not df.empty:
        st.subheader("📋 All SKU Entries")
        st.dataframe(df)
        st.download_button("⬇️ Export as CSV", df.to_csv(index=False), file_name="sku_data.csv", mime="text/csv")

with tab2:
    st.header("⚙️ Backend Editing (use local JSON)")
    st.write("To add/edit categories, partners, or weighing methods, edit the JSON files in the `/data` folder.")
