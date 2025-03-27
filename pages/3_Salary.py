import streamlit as st
import database as db
from datetime import datetime
import pandas as pd

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

st.title("Salary Management")

tab1, tab2, tab3 = st.tabs(["Calculate Salary", "Advance Management", "Update/Delete Advances"])

with tab1:
    employees = db.get_employees()
    if not employees.empty:
        employee_id = st.selectbox(
            "Select Employee",
            employees['id'].tolist(),
            format_func=lambda x: employees[employees['id'] == x]['name'].iloc[0]
        )

        month = st.selectbox("Month", range(1, 13))
        year = st.selectbox("Year", range(2020, datetime.now().year + 1))

        if st.button("Calculate Salary"):
            attendance = db.get_attendance(
                f"{year}-{month:02d}-01",
                f"{year}-{month:02d}-31"
            )

            if not attendance.empty:
                present_days = len(attendance[attendance['status'] == 'Present'])
                half_days = len(attendance[attendance['status'] == 'Half-day'])
                daily_wage = employees[employees['id'] == employee_id]['daily_wage'].iloc[0]

                total_salary = (present_days + (half_days * 0.5)) * daily_wage

                advances = db.get_advances(employee_id, month, year)
                total_advance = advances['amount'].sum() if not advances.empty else 0

                st.write(f"Present Days: {present_days}")
                st.write(f"Half Days: {half_days}")
                st.write(f"Total Salary: ₹{total_salary}")
                st.write(f"Total Advances: ₹{total_advance}")
                st.write(f"Net Salary: ₹{total_salary - total_advance}")
            else:
                st.warning("No attendance records found for selected period")
    else:
        st.info("No employees found")

with tab2:
    if not employees.empty:
        with st.form("advance_form"):
            emp_id = st.selectbox(
                "Select Employee",
                employees['id'].tolist(),
                format_func=lambda x: employees[employees['id'] == x]['name'].iloc[0],
                key="advance_emp_select"
            )
            amount = st.number_input("Advance Amount", min_value=0.0)

            if st.form_submit_button("Add Advance"):
                if db.add_advance(emp_id, amount):
                    st.success("Advance recorded successfully")
                    st.rerun()
                else:
                    st.error("Failed to record advance")
    else:
        st.info("No employees found")

with tab3:
    if not employees.empty:
        # View and manage advances
        selected_emp = st.selectbox(
            "Select Employee",
            employees['id'].tolist(),
            format_func=lambda x: employees[employees['id']==x]['name'].iloc[0],
            key="manage_advance_emp_select"
        )
        month = st.selectbox("Month", range(1, 13), key="manage_advance_month")
        year = st.selectbox("Year", range(2020, datetime.now().year + 1),
                          key="manage_advance_year")
        advances = db.get_advances(selected_emp, month, year)
        if not advances.empty:
            st.dataframe(advances)
            # Update advance
            st.subheader("Update Advance")
            with st.form("update_advance"):
                advance_id = st.selectbox(
                    "Select Advance to Update",
                    advances['id'].tolist(),
                    format_func=lambda x: f"Amount: ₹{advances[advances['id']==x]['amount'].iloc[0]} "
                                        f"(Date: {advances[advances['id']==x]['date'].iloc[0]})"
                )
                new_amount = st.number_input(
                    "New Amount",
                    value=float(advances[advances['id']==advance_id]['amount'].iloc[0]),
                    min_value=0.0
                )
                if st.form_submit_button("Update Advance"):
                    if db.update_advance(advance_id, new_amount):
                        st.success("Advance updated successfully")
                        st.rerun()
                    else:
                        st.error("Failed to update advance")
            # Delete advance
            st.subheader("Delete Advance")
            with st.form("delete_advance"):
                advance_id_to_delete = st.selectbox(
                    "Select Advance to Delete",
                    advances['id'].tolist(),
                    format_func=lambda x: f"Amount: ₹{advances[advances['id']==x]['amount'].iloc[0]} "
                                        f"(Date: {advances[advances['id']==x]['date'].iloc[0]})"
                )
                confirm = st.text_input(
                    "Type 'DELETE' to confirm",
                    help="This action is irreversible"
                )
                if st.form_submit_button("Delete Advance"):
                    if confirm == "DELETE":
                        if db.delete_advance(advance_id_to_delete):
                            st.success("Advance deleted successfully")
                            st.rerun()
                        else:
                            st.error("Failed to delete advance")
                    else:
                        st.error("Please type 'DELETE' to confirm")
        else:
            st.info("No advances found for selected period")
    else:
        st.info("No employees found")