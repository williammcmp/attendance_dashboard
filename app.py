from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# gets the entire google sheets
def get_sheet_data() -> pd.DataFrame:
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=600)
    df = conn.read()

    df = pd.DataFrame(df)

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    return df

# Will get n-1 days from today in the past
def get_data_for_days_ago(data: pd.DataFrame | None = None, days: int = 1) -> pd.DataFrame:
    if data is None:
        data = get_sheet_data()

    target_date = datetime.now().date() - timedelta(days=days)

    return data[data["Timestamp"].dt.date == target_date]

    
def get_all_users_names(data : pd.DataFrame | None = None) -> pd.DataFrame:
    if data is None:
        data = get_sheet_data()

    name_list = data['Person of Intrest'].unique()
    return name_list
    
def get_attendance_list(data : pd.DataFrame | None = None) -> dict:
    # TODO make this logic a bit more robust
    if data is None:
        data = get_sheet_data()

    todays_data = get_data_for_days_ago(data, 0)

    # Drop rows with missing names or status
    filtered = todays_data.dropna(subset=['Person of Intrest', 'Where is the Person of Intrest?'])

    filtered['Person of Intrest'] = filtered['Person of Intrest'].astype(str).str.strip()
    filtered['Where is the Person of Intrest?'] = filtered['Where is the Person of Intrest?'].astype(str).str.strip()

    on_campus = filtered.loc[filtered['Where is the Person of Intrest?'] == 'In the Office', 'Person of Intrest'].dropna().unique()
    
    all_names = get_all_users_names()
    off_campus = []
    for name in all_names:
        if name not in on_campus:
            off_campus.append(name)

    # print(on_campus, off_campus)
    return {'on_campus': on_campus, 'off_campus': off_campus}

def get_metric(mode : str = 'on_campus', data: pd.DataFrame | None = None) -> st.metric:
    if data is None:
        data = get_sheet_data()

    today_dict = get_attendance_list(get_data_for_days_ago(days=0))
    yesterday_dict = get_attendance_list(get_data_for_days_ago(days=1))

    if mode == 'on_campus':
        text = "On Campus 🏫"
    else:
        text = "off Campus 🏝️"

    return st.metric(text, len(today_dict[mode]), len(yesterday_dict[mode]))





st.set_page_config(page_title="Office Presence Today", layout="wide")

st.title("🏢 Who’s In the Office Today?")

# Fetch data from Google Sheet
data = get_sheet_data()

attendance_dict = get_attendance_list(get_data_for_days_ago(data, 0))


col1, col2 = st.columns(2)

with col1:
    get_metric('on_campus', data)
    st.dataframe(attendance_dict['on_campus'])

with col2:
    get_metric('off_campus', data)
    st.dataframe(attendance_dict['off_campus'])




with st.expander("J-Dog and Friends Google Form"):
    st.text("Applogies for the sudden bright mode for the good sheet. Please forgive 🙏")
    st.markdown(
        """
        <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSfz9XKgkhV8ls8UFgN1iWWLdy5VxxxMiIX8OKHN-1k0sEUeEg/viewform?embedded=true" width="100%" height="1860" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
        """,
        unsafe_allow_html=True,
    )