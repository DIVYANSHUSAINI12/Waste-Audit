import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Set up Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("waste-ka-audit-0d8e59002a77.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("Wasteaudit").sheet1  # Use the name of your Google Sheet

st.set_page_config(page_title="Waste Audit", layout="wide")
col1, col2 = st.columns([1, 1])

with col1:
    st.image("USAID.png", width=200)

with col2:
    st.image("images.png", width=150)

# Title of the app
st.markdown("<h3>Waste Audit Sheet</h3>", unsafe_allow_html=True)

# Text input for the school name
school_name = st.text_input("Name of your school")

# Define the number of rows and columns
rows = 10
cols = 10

# Define the column names
column_names = ['Type of Waste', 'Number of Box/bag', 'Weight of the waste in box/bag 1 (in Kg)', 'Weight of the waste in box/bag 2 (in Kg)', 'Weight of the waste in box/bag 3 (in Kg)', 'Total weight (in Kg)', 'Weight of the waste (in Kg)', 'Source/Origin of waste', 'Percentage Total', 'How is it handled currently?']

# Create a DataFrame with the specified number of rows and columns
data = {
    'Type of Waste': ['Food waste', 'Paper', 'Plastic Waste','Metal (Aluminium foil)','Sanitary waste', 'Horticulture/Garden waste', 'Glass','Wood (furniture waste, pencil shavings)', 'E- waste', 'Others'],
    'Number of Box/beg': [''] * rows,
    'Weight of the waste in box/bag 1 (in Kg)': [''] * rows,
    'Weight of the waste in box/bag 2 (in Kg)': [''] * rows,
    'Weight of the waste in box/bag 3 (in Kg)': [''] * rows,
    'Total weight (in Kg)': [''] * rows,
    'Weight of the waste (in Kg)': [''] * rows,
    'Source/Origin of waste': [''] * rows,
    'Percentage Total': [''] * rows,
    'How is it handled currently?': [''] * rows,
}
df = pd.DataFrame(data, columns=column_names)

# Display the DataFrame with editing capabilities
edited_df = st.data_editor(df, num_rows=rows)

# Custom CSS to wrap up the text in the topmost row
st.markdown("""
    <style>
    .data-editor-container .data-grid-container .data-grid-header-container .data-grid-header-row .cell {
        white-space: normal; /* Wrap up the text */
        overflow: hidden; /* Hide overflow */
        text-overflow: ellipsis; /* Show ellipsis for long text */
        line-height: 8.5; /* Adjust line height for better readability */
    }
    </style>
""", unsafe_allow_html=True)

# Add a form for users to input data manually
with st.form(key='data_form'):
    st.write("Enter data manually:")
    # Use form to collect data from users
    submitted = st.form_submit_button('Submit')
    if submitted:
        if not school_name:
            st.error("Please enter the name of your school.")
        else:
            # Get the current date
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Prepare the data for appending to the Google Sheet
            sheet_data = edited_df.values.tolist()
            for row in sheet_data:
                row.insert(0, school_name)
                row.insert(0, current_date)
            
            # Append each row to the Google Sheet
            for row in sheet_data:
                sheet.append_row(row)
                
            st.success("Data has been successfully updated in the Google Sheet.")
