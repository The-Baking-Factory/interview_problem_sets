table! {
    stocks (ticker) {
        ticker -> Text,
        website -> Nullable<Text>,
        ratio_usd -> Nullable<Text>,
        marketcap_usd -> Nullable<Text>,
        price_change -> Nullable<Text>,
        high_24h -> Nullable<Text>,
        low_24h -> Nullable<Text>,
        high_24h_change -> Nullable<Text>,
        low_24h_change -> Nullable<Text>,
        short_ratio -> Nullable<Text>,
        held_per_insiders -> Nullable<Text>,
        held_per_institutions -> Nullable<Text>,
        updated_at -> BigInt,
    }
}

table! {
    servers (server_id) {
        server_id -> Text,
        server_name -> Text,
    }
}

table! {
    reminders (server_id, channel_id, msg_content) {
        server_id -> Text,
        channel_id -> Text,
        msg_content -> Text,
        msg_interval -> BigInt,
        msg_type -> Integer,
        embed_color -> Nullable<Text>,
        embed_title -> Nullable<Text>,
        thumbnail_icon -> Nullable<Text>,
    }
}

joinable!(reminders -> servers (server_id));