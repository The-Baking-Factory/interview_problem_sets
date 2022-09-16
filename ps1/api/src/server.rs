//! Spin up a HTTPServer

use crate::auth::get_identity_service;
use crate::cache::add_cache;
use crate::config::CONFIG;
use crate::database::add_pool;
use crate::routes::routes;
use crate::state::new_state;
use actix_cors::Cors;
use actix_web::{middleware::Logger, App, HttpServer};
use listenfd::ListenFd;

//use actix_ratelimit::{RateLimiter, MemoryStore, MemoryStoreActor};
//use std::time::Duration;

pub async fn server() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init();

    // Create the application state
    // String is used here, but it can be anything
    // Invoke in hanlders using data: AppState<'_, String>
    let data = new_state::<String>();

    //A store is a data structure, database connection or anything which can be used to store ratelimit data associated with a client.
    // A store actor which acts on this store is responsible for performiing all sorts of operations(SET, GET, DEL, etc).
    // It is Important to note that there are multiple store actors acting on a single store.
    //let store = MemoryStore::new(); // based on concurrent hashmap

    // using defaults for now, for more details see https://github.com/actix/actix-web/blob/master/src/server.rs
    // 25k max connections for per-worker number of concurrent connections
    // 256 max per-worker concurrent connection establish process
    // 512/worker for max number of threads for each worker's blocking task thread pool


    let mut listenfd = ListenFd::from_env();
    let mut server = HttpServer::new(move || {
        App::new()
            .configure(add_cache)
            .wrap(
                Cors::new()
                .supports_credentials()
                .finish(),
            )
            .wrap(Logger::default())
            .wrap(get_identity_service())
            /*.wrap(
                RateLimiter::new( //maximum of X requests per Y per client based on ip
                    MemoryStoreActor::from(store.clone()).start())
                        .with_interval(Duration::from_secs(CONFIG.request_duration_limit))
                        .with_max_requests(CONFIG.request_num_limit)
            )*/
            /*.wrap(
                RateLimiter::new( //maximum of X requests per Y per client based on api key
                MemoryStoreActor::from(store.clone()).start())
                    .with_interval(Duration::from_secs(CONFIG.request_duration_limit))
                    .with_max_requests(CONFIG.request_num_limit)
                    .with_identifier(|req| {
                        if let Some(key) = req.headers().get("authorization") { // there is a separate auth middleware to verify this
                            let key = key.to_str().unwrap();
                            Ok(key.to_string())
                        } else {
                            let key = "preflight";
                            Ok(key.to_string())
                        }
                    })
            )*/
            .configure(add_pool)
            .app_data(data.clone())
            .configure(routes)
    });

    server = if let Some(l) = listenfd.take_tcp_listener(0)? {
        server.listen(l)?
    } else {
        server.bind(&CONFIG.server)?
    };

    server.run().await
}
