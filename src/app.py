"""
Created on Thu Sep 14 13:00:00 2023

@author: samagra shrivastava
"""

import hashlib
import streamlit as st
import pickle
import os
from streamlit_option_menu import option_menu
import datetime
import pandas as pd
import plotly.express as px
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import secrets

NOTIFICATIONS_FILE = 'notifications.pkl'
NEW_DISEASES_FILE = 'new_diseases.pkl'
SESSIONS_FILE = 'sessions.pkl'
SESSION_COOKIE = 'dps_session_id'

def log_notification(message, notif_type='info'):
    notifications = []
    if os.path.exists(NOTIFICATIONS_FILE):
        with open(NOTIFICATIONS_FILE, 'rb') as f:
            notifications = pickle.load(f)
    notifications.append({
        'message': message,
        'type': notif_type,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    with open(NOTIFICATIONS_FILE, 'wb') as f:
        pickle.dump(notifications, f)

def get_notifications():
    if not os.path.exists(NOTIFICATIONS_FILE):
        return []
    with open(NOTIFICATIONS_FILE, 'rb') as f:
        return pickle.load(f)

def log_new_disease_report(report):
    reports = []
    if os.path.exists(NEW_DISEASES_FILE):
        with open(NEW_DISEASES_FILE, 'rb') as f:
            reports = pickle.load(f)
    reports.append(report)
    with open(NEW_DISEASES_FILE, 'wb') as f:
        pickle.dump(reports, f)

def get_new_disease_reports():
    if not os.path.exists(NEW_DISEASES_FILE):
        return []
    with open(NEW_DISEASES_FILE, 'rb') as f:
        return pickle.load(f)

def log_user_event(username, event):
    sessions = {}
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'rb') as f:
            sessions = pickle.load(f)
    if username not in sessions:
        sessions[username] = []
    sessions[username].append({
        'event': event,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    with open(SESSIONS_FILE, 'wb') as f:
        pickle.dump(sessions, f)

def get_user_sessions(username=None):
    if not os.path.exists(SESSIONS_FILE):
        return {}
    with open(SESSIONS_FILE, 'rb') as f:
        sessions = pickle.load(f)
    if username:
        return sessions.get(username, [])
    return sessions

MEDICINE_SUGGESTIONS = {
    'Diabetes': ['Metformin', 'Insulin', 'Glipizide'],
    'Heart Disease': ['Aspirin', 'Atorvastatin', 'Beta-blockers'],
    'Parkinsons': ['Levodopa', 'Carbidopa', 'Pramipexole'],
    'Malaria': ['Artemether-lumefantrine', 'Quinine', 'Chloroquine'],
    'Typhoid': ['Ciprofloxacin', 'Azithromycin', 'Ceftriaxone'],
    'AIDS': ['Antiretroviral therapy (ART)', 'Tenofovir', 'Efavirenz'],
}

# --- Prediction History Utilities ---
PREDICTIONS_FILE = 'predictions.pkl'

def load_predictions():
    if os.path.exists(PREDICTIONS_FILE):
        with open(PREDICTIONS_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_predictions(predictions):
    with open(PREDICTIONS_FILE, 'wb') as f:
        pickle.dump(predictions, f)

def log_prediction(username, disease, result, features):
    predictions = load_predictions()
    if username not in predictions:
        predictions[username] = []
    predictions[username].append({
        'disease': disease,
        'result': result,
        'features': features,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_predictions(predictions)

def get_user_predictions(username):
    predictions = load_predictions()
    return predictions.get(username, [])

# --- User Authentication Utilities ---
USERS_FILE = 'users.pkl'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'wb') as f:
        pickle.dump(users, f)

def register_user(username, password, role='doctor', email=None):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        'password': hash_password(password),
        'role': role,
        'registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'email': email,
        'verified': False if role == 'doctor' else True,
        'token': None
    }
    save_users(users)
    return True

def authenticate_user(username, password):
    users = load_users()
    return username in users and users[username]['password'] == hash_password(password)

def get_user_role(username=None):
    if username:
        users = load_users()
        return users.get(username, {}).get('role', 'doctor')
    if 'role' in st.session_state:
        return st.session_state.role
    return 'doctor'

def get_all_users():
    users = load_users()
    return users

# --- Streamlit App Styling ---
CUSTOM_CSS = '''
<style>
body {
    background-color: #f4f6fa;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027 0%, #2c5364 100%);
    color: #fff;
}
.stButton>button {
    background-color: #e63946;
    color: #fff;
    border-radius: 8px;
    font-weight: bold;
    border: none;
    padding: 0.5em 1.5em;
    margin: 0.5em 0;
}
.stButton>button:hover {
    background-color: #457b9d;
    color: #fff;
}
.stTextInput>div>div>input {
    background-color: #f1faee;
    color: #1d3557;
    border-radius: 6px;
}
.stSelectbox>div>div>div>div {
    background-color: #f1faee;
    color: #1d3557;
    border-radius: 6px;
}
h1, h2, h3, h4 {
    color: #1d3557;
}
hr {
    border: 1px solid #e63946;
}
</style>
'''
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Session State for Auth ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'page' not in st.session_state:
    st.session_state.page = 'Login'

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.page = 'Login'

# --- Sidebar Navigation ---
with st.sidebar:
    st.image('https://img.icons8.com/color/96/000000/hospital-3.png', width=80)
    st.markdown('<h2 style="color:#fff;">Nairobi Hospital DPS</h2>', unsafe_allow_html=True)
    if st.session_state.logged_in:
        role = get_user_role(st.session_state.username)
        sidebar_options = ['Dashboard', 'Diabetes Prediction', 'Heart Disease Prediction', 'Parkinsons Prediction', 'Malaria Prediction', 'Typhoid Prediction', 'AIDS Prediction', 'Other Disease', 'Reports', 'Logout', 'About']
        sidebar_icons = ['house', 'activity', 'heart', 'person', 'bug', 'droplet', 'alert-triangle', 'plus-circle', 'bar-chart', 'box-arrow-right', 'info-circle']
        if role == 'admin':
            sidebar_options.insert(-2, 'Admin')
            sidebar_icons.insert(-2, 'people')
        selected = option_menu(
            menu_title=None,
            options=sidebar_options,
            icons=sidebar_icons,
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#0f2027"},
                "icon": {"color": "#e63946", "font-size": "20px"},
                "nav-link": {"color": "#fff", "font-size": "16px", "text-align": "left", "margin":"0px"},
                "nav-link-selected": {"background-color": "#457b9d"},
            }
        )
    else:
        selected = option_menu(
            menu_title=None,
            options=['Login', 'Register', 'About'],
            icons=['box-arrow-in-right', 'person-plus', 'info-circle'],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#0f2027"},
                "icon": {"color": "#e63946", "font-size": "20px"},
                "nav-link": {"color": "#fff", "font-size": "16px", "text-align": "left", "margin":"0px"},
                "nav-link-selected": {"background-color": "#457b9d"},
            }
        )

# --- Auth Pages ---
# --- Ensure default admin user exists ---
def ensure_admin_user():
    users = load_users()
    if 'admin' not in users:
        users['admin'] = {
            'password': hash_password('admin1234#'),
            'role': 'admin',
            'registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_users(users)
ensure_admin_user()

# --- Login Page (session_state only) ---
if selected == 'Login':
    st.title('Login')
    st.markdown('Log in to access the Disease Prediction System.')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    if st.button('Login'):
        auth_result = authenticate_user(username, password)
        if auth_result is True:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = get_user_role(username)
            st.success(f'Welcome, {username}!')
            st.session_state.page = 'Dashboard'
            log_user_event(username, 'login')
            st.rerun()
        elif auth_result == 'unverified':
            st.error('Your account is not verified. Please check your email or contact admin for approval.')
        else:
            st.error('Invalid username or password.')
    st.stop()

# --- Logout (session_state only) ---
if selected == 'Logout':
    log_user_event(st.session_state.username, 'logout')
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.role = 'doctor'
    st.success('You have been logged out.')
    st.stop()

# --- Role checks and access control ---
def get_user_role(username=None):
    if username:
        users = load_users()
        return users.get(username, {}).get('role', 'doctor')
    if 'role' in st.session_state:
        return st.session_state.role
    return 'doctor'

# --- Restrict access to prediction pages ---
if not st.session_state.get('logged_in', False) and selected not in ['About', 'Login', 'Register']:
    st.warning('Please log in to access this page.')
    st.stop()

# --- Dashboard ---
if st.session_state.get('logged_in', False):
    username = st.session_state.username
    role = st.session_state.role
else:
    username = ''
    role = 'doctor'

if st.session_state.logged_in and selected == 'Dashboard':
    st.markdown('<h1 style="color:#e63946;">Welcome to Nairobi Hospital Disease Prediction System</h1>', unsafe_allow_html=True)
    st.markdown(f'<h3 style="color:#457b9d;">Hello, {st.session_state.username}!</h3>', unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    # Profile section
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image('https://img.icons8.com/color/96/000000/user-male-circle--v2.png', width=80)
    with col2:
        st.markdown(f'<div style="background:#457b9d;color:#fff;padding:1em;border-radius:10px;box-shadow:0 2px 8px #ccc;display:flex;align-items:center;">'
                    f'<b>Username:</b> {st.session_state.username}<br>'
                    f'<b>Role:</b> {get_user_role(st.session_state.username).capitalize()}<br>'
                    f'<b>Login time:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                    '</div>', unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    # Prediction history
    user_preds = get_user_predictions(st.session_state.username)
    total_preds = len(user_preds)
    # --- Modern Stat Cards ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''<div style="background:#e63946;color:#fff;padding:1.2em 1em;border-radius:12px;box-shadow:0 2px 8px #ccc;text-align:center;">
        <span style="font-size:2em;">🩺</span><br><b>Total Predictions</b><br><span style="font-size:2em;">{total_preds}</span></div>''', unsafe_allow_html=True)
    with col2:
        if total_preds > 0:
            df = pd.DataFrame(user_preds)
            disease_counts = df['disease'].value_counts().to_dict()
            most_pred = max(disease_counts, key=disease_counts.get)
            st.markdown(f'''<div style="background:#457b9d;color:#fff;padding:1.2em 1em;border-radius:12px;box-shadow:0 2px 8px #ccc;text-align:center;">
            <span style="font-size:2em;">🏆</span><br><b>Most Predicted Disease</b><br><span style="font-size:1.5em;">{most_pred}</span></div>''', unsafe_allow_html=True)
        else:
            st.markdown(f'''<div style="background:#457b9d;color:#fff;padding:1.2em 1em;border-radius:12px;box-shadow:0 2px 8px #ccc;text-align:center;">
            <span style="font-size:2em;">🏆</span><br><b>Most Predicted Disease</b><br><span style="font-size:1.5em;">-</span></div>''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div style="background:#1d3557;color:#fff;padding:1.2em 1em;border-radius:12px;box-shadow:0 2px 8px #ccc;text-align:center;">
        <span style="font-size:2em;">⏰</span><br><b>Last Prediction</b><br><span style="font-size:1.2em;">{df['timestamp'].max() if total_preds > 0 else '-'}</span></div>''', unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    # --- Charts ---
    if total_preds > 0:
        # Pie chart: predictions by disease
        pie_fig = px.pie(df, names='disease', title='Predictions by Disease', color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(pie_fig, use_container_width=True)
        # Bar chart: predictions over time (by day)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        bar_fig = px.bar(df.groupby('date').size().reset_index(name='count'), x='date', y='count', title='Predictions Over Time', color='count', color_continuous_scale=px.colors.sequential.Blues)
        st.plotly_chart(bar_fig, use_container_width=True)
    # --- Recent Activity Timeline ---
    st.markdown('<h4 style="color:#e63946;">Recent Activity</h4>', unsafe_allow_html=True)
    if total_preds > 0:
        recent = df[['timestamp', 'disease', 'result', 'features']].sort_values('timestamp', ascending=False).head(5)
        for _, row in recent.iterrows():
            st.markdown(f'''<div style="background:#f1faee;padding:0.7em 1em;margin-bottom:0.5em;border-radius:8px;box-shadow:0 1px 4px #ccc;">
            <span style="color:#e63946;font-weight:bold;">{row['timestamp']}</span> — <b>{row['disease']}</b>: <span style="color:#457b9d;">{row['result']}</span><br>
            <span style="font-size:0.9em;color:#333;">Patient: {row['features'].get('Patient Name', '-')}</span>
            </div>''', unsafe_allow_html=True)
    else:
        st.info('No predictions yet. Use the sidebar to make your first prediction!')
    st.stop()

# --- Other Disease Reporting Page ---
if st.session_state.logged_in and selected == 'Other Disease':
    st.title('Report New/Other Disease')
    st.markdown('''<div style="background-color:#f1faee;padding:1em;border-radius:8px;margin-bottom:1em;">
    If a patient presents with a disease not listed in the system, please fill out this form. The admin will be notified and the case will be reviewed for future system updates.
    </div>''', unsafe_allow_html=True)
    patient_name = st.text_input('Patient Name (Other Disease)')
    suspected_disease = st.text_input('Suspected Disease Name')
    symptoms = st.text_area('Symptoms (comma-separated)')
    notes = st.text_area('Additional Notes (optional)')
    if st.button('Submit Other Disease Report'):
        if not patient_name or not suspected_disease or not symptoms:
            st.error('Please fill in all required fields.')
        else:
            report = {
                'doctor': st.session_state.username,
                'patient_name': patient_name,
                'suspected_disease': suspected_disease,
                'symptoms': symptoms,
                'notes': notes,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            log_new_disease_report(report)
            log_notification(f'New disease reported: {suspected_disease} (by Dr. {st.session_state.username})', notif_type='new_disease')
            st.success('Report submitted! The admin will be notified.')
    st.stop()

# --- Admin Page ---
if st.session_state.logged_in and selected == 'Admin':
    import plotly.express as px
    from datetime import datetime
    st.title('Admin Dashboard')
    users = get_all_users()
    user_preds = {u: get_user_predictions(u) for u in users}
    total_users = len(users)
    total_doctors = sum(1 for u in users.values() if u.get('role') == 'doctor')
    total_admins = sum(1 for u in users.values() if u.get('role') == 'admin')
    total_preds = sum(len(p) for p in user_preds.values())
    unverified = [u for u, info in users.items() if info.get('role') == 'doctor' and not info.get('verified', False)]
    new_disease_reports = get_new_disease_reports()
    # --- Modern Stat Cards ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''<div style="background:#e63946;color:#fff;padding:1.2em 1em;border-radius:12px;box-shadow:0 2px 8px #ccc;text-align:center;">
        <span style="font-size:2em;">👥</span><br><b>Total Users</b><br><span style="font-size:2em;">{total_users}</span></div>''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''<div style="background:#457b9d;color:#fff;padding:1.2em 1em;border-radius:12px;box-shadow:0 2px 8px #ccc;text-align:center;">
        <span style="font-size:2em;">🩺</span><br><b>Total Doctors</b><br><span style="font-size:2em;">{total_doctors}</span></div>''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div style="background:#1d3557;color:#fff;padding:1.2em 1em;border-radius:12px;box-shadow:0 2px 8px #ccc;text-align:center;">
        <span style="font-size:2em;">🔒</span><br><b>Unverified</b><br><span style="font-size:2em;">{len(unverified)}</span></div>''', unsafe_allow_html=True)
    with col4:
        st.markdown(f'''<div style="background:#2a9d8f;color:#fff;padding:1.2em 1em;border-radius:12px;box-shadow:0 2px 8px #ccc;text-align:center;">
        <span style="font-size:2em;">📊</span><br><b>Total Predictions</b><br><span style="font-size:2em;">{total_preds}</span></div>''', unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    # --- System-wide Charts ---
    # User roles pie chart
    role_counts = pd.Series([u.get('role', 'doctor') for u in users.values()]).value_counts()
    pie_fig = px.pie(role_counts, names=role_counts.index, values=role_counts.values, title='User Roles', color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(pie_fig, use_container_width=True)
    # Registration trend
    reg_dates = [u.get('registered', '')[:10] for u in users.values() if u.get('registered')]
    if reg_dates:
        reg_df = pd.DataFrame({'date': reg_dates})
        reg_counts = reg_df['date'].value_counts().sort_index().reset_index()
        reg_counts.columns = ['date', 'count']
        reg_fig = px.bar(reg_counts, x='date', y='count', labels={'date':'Date','count':'Registrations'}, title='Registrations Over Time', color='count', color_continuous_scale=px.colors.sequential.Blues)
        st.plotly_chart(reg_fig, use_container_width=True)
    # --- Recent Activity Timeline ---
    st.markdown('<h4 style="color:#e63946;">Recent Activity</h4>', unsafe_allow_html=True)
    notifications = get_notifications()
    if notifications:
        for n in sorted(notifications, key=lambda x: x['timestamp'], reverse=True)[:7]:
            icon = '✅' if n['type'] == 'registration' else ('🆕' if n['type'] == 'new_disease' else '🔔')
            st.markdown(f'''<div style="background:#f1faee;padding:0.7em 1em;margin-bottom:0.5em;border-radius:8px;box-shadow:0 1px 4px #ccc;">
            <span style="color:#e63946;font-weight:bold;">{n['timestamp']}</span> — {icon} {n['message']}
            </div>''', unsafe_allow_html=True)
    else:
        st.info('No recent activity.')
    st.markdown('<hr>', unsafe_allow_html=True)
    # --- Unverified Users: Approve/Resend ---
    st.markdown('<b>Unverified Doctors</b>', unsafe_allow_html=True)
    if unverified:
        for uname in unverified:
            uinfo = users[uname]
            st.markdown(f'''<div style="background:#fff3cd;padding:1em;border-radius:8px;margin-bottom:0.5em;box-shadow:0 1px 4px #ccc;">
            <b>{uname}</b> | Email: {uinfo.get('email','-')} | Registered: {uinfo.get('registered','-')}<br>
            <span style="color:#e63946;">Not verified</span>
            </div>''', unsafe_allow_html=True)
            colA, colB = st.columns([1,1])
            with colA:
                if st.button(f'Approve {uname}', key=f'approve_{uname}'):
                    users[uname]['verified'] = True
                    save_users(users)
                    st.success(f'Doctor {uname} approved!')
                    st.rerun()
            with colB:
                if st.button(f'Resend Verification Email to {uname}', key=f'resend_{uname}'):
                    token = users[uname].get('token')
                    send_verification_email(uinfo.get('email',''), token)
                    st.success(f'Verification email resent to {uname}!')
    else:
        st.info('No unverified doctors.')
    st.markdown('<hr>', unsafe_allow_html=True)
    # --- All Users Table ---
    st.markdown('<b>All Users</b>', unsafe_allow_html=True)
    user_data = []
    for uname, uinfo in users.items():
        user_data.append({
            'Username': uname,
            'Role': uinfo.get('role', 'doctor'),
            'Email': uinfo.get('email', ''),
            'Verified': uinfo.get('verified', False),
            'Registered': uinfo.get('registered', ''),
            'Predictions': len(get_user_predictions(uname)),
            'Last Login': max([s['timestamp'] for s in get_user_sessions(uname) if s['event']=='login'], default='-')
        })
    df_users = pd.DataFrame(user_data)
    st.dataframe(df_users, use_container_width=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    # --- New Disease Reports Table ---
    st.markdown('<b>New Disease Reports</b>', unsafe_allow_html=True)
    if new_disease_reports:
        df_newd = pd.DataFrame(new_disease_reports)
        st.dataframe(df_newd.sort_values('timestamp', ascending=False), use_container_width=True)
        csv = df_newd.to_csv(index=False).encode('utf-8')
        st.download_button('Download New Disease Reports (CSV)', csv, 'new_disease_reports.csv', 'text/csv')
    else:
        st.info('No new disease reports yet.')
    st.markdown('<hr>', unsafe_allow_html=True)
    # --- All Predictions Table ---
    st.markdown('<b>All Predictions (System-wide)</b>', unsafe_allow_html=True)
    all_preds = []
    for uname in users:
        for pred in get_user_predictions(uname):
            all_preds.append({'User': uname, **pred})
    if all_preds:
        df_all = pd.DataFrame(all_preds)
        st.dataframe(df_all, use_container_width=True)
        csv = df_all.to_csv(index=False).encode('utf-8')
        st.download_button('Download All Predictions (CSV)', csv, 'all_predictions.csv', 'text/csv')
    else:
        st.info('No predictions in the system yet.')
    st.stop()

# --- Reports Page ---
if st.session_state.logged_in and selected == 'Reports':
    st.title('Reports & History')
    st.markdown('<b>Filter and export your prediction history.</b>', unsafe_allow_html=True)
    user_preds = get_user_predictions(st.session_state.username)
    if user_preds:
        df = pd.DataFrame(user_preds)
        # Filters
        patient_filter = st.text_input('Filter by Patient Name')
        disease_filter = st.selectbox('Filter by Disease', ['All'] + sorted(df['disease'].unique().tolist()))
        date_filter = st.date_input('Filter by Date', [])
        filtered = df.copy()
        if patient_filter:
            filtered = filtered[filtered['features'].apply(lambda f: patient_filter.lower() in f.get('Patient Name', '').lower())]
        if disease_filter != 'All':
            filtered = filtered[filtered['disease'] == disease_filter]
        if date_filter:
            filtered = filtered[filtered['timestamp'].str.startswith(str(date_filter))]
        st.dataframe(filtered[['timestamp', 'disease', 'result', 'features']], use_container_width=True)
        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button('Download Filtered Report (CSV)', csv, 'filtered_report.csv', 'text/csv')
    else:
        st.info('No predictions yet.')
    st.stop()

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root, then into models folder
models_dir = os.path.join(os.path.dirname(current_dir), 'models')

# loading the saved models
diabetes_model = pickle.load(open(os.path.join(models_dir, 'diabetes_model.sav'), 'rb'))
heart_disease_model = pickle.load(open(os.path.join(models_dir, 'heart_disease_model.sav'), 'rb'))
parkinsons_model = pickle.load(open(os.path.join(models_dir, 'parkinsons_model.sav'), 'rb'))

try:
    malaria_model = pickle.load(open(os.path.join(models_dir, 'malaria_model.sav'), 'rb'))
except Exception:
    malaria_model = None
try:
    typhoid_model = pickle.load(open(os.path.join(models_dir, 'typhoid_model.sav'), 'rb'))
except Exception:
    typhoid_model = None
try:
    aids_model = pickle.load(open(os.path.join(models_dir, 'aids_model.sav'), 'rb'))
except Exception:
    aids_model = None
    
    
# Diabetes Prediction Page
if (selected == 'Diabetes Prediction'):
    
    # page title
    st.title('Diabetes Prediction using ML')
    
    
    # getting the input data from the user
    patient_name = st.text_input('Patient Name')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        Pregnancies = st.text_input('Number of Pregnancies')
        
    with col2:
        Glucose = st.text_input('Glucose Level')
    
    with col3:
        BloodPressure = st.text_input('Blood Pressure value')
    
    with col1:
        SkinThickness = st.text_input('Skin Thickness value')
    
    with col2:
        Insulin = st.text_input('Insulin Level')
    
    with col3:
        BMI = st.text_input('BMI value')
    
    with col1:
        DiabetesPedigreeFunction = st.text_input('Diabetes Pedigree Function value')
    
    with col2:
        Age = st.text_input('Age of the Person')
    
    
    # code for Prediction
    diab_diagnosis = ''
    
    # creating a button for Prediction
    
    if st.button('Diabetes Test Result'):
        try:
            input_values = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]
            if any(v.strip() == '' for v in input_values) or patient_name.strip() == '':
                st.error('Please fill in all fields including patient name with valid numbers.')
            else:
                input_floats = [float(v) for v in input_values]
                diab_prediction = diabetes_model.predict([input_floats])
                if (diab_prediction[0] == 1):
                    diab_diagnosis = 'The person is diabetic'
                    st.success(diab_diagnosis)
                    st.markdown('**Suggested Medicines:**')
                    for med in MEDICINE_SUGGESTIONS['Diabetes']:
                        st.markdown(f'- {med}')
                else:
                    diab_diagnosis = 'The person is not diabetic'
                    st.success(diab_diagnosis)
                    st.info('No medication needed. Please consult a doctor for further advice.')
                log_prediction(st.session_state.username, 'Diabetes', diab_diagnosis, {
                    'Patient Name': patient_name,
                    'Pregnancies': Pregnancies, 'Glucose': Glucose, 'BloodPressure': BloodPressure, 'SkinThickness': SkinThickness, 'Insulin': Insulin, 'BMI': BMI, 'DiabetesPedigreeFunction': DiabetesPedigreeFunction, 'Age': Age
                })
        except ValueError:
            st.error('Please enter valid numbers for all fields.')




# Heart Disease Prediction Page
if (selected == 'Heart Disease Prediction'):
    
    # page title
    st.title('Heart Disease Prediction using ML')
    
    patient_name = st.text_input('Patient Name')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age = st.number_input('Age (years)', min_value=1, max_value=120, value=30)
    with col2:
        sex = st.selectbox('Sex', options=[0, 1], format_func=lambda x: 'Female' if x == 0 else 'Male')
    with col3:
        cp = st.selectbox('Chest Pain Type', options=[0, 1, 2, 3],
            format_func=lambda x: ['Typical Angina', 'Atypical Angina', 'Non-anginal Pain', 'Asymptomatic'][x])
    with col1:
        trestbps = st.number_input('Resting Blood Pressure (mm Hg)', min_value=50, max_value=250, value=120)
    with col2:
        chol = st.number_input('Serum Cholesterol (mg/dl)', min_value=100, max_value=600, value=200)
    with col3:
        fbs = st.selectbox('Fasting Blood Sugar > 120 mg/dl', options=[0, 1], format_func=lambda x: 'No' if x == 0 else 'Yes')
    with col1:
        restecg = st.selectbox('Resting Electrocardiographic Results', options=[0, 1, 2],
            format_func=lambda x: ['Normal', 'ST-T wave abnormality', 'Left ventricular hypertrophy'][x])
    with col2:
        thalach = st.number_input('Maximum Heart Rate Achieved', min_value=60, max_value=250, value=150)
    with col3:
        exang = st.selectbox('Exercise Induced Angina', options=[0, 1], format_func=lambda x: 'No' if x == 0 else 'Yes')
    with col1:
        oldpeak = st.number_input('ST Depression Induced by Exercise (oldpeak)', min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    with col2:
        slope = st.selectbox('Slope of the Peak Exercise ST Segment', options=[0, 1, 2],
            format_func=lambda x: ['Upsloping', 'Flat', 'Downsloping'][x])
    with col3:
        ca = st.number_input('Number of Major Vessels Colored by Fluoroscopy (0-3)', min_value=0, max_value=3, value=0)
    with col1:
        thal = st.selectbox('Thal', options=[1, 2, 3],
            format_func=lambda x: {1: 'Normal', 2: 'Fixed Defect', 3: 'Reversible Defect'}[x])
     
    # code for Prediction
    heart_diagnosis = ''
    
    # creating a button for Prediction
    if st.button('Heart Disease Test Result'):
        try:
            input_values = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
            if patient_name.strip() == '' or any(str(v).strip() == '' for v in input_values):
                st.error('Please fill in all fields including patient name with valid numbers.')
            else:
                input_floats = [float(v) for v in input_values]
                heart_prediction = heart_disease_model.predict([input_floats])
                if (heart_prediction[0] == 1):
                    heart_diagnosis = 'The person is having heart disease'
                    st.success(heart_diagnosis)
                    st.markdown('**Suggested Medicines:**')
                    for med in MEDICINE_SUGGESTIONS['Heart Disease']:
                        st.markdown(f'- {med}')
                else:
                    heart_diagnosis = 'The person does not have any heart disease'
                    st.success(heart_diagnosis)
                    st.info('No medication needed. Please consult a doctor for further advice.')
                log_prediction(st.session_state.username, 'Heart Disease', heart_diagnosis, {
                    'Patient Name': patient_name,
                    'Age': age, 'Sex': sex, 'Chest Pain Type': cp, 'Resting Blood Pressure': trestbps, 'Serum Cholesterol': chol, 'Fasting Blood Sugar': fbs, 'Resting ECG': restecg, 'Max Heart Rate': thalach, 'Exercise Induced Angina': exang, 'ST Depression': oldpeak, 'Slope': slope, 'Number of Major Vessels': ca, 'Thal': thal
                })
        except ValueError:
            st.error('Please enter valid numbers for all fields.')
        
    
    

# Parkinson's Prediction Page
if (selected == "Parkinsons Prediction"):
    
    # page title
    st.title("Parkinson's Disease Prediction using ML")
    st.markdown('''<div style="background-color:#f1faee;padding:1em;border-radius:8px;margin-bottom:1em;">
    Please fill in all fields with valid numbers. All features are required for accurate prediction.
    </div>''', unsafe_allow_html=True)
    patient_name = st.text_input('Patient Name')
    col1, col2, col3, col4, col5 = st.columns(5)  
    with col1:
        fo = st.text_input('MDVP:Fo(Hz)')
        RAP = st.text_input('MDVP:RAP')
        APQ3 = st.text_input('Shimmer:APQ3')
        HNR = st.text_input('HNR')
        D2 = st.text_input('D2')
    with col2:
        fhi = st.text_input('MDVP:Fhi(Hz)')
        PPQ = st.text_input('MDVP:PPQ')
        APQ5 = st.text_input('Shimmer:APQ5')
        RPDE = st.text_input('RPDE')
        PPE = st.text_input('PPE')
    with col3:
        flo = st.text_input('MDVP:Flo(Hz)')
        DDP = st.text_input('Jitter:DDP')
        APQ = st.text_input('MDVP:APQ')
        DFA = st.text_input('DFA')
    with col4:
        Jitter_percent = st.text_input('MDVP:Jitter(%)')
        Shimmer = st.text_input('MDVP:Shimmer')
        DDA = st.text_input('Shimmer:DDA')
        spread1 = st.text_input('spread1')
    with col5:
        Jitter_Abs = st.text_input('MDVP:Jitter(Abs)')
        Shimmer_dB = st.text_input('MDVP:Shimmer(dB)')
        NHR = st.text_input('NHR')
        spread2 = st.text_input('spread2')
    parkinsons_diagnosis = ''
    if st.button("Parkinson's Test Result"):
        try:
            input_values = [fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP, Shimmer, Shimmer_dB, APQ3, APQ5, APQ, DDA, NHR, HNR, RPDE, DFA, spread1, spread2, D2, PPE]
            if any(v.strip() == '' for v in input_values) or patient_name.strip() == '':
                st.error('Please fill in all fields including patient name with valid numbers.')
            else:
                input_floats = [float(v) for v in input_values]
                parkinsons_prediction = parkinsons_model.predict([input_floats])
                if (parkinsons_prediction[0] == 1):
                    parkinsons_diagnosis = "The person has Parkinson's disease"
                    st.success(parkinsons_diagnosis)
                    st.markdown('**Suggested Medicines:**')
                    for med in MEDICINE_SUGGESTIONS['Parkinsons']:
                        st.markdown(f'- {med}')
                else:
                    parkinsons_diagnosis = "The person does not have Parkinson's disease"
                    st.success(parkinsons_diagnosis)
                    st.info('No medication needed. Please consult a doctor for further advice.')
                log_prediction(st.session_state.username, 'Parkinsons', parkinsons_diagnosis, {
                    'Patient Name': patient_name,
                    'MDVP:Fo(Hz)': fo, 'MDVP:Fhi(Hz)': fhi, 'MDVP:Flo(Hz)': flo, 'MDVP:Jitter(%)': Jitter_percent, 'MDVP:Jitter(Abs)': Jitter_Abs, 'MDVP:RAP': RAP, 'MDVP:PPQ': PPQ, 'Jitter:DDP': DDP, 'MDVP:Shimmer': Shimmer, 'MDVP:Shimmer(dB)': Shimmer_dB, 'Shimmer:APQ3': APQ3, 'Shimmer:APQ5': APQ5, 'MDVP:APQ': APQ, 'Shimmer:DDA': DDA, 'NHR': NHR, 'HNR': HNR, 'RPDE': RPDE, 'DFA': DFA, 'spread1': spread1, 'spread2': spread2, 'D2': D2, 'PPE': PPE
                })
        except ValueError:
            st.error('Please enter valid numbers for all fields.')
    st.success(parkinsons_diagnosis)

# Malaria Prediction Page
if selected == 'Malaria Prediction':
    st.title('Malaria Prediction using ML')
    patient_name = st.text_input('Patient Name')
    col1, col2, col3 = st.columns(3)
    with col1:
        fever = st.selectbox('Fever', ['No', 'Yes'])
        chills = st.selectbox('Chills', ['No', 'Yes'])
        headache = st.selectbox('Headache', ['No', 'Yes'])
    with col2:
        nausea = st.selectbox('Nausea/Vomiting', ['No', 'Yes'])
        muscle_pain = st.selectbox('Muscle Pain', ['No', 'Yes'])
        fatigue = st.selectbox('Fatigue', ['No', 'Yes'])
    with col3:
        travel = st.selectbox('Recent Travel to Malaria Area', ['No', 'Yes'])
        blood_test = st.selectbox('Positive Malaria Blood Test', ['No', 'Yes'])
    malaria_diagnosis = ''
    if st.button('Malaria Test Result'):
        if malaria_model:
            malaria_input = [int(fever=='Yes'), int(chills=='Yes'), int(headache=='Yes'), int(nausea=='Yes'), int(muscle_pain=='Yes'), int(fatigue=='Yes'), int(travel=='Yes'), int(blood_test=='Yes')]
            if patient_name.strip() == '' or any(str(v).strip() == '' for v in malaria_input):
                st.error('Please fill in all fields including patient name.')
            else:
                malaria_prediction = malaria_model.predict([malaria_input])
                if malaria_prediction[0] == 1:
                    malaria_diagnosis = 'The person is likely to have Malaria.'
                    st.success(malaria_diagnosis)
                    st.markdown('**Suggested Medicines:**')
                    for med in MEDICINE_SUGGESTIONS['Malaria']:
                        st.markdown(f'- {med}')
                else:
                    malaria_diagnosis = 'The person is unlikely to have Malaria.'
                    st.success(malaria_diagnosis)
                    st.info('No medication needed. Please consult a doctor for further advice.')
                log_prediction(st.session_state.username, 'Malaria', malaria_diagnosis, {
                    'Patient Name': patient_name,
                    'Fever': fever, 'Chills': chills, 'Headache': headache, 'Nausea/Vomiting': nausea, 'Muscle Pain': muscle_pain, 'Fatigue': fatigue, 'Recent Travel to Malaria Area': travel, 'Positive Malaria Blood Test': blood_test
                })
        else:
            malaria_diagnosis = 'Malaria prediction model not available.'
            st.error(malaria_diagnosis)
    st.success(malaria_diagnosis)
    if not malaria_model:
        st.warning('Malaria model file not found. Please add malaria_model.sav to the models directory.')
# Typhoid Prediction Page
if selected == 'Typhoid Prediction':
    st.title('Typhoid Prediction using ML')
    patient_name = st.text_input('Patient Name')
    col1, col2, col3 = st.columns(3)
    with col1:
        fever = st.selectbox('Prolonged Fever', ['No', 'Yes'], key='typhoid_fever')
        abdominal_pain = st.selectbox('Abdominal Pain', ['No', 'Yes'])
        headache = st.selectbox('Headache', ['No', 'Yes'], key='typhoid_headache')
    with col2:
        diarrhea = st.selectbox('Diarrhea', ['No', 'Yes'])
        constipation = st.selectbox('Constipation', ['No', 'Yes'])
        rash = st.selectbox('Rose Spots (Rash)', ['No', 'Yes'])
    with col3:
        weakness = st.selectbox('Weakness', ['No', 'Yes'])
        appetite = st.selectbox('Loss of Appetite', ['No', 'Yes'])
        blood_test = st.selectbox('Positive Typhoid Blood/Stool Test', ['No', 'Yes'])
    typhoid_diagnosis = ''
    if st.button('Typhoid Test Result'):
        if typhoid_model:
            typhoid_input = [int(fever=='Yes'), int(abdominal_pain=='Yes'), int(headache=='Yes'), int(diarrhea=='Yes'), int(constipation=='Yes'), int(rash=='Yes'), int(weakness=='Yes'), int(appetite=='Yes'), int(blood_test=='Yes')]
            if patient_name.strip() == '' or any(str(v).strip() == '' for v in typhoid_input):
                st.error('Please fill in all fields including patient name.')
            else:
                typhoid_prediction = typhoid_model.predict([typhoid_input])
                if typhoid_prediction[0] == 1:
                    typhoid_diagnosis = 'The person is likely to have Typhoid.'
                    st.success(typhoid_diagnosis)
                    st.markdown('**Suggested Medicines:**')
                    for med in MEDICINE_SUGGESTIONS['Typhoid']:
                        st.markdown(f'- {med}')
                else:
                    typhoid_diagnosis = 'The person is unlikely to have Typhoid.'
                    st.success(typhoid_diagnosis)
                    st.info('No medication needed. Please consult a doctor for further advice.')
                log_prediction(st.session_state.username, 'Typhoid', typhoid_diagnosis, {
                    'Patient Name': patient_name,
                    'Prolonged Fever': fever, 'Abdominal Pain': abdominal_pain, 'Headache': headache, 'Diarrhea': diarrhea, 'Constipation': constipation, 'Rose Spots (Rash)': rash, 'Weakness': weakness, 'Loss of Appetite': appetite, 'Positive Typhoid Blood/Stool Test': blood_test
                })
        else:
            typhoid_diagnosis = 'Typhoid prediction model not available.'
            st.error(typhoid_diagnosis)
    st.success(typhoid_diagnosis)
    if not typhoid_model:
        st.warning('Typhoid model file not found. Please add typhoid_model.sav to the models directory.')
# AIDS Prediction Page
if selected == 'AIDS Prediction':
    st.title('AIDS (HIV) Prediction using ML')
    patient_name = st.text_input('Patient Name')
    col1, col2, col3 = st.columns(3)
    with col1:
        weight_loss = st.selectbox('Unexplained Weight Loss', ['No', 'Yes'])
        fever = st.selectbox('Fever', ['No', 'Yes'], key='aids_fever')
        night_sweats = st.selectbox('Night Sweats', ['No', 'Yes'])
    with col2:
        fatigue = st.selectbox('Fatigue', ['No', 'Yes'], key='aids_fatigue')
        lymph_nodes = st.selectbox('Swollen Lymph Nodes', ['No', 'Yes'])
        risky_behavior = st.selectbox('History of Risky Behavior', ['No', 'Yes'])
    with col3:
        hiv_test = st.selectbox('Positive HIV Test', ['No', 'Yes'])
    aids_diagnosis = ''
    if st.button('AIDS Test Result'):
        if aids_model:
            aids_input = [int(weight_loss=='Yes'), int(fever=='Yes'), int(night_sweats=='Yes'), int(fatigue=='Yes'), int(lymph_nodes=='Yes'), int(risky_behavior=='Yes'), int(hiv_test=='Yes')]
            if patient_name.strip() == '' or any(str(v).strip() == '' for v in aids_input):
                st.error('Please fill in all fields including patient name.')
            else:
                aids_prediction = aids_model.predict([aids_input])
                if aids_prediction[0] == 1:
                    aids_diagnosis = 'The person is likely to have AIDS (HIV positive).'
                    st.success(aids_diagnosis)
                    st.markdown('**Suggested Medicines:**')
                    for med in MEDICINE_SUGGESTIONS['AIDS']:
                        st.markdown(f'- {med}')
                else:
                    aids_diagnosis = 'The person is unlikely to have AIDS (HIV negative).'
                    st.success(aids_diagnosis)
                    st.info('No medication needed. Please consult a doctor for further advice.')
                log_prediction(st.session_state.username, 'AIDS', aids_diagnosis, {
                    'Patient Name': patient_name,
                    'Unexplained Weight Loss': weight_loss, 'Fever': fever, 'Night Sweats': night_sweats, 'Fatigue': fatigue, 'Swollen Lymph Nodes': lymph_nodes, 'History of Risky Behavior': risky_behavior, 'Positive HIV Test': hiv_test
                })
        else:
            aids_diagnosis = 'AIDS prediction model not available.'
            st.error(aids_diagnosis)

# About Page
if selected == 'About':
    st.title('About the Project')
    st.markdown('''
**School of Technology**  
**Bachelor of Science in Data Science**  
**Project:** Nairobi Hospital Disease Prediction System  
**Student:** Cherotich Laura  
**Reg No:** 23/08450  
**Supervisor:** Ernest Madara

---

### Project Summary
This system uses machine learning to predict diseases (Diabetes, Heart Disease, Parkinson's Disease) based on patient symptoms. It is designed to support healthcare workers at Nairobi Hospital by providing quick, data-driven diagnostic support.

#### Objectives
- Collect and prepare patient data
- Identify patterns between symptoms and diseases
- Train/test ML models for prediction
- Build an interactive interface for symptom entry and predictions
- Evaluate system accuracy and usefulness

#### Methodology
- Data collection and cleaning
- Model development and testing
- User interface building
- Final integration, testing, and documentation

#### References
- Shrestha & Chatterjee (2019)
- Srivastava & Singh (2022)
- Jindal et al. (2021)
- Heller et al. (1984)
- Cáceres & Paccanaro (2019)
    ''')