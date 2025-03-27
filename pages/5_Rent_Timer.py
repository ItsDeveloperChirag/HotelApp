import streamlit as st
import database as db
from datetime import datetime, timedelta
import pandas as pd
import sqlite3

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

st.title("Rent Timer")

tab1, tab2 = st.tabs(["Add Rent Payment", "View Payments"])

with tab1:
    with st.form("rent_form"):
        due_date = st.date_input("Due Date")
        amount = st.number_input("Amount", min_value=0.0)
        status = st.selectbox("Status", ["Pending", "Paid"])

        if st.form_submit_button("Add Payment"):
            if db.add_rent_payment(due_date.strftime('%Y-%m-%d'), amount, status):
                st.success("Payment record added successfully")
                st.rerun()
            else:
                st.error("Failed to add payment record")

with tab2:
    payments = db.get_rent_payments()
    if not payments.empty:
        st.dataframe(payments)

        # Show upcoming payments
        upcoming = payments[
            (payments['status'] == 'Pending') &
            (pd.to_datetime(payments['due_date']) > datetime.now())
            ]
        if not upcoming.empty:
            st.warning("Upcoming Payments")
            st.dataframe(upcoming)
        # Update payment
        st.subheader("Update Payment")
        with st.form("update_payment"):
            payment_id = st.selectbox(
                "Select Payment to Update",
                payments['id'].tolist(),
                format_func=lambda x: f"₹{payments[payments['id'] == x]['amount'].iloc[0]} "
                                      f"(Due: {payments[payments['id'] == x]['due_date'].iloc[0]})"
            )
            selected_payment = payments[payments['id'] == payment_id].iloc[0]
            new_amount = st.number_input("New Amount",
                                         value=float(selected_payment['amount']),
                                         min_value=0.0)
            new_status = st.selectbox("New Status",
                                      ["Pending", "Paid"],
                                      index=0 if selected_payment['status'] == "Pending" else 1)
            if st.form_submit_button("Update Payment"):
                if db.update_rent_payment(payment_id, new_amount, new_status):
                    st.success("Payment updated successfully")
                    st.rerun()
                else:
                    st.error("Failed to update payment")
        # Delete payment
        st.subheader("Delete Payment")
        with st.form("delete_payment"):
            payment_id_to_delete = st.selectbox(
                "Select Payment to Delete",
                payments['id'].tolist(),
                format_func=lambda x: f"₹{payments[payments['id'] == x]['amount'].iloc[0]} "
                                      f"(Due: {payments[payments['id'] == x]['due_date'].iloc[0]})"
            )
            confirm = st.text_input(
                "Type 'DELETE' to confirm",
                help="This action is irreversible"
            )
            if st.form_submit_button("Delete Payment"):
                if confirm == "DELETE":
                    if db.delete_rent_payment(payment_id_to_delete):
                        st.success("Payment deleted successfully")
                        st.rerun()
                    else:
                        st.error("Failed to delete payment")
                else:
                    st.error("Please type 'DELETE' to confirm")
    else:
        st.info("No payment records found")