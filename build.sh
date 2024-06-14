#!/bin/bash

WD=$PWD

cd $WD/actix-webserver
echo "Building Actix Webserver:"
cargo build --release
chmod +x target/release/actix-webserver

cd $WD/axum-webserver
echo "Building Axum Webserver:"
cargo build --release
chmod +x target/release/axum-webserver


echo "Created binary: $(ls $WD/actix-webserver/target/release/actix-webserver)"
echo "Created binary: $(ls $WD/axum-webserver/target/release/axum-webserver)"
