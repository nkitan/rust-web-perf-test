import requests
import time
import subprocess
import os
import psutil
import websocket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from datetime import datetime

HW_TEST = False

# Paths to the Actix, Axum and Rocket program executables
ACTIX_PROGRAM_PATH = "./actix-webserver/target/release/actix-webserver"
AXUM_PROGRAM_PATH = "./axum-webserver/target/release/axum-webserver"
ROCKET_PROGRAM_PATH = "./rocket-webserver/target/release/rocket-webserver"

# URL endpoints for Actix, Axum and Rocket programs
ACTIX_URL = "http://127.0.0.1:8080/api/logo"
AXUM_URL = "http://127.0.0.1:8080/api/logo"
ROCKET_URL = "http://127.0.0.1:8080/api/logo"

ACTIX_WS_URL = "ws://127.0.0.1:8080/ws/"
AXUM_WS_URL = "ws://127.0.0.1:8080/ws/"
ROCKET_WS_URL = "ws://127.0.0.1:8080/ws/"

# Data to be used in requests
data = {
    "id": 1,
    "url": "http://example.com/logo.png"
}

def send_post_request(url):
    response = requests.post(url, json=data)
    return f"POST {url}: {response.status_code}"

def send_get_request(url):
    response = requests.get(url)
    return f"GET {url}: {response.status_code}"

def send_put_request(url):
    response = requests.put(f"{url}/1", json=data)
    return f"PUT {url}/1: {response.status_code}"

def send_delete_request(url):
    response = requests.delete(f"{url}/1")
    return f"DELETE {url}/1: {response.status_code}"

def load_test(url, ws_url):
    start_time = time.time()
    log = []

    def on_message(ws, message):
        log.append(f"WS Message: {message}")

    def on_error(ws, error):
        log.append(f"WS Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        log.append(f"WS Close: {close_status_code} {close_msg}")

    def on_open(ws):
        for i in range(5000):
            ws.send("Hello WebSocket")

    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()

    request_queue = Queue()
    for _ in range(5000):
        request_queue.put(('POST', send_post_request, url))
        request_queue.put(('GET', send_get_request, url))
        request_queue.put(('PUT', send_put_request, url))
        request_queue.put(('DELETE', send_delete_request, url))

    def worker():
        while not request_queue.empty():
            try:
                req_type, func, req_url = request_queue.get_nowait()
                log.append(func(req_url))
                request_queue.task_done()
            except Queue.Empty:
                break

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(worker) for _ in range(100)]
        for future in as_completed(futures):
            pass

    ws.close()
    ws_thread.join()

    end_time = time.time()
    duration = end_time - start_time

    return log, duration

# Function to monitor CPU and memory usage
def monitor_resource_usage(process, duration):
    cpu_usage = []
    memory_usage = []

    start_time = time.time()
    while time.time() - start_time < duration:
        cpu_usage.append(process.cpu_percent(interval=1))
        memory_usage.append(process.memory_info().rss)
    
    return cpu_usage, memory_usage

# Function to run a program, test it, and shut it down
def run_test(program_path, url, ws_url, log_file):
    print(f"Starting {program_path}...")

    # Start the program
    process = subprocess.Popen(program_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Give the server some time to start
    time.sleep(5)

    print(f"Running load test for {program_path}...")
    log, duration = load_test(url, ws_url)

    # Get the current date and time
    now = datetime.now()
    # Format the current date and time
    formatted_now = now.strftime("%Y-%m-%d-%H:%M:%S")

    # Save logs
    with open(f"./logs/{log_file}_{formatted_now}.txt", "w") as f:
        for entry in log:
            f.write(entry + "\n")
    print(f"Load test for {program_path} completed in {duration} seconds. Logs are saved in {log_file}.")


    if(HW_TEST):
        psutil_process = psutil.Process(process.pid)

        # Monitor resource usage
        cpu_usage, memory_usage = monitor_resource_usage(psutil_process, duration)

        # Save resource usage logs
        with open(f"./logs/hw/{log_file}_cpu_{formatted_now}.txt", "w") as f:
            for entry in cpu_usage:
                f.write(f"{entry}\n")

        with open(f"./logs/hw/{log_file}_memory_{formatted_now}.txt", "w") as f:
            for entry in memory_usage:
                f.write(f"{entry}\n")


    # Terminate the process
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
    print(f"{program_path} has been shut down.")

# Main function to run the tests for Actix and Axum
def main():
    try:
        run_test(ACTIX_PROGRAM_PATH, ACTIX_URL, ACTIX_WS_URL, "actix_log")
        run_test(AXUM_PROGRAM_PATH, AXUM_URL, AXUM_WS_URL, "axum_log")
        run_test(ROCKET_PROGRAM_PATH, ROCKET_URL, ROCKET_WS_URL, "rocket_log")
    except FileNotFoundError as fnf:
        print("File Doesn't Exist. You need to build executables first. Did you run setup.sh?\n- ", fnf)
    except Exception as e:
        print("Unknown Error Occurred: ", e)

if __name__ == "__main__":
    main()
