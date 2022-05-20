CREATE TABLE reminder (
    id ASCII,
    user_id BIGINT,
    message_id BIGINT, -- NULLABLE
    channel_id BIGINT,
    guild_id BIGINT, -- NULLABLE
    datetime TIMESTAMP,
    content TEXT,-- NULLABLE
    PRIMARY KEY (user_id, id, datetime)
) WITH CLUSTERING ORDER BY (id ASC, datetime ASC);

CREATE INDEX ON reminder(datetime);
