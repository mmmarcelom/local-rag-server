-- Script para criar as novas tabelas no Supabase
-- Execute este script no SQL Editor do Supabase

-- 1. Remover tabelas existentes (se existirem)
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;

-- Criar tabela de conversas
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) NOT NULL,
    user_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ
);

-- Criar tabela de mensagens com nova estrutura
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL, -- 'whatsapp', 'instagram', 'messenger'
    sender VARCHAR(20) NOT NULL,
    receiver VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    direction VARCHAR(20) NOT NULL, -- 'incoming' ou 'outgoing'
    message_type VARCHAR(20) NOT NULL, -- 'text', 'audio', 'video'
    external_message_id VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Criar índices para performance
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_platform ON messages(platform);
CREATE INDEX idx_messages_sender ON messages(sender);
CREATE INDEX idx_messages_receiver ON messages(receiver);

-- Comentários para documentação
COMMENT ON TABLE conversations IS 'Tabela para armazenar conversas dos usuários';
COMMENT ON TABLE messages IS 'Tabela para armazenar mensagens das conversas';
COMMENT ON COLUMN messages.platform IS 'Plataforma da mensagem: whatsapp, instagram, messenger';
COMMENT ON COLUMN messages.sender IS 'Remetente da mensagem';
COMMENT ON COLUMN messages.receiver IS 'Destinatário da mensagem';
COMMENT ON COLUMN messages.message_type IS 'Tipo da mensagem: incoming ou outgoing'; 