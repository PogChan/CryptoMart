import sqlite3
import os

# Database setup
DATABASE = "marketplace.db"

def init_db():
    """Initialize the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create the listings table with `expiration` as DATETIME
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            btc_price REAL,
            expiration DATETIME,
            btc_value_at_listing REAL,
            image_path TEXT
        )
    """)
    # Create the contracts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer TEXT,
            btc REAL,
            listing_id INTEGER,
            FOREIGN KEY(listing_id) REFERENCES listings(id)
        )
    """)
    conn.commit()
    conn.close()

def save_listing(title, btc_price, expiration, btc_value_at_listing, image_path):
    """Save a listing into the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO listings (title, btc_price, expiration, btc_value_at_listing, image_path)
        VALUES (?, ?, ?, ?, ?)
    """, (title, btc_price, expiration, btc_value_at_listing, image_path))
    conn.commit()
    conn.close()

def load_listings():
    """Load all listings from the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, btc_price, expiration, btc_value_at_listing, image_path FROM listings")
    results = cursor.fetchall()
    conn.close()
    return results

def save_contract(buyer, btc, listing_id):
    """Save a contract into the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contracts (buyer, btc, listing_id)
        VALUES (?, ?, ?)
    """, (buyer, btc, listing_id))
    conn.commit()
    conn.close()

def count_contracts_by_listing(listing_id):
    """Count the number of contracts for a given listing."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM contracts WHERE listing_id = ?", (listing_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_last_buyer_by_listing(listing_id):
    """Get the last buyer for a given listing."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT buyer FROM contracts WHERE listing_id = ? ORDER BY id DESC LIMIT 1", (listing_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def delete_listing(listing_id):
    """Delete a listing from the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
    conn.commit()
    conn.close()

def update_listing(listing_id, title, btc_price, expiration, btc_value_at_listing, image_path):
    """Update a listing in the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE listings
        SET title = ?, btc_price = ?, expiration = ?, btc_value_at_listing = ?, image_path = ?
        WHERE id = ?
    """, (title, btc_price, expiration, btc_value_at_listing, image_path, listing_id))
    conn.commit()
    conn.close()
