use crate::config::CONFIG;
use actix_identity::{CookieIdentityPolicy, IdentityService};

/// Gets the identidy service for injection into an Actix app
pub fn get_identity_service() -> IdentityService<CookieIdentityPolicy> {
    IdentityService::new(
        CookieIdentityPolicy::new(&CONFIG.session_key.as_ref())
            .name(&CONFIG.session_name)
            .max_age_time(chrono::Duration::minutes(CONFIG.session_timeout))
            .secure(CONFIG.session_secure),
    )
}