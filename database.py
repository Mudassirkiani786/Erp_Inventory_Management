
import sqlite3

DB_NAME = "erp_inventory.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT DEFAULT '',
                unit TEXT DEFAULT 'PCS',
                cost_price REAL NOT NULL DEFAULT 0,
                sale_price REAL NOT NULL DEFAULT 0,
                stock_qty REAL NOT NULL DEFAULT 0,
                min_stock REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                address TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL
                    CHECK (movement_type IN ('IN', 'OUT')),
                quantity REAL NOT NULL CHECK (quantity > 0),
                reference TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id)
                    REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number TEXT NOT NULL UNIQUE,
                supplier_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Draft'
                    CHECK (status IN (
                        'Draft',
                        'Confirmed',
                        'Received',
                        'Cancelled'
                    )),
                total_amount REAL NOT NULL DEFAULT 0,
                notes TEXT DEFAULT '',
                grn_reference TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id)
                    REFERENCES suppliers(id)
            );

            CREATE TABLE IF NOT EXISTS purchase_order_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL CHECK (quantity > 0),
                unit_price REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (purchase_order_id)
                    REFERENCES purchase_orders(id),
                FOREIGN KEY (product_id)
                    REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                customer TEXT DEFAULT '',
                location TEXT DEFAULT '',
                start_date TEXT DEFAULT '',
                end_date TEXT DEFAULT '',
                budget REAL NOT NULL DEFAULT 0
                    CHECK (budget >= 0),
                status TEXT NOT NULL DEFAULT 'Planned'
                    CHECK (status IN (
                        'Planned',
                        'In Progress',
                        'On Hold',
                        'Completed',
                        'Cancelled'
                    )),
                progress INTEGER NOT NULL DEFAULT 0
                    CHECK (progress BETWEEN 0 AND 100),
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Add GRN column only if it does not already exist.
        columns = conn.execute(
            "PRAGMA table_info(purchase_orders)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "grn_reference" not in column_names:
            conn.execute("""
                ALTER TABLE purchase_orders
                ADD COLUMN grn_reference TEXT DEFAULT ''
            """)


if __name__ == "__main__":
    init_db()
    print("ERP database initialized successfully.")
