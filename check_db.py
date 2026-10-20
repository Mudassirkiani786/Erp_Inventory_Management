
import sqlite3

conn = sqlite3.connect("erp_inventory.db")

for table in ["purchase_order_lines", "purchase_orders"]:
    print(f"\nTable: {table}")

    columns = conn.execute(
        f"PRAGMA table_info({table})"
    ).fetchall()

    for column in columns:
        print(column[1])

conn.close()
