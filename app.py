from flask import Flask, render_template_string, request
import threading, requests, time

app = Flask(__name__)

# Global flag to control the wake loop
wake_running = False

def wake_web():
    global wake_running
    while wake_running:
        with open('weblist.txt', 'r') as f:
            url = f.readline()
            while url:
                try:
                    response = requests.get(url.strip())
                    response.raise_for_status()
                    print(f'Successfully visited your web: {url.strip()}')
                    print(f'Status code: {response.status_code}')
                except requests.RequestException as e:
                    print(f'Error detected as: {e}')
                url = f.readline()
        time.sleep(30)

@app.route('/')
def index():
    return render_template_string('''
        <h2>Wake Web Service</h2>
        <form action="/start" method="post">
            <button type="submit">Start Wake</button>
        </form>
        <form action="/stop" method="post">
            <button type="submit">Stop Wake</button>
        </form>
    ''')

@app.route('/start', methods=['POST'])
def start_wake():
    global wake_running
    if not wake_running:
        wake_running = True
        threading.Thread(target=wake_web, daemon=True).start()
    return "Wake process started. <a href='/'>Back</a>"

@app.route('/stop', methods=['POST'])
def stop_wake():
    global wake_running
    wake_running = False
    return "Wake process stopped. <a href='/'>Back</a>"
