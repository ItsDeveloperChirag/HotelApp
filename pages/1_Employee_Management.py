import streamlit as st
import database as db
import pandas as pd

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

st.title("Employee Management")

tab1, tab2, tab3 = st.tabs(["Add Employee", "View/Update Employees", "Delete Employee"])

with tab1:
    with st.form("add_employee"):
        name = st.text_input("Name")
        aadhar = st.text_input("Aadhar Number")
        phone = st.text_input("Phone Number")
        address = st.text_area("Address")
        wage = st.number_input("Daily Wage", min_value=0.0)

        if st.form_submit_button("Add Employee"):
            if db.add_employee(name, aadhar, phone, address, wage):
                st.success("Employee added successfully")
                st.rerun()
            else:
                st.error("Failed to add employee. Aadhar number might be duplicate")

with tab2:
    employees = db.get_employees()
    if not employees.empty:
        st.dataframe(employees)
        # Update employee section
        st.subheader("Update Employee")
        with st.form("update_employee"):
            emp_id = st.selectbox(
                "Select Employee",
                employees['id'].tolist(),
                format_func=lambda x: employees[employees['id'] == x]['name'].iloc[0]
            )
            selected_emp = employees[employees['id'] == emp_id].iloc[0]
            update_name = st.text_input("Name", value=selected_emp['name'])
            update_phone = st.text_input("Phone", value=selected_emp['phone'])
            update_address = st.text_area("Address", value=selected_emp['address'])
            update_wage = st.number_input("Daily Wage",
                                          value=float(selected_emp['daily_wage']),
                                          min_value=0.0)
            if st.form_submit_button("Update Employee"):
                if db.update_employee(emp_id, update_name, update_phone,
                                      update_address, update_wage):
                    st.success("Employee updated successfully")
                    st.rerun()
                else:
                    st.error("Failed to update employee")
    else:
        st.info("No employees found")
    with tab3:
        if not employees.empty:
            st.warning("⚠️ Warning: This action cannot be undone!")
            with st.form("delete_employee"):
                emp_id_to_delete = st.selectbox(
                    "Select Employee to Delete",
                    employees['id'].tolist(),
                    format_func=lambda x: f"{employees[employees['id'] == x]['name'].iloc[0]} "
                                          f"(ID: {x})"
                )
                confirm = st.text_input(
                    "Type 'DELETE' to confirm",
                    help="This action is irreversible"
                )
                if st.form_submit_button("Delete Employee"):
                    if confirm == "DELETE":
                        if db.delete_employee(emp_id_to_delete):
                            st.success("Employee deleted successfully")
                            st.rerun()
                        else:
                            st.error("Failed to delete employee")
                    else:
                        st.error("Please type 'DELETE' to confirm")
        else:
            st.info("No employees found")
