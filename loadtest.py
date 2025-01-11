import requests
import time
import subprocess
import os

# Paths to the Actix, Axum and Rocket program executables
ACTIX_PROGRAM_PATH = "./actix-webserver/target/release/actix-webserver"
AXUM_PROGRAM_PATH = "./axum-webserver/target/release/axum-webserver"
ROCKET_PROGRAM_PATH = "./rocket-webserver/target/release/rocket-webserver"

# URL endpoints for Actix, Axum and Rocket programs
ACTIX_URL = "http://127.0.0.1:8080/api/logo"
AXUM_URL = "http://127.0.0.1:8080/api/logo"
ROCKET_URL = "http://127.0.0.1:8080/api/logo"


# Data to be used in requests
data = {
    "id": 1,
    "url": "http://example.com/logo.png"
}

# Function to perform load testing
def load_test(url):
    start_time = time.time()
    log = []

    # POST requests
    for _ in range(5000):
        response = requests.post(url, json=data)
        log.append(f"POST {url}: {response.status_code}")

    # GET requests
    for _ in range(5000):
        response = requests.get(url)
        log.append(f"GET {url}: {response.status_code}")

    # PUT requests
    for _ in range(5000):
        response = requests.put(f"{url}/1", json=data)
        log.append(f"PUT {url}/1: {response.status_code}")

    # DELETE requests
    for _ in range(5000):
        response = requests.delete(f"{url}/1")
        log.append(f"DELETE {url}/1: {response.status_code}")

    end_time = time.time()
    duration = end_time - start_time

    return log, duration

# Function to run a program, test it, and shut it down
def run_test(program_path, url, log_file):
    print(f"Starting {program_path}...")

    # Start the program
    process = subprocess.Popen(program_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Give the server some time to start
    time.sleep(5)

    print(f"Running load test for {program_path}...")
    log, duration = load_test(url)
    
    # Save logs
    with open(f"./logs/{log_file}", "w") as f:
        for entry in log:
            f.write(entry + "\n")
    print(f"Load test for {program_path} completed in {duration} seconds. Logs are saved in {log_file}.")

    # Terminate the process
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
    print(f"{program_path} has been shut down.")

# Main function to run the tests for Actix and Axum
def main():
    run_test(ACTIX_PROGRAM_PATH, ACTIX_URL, "actix_log.txt")
    run_test(AXUM_PROGRAM_PATH, AXUM_URL, "axum_log.txt")
    run_test(ROCKET_PROGRAM_PATH, ROCKET_URL, "rocket_log.txt")

if __name__ == "__main__":
    main()

