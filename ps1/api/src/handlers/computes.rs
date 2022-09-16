use uuid::Uuid;
use chrono::{Utc};

pub fn get_uuid_id() -> String {
    return Uuid::new_v4().to_string()
}