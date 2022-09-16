use crate::database::PoolType;
use crate::errors::ApiError;
use diesel::prelude::*;
use crate::schema::*;
use crate::handlers::reminders::{
    ReminderResponse,
    RemindersResponse,
};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Identifiable, Queryable, Insertable)]
#[primary_key(server_id, channel_id, msg_content)]
#[table_name = "reminders"]
pub struct Reminder {
    pub server_id: String,
    pub channel_id: String,
    pub msg_content: String,
    pub msg_interval: i64,
    pub msg_type: i32,
    pub embed_color: Option<String>,
    pub embed_title: Option<String>,
    pub thumbnail_icon: Option<String>,
}

pub fn reminders_by_server(
    pool: &PoolType,
    server_id: &String,
) -> Result<RemindersResponse, ApiError> {
    use crate::schema::reminders::dsl::*;

    let conn = pool.get()?;
    let data: Vec<Reminder> = reminders
        .filter(server_id.eq(server_id))
        .select((
            server_id,
            channel_id,
            msg_content,
            msg_interval,
            msg_type,
            embed_color,
            embed_title,
            thumbnail_icon,
        ))
        .load(&conn)?;
    Ok(data.into())
}