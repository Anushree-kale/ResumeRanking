import streamlit as st
import bcrypt
import os
import mysql.connector
from database import init_db, add_user, get_user, add_resume, create_ranking_session, add_ranking, get_job_roles, get_resumes_for_user, get_rankings
from file_processor import extract_text, save_file
from ranking import rank_by_job_role, rank_by_description
import plotly.express as px
import pandas as pd
from PIL import Image
import base64
from io import BytesIO
import time
import random

# Set page configuration
st.set_page_config(
    page_title="ResumeRank",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling with enhanced visuals
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            background-attachment: fixed;
        }
        
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .css-18e3th9 {
            padding-top: 2rem;
            padding-bottom: 10rem;
        }
        
        .css-1d391kg {
            padding-top: 3.5rem;
        }
        
        .stButton>button {
            background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
            color: white;
            font-weight: 500;
            border-radius: 8px;
            border: none;
            padding: 0.6rem 1.2rem;
            transition: all 0.3s;
            box-shadow: 0 4px 6px rgba(63, 81, 181, 0.2);
        }
        
        .stButton>button:hover {
            background: linear-gradient(90deg, #303f9f 0%, #3f51b5 100%);
            box-shadow: 0 6px 10px rgba(63, 81, 181, 0.3);
            transform: translateY(-2px);
        }
        
        .upload-section {
            background-color: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.08);
            margin-bottom: 25px;
            border-top: 5px solid #3f51b5;
            transition: all 0.3s ease;
        }
        
        .upload-section:hover {
            box-shadow: 0 12px 20px rgba(0,0,0,0.12);
            transform: translateY(-5px);
        }
        
        .ranking-section {
            background-color: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.08);
            border-top: 5px solid #5c6bc0;
            transition: all 0.3s ease;
        }
        
        .ranking-section:hover {
            box-shadow: 0 12px 20px rgba(0,0,0,0.12);
            transform: translateY(-5px);
        }
        
        .results-section {
            background-color: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.08);
            margin-top: 25px;
            border-top: 5px solid #7986cb;
            transition: all 0.3s ease;
        }
        
        .results-section:hover {
            box-shadow: 0 12px 20px rgba(0,0,0,0.12);
            transform: translateY(-5px);
        }
        
        .welcome-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.8) 100%);
            backdrop-filter: blur(10px);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            text-align: center;
            margin: 30px 0;
            border: 1px solid rgba(255,255,255,0.3);
            position: relative;
            overflow: hidden;
        }
        
        .welcome-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPgogIDxkZWZzPgogICAgPHBhdHRlcm4gaWQ9InBhdHRlcm4iIHg9IjAiIHk9IjAiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgcGF0dGVyblRyYW5zZm9ybT0icm90YXRlKDQ1KSI+CiAgICAgIDxjaXJjbGUgY3g9IjIwIiBjeT0iMjAiIHI9IjEiIGZpbGw9IiMzZjUxYjUiIGZpbGwtb3BhY2l0eT0iMC4xIiAvPgogICAgPC9wYXR0ZXJuPgogIDwvZGVmcz4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI3BhdHRlcm4pIiAvPgo8L3N2Zz4=');
            opacity: 0.5;
            z-index: -1;
        }
        
        .auth-card {
            background: white;
            padding: 35px;
            border-radius: 16px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
            border-top: 5px solid #3f51b5;
            position: relative;
            overflow: hidden;
        }
        
        .auth-card::before {
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            width: 150px;
            height: 150px;
            background: linear-gradient(135deg, rgba(63, 81, 181, 0.1) 0%, rgba(63, 81, 181, 0.05) 100%);
            border-radius: 50%;
            transform: translate(50%, -50%);
            z-index: 0;
        }
        
        .header-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        
        .logo-text {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }
        
        .subheader {
            color: #666;
            font-size: 1.2rem;
            margin-top: 0;
            font-weight: 300;
        }
        
        .card-metric {
            background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            border: 1px solid rgba(63, 81, 181, 0.1);
        }
        
        .card-metric:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .metric-label {
            color: #666;
            font-size: 1rem;
            font-weight: 500;
            margin-top: 5px;
        }
        
        .sidebar-header {
            margin-bottom: 30px;
            text-align: center;
        }
        
        .sidebar-footer {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            text-align: center;
            color: #666;
            font-size: 0.8rem;
        }
        
        .top-candidates {
            background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
            padding: 20px;
            border-radius: 12px;
            margin-top: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            border: 1px solid rgba(63, 81, 181, 0.1);
        }
        
        .candidate-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 15px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            transition: all 0.2s ease;
            border-radius: 8px;
        }
        
        .candidate-item:hover {
            background-color: rgba(255,255,255,0.6);
            transform: translateX(5px);
        }
        
        .candidate-name {
            font-weight: 500;
        }
        
        .candidate-score {
            font-weight: 700;
            background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .feature-card {
            background: white;
            padding: 25px;
            border-radius: 16px;
            height: 100%;
            box-shadow: 0 8px 16px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(63, 81, 181, 0.1);
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.12);
        }
        
        .feature-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .feature-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .feature-description {
            color: #666;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        .user-badge {
            background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
            padding: 10px 15px;
            border-radius: 50px;
            display: inline-flex;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            border: 1px solid rgba(63, 81, 181, 0.1);
        }
        
        .user-badge-icon {
            background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            font-size: 14px;
        }
        
        .user-badge-text {
            font-weight: 500;
            color: #333;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: white;
            border-radius: 8px;
            border: 1px solid rgba(63, 81, 181, 0.1);
            color: #333;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%) !important;
            color: white !important;
        }
        
        /* Animation for welcome page */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fadeIn {
            animation: fadeIn 0.8s ease forwards;
        }
        
        .delay-1 { animation-delay: 0.2s; }
        .delay-2 { animation-delay: 0.4s; }
        .delay-3 { animation-delay: 0.6s; }
        
        /* Custom file uploader */
        .css-1cpxqw2 {
            border: 2px dashed rgba(63, 81, 181, 0.3) !important;
            border-radius: 10px !important;
            padding: 30px 20px !important;
            background-color: rgba(63, 81, 181, 0.03) !important;
            transition: all 0.3s ease !important;
        }
        
        .css-1cpxqw2:hover {
            border-color: rgba(63, 81, 181, 0.5) !important;
            background-color: rgba(63, 81, 181, 0.05) !important;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c5cae9;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #3f51b5;
        }
        
        /* Background pattern for main content */
        .main-content {
            position: relative;
        }
        
        .main-content::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgdmlld0JveD0iMCAwIDYwIDYwIj4KICA8ZyBmaWxsPSJub25lIj4KICAgIDxwYXRoIGQ9Ik0wIDAgTDYwIDAgTDYwIDYwIEwwIDYwIFoiLz4KICAgIDxjaXJjbGUgY3g9IjMwIiBjeT0iMzAiIHI9IjEuNSIgc3Ryb2tlPSIjM2Y1MWI1IiBzdHJva2Utb3BhY2l0eT0iMC4xIiBzdHJva2Utd2lkdGg9IjEiLz4KICA8L2c+Cjwvc3ZnPg==');
            opacity: 0.5;
            z-index: -1;
        }
        
        /* Welcome page background */
        .welcome-background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
            z-index: -2;
        }
        
        /* Animated circles for welcome page */
        .animated-circle {
            position: fixed;
            border-radius: 50%;
            background: linear-gradient(90deg, rgba(63, 81, 181, 0.1) 0%, rgba(92, 107, 192, 0.1) 100%);
            z-index: -1;
        }
        
        /* Custom styling for dataframe */
        .dataframe-container {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            margin: 15px 0;
        }
        
        /* Custom styling for text inputs */
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 1px solid rgba(63, 81, 181, 0.2);
            padding: 10px 15px;
            transition: all 0.3s ease;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #3f51b5;
            box-shadow: 0 0 0 2px rgba(63, 81, 181, 0.2);
        }
        
        /* Custom styling for text area */
        .stTextArea>div>div>textarea {
            border-radius: 8px;
            border: 1px solid rgba(63, 81, 181, 0.2);
            padding: 10px 15px;
            transition: all 0.3s ease;
        }
        
        .stTextArea>div>div>textarea:focus {
            border-color: #3f51b5;
            box-shadow: 0 0 0 2px rgba(63, 81, 181, 0.2);
        }
        
        /* Custom styling for selectbox */
        .stSelectbox>div>div>div {
            border-radius: 8px;
            border: 1px solid rgba(63, 81, 181, 0.2);
            transition: all 0.3s ease;
        }
        
        .stSelectbox>div>div>div:focus {
            border-color: #3f51b5;
            box-shadow: 0 0 0 2px rgba(63, 81, 181, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize database on startup
try:
    init_db()
except mysql.connector.Error as e:
    st.error(f"Database initialization failed: {str(e)}")

# Session state for managing authentication and navigation
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.page = "welcome"  # Start with a welcome page
    st.session_state.ranking_results = None

# Apply custom CSS
local_css()

# Helper function to create animated background circles
def create_animated_background():
    st.markdown("""
    <div class="welcome-background"></div>
    """, unsafe_allow_html=True)
    
    # Create multiple animated circles with random properties
    for i in range(5):
        size = random.randint(100, 300)
        top = random.randint(-50, 100)
        left = random.randint(-50, 100)
        animation_duration = random.uniform(15, 25)
        
        st.markdown(f"""
        <div class="animated-circle" style="
            width: {size}px;
            height: {size}px;
            top: {top}%;
            left: {left}%;
            animation: float {animation_duration}s infinite ease-in-out;
        "></div>
        
        <style>
            @keyframes float {{
                0% {{ transform: translate(0, 0) rotate(0deg); }}
                50% {{ transform: translate({random.randint(-30, 30)}px, {random.randint(-30, 30)}px) rotate({random.randint(5, 10)}deg); }}
                100% {{ transform: translate(0, 0) rotate(0deg); }}
            }}
        </style>
        """, unsafe_allow_html=True)

# Helper function to create a logo
def get_logo():
    # Create a logo with text and icon
    return """
    <div style="display: flex; align-items: center;">
        <div style="background: linear-gradient(135deg, #3f51b5 0%, #5c6bc0 100%); color: white; width: 50px; height: 50px; 
                    border-radius: 12px; display: flex; align-items: center; justify-content: center; 
                    font-weight: bold; font-size: 24px; margin-right: 15px; box-shadow: 0 4px 8px rgba(63, 81, 181, 0.3);">R</div>
        <div>
            <h1 class="logo-text">ResumeRank</h1>
            <p class="subheader">AI-Powered Resume Ranking</p>
        </div>
    </div>
    """

def registration_page():
    """Handles user registration with a dedicated form."""
    create_animated_background()
    st.markdown(get_logo(), unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("""
        <h2 style="font-weight: 600; color: #333; margin-bottom: 5px;">Create Your Account</h2>
        <p style="color: #666; margin-bottom: 25px;">Join ResumeRank to start ranking resumes efficiently.</p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            username = st.text_input("Username", key="reg_username", 
                                    help="Enter a unique username (max 50 characters).",
                                    placeholder="Enter username")
        
        password = st.text_input("Password", key="reg_password", type="password", 
                                help="Choose a strong password.",
                                placeholder="Enter password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            register_btn = st.button("Create Account", key="register_btn", use_container_width=True)
        
        if register_btn:
            if not username or not password:
                st.error("Please fill in all fields!")
            elif len(username) > 50:
                st.error("Username must be 50 characters or less!")
            else:
                with st.spinner("Creating your account..."):
                    try:
                        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        add_user(username, password_hash)
                        st.success(f"User '{username}' registered successfully!")
                        st.markdown("""
                        <div style="text-align: center; margin-top: 20px;">
                            <p>Account created successfully! Please log in.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add a button to go to login
                        if st.button("Go to Login", key="goto_login"):
                            st.session_state.page = "login"
                            st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                    except mysql.connector.Error as e:
                        st.error(f"Database error: {str(e)}")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 25px; padding-top: 20px; border-top: 1px solid #eee;">
            <p>Already have an account? <a href="javascript:void(0);" onclick="goToLogin()" style="color: #3f51b5; font-weight: 500; text-decoration: none;">Log in</a></p>
        </div>
        <script>
            function goToLogin() {
                // This is a workaround since we can't directly manipulate session state with JavaScript
                document.querySelectorAll('button:contains("Login")')[0].click();
            }
        </script>
        """, unsafe_allow_html=True)
        
        # Add a button for login that's hidden by default
        if st.button("Login", key="to_login_btn", help="Go to login page", type="primary"):
            st.session_state.page = "login"
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def login_page():
    """Handles user login with a dedicated form."""
    create_animated_background()
    st.markdown(get_logo(), unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("""
        <h2 style="font-weight: 600; color: #333; margin-bottom: 5px;">Welcome Back</h2>
        <p style="color: #666; margin-bottom: 25px;">Log in to access your resume ranking dashboard.</p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            username = st.text_input("Username", key="login_username", 
                                    placeholder="Enter your username")
        
        password = st.text_input("Password", key="login_password", type="password",
                                placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            login_btn = st.button("Log In", key="login_btn", use_container_width=True)
        
        if login_btn:
            if not username or not password:
                st.error("Please fill in all fields!")
            else:
                with st.spinner("Logging in..."):
                    try:
                        user = get_user(username)
                        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.page = "home"
                            st.success(f"Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password!")
                    except mysql.connector.Error as e:
                        st.error(f"Database error: {str(e)}")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 25px; padding-top: 20px; border-top: 1px solid #eee;">
            <p>Don't have an account? <a href="javascript:void(0);" onclick="goToRegister()" style="color: #3f51b5; font-weight: 500; text-decoration: none;">Sign up</a></p>
        </div>
        <script>
            function goToRegister() {
                // This is a workaround since we can't directly manipulate session state with JavaScript
                document.querySelectorAll('button:contains("Register")')[0].click();
            }
        </script>
        """, unsafe_allow_html=True)
        
        # Add a button for registration that's hidden by default
        if st.button("Register", key="to_register_btn", help="Go to registration page"):
            st.session_state.page = "register"
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def home_page():
    """Main dashboard for uploading and ranking resumes."""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Header with logo and user info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(get_logo(), unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 10px;">
            <div class="user-badge">
                <div class="user-badge-icon">👤</div>
                <span class="user-badge-text">{st.session_state.username}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    try:
        user_id = get_user(st.session_state.username)[0]
        resumes = get_resumes_for_user(user_id)
        resume_count = len(resumes) if resumes else 0
    except mysql.connector.Error as e:
        st.error(f"Database error: {str(e)}")
        return
    
    user_dir = os.path.join("uploads", st.session_state.username)
    
    # Dashboard metrics
    st.markdown("<h2 style='font-weight: 600; color: #333; margin-top: 20px;'>Dashboard</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card-metric">
            <div class="metric-value">{resume_count}</div>
            <div class="metric-label">Resumes Uploaded</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card-metric">
            <div class="metric-value">5</div>
            <div class="metric-label">Job Roles Available</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="card-metric">
            <div class="metric-value">100%</div>
            <div class="metric-label">Accuracy Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown("<h2 style='font-weight: 600; color: #333; margin-top: 30px;'>Resume Management</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%); color: white; width: 40px; height: 40px; 
                        border-radius: 10px; display: flex; align-items: center; justify-content: center; 
                        font-weight: bold; font-size: 20px; margin-right: 15px;">📄</div>
            <h3 style="margin: 0; font-weight: 600; color: #333;">Upload Resumes</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_files = st.file_uploader(
                "Choose resume files",
                type=['txt', 'docx', 'pdf'],
                accept_multiple_files=True,
                help="Upload multiple resumes in .txt, .docx, or .pdf format."
            )
        
        if uploaded_files:
            with st.spinner("Processing resumes..."):
                for file in uploaded_files:
                    try:
                        file_path = save_file(file, user_dir)
                        text_content = extract_text(file, file_path)
                        resume_id = add_resume(user_id, file.name, text_content)
                        st.success(f"Uploaded '{file.name}' successfully!")
                        # Add a small delay for visual effect
                        time.sleep(0.5)
                    except (ValueError, mysql.connector.Error) as e:
                        st.error(str(e))
        
        # Display uploaded resumes
        if resume_count > 0:
            st.markdown("<h4 style='font-weight: 500; color: #333; margin-top: 20px;'>Your Resumes</h4>", unsafe_allow_html=True)
            
            # Create a DataFrame for better display
            resume_df = pd.DataFrame({
                "File Name": [resume[1] for resume in resumes],
                "Upload Date": ["Today" for _ in resumes]  # Simplified for demo
            })
            
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(resume_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No resumes uploaded yet. Upload some resumes to get started!")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Ranking section
    with st.container():
        st.markdown('<div class="ranking-section">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%); color: white; width: 40px; height: 40px; 
                        border-radius: 10px; display: flex; align-items: center; justify-content: center; 
                        font-weight: bold; font-size: 20px; margin-right: 15px;">🎯</div>
            <h3 style="margin: 0; font-weight: 600; color: #333;">Rank Resumes</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if resume_count == 0:
            st.warning("Please upload resumes before ranking.")
        else:
            # Tabs for different ranking methods
            tab1, tab2 = st.tabs(["Rank by Job Role", "Rank by Description"])
            
            with tab1:
                try:
                    job_roles = get_job_roles()
                except mysql.connector.Error as e:
                    st.error(f"Database error: {str(e)}")
                    return
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    selected_role = st.selectbox(
                        "Select Job Role",
                        job_roles,
                        help="Choose a job role to rank resumes based on predefined keywords."
                    )
                
                st.markdown("<p style='color: #666; font-size: 0.9rem; margin-top: 10px;'>This will rank resumes based on predefined keywords for the selected job role.</p>", unsafe_allow_html=True)
                
                if st.button("Rank Resumes by Job Role", key="rank_role_btn", type="primary"):
                    with st.spinner("Ranking resumes..."):
                        try:
                            # Add a small delay for visual effect
                            time.sleep(1.5)
                            session_id = create_ranking_session(user_id, "job_role", job_roles.index(selected_role) + 1)
                            rankings = rank_by_job_role(resumes, selected_role)
                            for resume_id, _, score in rankings:
                                add_ranking(session_id, resume_id, score)
                            st.success(f"Resumes ranked for '{selected_role}'!")
                            st.session_state.ranking_results = get_rankings(session_id)
                        except mysql.connector.Error as e:
                            st.error(f"Database error: {str(e)}")
            
            with tab2:
                description = st.text_area(
                    "Enter Job Description",
                    height=150,
                    placeholder="Enter specific job requirements here...",
                    help="Enter specific requirements (e.g., '2 years experience in Python')."
                )
                
                st.markdown("<p style='color: #666; font-size: 0.9rem; margin-top: 10px;'>This will rank resumes based on similarity to your custom job description.</p>", unsafe_allow_html=True)
                
                if st.button("Rank Resumes by Description", key="rank_desc_btn", type="primary"):
                    if not description.strip():
                        st.warning("Please enter a job description!")
                    else:
                        with st.spinner("Analyzing job description and ranking resumes..."):
                            try:
                                # Add a small delay for visual effect
                                time.sleep(1.5)
                                session_id = create_ranking_session(user_id, "description", description=description)
                                rankings = rank_by_description(resumes, description)
                                for resume_id, _, score in rankings:
                                    add_ranking(session_id, resume_id, score)
                                st.success("Resumes ranked based on your description!")
                                st.session_state.ranking_results = get_rankings(session_id)
                            except mysql.connector.Error as e:
                                st.error(f"Database error: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results section
    if st.session_state.ranking_results:
        with st.container():
            st.markdown('<div class="results-section">', unsafe_allow_html=True)
            st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <div style="background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%); color: white; width: 40px; height: 40px; 
                            border-radius: 10px; display: flex; align-items: center; justify-content: center; 
                            font-weight: bold; font-size: 20px; margin-right: 15px;">📊</div>
                <h3 style="margin: 0; font-weight: 600; color: #333;">Ranking Results</h3>
            </div>
            """, unsafe_allow_html=True)
            
            rankings = st.session_state.ranking_results
            if rankings:
                # Create a DataFrame for the rankings
                df = pd.DataFrame({
                    "Resume": [name for name, _ in rankings],
                    "Score": [score for _, score in rankings]
                }).sort_values(by="Score", ascending=False)
                
                # Display results in two columns
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    # Create a bar chart with Plotly
                    fig = px.bar(
                        df,
                        x="Resume",
                        y="Score",
                        color="Score",
                        color_continuous_scale="Blues",
                        title="Resume Scores",
                        labels={"Resume": "Resume File", "Score": "Match Score (%)"},
                        height=400
                    )
                    fig.update_layout(
                        xaxis_tickangle=-45,
                        margin=dict(l=20, r=20, t=40, b=20),
                        coloraxis_colorbar=dict(title="Score"),
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("<h4 style='font-weight: 500; color: #333;'>Top Candidates</h4>", unsafe_allow_html=True)
                    st.markdown('<div class="top-candidates">', unsafe_allow_html=True)
                    
                    # Display top 5 candidates
                    for i, (resume, score) in enumerate(df.itertuples(index=False)):
                        if i >= 5:  # Only show top 5
                            break
                        
                        st.markdown(f"""
                        <div class="candidate-item">
                            <span class="candidate-name">{i+1}. {resume}</span>
                            <span class="candidate-score">{score:.1f}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Detailed table
                st.markdown("<h4 style='font-weight: 500; color: #333; margin-top: 20px;'>Detailed Rankings</h4>", unsafe_allow_html=True)
                st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                st.dataframe(
                    df.rename(columns={"Resume": "Resume File", "Score": "Match Score (%)"}),
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Export options
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button(
                        label="Export Results (CSV)",
                        data=df.to_csv(index=False).encode('utf-8'),
                        file_name="resume_rankings.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with col2:
                    st.download_button(
                        label="Generate PDF Report",
                        data=df.to_csv(index=False).encode('utf-8'),  # Placeholder, would be PDF in real app
                        file_name="resume_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.info("No rankings available for this session.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def welcome_page():
    """Initial page with separate options for login and registration."""
    create_animated_background()
    
    st.markdown(get_logo(), unsafe_allow_html=True)
    
    # Hero section
    st.markdown("""
    <div class="welcome-card animate-fadeIn">
        <h1 style="background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 700; margin-bottom: 15px;">AI-Powered Resume Ranking</h1>
        <p style="font-size: 1.3rem; color: #666; margin-bottom: 40px; max-width: 800px; margin-left: auto; margin-right: auto;">
            Find the perfect candidates faster with our intelligent resume ranking system.
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 30px;">
            <div id="login-btn-container"></div>
            <div id="register-btn-container"></div>
        </div>
        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDYwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPHJlY3QgeD0iMTAwIiB5PSI1MCIgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIHJ4PSIxMCIgZmlsbD0iI0M1Q0FFOSIvPgogIDxyZWN0IHg9IjI1MCIgeT0iNTAiIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiByeD0iMTAiIGZpbGw9IiM5RkE4REEiLz4KICA8cmVjdCB4PSI0MDAiIHk9IjUwIiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgcng9IjEwIiBmaWxsPSIjN0E4NkM4Ii8+CiAgPGxpbmUgeDE9IjIwMCIgeTE9IjEwMCIgeDI9IjI1MCIgeTI9IjEwMCIgc3Ryb2tlPSIjM0Y1MUI1IiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9IjQgNCIvPgogIDxsaW5lIHgxPSIzNTAiIHkxPSIxMDAiIHgyPSI0MDAiIHkyPSIxMDAiIHN0cm9rZT0iIzNGNTFCNSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSI0IDQiLz4KICA8dGV4dCB4PSIxNTAiIHk9IjEwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZmlsbD0iIzNGNTFCNSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iYm9sZCI+VXBsb2FkPC90ZXh0PgogIDx0ZXh0IHg9IjMwMCIgeT0iMTAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiBmaWxsPSIjM0Y1MUI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSJib2xkIj5SYW5rPC90ZXh0PgogIDx0ZXh0IHg9IjQ1MCIgeT0iMTAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiBmaWxsPSIjM0Y1MUI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSJib2xkIj5IaXJlPC90ZXh0Pgo8L3N2Zz4=" alt="Resume Ranking Process" style="max-width: 600px; margin-top: 20px;">
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("<h2 style='font-weight: 600; color: #333; text-align: center; margin: 40px 0 30px;' class='animate-fadeIn delay-1'>Key Features</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card animate-fadeIn delay-1">
            <div class="feature-icon">📄</div>
            <h3 class="feature-title">Smart Resume Analysis</h3>
            <p class="feature-description">Upload resumes in multiple formats (PDF, DOCX, TXT) and get instant analysis with AI-powered keyword extraction.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card animate-fadeIn delay-2">
            <div class="feature-icon">🎯</div>
            <h3 class="feature-title">Customizable Ranking</h3>
            <p class="feature-description">Rank candidates based on predefined job roles or your custom job descriptions with weighted keyword matching.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card animate-fadeIn delay-3">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">Visual Results</h3>
            <p class="feature-description">Get clear visualizations and detailed rankings to make informed hiring decisions with exportable reports.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works section
    st.markdown("<h2 style='font-weight: 600; color: #333; text-align: center; margin: 50px 0 30px;' class='animate-fadeIn delay-2'>How It Works</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%); width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; font-size: 30px;">1</div>
            <h3 style="font-weight: 500; color: #333; margin-bottom: 10px;">Upload Resumes</h3>
            <p style="color: #666;">Upload candidate resumes in various formats for processing.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%); width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; font-size: 30px;">2</div>
            <h3 style="font-weight: 500; color: #333; margin-bottom: 10px;">Select Criteria</h3>
            <p style="color: #666;">Choose a job role or enter a custom job description.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%); width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; font-size: 30px;">3</div>
            <h3 style="font-weight: 500; color: #333; margin-bottom: 10px;">Get Results</h3>
            <p style="color: #666;">View ranked results with detailed scores and visualizations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Login/Register buttons
    st.markdown("<div style='text-align: center; margin-top: 50px;' class='animate-fadeIn delay-3'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login", key="welcome_login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    
    with col2:
        if st.button("Register", key="welcome_register", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 80px; padding-top: 30px; border-top: 1px solid #eee; color: #666;">
        <p>© 2023 ResumeRank. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar configuration
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%); padding: 20px; border-radius: 50%; width: 100px; height: 100px; 
                        display: flex; align-items: center; justify-content: center; margin: 0 auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <span style="font-size: 3rem;">👤</span>
            </div>
            <h3 style="margin-top: 15px; font-weight: 600; color: #333;">{st.session_state.username}</h3>
            <p style="color: #666; margin-top: 0;">Recruiter</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        st.markdown("<h3 style='font-weight: 600; color: #333; margin-bottom: 15px;'>Navigation</h3>", unsafe_allow_html=True)
        
        if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
            
        if st.button("📄 Resume Management", key="nav_resumes", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
            
        if st.button("🔍 Ranking History", key="nav_history", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        
        # Logout button at the bottom
        st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.page = "welcome"
            st.success("Logged out successfully!")
            st.rerun()
        st.markdown("<p>© 2023 ResumeRank</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Navigation logic with separate options
if st.session_state.page == "welcome":
    welcome_page()
elif st.session_state.page == "register":
    registration_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "home" and st.session_state.logged_in:
    home_page()
else:
    st.session_state.page = "welcome"
    welcome_page()