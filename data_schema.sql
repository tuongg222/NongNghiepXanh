CREATE TABLE IF NOT EXISTS user_data (
  user_id INTEGER NOT NULL,
  data_key TEXT NOT NULL,
  json_data TEXT NOT NULL,
  updated_at INTEGER NOT NULL,
  PRIMARY KEY (user_id, data_key),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
