//use crate::auth::{decode_jwt, PrivateClaim};
//use crate::errors::ApiError;
//use actix_identity::RequestIdentity;
use actix_service::{Service, Transform};
use actix_web::{
    dev::{ServiceRequest, ServiceResponse},
    Error, HttpResponse,
};
use futures::{Future, future::{ok, Ready}};
use std::pin::Pin;
use std::task::{Context, Poll};

use crate::config::CONFIG;
//use crate::database::PoolType;
//use actix_web::web::Data;

pub struct Authv1;

impl<S, B> Transform<S> for Authv1
where
    S: Service<Request = ServiceRequest, Response = ServiceResponse<B>, Error = Error>,
    S::Future: 'static,
{
    type Request = ServiceRequest;
    type Response = ServiceResponse<B>;
    type Error = Error;
    type InitError = ();
    type Transform = AuthMiddleware<S>;
    type Future = Ready<Result<Self::Transform, Self::InitError>>;

    fn new_transform(&self, service: S) -> Self::Future {
        ok(AuthMiddleware { service })
    }
}
pub struct AuthMiddleware<S> {
    service: S,
}

impl<S, B> Service for AuthMiddleware<S>
where
    S: Service<Request = ServiceRequest, Response = ServiceResponse<B>, Error = Error>,
    S::Future: 'static,
{
    type Request = ServiceRequest;
    type Response = ServiceResponse<B>;
    type Error = Error;
    type Future = Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>>>>;

    fn poll_ready(&mut self, cx: &mut Context) -> Poll<Result<(), Self::Error>> {
        self.service.poll_ready(cx)
    }

    fn call(&mut self, req: ServiceRequest) -> Self::Future {
        // ServiceRequest allows mutable access to request's internal structures

        // delaying jwt token based on sign in on admin portal for now //
        /*
        // check whether admin is logged in for specific endpoints
        if req.path().contains("/idos/create") {
            let identity = RequestIdentity::get_identity(&req).unwrap_or("".into());
            let private_claim: Result<PrivateClaim, ApiError> = decode_jwt(&identity);
            let is_logged_in = private_claim.is_ok();
            unauthorized = !is_logged_in && req.path() != "/api/v1/auth/login";
        }
        */

        // api key based auth
        // only admin key can access any endpoint
        let mut unauthorized = true;
        if let Some(value) = req.headers().get("authorization") {
            if &value.to_str().unwrap().to_string() == &CONFIG.admin_key.as_ref() {
                unauthorized = false;
            }
        }

        // api key based auth
        /*
        use crate::schema::users::dsl::{key,users};
        use crate::models;
        use diesel::prelude::*;

        let pool: Option<Data<PoolType>> = req.app_data();
        let mut unauthorized = false;

        if let Some(p) = pool {
            let conn = &mut p.get().unwrap();
            if let Some(value) = req.headers().get("authorization") {

                let _user = users
                    .filter(key.eq(&value.to_str().unwrap().to_string()))
                    .first::<models::user::User>(&*conn)
                    .map_err(|_| unauthorized = true);

                if !unauthorized {
                    // only admin key can access certain endpoints
                    if (req.path().contains("/user/create") ||
                        req.path().contains("/idos/create") ||
                        req.path().contains("/coins/create") ||
                        req.path().contains("/news/create") ||
                        req.path().contains("/participants/create")
                    ) && (&value.to_str().unwrap().to_string() != &CONFIG.admin_key.as_ref()) {
                        unauthorized = true;
                    }
                }
            } else {
                unauthorized = true;
            }
        }
        */

        if unauthorized {
            return Box::pin(async move {
                Ok(req.into_response(HttpResponse::Unauthorized().finish().into_body()))
            })
        }

        let fut = self.service.call(req);

        Box::pin(async move {
            let res = fut.await?;
            Ok(res)
        })
    }
}
