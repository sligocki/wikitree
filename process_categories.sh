# Convert categories CSV -> SQLite.

set -u
set -e

VERSION=$1

sqlite3 data/version/${VERSION}/categories.db <<EOF
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (user_num INT, category_name STRING);

.mode tabs
.import data/version/${VERSION}/dump_categories.csv categories

CREATE INDEX idx_categories_user ON categories(user_num);
CREATE INDEX idx_categories_category ON categories(category_name);
EOF
