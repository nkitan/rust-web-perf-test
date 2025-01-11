python3 -m venv venv
venv/bin/pip3 install -r requirements.txt
mkdir -p logs/hw

CWD=$(pwd)
ACTIX_DIR=actix-webserver/
AXUM_DIR=axum-webserver/
ROCKET_DIR=rocket-webserver/

cd $CWD/$ACTIX_DIR && cargo build --release
cd $CWD/$AXUM_DIR && cargo build --release
cd $CWD/$ROCKET_DIR && cargo build --release

echo "Rust Web Server Perf Test Has Been Set Up"
