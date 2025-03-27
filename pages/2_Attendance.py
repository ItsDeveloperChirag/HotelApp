import streamlit as st
import database as db
from datetime import datetime, timedelta
import pandas as pd

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login first")
    st.stop()

st.title("Attendance Management")

tab1, tab2, tab3 = st.tabs(["Mark Attendance", "View/Update Attendance", "Delete Attendance"])

with tab1:
    employees = db.get_employees()
    date = st.date_input("Date", datetime.now())

    if not employees.empty:
        attendance_data = []
        with st.form("attendance_form"):
            for _, employee in employees.iterrows():
                status = st.selectbox(
                    f"Status for {employee['name']}",
                    ['Present', 'Absent', 'Half-day'],
                    key=f"attendance_{employee['id']}"
                )
                attendance_data.append({
                    'employee_id': employee['id'],
                    'status': status
                })
            if st.form_submit_button("Mark Attendance"):
                success = True
                for data in attendance_data:
                    if not db.mark_attendance(
                        data['employee_id'],
                        date.strftime('%Y-%m-%d'),
                        data['status']
                    ):
                        success = False
                        break
                if success:
                    st.success("Attendance marked successfully")
                    st.rerun()
                else:
                    st.error("Failed to mark attendance")
    else:
        st.info("No employees found")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date",
                                   datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    attendance = db.get_attendance(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )



    if not attendance.empty:
        st.dataframe(attendance)
        # Update attendance section
        st.subheader("Update Attendance")
        with st.form("update_attendance"):
            attendance_id = st.selectbox(
                "Select Attendance Record",
                attendance['id'].tolist(),
                format_func=lambda x: f"{attendance[attendance['id'] == x]['name'].iloc[0]} - "
                                      f"{attendance[attendance['id'] == x]['date'].iloc[0]}"
            )
            new_status = st.selectbox(
                "New Status",
                ['Present', 'Absent', 'Half-day']
            )
            if st.form_submit_button("Update Attendance"):
                if db.update_attendance(attendance_id, new_status):
                    st.success("Attendance updated successfully")
                    st.rerun()
                else:
                    st.error("Failed to update attendance")
    else:
        st.info("No attendance records found")

with tab3:
    if not attendance.empty:
        st.warning("⚠️ Warning: This action cannot be undone!")
        with st.form("delete_attendance"):
            attendance_id_to_delete = st.selectbox(
                "Select Attendance Record to Delete",
                attendance['id'].tolist(),
                format_func=lambda x: f"{attendance[attendance['id']==x]['name'].iloc[0]} - "
                                    f"{attendance[attendance['id']==x]['date'].iloc[0]}"
            )
            confirm = st.text_input(
                "Type 'DELETE' to confirm",
                help="This action is irreversible"
            )
            if st.form_submit_button("Delete Attendance"):
                if confirm == "DELETE":
                    if db.delete_attendance(attendance_id_to_delete):
                        st.success("Attendance record deleted successfully")
                        st.rerun()
                    else:
                        st.error("Failed to delete attendance record")
                else:
                    st.error("Please type 'DELETE' to confirm")
    else:
        st.info("No attendance records found")