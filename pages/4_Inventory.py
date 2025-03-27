import streamlit as st
import database as db
import pandas as pd

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

st.title("Inventory Management")

tab1, tab2 = st.tabs(["Update Inventory", "View Inventory"])

with tab1:
    with st.form("inventory_form"):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=0.0)
        unit = st.selectbox("Unit", ["kg", "liters", "pieces", "packets"])

        if st.form_submit_button("Update Inventory"):
            if db.update_inventory(item_name, quantity, unit):
                st.success("Inventory updated successfully")
                st.rerun()
            else:
                st.error("Failed to update inventory")

with tab2:
    inventory = db.get_inventory()
    if not inventory.empty:
        st.dataframe(inventory)

        # Show low stock alerts
        low_stock = inventory[inventory['quantity'] < 10]
        if not low_stock.empty:
            st.warning("Low Stock Alert!")
            st.dataframe(low_stock)
            # Delete inventory item
            st.subheader("Delete Inventory Item")
            with st.form("delete_inventory"):
                item_id = st.selectbox(
                    "Select Item to Delete",
                    inventory['id'].tolist(),
                    format_func=lambda x: f"{inventory[inventory['id'] == x]['item_name'].iloc[0]} "
                                          f"({inventory[inventory['id'] == x]['quantity'].iloc[0]} "
                                          f"{inventory[inventory['id'] == x]['unit'].iloc[0]})"
                )
                confirm = st.text_input(
                    "Type 'DELETE' to confirm",
                    help="This action is irreversible"
                )
                if st.form_submit_button("Delete Item"):
                    if confirm == "DELETE":
                        if db.delete_inventory_item(item_id):
                            st.success("Item deleted successfully")
                            st.rerun()
                        else:
                            st.error("Failed to delete item")
                    else:
                        st.error("Please type 'DELETE' to confirm")
    else:
        st.info("No inventory items found")
