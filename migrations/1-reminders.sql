CREATE TABLE reminder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message_id INTEGER,
    channel_id INTEGER NOT NULL,
    guild_id INTEGER,
    time TIMESTAMP NOT NULL,
    content TEXT
);
