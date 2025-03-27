import streamlit as st
import database as db
from datetime import datetime
import logging
import sys
import os


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize database
try:
    db.init_db()
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    st.error("Failed to initialize database. Please check the logs.")
    st.stop()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False


def login():
    # Add hotel logo/image placeholder
    st.image("pic.png", width=100)
    st.title("Hotel Management System")
    st.markdown("""
        <style>
        .main-title {
            color: #2E86C1;
            text-align: center;
            padding: 20px;
        }
        .login-container {
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        </style>
        """, unsafe_allow_html=True)

    if not st.session_state.authenticated:
        with st.form("login_form"):
            st.subheader("🔐 Admin Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)


            if submit:
                try:
                    if db.verify_admin(username, password):
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except Exception as e:
                    logger.error(f"Login error: {str(e)}")
                    st.error("Login failed. Please try again.")
    else:
        st.success("Welcome to Hotel Management System")
        # Dashboard Overview
        st.markdown("### 📊 System Features")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("👥 Employee Management")
            st.markdown("- Add new employees\n- Track employee details\n- Update information")
        with col2:
            st.success("📅 Attendance & Salary")
            st.markdown("- Mark daily attendance\n- Calculate salaries\n- Manage advances")
        with col3:
            st.warning("📦 Inventory & Rent")
            st.markdown("- Track inventory\n- Monitor stock levels\n- Manage rent payments")
def main():
    try:
        if not st.session_state.authenticated:
            login()
        else:
            st.sidebar.title("Navigation")
            if st.sidebar.button("Logout"):
                st.session_state.authenticated = False
                st.rerun()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please refresh the page.")


if __name__ == "__main__":
    main()