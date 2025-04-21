
CREATE TABLE IF NOT EXISTS interactions (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    user_message TEXT,
    bot_response TEXT,
    timestamp TEXT,
    feedback TEXT
);

CREATE INDEX IF NOT EXISTS idx_interactions_session_id ON interactions(session_id);

CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp);