CREATE TABLE IF NOT EXISTS temp_demo (
  id SERIAL PRIMARY KEY,
  name TEXT,
  created_at TIMESTAMP DEFAULT now()
);
