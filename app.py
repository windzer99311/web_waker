import streamlit as st
import threading
import requests
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import os

# Constants
VIRTUAL_START_STR = "2025-06-13 00:00:00"
VIRTUAL_START = datetime.strptime(VIRTUAL_START_STR, "%Y-%m-%d %H:%M:%S")
BOOT_TIME_FILE = "boot_time.txt"
logs = []

# Load or create persistent server start time
if os.path.exists(BOOT_TIME_FILE):
    with open(BOOT_TIME_FILE, "r") as f:
        REAL_SERVER_START = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
else:
    REAL_SERVER_START = datetime.now()
    with open(BOOT_TIME_FILE, "w") as f:
        f.write(REAL_SERVER_START.strftime("%Y-%m-%d %H:%M:%S"))

# Wake web function with global log access
def wake_web():
    global logs
    while True:
        try:
            with open('weblist.txt', 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                for url in urls:
                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        msg1 = f"Successfully visited your web: {url}"
                        msg2 = f"Status code: {response.status_code}"
                        print(msg1)
                        print(msg2)
                        logs.append(msg1)
                        logs.append(msg2)
                    except requests.RequestException as e:
                        err = f"Error detected as: {e}"
                        print(err)
                        logs.append(err)
        except FileNotFoundError:
            logs.append("weblist.txt not found.")

        if len(logs) > 100:
            del logs[:len(logs) - 100]

        time.sleep(30)

# Ensure the thread starts only once
if 'thread_started' not in st.session_state:
    print("Starting background thread...")
    threading.Thread(target=wake_web, daemon=True).start()
    st.session_state.thread_started = True

# Refresh UI every second
st_autorefresh(interval=1000, key="timer_refresh")

# Display virtual time
elapsed_real = (datetime.now() - REAL_SERVER_START).total_seconds()
current_virtual = VIRTUAL_START + timedelta(seconds=elapsed_real)

st.title("Wake Web Streamlit")
st.write("### Time running since:")
st.code(current_virtual.strftime("%Y-%m-%d %H:%M:%S"))

# Show log
st.write("### Request Log")
st.code("\n".join(logs[-100:]))
