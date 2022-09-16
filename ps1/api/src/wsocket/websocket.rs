use actix_web::{web, Error, HttpRequest, HttpResponse};
use actix_web_actors::ws;
use crate::wsocket::server::MyWebSocket;

/// WebSocket handshake and start `MyWebSocket` actor.
pub async fn echo_ws(req: HttpRequest, stream: web::Payload) -> Result<HttpResponse, Error> {
    ws::start(MyWebSocket::new(), &req, stream)
}