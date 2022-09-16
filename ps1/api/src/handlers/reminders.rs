use crate::database::PoolType;
use crate::errors::ApiError;
use crate::helpers::{respond_json, respond_ok};
use actix_web::web::{block, Data, HttpResponse, Json, Query};
use rayon::prelude::*;
use serde::Serialize;
use crate::models::reminders::{
    reminders_by_server,
    Reminder,
};
use crate::handlers::params::{
    ServerParams,
};

#[derive(Debug, Deserialize, Serialize, PartialEq)]
pub struct ReminderResponse {
    server_id: String,
    channel_id: String,
    msg_content: String,
    msg_interval: i64,
    msg_type: i32,
    embed_color: Option<String>,
    embed_title: Option<String>,
    thumbnail_icon: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, PartialEq)]
pub struct RemindersResponse(pub Vec<ReminderResponse>);

pub async fn get_reminders_by_server(
    Query(param): Query<ServerParams>,
    pool: Data<PoolType>,
) -> Result<Json<RemindersResponse>, ApiError> {
    let reminders = block(move || reminders_by_server(&pool, &param.server_id)).await?;
    respond_json(reminders)
}

impl From<Reminder> for ReminderResponse {
    fn from(s: Reminder) -> Self {
        ReminderResponse {
            server_id: s.server_id.to_string(),
            channel_id: s.channel_id.to_string(),
            msg_content: s.msg_content.to_string(),
            msg_interval: s.msg_interval,
            msg_type: s.msg_type,
            embed_color: s.embed_color.to_owned(),
            embed_title: s.embed_title.to_owned(),
            thumbnail_icon: s.thumbnail_icon.to_owned(),
        }
    }
}

impl From<Vec<Reminder>> for RemindersResponse {
    fn from(gs: Vec<Reminder>) -> Self {
        RemindersResponse(gs.into_par_iter().map(|g| g.into()).collect())
    }
}