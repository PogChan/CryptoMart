import streamlit as st
from streamlit_date_picker import date_range_picker, date_picker, PickerType

from datetime import datetime, timedelta
import os
import random
from db import *
from PIL import Image

# Initialize the database
init_db()

UPLOAD_DIR = "uploaded_images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Simulate BTC price
global btc_price
btc_price = 50000  # Initial BTC price for simulation

def timeFromNow(expiration):
    """Display how far in the future the expiration is."""
    time_difference = expiration - datetime.now()
    days = time_difference.days
    seconds = time_difference.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    months = days // 30
    remaining_days = days % 30

    st.write(f"⏳ Expiration: {expiration}")
    st.write(f"Time until expiration: **{months} months, {remaining_days} days, {hours} hours, {minutes} minutes**")

def simulate_btc_price(current_price, min_change=-1.0, max_change=1.0):
    """Simulate continuous BTC price changes by ±1% max (just for fun)."""
    percentage_change = random.uniform(min_change, max_change) / 100
    updated_price = current_price * (1 + percentage_change)
    return round(updated_price, 2)

# ----------------------------------------------------------------------
#                   USER / WALLET UTILS
# ----------------------------------------------------------------------
def ensure_session_user():
    """
    Ensure we have a session-level user (username).
    We'll store it in st.session_state.
    """
    if "username" not in st.session_state or not st.session_state.username:
        st.session_state.username = f"User_{random.randint(1,999)}"  # or you can let them input a name

    # Retrieve or create user in DB
    user_record = get_or_create_user(st.session_state.username)
    # user_record is (id, username, balance)
    return user_record

def show_user_wallet():
    """Display user wallet (balance) and deposit/withdraw options."""
    user_record = ensure_session_user()
    user_id, username, balance = user_record

    st.write(f"👤 Current User: **{username}**")
    st.write(f"💰 Wallet Balance: **{balance:.4f} BTC**")

    with st.expander("Manage Wallet"):
        deposit_amount = st.number_input("Deposit BTC", min_value=0.0, step=0.01, value=0.0)
        if st.button("Deposit"):
            if deposit_amount > 0:
                new_balance = balance + deposit_amount
                update_user_balance(username, new_balance)
                st.success(f"Deposited {deposit_amount:.4f} BTC! New Balance: {new_balance:.4f} BTC")
                st.rerun()

        withdraw_amount = st.number_input("Withdraw BTC", min_value=0.0, step=0.01, value=0.0, key="wd")
        if st.button("Withdraw"):
            if withdraw_amount > 0:
                if withdraw_amount <= balance:
                    new_balance = balance - withdraw_amount
                    update_user_balance(username, new_balance)
                    st.success(f"Withdrew {withdraw_amount:.4f} BTC! New Balance: {new_balance:.4f} BTC")
                    st.rerun()
                else:
                    st.error("Not enough balance.")

# ----------------------------------------------------------------------
#                          MAIN APP
# ----------------------------------------------------------------------
st.title("🚀 BTC Speculative Marketplace 🪙")

# We can simulate or set custom BTC price
st.sidebar.title("Settings & Wallet")

# Ensure user / wallet
user_record = ensure_session_user()
_, username, current_balance = user_record  # ignoring user_id for now

# Let user override the BTC price or keep simulating
custom_price = st.sidebar.number_input("Set Custom BTC Price (Optional)", min_value=10000.0, step=1000.0, value=float(btc_price))
if custom_price != btc_price:
    btc_price = custom_price
btc_price = simulate_btc_price(btc_price)

st.sidebar.write(f"💸 **Current BTC Price:** ${btc_price:,.2f}")
show_user_wallet()  # Show wallet controls in sidebar

# Sidebar: choose user dashboard
user_type = st.sidebar.radio("📋 Dashboard", ["Seller", "Buyer", "Control Panel"], index=0)

# -------------------------- SELLER DASHBOARD ---------------------------
if user_type == "Seller":
    st.header("🧑‍💼 Seller Dashboard")
    st.markdown("""
    List products in **BTC**.
    If the product is cheaper in USD, you may profit if BTC price falls,
    or lose if BTC price goes up.
    """)

    st.subheader("Create a Listing")
    title = st.text_input("📝 Product Title")
    btc_price_input = st.number_input("💲 Price in BTC", min_value=0.01, step=0.01)

    if btc_price_input > 0:
        usd_value = btc_price_input * btc_price
        st.write(f"**Approx USD Value:** ${usd_value:,.2f}")

    st.subheader("⏱ Select Expiration Date-Time")
    expiration_datetime = date_picker(picker_type=PickerType.time, value=datetime.now(), key='date_picker_seller')
    expiration = None
    if expiration_datetime:
        expiration = datetime.strptime(expiration_datetime, "%Y-%m-%d %H:%M:%S")
        timeFromNow(expiration)

    uploaded_file = st.file_uploader("🖼 Upload Image", type=["jpg", "jpeg", "png", "webp"])

    if st.button("📌 List Product"):
        if title and btc_price_input > 0 and expiration:
            image_path = None
            if uploaded_file:
                image_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            # Save listing
            save_listing(
                title,
                btc_price_input,
                expiration.strftime("%Y-%m-%d %H:%M:%S"),
                btc_price,  # store current BTC price
                image_path
            )
            st.success(f"🌟 Listing '{title}' created successfully!")
        else:
            st.error("Please complete all fields to create a listing.")

# -------------------------- BUYER DASHBOARD ----------------------------
if user_type == "Buyer":
    st.header("🤝 Buyer Dashboard")
    st.markdown("Lock in contracts **in BTC** at the current price, hoping to gain from BTC fluctuations.")

    listings = load_listings()
    if listings:
        for listing in listings:
            listing_id, listing_title, listing_btc_price, listing_expiration, listing_btc_value_at_listing, listing_image_path = listing
            st.subheader(f"🔖 Listing #{listing_id}: {listing_title}")
            current_usd_price = listing_btc_price * btc_price
            st.write(f"**Price**: {listing_btc_price} BTC (~${current_usd_price:,.2f} USD)")
            st.write(f"*(Seller created when BTC was ${listing_btc_value_at_listing:,.2f})*")

            try:
                listing_expiration_dt = datetime.fromisoformat(listing_expiration)
            except ValueError:
                st.error(f"Invalid expiration format for listing #{listing_id}.")
                continue
            timeFromNow(listing_expiration_dt)

            # Display image if available
            if listing_image_path and os.path.exists(listing_image_path):
                image = Image.open(listing_image_path)
                st.image(image, width=300)

            # Button to lock in contract
            if st.button(f"🔒 Lock Contract for {listing_title}", key=f"lock_{listing_id}"):
                # Check buyer's balance
                if listing_btc_price <= current_balance:
                    # Deduct from buyer's wallet
                    new_balance = current_balance - listing_btc_price
                    update_user_balance(username, new_balance)
                    # Save contract
                    save_contract(username, listing_btc_price, listing_id)
                    st.success(f"Contract locked! Escrow {listing_btc_price:.4f} BTC. New Balance: {new_balance:.4f} BTC")
                    st.rerun()
                else:
                    st.error("Insufficient BTC balance.")

            # If buyer has an ACTIVE contract for this listing, show a 'Cancel' button
            existing_contract = get_contract_by_listing_and_buyer(listing_id, username)
            if existing_contract:
                contract_id, c_buyer, c_btc, c_listing_id, c_status = existing_contract
                st.info(f"**You have an active contract** here for {c_btc:.4f} BTC.")

                # Cancel (withdraw) with a penalty of e.g. 10%
                if st.button(f"❌ Withdraw Contract (Penalty 10%) - {listing_title}", key=f"cancel_{listing_id}"):
                    penalty = c_btc * 0.10
                    refund = c_btc - penalty
                    # Mark contract CANCELLED
                    update_contract_status(contract_id, "CANCELLED")
                    # Return BTC minus penalty
                    updated_balance = current_balance + refund
                    update_user_balance(username, updated_balance)
                    st.warning(f"Contract cancelled. You lost {penalty:.4f} BTC as a penalty.")
                    st.write(f"Your new balance is {updated_balance:.4f} BTC")
                    st.rerun()

    else:
        st.write("⚠️ No listings available.")

# ------------------------- CONTROL PANEL -------------------------------
if user_type == "Control Panel":
    st.header("🛠 Control Panel")
    st.markdown("Manage listings, fast-forward expirations, etc.")

    listings = load_listings()
    if listings:
        for listing in listings:
            listing_id, listing_title, listing_btc_price, listing_expiration, listing_btc_value_at_listing, listing_image_path = listing
            st.subheader(f"Listing ID: {listing_id}")
            st.write(f"Title: **{listing_title}**")
            st.write(f"Price: **{listing_btc_price} BTC**")

            if listing_image_path and os.path.exists(listing_image_path):
                st.image(listing_image_path, width=300)

            try:
                listing_expiration_dt = datetime.fromisoformat(listing_expiration)
            except ValueError:
                st.error(f"Invalid expiration format for listing #{listing_id}.")
                continue
            timeFromNow(listing_expiration_dt)

            with st.expander("✏️ Edit Listing"):
                new_title = st.text_input(f"Edit Title (ID: {listing_id})", value=listing_title)
                new_btc_price = st.number_input(f"Edit Price in BTC (ID: {listing_id})", min_value=0.01, value=listing_btc_price)

                if st.button("⏩ Fast Forward Expiration", key=f"ff_{listing_id}"):
                    # Expire in 1 second
                    update_listing(
                        listing_id=listing_id,
                        title=listing_title,
                        btc_price=listing_btc_price,
                        expiration=(datetime.now() + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"),
                        btc_value_at_listing=listing_btc_value_at_listing,
                        image_path=listing_image_path,
                    )
                    st.success(f"Listing {listing_id} will expire in 1 second!")
                    st.rerun()

                st.write("Edit Expiration Date-Time:")
                new_expiration_datetime = date_picker(
                    picker_type=PickerType.time,
                    value=listing_expiration_dt,
                    key=f"date_picker_{listing_id}"
                )
                if new_expiration_datetime:
                    try:
                        new_expiration = datetime.strptime(new_expiration_datetime, "%Y-%m-%d %H:%M:%S")
                    except:
                        new_expiration = listing_expiration_dt

                new_uploaded_file = st.file_uploader(f"Upload New Image (Optional, ID: {listing_id})", type=["jpg", "jpeg", "png", "webp"], key=f"file_{listing_id}")
                new_image_path = listing_image_path
                if new_uploaded_file:
                    new_image_path = os.path.join(UPLOAD_DIR, new_uploaded_file.name)
                    with open(new_image_path, "wb") as f:
                        f.write(new_uploaded_file.getbuffer())

                if st.button(f"Update Listing (ID: {listing_id})", key=f"update_{listing_id}"):
                    if new_expiration_datetime:
                        update_listing(listing_id, new_title, new_btc_price, new_expiration.strftime("%Y-%m-%d %H:%M:%S"), listing_btc_value_at_listing, new_image_path)
                    else:
                        update_listing(listing_id, new_title, new_btc_price, listing_expiration, listing_btc_value_at_listing, new_image_path)
                    st.success(f"Listing ID {listing_id} updated successfully!")
                    st.rerun()

            # Delete listing
            if st.button(f"🗑 Delete Listing (ID: {listing_id})", key=f"delete_{listing_id}"):
                delete_listing(listing_id)
                st.success(f"Listing ID {listing_id} deleted successfully!")
                st.rerun()
    else:
        st.write("No listings available.")
