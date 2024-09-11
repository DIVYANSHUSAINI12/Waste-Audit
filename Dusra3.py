import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Cache Google Sheets API credentials in Streamlit session state
if 'creds' not in st.session_state:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("C://Users//Divyanshu//Desktop//Python_Demo//waste-ka-audit-c832a68a08ff.json", scope)
    st.session_state.creds = creds

client = gspread.authorize(st.session_state.creds)

# Open the Google Sheet
sheet = client.open("Wasteaudit").sheet1

st.set_page_config(page_title="Waste Audit", layout="wide")

# Center the title
st.markdown("<h3 style='text-align: center;'>Waste Audit Sheet</h3>", unsafe_allow_html=True)

# Text input for the school name
school_name = st.text_input("Name of your school")

# Text input for the date of the audit
audit_date = st.text_input("Date of the audit (DD-MM-YYYY)", value=datetime.today().strftime('%d-%m-%Y'))

# Define the waste types
waste_types = ['Food waste', 'Paper', 'Plastic Waste', 'Metal (Aluminium foil)', 
               'Sanitary waste', 'Horticulture/Garden waste', 'Glass', 
               'Wood (furniture waste, pencil shavings)', 'E- waste', 'Others']

# Select multiple waste types to display
selected_waste_types = st.multiselect("Select Type(s) of Waste", waste_types)

# Define the initial columns
base_columns = ['Type of Waste', 'Source/Origin of waste', 'Number of Box/beg (A)', 'Weight of the box (B)', 'Weight of the waste in box/bag 1 (in Kg) (C)', 
                'Total weight (in Kg) (D=Addition of C)', 
                'Weight of the waste (in Kg) (E=D-A*B)', 'Percentage Total (Total E-E)/Total E', 'How is it handled currently?']

# Initialize dynamic columns in session state
if 'dynamic_columns' not in st.session_state:
    st.session_state.dynamic_columns = []

# Add button for adding a new weight column
if st.button("➕ Add another weight column"):
    new_col_name = f'Weight of the waste in box/bag {len(st.session_state.dynamic_columns) + 2} (in Kg) (C)'
    st.session_state.dynamic_columns.append(new_col_name)

# Delete button for removing the last added column
if st.button("➖ Delete last added weight column") and st.session_state.dynamic_columns:
    st.session_state.dynamic_columns.pop()

# Combine base and dynamic columns
all_columns = base_columns[:5] + st.session_state.dynamic_columns + base_columns[5:]

# Create an empty DataFrame
df = pd.DataFrame(columns=all_columns)

# Add rows to the DataFrame based on the selected waste types
for waste_type in selected_waste_types:
    data = {
        'Type of Waste': [waste_type],
        'Source/Origin of waste': [''],
        'Number of Box/beg (A)': [''],
        'Weight of the box (B)': [''],
        'Weight of the waste in box/bag 1 (in Kg) (C)': [''],
        'Total weight (in Kg) (D=Addition of C)':[''],
        'Weight of the waste (in Kg) (E=D-A*B)':[''],
        'Percentage Total (Total E-E)/Total E': [''],
        'How is it handled currently?': ['']
    }
    # Add placeholders for dynamic columns
    for col in st.session_state.dynamic_columns:
        data[col] = ['']
    
    waste_df = pd.DataFrame(data, columns=all_columns)
    df = pd.concat([df, waste_df], ignore_index=True)

# Adjust the index to start from 1 instead of 0
df.index = df.index + 1

# Display the editable DataFrame
if not df.empty:
    st.write("Editing data for selected waste type(s):")
    edited_df = st.data_editor(df)

# Add a form for users to submit the data
with st.form(key='data_form'):
    st.write("Submit the audit data:")
    submitted = st.form_submit_button('Submit')
    if submitted:
        if not school_name:
            st.error("Please enter the name of your school.")
        elif not audit_date:
            st.error("Please enter the date of the audit.")
        else:
            # Prepare the data for appending to the Google Sheet
            sheet_data = edited_df.values.tolist()
            for row in sheet_data:
                row.insert(0, audit_date)
                row.insert(1, school_name)
            
            # Append each row to the Google Sheet
            for row in sheet_data:
                sheet.append_row(row)
                
            st.success(f"Data for {', '.join(selected_waste_types)} has been successfully updated.")
