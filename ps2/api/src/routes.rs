//! Place all Actix routes here, multiple route configs can be used and
//! combined.

use crate::handlers::{
    health::get_health,
    stocks::{
        get_stock_by_ticker,
        get_stocks_list,
    },
    reminders::{
        get_reminders_by_server,
    },
};
use crate::middleware::auth::Authv1 as AuthMiddlewarev1;
use actix_web::{web};

pub fn routes(cfg: &mut web::ServiceConfig) {
    cfg
        // api v1 routes
        .service(
            web::scope("/api")
            .service(
                web::scope("/v1")
                    // Lock down routes with AUTH Middlewarev1 instead of guards
                    .wrap(AuthMiddlewarev1)
                    // Healthcheck
                    .route("/health", web::get().to(get_health))
                    // data endpoint routes
                    .service(
                        web::scope("/stocks")
                            .route("", web::get().to(get_stock_by_ticker))
                            .route("/list", web::get().to(get_stocks_list))
                    )
                    .service(
                        web::scope("/reminders")
                            .route("", web::get().to(get_reminders_by_server))
                    )
            )
        );
}
