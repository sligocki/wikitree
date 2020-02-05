# Convert categories CSV -> SQLite.

sqlite3 data/categories.db <<EOF
CREATE TABLE categories (user_num INT, category_name STRING);

.mode tabs
.import data/dump_categories.csv categories

CREATE INDEX idx_categories_user ON categories(user_num);
CREATE INDEX idx_categories_category ON categories(category_name);
EOF
