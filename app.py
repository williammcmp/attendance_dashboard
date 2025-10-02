from datetime import datetime, timedelta
import pytz
import streamlit as st
import numpy as np
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# gets the entire google sheets
def get_sheet_data() -> pd.DataFrame:
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=30) # Update time set to refresh the connection every 30 s
    df = conn.read()

    df = pd.DataFrame(df)

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    return df

# Will get n-1 days from today in the past
def get_data_for_days_ago(data: pd.DataFrame, days: int = 1, tz="Australia/Melbourne") -> pd.DataFrame:

    # Get Australian timezone
    au_tz = pytz.timezone(tz)

    # Current date in that zone
    target_date = datetime.now(au_tz).date() - timedelta(days=days)

    return data[data["Timestamp"].dt.date == target_date]

    
def get_all_users_names(data : pd.DataFrame) -> pd.DataFrame:

    name_list = data['Person of Intrest'].unique()
    return name_list
    
def get_attendance_list(data : pd.DataFrame) -> dict:
    # TODO make this logic a bit more robust

    # Drop rows with missing names or status
    filtered = data.dropna(subset=['Person of Intrest', 'Where is the Person of Intrest?'])

    filtered['Person of Intrest'] = filtered['Person of Intrest'].astype(str).str.strip()
    filtered['Where is the Person of Intrest?'] = filtered['Where is the Person of Intrest?'].astype(str).str.strip()

    on_campus = filtered.loc[filtered['Where is the Person of Intrest?'] == 'In the Office', 'Person of Intrest'].dropna().unique()
    
    all_names = get_all_users_names(data)
    off_campus = []
    for name in all_names:
        if name not in on_campus:
            off_campus.append(name)

    return {'on_campus': np.sort(on_campus), 'off_campus': np.sort(off_campus)}

def get_last_5_days(data: pd.DataFrame):

    temp_on_campus = []
    temp_off_campus = []

    for i in range(5):
        
        temp_dict = get_attendance_list(get_data_for_days_ago(data=data, days=i))
        temp_on_campus.append(len(temp_dict['on_campus']))
        temp_off_campus.append(len(temp_dict['off_campus']))

    temp_on_campus.reverse()
    temp_off_campus.reverse()

    print(temp_on_campus, temp_off_campus)

def get_metric(data: pd.DataFrame, mode : str = 'on_campus') -> st.metric:

    today_dict = get_attendance_list(get_data_for_days_ago(data, days=0))
    yesterday_dict = get_attendance_list(get_data_for_days_ago(data, days=1))

    if mode == 'on_campus':
        text = "On Campus 🏫"
    else:
        text = "Off Campus 🏝️"

    # return st.metric(text, len(today_dict[mode]))
    return st.metric(text, len(today_dict[mode]), len(today_dict[mode])-len(yesterday_dict[mode]))


st.set_page_config(page_title="Office Presence Today", layout="wide")

st.title("🏢 Who’s In the Office Today?")

if st.button("🔄 Refresh data now"):
    st.cache_data.clear()   # clear cached data
    st.rerun()

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

if st.button('test'):
    get_last_5_days()

with st.expander("J-Dog and Friends Google Form"):
    st.text("Applogies for the sudden bright mode for the good sheet. Please forgive 🙏")
    st.markdown(
        """
        <iframe src="https://docs.google.com/forms/d/e/1FAIpQLSfz9XKgkhV8ls8UFgN1iWWLdy5VxxxMiIX8OKHN-1k0sEUeEg/viewform?embedded=true" width="100%" height="1860" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>
        """,
        unsafe_allow_html=True,
    )