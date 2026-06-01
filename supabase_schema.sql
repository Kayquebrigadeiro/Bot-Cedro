-- Script SQL para criar as tabelas no Supabase
-- Execute este script no SQL Editor do Supabase

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    name TEXT,
    joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de eBooks
CREATE TABLE IF NOT EXISTS ebooks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    file_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de podcasts
CREATE TABLE IF NOT EXISTS podcasts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    file_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de sessões
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    date_str TEXT NOT NULL,
    link TEXT NOT NULL,
    date_ts BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de log de acessos
CREATE TABLE IF NOT EXISTS access_log (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    item_type TEXT,
    item_id INTEGER,
    accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_ebooks_created ON ebooks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_podcasts_created ON podcasts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date_ts ASC, id DESC);
CREATE INDEX IF NOT EXISTS idx_access_log_item ON access_log(item_type, item_id);
CREATE INDEX IF NOT EXISTS idx_access_log_user ON access_log(user_id);

-- Comentários nas tabelas
COMMENT ON TABLE users IS 'Usuários do bot';
COMMENT ON TABLE ebooks IS 'eBooks cadastrados';
COMMENT ON TABLE podcasts IS 'Podcasts cadastrados';
COMMENT ON TABLE sessions IS 'Sessões em grupo agendadas';
COMMENT ON TABLE access_log IS 'Log de acessos aos conteúdos';
