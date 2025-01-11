use rocket::{get, post, put, delete, routes, serde::{Deserialize, Serialize}};
use rocket::serde::json::Json;
use rocket::http::Status;

#[macro_use] extern crate rocket;

#[derive(Serialize, Deserialize)]
pub struct Logo {
    pub id: u32,
    pub url: String,
}

#[derive(Serialize, Deserialize)]
pub struct DeletedLogo {
    pub id: u32,
}

#[get("/api/logo")]
pub async fn get_logo() -> Json<Logo> {
    Json(Logo { id: 1, url: "http://example.com/logo.png".to_string() })
}

#[post("/api/logo", data = "<logo>")]
pub async fn create_logo(logo: Json<Logo>) -> (Status, Json<Logo>) {
    (Status::Created, logo)
}

#[put("/api/logo/<id>", data = "<logo>")]
pub async fn update_logo(id: u32, logo: Json<Logo>) -> Json<Logo> {
    Json(Logo { id, url: logo.url.clone() })
}

#[delete("/api/logo/<id>")]
pub async fn delete_logo(id: u32) -> Json<DeletedLogo> {
    Json(DeletedLogo { id })
}

#[get("/ws")]
fn websocket_handler(ws: rocket_ws::WebSocket) -> rocket_ws::Stream!['static] {
    rocket_ws::Stream! { ws =>
        for await message in ws {
            yield message?;
        }
    }
}

#[launch]
fn rocket() -> _ {
    rocket::build()
        .mount("/", routes![get_logo, create_logo, update_logo, delete_logo, websocket_handler])
}
