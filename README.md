# QuickBill: Relational Store & Billing System

A lightweight, transaction-safe billing and inventory management application backed by a normalized relational database schema.

## Key Features
* **Normalized Relational Schema:** Designed with 4 interconnected entities (`Customers`, `Products`, `Orders`, and `Order_Items`) enforcing 3NF principles and referential integrity.
* **ACID Transaction Handling:** Implements atomic checkout workflows ensuring inventory stock is consistently decremented or rolled back during interrupted operations.
* **Sales Analytics Engine:** Aggregates real-time order history, unit movement, and customer spending via multi-table SQL `JOIN` and `GROUP BY` operations.

## Tech Stack
* **Language:** Python 3
* **Database:** SQLite / Relational SQL

## Database Schema Design
* `customers` (`customer_id` PK, `name`, `phone` UNIQUE)
* `products` (`product_id` PK, `name`, `price`, `stock`)
* `orders` (`order_id` PK, `customer_id` FK, `order_date`, `total_amount`)
* `order_items` (`item_id` PK, `order_id` FK, `product_id` FK, `quantity`, `unit_price`)

## Getting Started
Clone the repository and run directly without external package dependencies:

```bash
git clone [https://github.com/](https://github.com/)<your-username>/quickbill-rdbms.git
cd quickbill-rdbms
python main.py
