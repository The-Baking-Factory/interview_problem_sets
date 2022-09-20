/**
 * @TODO
 * 1. Modify reminders table so it has a foreign key reference to servers table through server_id
 * 2. Modify the foreign key from 1. to add constraint to actively prevent deletion of a row from servers table,
        if there are reminders that reference that row's server_id (hint: this is the default)
 * 3. For reminders table, assume server_id is a 10 digit bar code and because of expansion, you need to change it to a 13-digit bar code.
        Now if you change this primary key value, any tables that have foreign key references to the value should be changed accordingly.
        What foreign key constraint would you use?
 * 4. Modify reminders table to create an index if it doesn't exist on server_id in reminders table. Why is this useful?
 * 5. Modify reminders table to enforce uniqueness of server_id, channel_id, and msg_content combination for a row.
        Explain what this means for reminders, can one server have multiple reminders? What about a channel?
 * 6. Reminders table doesn't have a primary key. Is this a problem? Why or why not?
 * 7. Are there any questions or general improvements you could propose to this schema?
 */

CREATE TABLE IF NOT EXISTS "servers"
(
    [server_id]         TEXT PRIMARY KEY NOT NULL, /* server id */
    [server_name]       TEXT NOT NULL /* server name */
);

CREATE TABLE IF NOT EXISTS "reminders"
(
    [server_id]          TEXT NOT NULL, /* message server id */
    [channel_id]         TEXT NOT NULL, /* message channel id, a server can have multiple channels */
    [msg_content]        TEXT NOT NULL, /* message content */
    [msg_interval]       INTEGER NOT NULL, /* time in seconds */
    [msg_type]           INTEGER DEFAULT 1 NOT NULL CHECK(msg_type == 1 OR msg_type == 2), /* 1 is regular message, 2 is embed */
    [embed_color]        TEXT, /* message color if embed */
    [embed_title]        TEXT, /* message title if embed */
    [thumbnail_icon]     TEXT, /* image pointer to message icon if embed, pointer is to s3 bucket */
    /* .... */
);
/* .... */

CREATE TABLE IF NOT EXISTS "stocks"
(
    [ticker]                    TEXT PRIMARY KEY NOT NULL,
    [ratio_usd]                 TEXT,
    [marketcap_usd]             TEXT,
    [price_change]              TEXT,
    [high_24h]                  TEXT,
    [low_24h]                   TEXT,
    [updated_at]                INTEGER
);

INSERT INTO servers
    ( server_id, server_name )
VALUES
    ( "1021779407972618310", "test server" );

INSERT INTO reminders
	( server_id, channel_id, msg_content, msg_interval, msg_type )
VALUES
	( "1021779407972618310", "1021780309223690260", "reminder message 1", 120, 1 ),
    ( "1021779407972618310", "1021780330488807425", "reminder message 2", 100, 1 );
