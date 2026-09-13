import sqlite3
from datetime import datetime

DB_FILE = "store.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.close()

def list_inventory():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, price, stock FROM products")
    rows = cursor.fetchall()
    conn.close()

    print("\n--- Current Inventory ---")
    print(f"{'ID':<6} {'Product Name':<25} {'Price (INR)':<12} {'Stock':<6}")
    print("-" * 52)
    for r in rows:
        print(f"{r[0]:<6} {r[1]:<25} {r[2]:<12.2f} {r[3]:<6}")

def generate_bill():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        phone = input("\nEnter customer phone: ").strip()
        cursor.execute("SELECT customer_id, name FROM customers WHERE phone = ?", (phone,))
        cust = cursor.fetchone()

        if not cust:
            name = input("New customer detected. Enter name: ").strip()
            cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
            customer_id = cursor.lastrowid
        else:
            customer_id, name = cust
            print(f"Customer Found: {name}")

        # Start billing transaction
        cursor.execute("INSERT INTO orders (customer_id, total_amount) VALUES (?, 0.0)", (customer_id,))
        order_id = cursor.lastrowid

        total_order_amount = 0.0
        items_bought = []

        while True:
            list_inventory()
            p_id = input("\nEnter Product ID to buy (or 'done' to complete): ").strip()
            if p_id.lower() == 'done':
                break

            qty = int(input("Enter quantity: ").strip())

            # Verify product and stock
            cursor.execute("SELECT name, price, stock FROM products WHERE product_id = ?", (p_id,))
            product = cursor.fetchone()

            if not product:
                print("Invalid Product ID!")
                continue

            prod_name, price, stock = product
            if stock < qty:
                print(f"Insufficient stock! Available: {stock}")
                continue

            # Record item and decrement stock
            subtotal = price * qty
            total_order_amount += subtotal

            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, p_id, qty, price)
            )
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE product_id = ?",
                (qty, p_id)
            )
            items_bought.append((prod_name, qty, price, subtotal))

        if not items_bought:
            conn.rollback()
            print("Order cancelled. No items selected.")
            return

        # Finalize order
        cursor.execute("UPDATE orders SET total_amount = ? WHERE order_id = ?", (total_order_amount, order_id))
        conn.commit()

        # Print Invoice
        print("\n" + "=" * 45)
        print(f"           TAX INVOICE (Order #{order_id})")
        print("=" * 45)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Customer: {name} | Phone: {phone}")
        print("-" * 45)
        for item in items_bought:
            print(f"{item[0]:<20} x{item[1]:<3} @ {item[2]:<8.2f} = {item[3]:.2f}")
        print("-" * 45)
        print(f"GRAND TOTAL: INR {total_order_amount:.2f}")
        print("=" * 45 + "\n")

    except Exception as e:
        conn.rollback()
        print(f"Transaction failed: {e}")
    finally:
        conn.close()

def view_sales_report():
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT 
        o.order_id,
        c.name AS customer_name,
        o.order_date,
        COUNT(oi.item_id) AS total_units,
        o.total_amount
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id
    ORDER BY o.order_date DESC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    print("\n--- Sales & Analytics Summary ---")
    print(f"{'Order ID':<10} {'Customer':<18} {'Date':<20} {'Items':<8} {'Total (INR)':<10}")
    print("-" * 68)
    for r in rows:
        print(f"{r[0]:<10} {r[1]:<18} {r[2]:<20} {r[3]:<8} {r[4]:<10.2f}")

def main():
    init_db()
    while True:
        print("\n=== QuickBill System ===")
        print("1. View Inventory")
        print("2. Create New Bill (Checkout)")
        print("3. View Sales Analytics Report")
        print("4. Exit")
        choice = input("Select an option (1-4): ").strip()

        if choice == '1':
            list_inventory()
        elif choice == '2':
            generate_bill()
        elif choice == '3':
            view_sales_report()
        elif choice == '4':
            print("Exiting application.")
            break
        else:
            print("Invalid selection. Try again.")

if __name__ == "__main__":
    main()
