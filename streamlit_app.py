import streamlit as st
import os
import pandas as pd
from auth import create_user, verify_user, load_users
from auth import load_users as _load_users_internal, get_verify_token, set_verified
from auth import regenerate_verify_token
from db import ensure_schema, insert_user
from email_utils import send_verification_email

def analyze_student_marks(students):
    """Analyze student marks and provide comprehensive analysis."""
    
    results = {
        'failed_students': [],
        'student_averages': {},
        'class_topper': '',
        'subject_toppers': {'Math': '', 'Science': '', 'English': ''}
    }
    
    subject_highest = {'Math': 0, 'Science': 0, 'English': 0}
    highest_average = 0
    
    for student_name, marks in students.items():
        math, science, english = marks
        
        # Check for failing students (marks below 40)
        if math < 40 or science < 40 or english < 40:
            results['failed_students'].append(student_name)
        
        # Calculate average marks
        average = (math + science + english) / 3
        results['student_averages'][student_name] = round(average, 2)
        
        # Track class topper (highest average)
        if average > highest_average:
            highest_average = average
            results['class_topper'] = student_name
        
        # Track subject-wise toppers
        if math > subject_highest['Math']:
            subject_highest['Math'] = math
            results['subject_toppers']['Math'] = student_name
        
        if science > subject_highest['Science']:
            subject_highest['Science'] = science
            results['subject_toppers']['Science'] = student_name
        
        if english > subject_highest['English']:
            subject_highest['English'] = english
            results['subject_toppers']['English'] = student_name
    
    return results

def _ensure_session_state():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = ""


def _render_auth():
    _ensure_session_state()

    if st.session_state["authenticated"]:
        # If email exists but is not verified, block access and show verification UI
        username = st.session_state.get("username", "")
        record = _load_users_internal().get(username)
        if record and record.get("email") and not record.get("verified", False):
            _inject_auth_styles()
            with st.sidebar:
                st.info(f"Logged in as {username} (verification pending)")
                if st.button("Logout"):
                    st.session_state["authenticated"] = False
                    st.session_state["username"] = ""
                    st.rerun()

            st.markdown("<div class='auth-wrapper'><div class='auth-card'>", unsafe_allow_html=True)
            st.markdown("<div class='auth-header'>Verify your email</div>", unsafe_allow_html=True)
            st.markdown("<div class='auth-subtitle'>Enter the verification code sent to your email</div>", unsafe_allow_html=True)
            with st.form("verify_email_form"):
                code = st.text_input("Verification code", max_chars=12)
                col_v1, col_v2 = st.columns([3, 2])
                with col_v1:
                    verify = st.form_submit_button("Verify", use_container_width=True)
                with col_v2:
                    resend = st.form_submit_button("Resend code")
                if verify:
                    if code.strip() and code.strip() == (record.get("verify_token") or ""):
                        if set_verified(username):
                            st.success("Email verified successfully!")
                            try:
                                if ensure_schema():
                                    insert_user(
                                        username,
                                        record.get("password_hash", ""),
                                        record.get("salt", ""),
                                        email=record.get("email"),
                                        verified=True,
                                        verify_token=None,
                                    )
                            except Exception:
                                pass
                            st.rerun()
                    else:
                        st.error("Invalid verification code")
                if 'resend' in locals() and resend:
                    new_token = regenerate_verify_token(username) or record.get("verify_token") or ""
                    if record.get("email"):
                        ok = send_verification_email(record.get("email"), username, new_token)
                        if ok:
                            st.info("A new verification code has been sent to your email.")
                        else:
                            st.warning("Could not send email. Check SMTP settings.")
            st.markdown("</div></div>", unsafe_allow_html=True)
            return False

        with st.sidebar:
            st.success(f"Logged in as {st.session_state['username']}")
            if st.button("Logout"):
                st.session_state["authenticated"] = False
                st.session_state["username"] = ""
                st.rerun()
        return True

    _inject_auth_styles()

    st.markdown("<div class='auth-wrapper'><div class='auth-card'>", unsafe_allow_html=True)
    st.markdown("<div class='auth-header'>📊 Student Marks Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-subtitle'>Secure access — log in or create an account</div>", unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Login", "Sign up"])

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            st.text_input("Username", key="login_username", placeholder="Enter your username")
            st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            submitted = st.form_submit_button("Log in", use_container_width=True, type="primary")
            if submitted:
                if verify_user(st.session_state.get("login_username", ""), st.session_state.get("login_password", "")):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = st.session_state.get("login_username", "")
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    with tab_signup:
        with st.form("signup_form", clear_on_submit=False):
            st.text_input("Choose a username", key="signup_username", placeholder="Pick a unique username")
            st.text_input("Email address (for verification)", key="signup_email", placeholder="you@example.com")
            st.text_input("Choose a password", type="password", key="signup_password", placeholder="At least 6 characters")
            st.text_input("Confirm password", type="password", key="signup_confirm", placeholder="Re-enter your password")
            created = st.form_submit_button("Create account", use_container_width=True)
            if created:
                username = st.session_state.get("signup_username", "").strip()
                email = st.session_state.get("signup_email", "").strip()
                password = st.session_state.get("signup_password", "")
                confirm = st.session_state.get("signup_confirm", "")
                if not username or not password:
                    st.error("Username and password are required")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif password != confirm:
                    st.error("Passwords do not match")
                    try:
                        st.toast("Passwords do not match", icon="⚠️")
                    except Exception:
                        pass
                elif load_users().get(username):
                    st.error("Username already exists")
                else:
                    if create_user(username, password, email=email):
                        st.success("Account created! You are now logged in.")
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        # Optional: Try persisting to MySQL if env is configured
                        try:
                            if ensure_schema():
                                # Fetch salt/hash from JSON store to keep single source of truth
                                record = _load_users_internal().get(username)
                                if record:
                                    insert_ok = insert_user(
                                        username,
                                        record.get("password_hash", ""),
                                        record.get("salt", ""),
                                        email=record.get("email"),
                                        verified=bool(record.get("verified", False)),
                                        verify_token=record.get("verify_token"),
                                    )
                                    if insert_ok:
                                        st.toast("User saved to MySQL", icon="✅")
                                    else:
                                        st.toast("Could not save user to MySQL", icon="⚠️")
                        except Exception:
                            pass

                        # Send verification email if email provided
                        if email:
                            token = get_verify_token(username) or ""
                            sent = send_verification_email(email, username, token)
                            if sent:
                                st.info("Verification code sent to your email. Check your inbox.")
                            else:
                                st.warning("Could not send verification email. Check SMTP settings.")
                                if os.getenv("SHOW_VERIFY_CODE", "0") == "1":
                                    with st.expander("Developer info: show verification code"):
                                        st.code(token)
                        st.rerun()
                    else:
                        st.error("Failed to create account. Try a different username.")


    st.markdown("<div class='auth-footer'>By continuing, you agree to our terms and privacy policy.</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    return False


def _inject_auth_styles():
    st.markdown(
        """
        <style>
            .block-container {max-width: 820px; padding-top: 0.5rem;}
            .auth-wrapper {
                display: flex;
                justify-content: center;
            }
            .auth-card {
                background: #ffffff;
                border: 1px solid rgba(0,0,0,0.06);
                box-shadow: 0 8px 24px rgba(0,0,0,0.08);
                border-radius: 12px;
                padding: 12px 20px 20px;
                margin-top: 12px;
                width: 100%;
                max-width: 420px;
            }
            .auth-header {
                font-weight: 700;
                font-size: 24px;
                line-height: 1.2;
                margin: 0 0 4px 0;
                text-align: center;
            }
            .auth-subtitle {
                color: #5f6368;
                margin-bottom: 16px;
                font-size: 14px;
                text-align: center;
            }
            .auth-footer {
                margin-top: 10px;
                color: #7a7f87;
                font-size: 12px;
                text-align: center;
            }
            /* Tabs styling */
            div[role="tablist"] button {
                padding-top: 10px !important;
                padding-bottom: 10px !important;
                font-weight: 600 !important;
            }
            /* Inputs */
            .stTextInput input {
                border-radius: 10px;
            }
            /* Buttons */
            .stButton button[kind="primary"] {
                border-radius: 10px;
                height: 40px;
                font-weight: 700;
            }
            .stButton button:not([kind]) {
                border-radius: 10px;
                height: 40px;
                font-weight: 700;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title="Student Marks Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    if not _render_auth():
        return

    st.title("📊 Student Marks Analyzer")
    st.markdown("---")
    
    # Sidebar for data input
    st.sidebar.header("📝 Data Input")
    
    # Option to use sample data or custom data
    data_option = st.sidebar.selectbox(
        "Choose data source:",
        ["Sample Data", "Custom Input"]
    )
    
    if data_option == "Sample Data":
        students = {
            'Alice': [85, 90, 78],
            'Bob': [72, 88, 91],
            'Charlie': [95, 85, 89],
            'David': [35, 65, 70]
        }
        st.sidebar.success("Using sample data")
        
    else:
        students = get_custom_data()
    
    # Main analysis
    if students:
        results = analyze_student_marks(students)
        display_analysis(results, students)
    
def get_custom_data():
    """Get custom student data from user input"""
    st.sidebar.subheader("Add Students")
    
    students = {}
    
    # Number of students
    num_students = st.sidebar.number_input("Number of students:", min_value=1, max_value=20, value=4)
    
    # Input fields for each student
    for i in range(num_students):
        st.sidebar.markdown(f"### Student {i+1}")
        
        name = st.sidebar.text_input(f"Name {i+1}:", key=f"name_{i}")
        math = st.sidebar.number_input(f"Math {i+1}:", min_value=0, max_value=100, value=85, key=f"math_{i}")
        science = st.sidebar.number_input(f"Science {i+1}:", min_value=0, max_value=100, value=90, key=f"science_{i}")
        english = st.sidebar.number_input(f"English {i+1}:", min_value=0, max_value=100, value=78, key=f"english_{i}")
        
        if name:  # Only add if name is provided
            students[name] = [math, science, english]
    
    return students

def display_analysis(results, students):
    """Display analysis results in Streamlit format"""
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(students))
    
    with col2:
        st.metric("Failed Students", len(results['failed_students']))
    
    with col3:
        class_avg = sum(results['student_averages'].values()) / len(results['student_averages'])
        st.metric("Class Average", f"{class_avg:.2f}%")
    
    with col4:
        top_avg = results['student_averages'][results['class_topper']]
        st.metric("Top Average", f"{top_avg:.2f}%")
    
    st.markdown("---")
    
    # Student marks table
    st.subheader("📊 Student Marks Table")
    
    # Create DataFrame for display
    data = []
    for name, marks in students.items():
        data.append({
            'Student': name,
            'Math': marks[0],
            'Science': marks[1],
            'English': marks[2],
            'Average': results['student_averages'][name],
            'Status': '❌ Failed' if name in results['failed_students'] else '✅ Passed'
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, width='stretch')
    
    # Failed students alert
    if results['failed_students']:
        st.error(f"⚠️ Students who failed: {', '.join(results['failed_students'])}")
    
    st.markdown("---")
    
    # Analysis results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Class Topper")
        st.info(f"**{results['class_topper']}** with {results['student_averages'][results['class_topper']]}% average")
        
        st.subheader("🥇 Subject Toppers")
        for subject, topper in results['subject_toppers'].items():
            st.success(f"**{subject}**: {topper}")
    
    with col2:
        st.subheader("📊 Performance Summary")
        
        # Create summary DataFrame
        summary_data = []
        for subject in ['Math', 'Science', 'English']:
            marks = [students[name][['Math', 'Science', 'English'].index(subject)] for name in students.keys()]
            summary_data.append({
                'Subject': subject,
                'Average': sum(marks) / len(marks),
                'Highest': max(marks),
                'Lowest': min(marks)
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, width='stretch')
    
    # All student averages
    st.subheader("📈 All Student Averages")
    
    avg_data = []
    for name, avg in results['student_averages'].items():
        avg_data.append({
            'Student': name,
            'Average': avg,
            'Grade': get_grade(avg)
        })
    
    avg_df = pd.DataFrame(avg_data)
    avg_df = avg_df.sort_values('Average', ascending=False)
    st.dataframe(avg_df, width='stretch')

def get_grade(average):
    """Convert average to grade"""
    if average >= 90:
        return "A+"
    elif average >= 80:
        return "A"
    elif average >= 70:
        return "B"
    elif average >= 60:
        return "C"
    elif average >= 50:
        return "D"
    else:
        return "F"

if __name__ == "__main__":
    main()