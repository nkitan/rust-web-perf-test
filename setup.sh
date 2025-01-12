# Setup Python Virtual Environment
python3 -m venv venv
venv/bin/pip3 install -r requirements.txt

# Setup Log directories
mkdir -p logs/hw

# Build Web Servers
CWD=$(pwd)
ACTIX_DIR=$CWD/actix-webserver/
AXUM_DIR=$CWD/axum-webserver/
ROCKET_DIR=$CWD/rocket-webserver/

cd $ACTIX_DIR && echo "Building Actix Webserver:" && cargo build --release && chmod +x $ACTIX_DIR/target/release/actix-webserver
cd $AXUM_DIR && echo "Building Axum Webserver:" && cargo build --release && chmod +x $AXUM_DIR/target/release/axum-webserver
cd $ROCKET_DIR && echo "Building Rocket Webserver" && cargo build --release && chmod +x $ROCKET_DIR/target/release/rocket-webserver

# Show status
echo "Created Actix binary: $(ls $ACTIX_DIR/target/release/actix-webserver)"
echo "Created Axum binary: $(ls $AXUM_DIR/target/release/axum-webserver)"
echo "Created Rocket binary: $(ls $ROCKET_DIR/target/release/rocket-webserver)"

echo "Rust Web Server Perf Test Has Been Set Up"
