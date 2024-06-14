use axum::{
    extract::{Path, Json, WebSocketUpgrade, ws::Message, ws::WebSocket},
    http::StatusCode,
    routing::{get, post, put, delete},
    Router,
    response::IntoResponse,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use futures_util::StreamExt;

#[derive(Serialize, Deserialize)]
struct Logo {
    id: u32,
    url: String,
}

#[derive(Serialize, Deserialize)]
struct DeletedLogo {
    id: u32,
}

async fn get_logo() -> impl IntoResponse {
    (StatusCode::OK, Json(Logo { id: 1, url: "http://example.com/logo.png".into() }))
}

async fn create_logo(Json(logo): Json<Logo>) -> impl IntoResponse {
    (StatusCode::CREATED, Json(logo))
}

async fn update_logo(Path(id): Path<u32>, Json(logo): Json<Logo>) -> impl IntoResponse {
    (StatusCode::OK, Json(Logo { id, url: logo.url }))
}

async fn delete_logo(Path(id): Path<u32>) -> impl IntoResponse {
    (StatusCode::OK, Json(DeletedLogo { id }))
}

async fn websocket_handler(ws: WebSocketUpgrade) -> impl IntoResponse {
    ws.on_upgrade(handle_websocket)
}

async fn handle_websocket(mut socket: WebSocket) {
    while let Some(Ok(msg)) = socket.next().await {
        match msg {
            Message::Text(text) => {
                if socket.send(Message::Text(text)).await.is_err() {
                    break;
                }
            }
            Message::Binary(bin) => {
                if socket.send(Message::Binary(bin)).await.is_err() {
                    break;
                }
            }
            _ => break,
        }
    }
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/api/logo", get(get_logo))
        .route("/api/logo", post(create_logo))
        .route("/api/logo/:id", put(update_logo))
        .route("/api/logo/:id", delete(delete_logo))
        .route("/ws/", get(websocket_handler)); // WebSocket route

    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    println!("Server running on {}", addr);
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}
