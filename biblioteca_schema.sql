-- =====================================================
-- SCHEMA: Sistema de Empréstimo de Biblioteca
-- SGBD alvo: PostgreSQL
-- Decisões de arquitetura documentadas em README.md
-- =====================================================

-- Tabela: usuarios
CREATE TABLE usuarios (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(150) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    telefone    VARCHAR(20),
    criado_em   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tabela: autores
CREATE TABLE autores (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(150) NOT NULL,
    biografia   VARCHAR(500)
);

-- Tabela: livros (título/conceito, não a cópia física)
CREATE TABLE livros (
    id              SERIAL PRIMARY KEY,
    titulo          VARCHAR(200) NOT NULL,
    isbn            VARCHAR(20) NOT NULL UNIQUE,
    editora         VARCHAR(120),
    ano_publicacao  INTEGER,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tabela associativa: livro_autor (N:N)
CREATE TABLE livro_autor (
    livro_id    INTEGER NOT NULL REFERENCES livros(id) ON DELETE CASCADE,
    autor_id    INTEGER NOT NULL REFERENCES autores(id) ON DELETE CASCADE,
    PRIMARY KEY (livro_id, autor_id)
);

-- Tabela: exemplares (cópia física)
CREATE TABLE exemplares (
    id                  SERIAL PRIMARY KEY,
    livro_id            INTEGER NOT NULL REFERENCES livros(id) ON DELETE RESTRICT,
    codigo_patrimonio   VARCHAR(30) NOT NULL UNIQUE,
    status              VARCHAR(20) NOT NULL DEFAULT 'ATIVO',
    adquirido_em        DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT ck_status_exemplar_valido CHECK (
        status IN ('ATIVO', 'BAIXADO', 'PERDIDO')
    )
);

-- Tabela: reservas (fila de espera por título)
CREATE TABLE reservas (
    id              SERIAL PRIMARY KEY,
    livro_id        INTEGER NOT NULL REFERENCES livros(id) ON DELETE RESTRICT,
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW(), -- desempate FIFO
    notificado_em   TIMESTAMP, -- NULL = na fila; preenchido = contando 48h
    CONSTRAINT ck_status_reserva_valido CHECK (
        status IN ('PENDENTE', 'AGUARDANDO_RETIRADA', 'ATENDIDA', 'EXPIRADA', 'CANCELADA')
    )
);

-- Impede reserva ativa duplicada do mesmo usuário para o mesmo título
CREATE UNIQUE INDEX uk_reserva_ativa
    ON reservas(usuario_id, livro_id)
    WHERE status IN ('PENDENTE', 'AGUARDANDO_RETIRADA');

-- Tabela: emprestimos (entidade central)
CREATE TABLE emprestimos (
    id                          SERIAL PRIMARY KEY,
    exemplar_id                 INTEGER NOT NULL REFERENCES exemplares(id) ON DELETE RESTRICT,
    usuario_id                  INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    reserva_id                  INTEGER UNIQUE REFERENCES reservas(id) ON DELETE RESTRICT, -- NULL = sem reserva de origem
    emprestado_em               TIMESTAMP NOT NULL DEFAULT NOW(),
    prevista_devolucao_em       DATE NOT NULL,
    devolvido_em                TIMESTAMP, -- NULL = ainda emprestado
    criado_em                   TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_devolucao_apos_emprestimo CHECK (
        devolvido_em IS NULL OR devolvido_em >= emprestado_em
    )
);

-- Garante no máximo 1 empréstimo em aberto por exemplar
CREATE UNIQUE INDEX uk_exemplar_emprestado
    ON emprestimos(exemplar_id)
    WHERE devolvido_em IS NULL;

-- Índices para consultas frequentes
CREATE INDEX idx_exemplares_livro ON exemplares(livro_id);
CREATE INDEX idx_emprestimos_usuario ON emprestimos(usuario_id);
CREATE INDEX idx_reservas_livro_status ON reservas(livro_id, status);
