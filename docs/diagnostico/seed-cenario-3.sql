-- Seed do Cenario 3. Rodar SOMENTE em biblioteca_diag.
DO $$
BEGIN
  IF current_database() <> 'biblioteca_diag' THEN
    RAISE EXCEPTION 'Banco errado: %', current_database();
  END IF;
END $$;

TRUNCATE emprestimos, reservas, exemplares, livro_autor, livros, usuarios
  RESTART IDENTITY CASCADE;

INSERT INTO livros (titulo, isbn) VALUES
  ('Dom Casmurro', '9788535914849'),
  ('Memorias Postumas', '9788535911664');

INSERT INTO exemplares (livro_id, codigo_patrimonio) VALUES
  (1, 'PAT-001'),
  (1, 'PAT-002'),
  (2, 'PAT-003');

INSERT INTO usuarios (nome, email) VALUES
  ('Ana',   'ana@diag.local'),
  ('Bruno', 'bruno@diag.local'),
  ('Carla', 'carla@diag.local');

INSERT INTO reservas (livro_id, usuario_id) VALUES
  (1, 1);