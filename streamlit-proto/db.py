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
            status TEXT DEFAULT 'ACTIVE',
            FOREIGN KEY(listing_id) REFERENCES listings(id)
        )
    """)

    # Create a simple users table for storing wallet balances
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            balance REAL
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
    """Save a contract into the database with status=ACTIVE by default."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contracts (buyer, btc, listing_id, status)
        VALUES (?, ?, ?, 'ACTIVE')
    """, (buyer, btc, listing_id))
    conn.commit()
    conn.close()

def get_contract_by_listing_and_buyer(listing_id, buyer):
    """Fetch an active contract for a given listing & buyer, if any."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, buyer, btc, listing_id, status
        FROM contracts
        WHERE listing_id = ? AND buyer = ? AND status = 'ACTIVE'
        ORDER BY id DESC
        LIMIT 1
    """, (listing_id, buyer))
    result = cursor.fetchone()
    conn.close()
    return result

def update_contract_status(contract_id, new_status):
    """Update the status of a contract (e.g., CANCELLED, COMPLETED, etc.)."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE contracts
        SET status = ?
        WHERE id = ?
    """, (new_status, contract_id))
    conn.commit()
    conn.close()

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

# --------------------------------------------------------------------------
#                  WALLET / USER-RELATED FUNCTIONS
# --------------------------------------------------------------------------
def get_or_create_user(username):
    """
    Retrieve the user by username. If not found, create a new user with 1 BTC by default
    (or whatever starting balance you prefer).
    Returns a tuple (id, username, balance).
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, balance FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user is None:
        # Create user with default balance 1.0 BTC or any value
        cursor.execute("INSERT INTO users (username, balance) VALUES (?, ?)", (username, 1.0))
        conn.commit()
        # fetch it again
        cursor.execute("SELECT id, username, balance FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
    conn.close()
    return user  # (id, username, balance)

def update_user_balance(username, new_balance):
    """Set the user's balance to `new_balance`."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET balance = ?
        WHERE username = ?
    """, (new_balance, username))
    conn.commit()
    conn.close()

def get_user_balance(username):
    """Get the current balance for a user."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return 0.0
