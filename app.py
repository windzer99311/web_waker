from flask import Flask
import threading, requests, time

app = Flask(__name__)

def wake_web():
    while True:
        with open('weblist.txt', 'r') as f:
            url = f.readline()
            while url:
                url = url.strip()
                if url:
                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        print(f'Successfully visited your web: {url}')
                        print(f'Status code: {response.status_code}')
                    except requests.RequestException as e:
                        print(f'Error detected as: {e}')
                url = f.readline()
        time.sleep(30)

@app.route('/')
def index():
    return "Wake web running..."

# Start wake_web in a background thread as soon as the app launches
threading.Thread(target=wake_web, daemon=True).start()
