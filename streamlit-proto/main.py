import streamlit as st
from streamlit_date_picker import date_range_picker, date_picker, PickerType

from datetime import datetime
import os
import random
from db import init_db, save_listing, load_listings, delete_listing, update_listing
from PIL import Image

# Initialize the database
init_db()

# Directory for uploaded images
UPLOAD_DIR = "uploaded_images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Simulate BTC price
btc_price = 50000  # Initial BTC price for simulation


def simulate_btc_price():
    """Simulate continuous BTC price changes."""
    global btc_price
    btc_price = random.randint(40000, 60000)


# Main layout
st.title("Crypto Marketplace")

# Sidebar user type selection
user_type = st.sidebar.radio("Select Dashboard", ["Buyer", "Seller", "Control Panel"])

# Simulate BTC price changes
simulate_btc_price()
st.sidebar.header("BTC Price Simulation")
st.sidebar.write(f"Current BTC Price: ${btc_price}")

# Seller Dashboard
if user_type == "Seller":
    st.header("Seller Dashboard")

    # Create a listing
    st.subheader("Create a Listing")
    title = st.text_input("Product Title")
    # BTC price input with USD equivalent
    btc_price_input = st.number_input("Price in BTC", min_value=0.01, step=0.01)
    if btc_price_input > 0:
        usd_value = btc_price_input * btc_price
        st.write(f"**Equivalent Price:** ${usd_value:,.2f} USD")

    # Single datetime picker for expiration
    st.subheader("Select Expiration Date-Time")
    expiration_datetime = date_picker(picker_type=PickerType.time, value=datetime.now(), key='date_picker')
    if expiration_datetime:
        expiration = datetime.strptime(expiration_datetime, "%Y-%m-%d %H:%M:%S")
        st.write(f"Selected Expiration: {expiration}")

    # File uploader
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "webp"])

    if st.button("List Product"):
        if title and btc_price_input > 0 and expiration:
            image_path = None
            if uploaded_file:
                image_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            save_listing(title, btc_price_input, expiration.strftime("%Y-%m-%d %H:%M:%S"), btc_price, image_path)
            st.success(f"Listing '{title}' created successfully!")
        else:
            st.error("Please complete all fields to create a listing.")

# Buyer Dashboard
if user_type == "Buyer":
    st.header("Buyer Dashboard")

    # Display listings
    listings = load_listings()
    if listings:
        for listing in listings:
            listing_id, listing_title, listing_btc_price, listing_expiration, listing_btc_value_at_listing, listing_image_path = listing
            st.subheader(f"Listing ID: {listing_id} - {listing_title}")
            st.write(f"Price: {listing_btc_price} BTC (~${listing_btc_price * btc_price:,.2f} USD)")
            st.write(f"Expires: {listing_expiration}")

            # Display image
            if listing_image_path and os.path.exists(listing_image_path):
                image = Image.open(listing_image_path)
                st.image(image, width=300)

            if st.button(f"Lock in Contract for {listing_title}", key=listing_id):
                st.success(f"Contract locked for {listing_title}!")
    else:
        st.write("No listings available.")

# Control Panel
if user_type == "Control Panel":
    st.header("Control Panel: Manage Listings")

    listings = load_listings()
    if listings:
        for listing in listings:
            listing_id, listing_title, listing_btc_price, listing_expiration, listing_btc_value_at_listing, listing_image_path = listing

            st.subheader(f"Listing ID: {listing_id}")
            st.write(f"Title: {listing_title}")
            st.write(f"Price: {listing_btc_price} BTC")
            st.write(f"Expiration: {listing_expiration}")
            if listing_image_path and os.path.exists(listing_image_path):
                st.image(listing_image_path, width=300)

            with st.expander("Edit Listing"):
                new_title = st.text_input(f"Edit Title (ID: {listing_id})", value=listing_title)
                new_btc_price = st.number_input(f"Edit Price in BTC (ID: {listing_id})", min_value=0.01, value=listing_btc_price)

                # Single datetime picker for editing expiration
                st.subheader("Edit Expiration Date-Time")

                new_expiration_datetime =date_picker(picker_type=PickerType.time, value=listing_expiration, key='date_picker')
                if new_expiration_datetime:
                    new_expiration = datetime.strptime(new_expiration_datetime, "%Y-%m-%d %H:%M:%S")


                new_uploaded_file = st.file_uploader(f"Upload New Image (Optional, ID: {listing_id})", type=["jpg", "jpeg", "png", "webp"])
                new_image_path = listing_image_path
                if new_uploaded_file:
                    new_image_path = os.path.join(UPLOAD_DIR, new_uploaded_file.name)
                    with open(new_image_path, "wb") as f:
                        f.write(new_uploaded_file.getbuffer())

                if st.button(f"Update Listing (ID: {listing_id})"):
                    update_listing(listing_id, new_title, new_btc_price, new_expiration.strftime("%Y-%m-%d %H:%M:%S"), btc_price, new_image_path)
                    st.success(f"Listing ID {listing_id} updated successfully!")
                    st.experimental_rerun()

            if st.button(f"Delete Listing (ID: {listing_id})"):
                delete_listing(listing_id)
                st.success(f"Listing ID {listing_id} deleted successfully!")
                st.experimental_rerun()
    else:
        st.write("No listings available.")
