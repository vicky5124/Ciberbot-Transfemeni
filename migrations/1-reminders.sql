CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    guild_id INTEGER,
    time DATETIME NOT NULL,
    content TEXT NOT NULL
);
