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
LOG_FILE = "logs.txt"

# Set or load the real boot time
if os.path.exists(BOOT_TIME_FILE):
    with open(BOOT_TIME_FILE, "r") as f:
        REAL_SERVER_START = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
else:
    REAL_SERVER_START = datetime.now()
    with open(BOOT_TIME_FILE, "w") as f:
        f.write(REAL_SERVER_START.strftime("%Y-%m-%d %H:%M:%S"))

# Wake web background task (writes to logs.txt)
def wake_web():
    while True:
        log_lines = []
        try:
            with open('weblist.txt', 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
                for url in urls:
                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        msg1 = f"Visited: {url}"
                        msg2 = f"Status: {response.status_code}"
                        log_lines.extend([msg1, msg2])
                        print(msg1, msg2)
                    except requests.RequestException as e:
                        err = f"Error: {e}"
                        log_lines.append(err)
                        print(err)
        except FileNotFoundError:
            log_lines.append("weblist.txt not found.")

        # Append new logs to file
        if log_lines:
            with open(LOG_FILE, "a") as f:
                for line in log_lines:
                    f.write(line + "\n")

        time.sleep(30)

# Start background thread only once
if "thread_started" not in st.session_state:
    threading.Thread(target=wake_web, daemon=True).start()
    st.session_state.thread_started = True

# Auto-refresh every 1s
st_autorefresh(interval=1000, key="refresh")

# Virtual time display
elapsed_real = (datetime.now() - REAL_SERVER_START).total_seconds()
current_virtual = VIRTUAL_START + timedelta(seconds=elapsed_real)

st.title("Wake Web Streamlit")
st.write("### Time running since:")
st.code(current_virtual.strftime("%Y-%m-%d %H:%M:%S"))

# Load last 100 log lines from file
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
        last_lines = lines[-100:]
        st.write("### Request Log")
        st.code("".join(last_lines))
else:
    st.write("### Request Log")
    st.info("No logs yet.")
