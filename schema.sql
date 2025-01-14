-- Таблица для хранения сообщений
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    username TEXT NOT NULL,
    interaction_type TEXT NOT NULL,
    full_name TEXT NOT NULL,
    message_text TEXT NOT NULL,
    user_id BIGINT NOT NULL
);

-- Таблица для общей статистики
CREATE TABLE IF NOT EXISTS general_statistics (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    week_start TIMESTAMP NOT NULL,
    participants INTEGER NOT NULL,
    stories INTEGER NOT NULL,
    UNIQUE(chat_id, week_start)
);

-- Таблица для мемной статистики
CREATE TABLE IF NOT EXISTS meme_statistics_weekly (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    week_start TIMESTAMP NOT NULL,
    total_memes_sent INTEGER DEFAULT 0,
    memes_published INTEGER DEFAULT 0,
    memes_deleted INTEGER DEFAULT 0,
    UNIQUE(chat_id, week_start)
);

CREATE TABLE participants_statistics (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    participants_count INT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
