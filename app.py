from flask import Flask, render_template_string, jsonify
import threading, requests, time
from datetime import datetime

app = Flask(__name__)

# Virtual start time and server boot time
virtual_start_str = "2025-06-13 00:00:00"
virtual_start = datetime.strptime(virtual_start_str, "%Y-%m-%d %H:%M:%S")
real_server_start = datetime.now()

# Store log messages
logs = []

# Wake web loop with logging
def wake_web():
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
            msg = "weblist.txt not found."
            print(msg)
            logs.append(msg)

        # Limit log size
        if len(logs) > 100:
            del logs[:len(logs) - 100]

        time.sleep(30)

@app.route('/')
def index():
    return render_template_string(f'''
        <html>
        <head>
            <title>Wake Web</title>
            <script>
                const virtualStart = new Date("{virtual_start_str}").getTime();
                const serverStart = new Date("{real_server_start.strftime('%Y-%m-%dT%H:%M:%S')}").getTime();
                const pageOpened = new Date().getTime();
                const offset = pageOpened - serverStart;

                function updateTime() {{
                    const now = new Date().getTime();
                    const elapsed = now - pageOpened + offset;
                    const displayTime = new Date(virtualStart + elapsed);

                    const year = displayTime.getFullYear();
                    const month = String(displayTime.getMonth() + 1).padStart(2, '0');
                    const day = String(displayTime.getDate()).padStart(2, '0');
                    const hour = String(displayTime.getHours()).padStart(2, '0');
                    const min = String(displayTime.getMinutes()).padStart(2, '0');
                    const sec = String(displayTime.getSeconds()).padStart(2, '0');

                    document.getElementById("timer").innerText =
                        `Time running since ${{year}}-${{month}}-${{day}} ${{hour}}:${{min}}:${{sec}}`;
                }}

                function fetchLogs() {{
                    fetch('/logs')
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById("log").innerText = data.logs.join("\\n");
                        }});
                }}

                setInterval(updateTime, 1000);
                setInterval(fetchLogs, 5000);
                window.onload = function() {{
                    updateTime();
                    fetchLogs();
                }};
            </script>
        </head>
        <body>
            <h2>Wake web running...</h2>
            <p id="timer">Time running since {virtual_start_str}</p>
            <h3>Request Log</h3>
            <pre id="log" style="background:#eee;padding:10px;border-radius:5px;height:300px;overflow:auto;"></pre>
        </body>
        </html>
    ''')

# Endpoint to fetch logs
@app.route('/logs')
def get_logs():
    return jsonify(logs=logs[-100:])  # send only last 100 messages

# Background thread
threading.Thread(target=wake_web, daemon=True).start()
