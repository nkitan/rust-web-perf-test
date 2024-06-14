use actix::{Actor, StreamHandler};
use actix_web::{delete, get, post, put, web, App, Error, HttpResponse, HttpRequest, HttpServer, Responder};
use actix_web_actors::ws;
use serde::{Deserialize, Serialize};

// Struct representing our WebSocket connection
struct MyWs;

impl Actor for MyWs {
    type Context = ws::WebsocketContext<Self>;
}

// Handler for WebSocket messages
impl StreamHandler<Result<ws::Message, ws::ProtocolError>> for MyWs {
    fn handle(&mut self, msg: Result<ws::Message, ws::ProtocolError>, ctx: &mut Self::Context) {
        match msg {
            Ok(ws::Message::Text(text)) => ctx.text(text),
            Ok(ws::Message::Binary(bin)) => ctx.binary(bin),
            _ => (),
        }
    }
}

#[derive(Serialize, Deserialize)]
struct Logo {
    id: u32,
    url: String,
}

#[derive(Serialize, Deserialize)]
struct DeletedLogo {
    id: u32,
}


#[get("/api/logo")]
async fn get_logo() -> impl Responder {
    HttpResponse::Ok().json(Logo { id: 1, url: "http://example.com/logo.png".into() })
}

#[post("/api/logo")]
async fn create_logo(logo: web::Json<Logo>) -> impl Responder {
    HttpResponse::Created().json(logo.into_inner())
}

#[put("/api/logo/{id}")]
async fn update_logo(id: web::Path<u32>, logo: web::Json<Logo>) -> impl Responder {
    HttpResponse::Ok().json(Logo { id: id.into_inner(), url: logo.url.clone() })
}

#[delete("/api/logo/{id}")]
async fn delete_logo(id: web::Path<u32>) -> impl Responder {
    HttpResponse::Ok().json(DeletedLogo { id: id.into_inner() })
}

// WebSocket endpoint
async fn ws_index(r: HttpRequest, stream: web::Payload) -> Result<HttpResponse, Error> {
    ws::start(MyWs {}, &r, stream)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(get_logo)
            .service(create_logo)
            .service(update_logo)
            .service(delete_logo)
            .route("/ws/", web::get().to(ws_index)) // WebSocket route
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}

