
"""
Complete Disease Prediction System with Enhanced Email Verication
Enhanced with email verification by: Assistant
"""

import hashlib
import streamlit as st
import pickle
import os
from streamlit_option_menu import option_menu
import datetime
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
ADMIN_EMAIL = "adnisdevelopers@gmail.com"
ADMIN_PASSWORD = "zvcoleswwqtooktq"  # Replace with your Gmail App Password

NOTIFICATIONS_FILE = 'notifications.pkl'
NEW_DISEASES_FILE = 'new_diseases.pkl'
SESSIONS_FILE = 'sessions.pkl'
SESSION_COOKIE = 'dps_session_id'
VERIFICATION_REQUESTS_FILE = 'verification_requests.pkl'

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

def log_verification_request(username, email, request_type='manual'):
    """Log verification requests from users"""
    requests = []
    if os.path.exists(VERIFICATION_REQUESTS_FILE):
        with open(VERIFICATION_REQUESTS_FILE, 'rb') as f:
            requests = pickle.load(f)

    requests.append({
        'username': username,
        'email': email,
        'request_type': request_type,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'pending'
    })

    with open(VERIFICATION_REQUESTS_FILE, 'wb') as f:
        pickle.dump(requests, f)

def get_verification_requests():
    if not os.path.exists(VERIFICATION_REQUESTS_FILE):
        return []
    with open(VERIFICATION_REQUESTS_FILE, 'rb') as f:
        return pickle.load(f)

def update_verification_request_status(username, status):
    """Update status of verification request"""
    if not os.path.exists(VERIFICATION_REQUESTS_FILE):
        return

    with open(VERIFICATION_REQUESTS_FILE, 'rb') as f:
        requests = pickle.load(f)

    for request in requests:
        if request['username'] == username and request['status'] == 'pending':
            request['status'] = status
            break

    with open(VERIFICATION_REQUESTS_FILE, 'wb') as f:
        pickle.dump(requests, f)

def send_email(to_email, subject, body, is_html=False):
    """Send email using Gmail SMTP"""
    try:
        # Skip email sending if password not configured
        if ADMIN_PASSWORD == "your_app_password_here":
            st.info(f"Email would be sent to {to_email}: {subject}")
            return True

        # Create message
        msg = MIMEMultipart()
        msg['From'] = ADMIN_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body to email
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable TLS encryption
        server.login(ADMIN_EMAIL, ADMIN_PASSWORD)

        # Send email
        text = msg.as_string()
        server.sendmail(ADMIN_EMAIL, to_email, text)
        server.quit()

        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def send_verification_email(email, username, token):
    """Send verification email to new doctor"""
    subject = "Account Verification - Nairobi Hospital Disease Prediction System"

    body = f"""
    Dear Dr. {username},

    Welcome to the Nairobi Hospital Disease Prediction System!

    Your account has been created and is pending verification. Our admin team will review your registration and approve your account within 24-48 hours.

    Account Details:
    - Username: {username}
    - Email: {email}
    - Registration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    - Verification Token: {token[:10]}...

    Once your account is approved, you will receive another email confirmation and can begin using the system.

    If you have any questions or need immediate assistance, please contact our support team.

    Best regards,
    Nairobi Hospital DPS Team
    Email: {ADMIN_EMAIL}

    Note: This is an automated message. Please do not reply to this email.
    """

    return send_email(email, subject, body)

def send_admin_notification_new_user(username, email):
    """Send notification to admin about new user registration"""
    subject = f"New Doctor Registration - {username}"

    body = f"""
    A new doctor has registered for the Disease Prediction System:

    Username: {username}
    Email: {email}
    Registration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    Please log into the admin panel to review and approve this registration.

    Admin Panel: Access through the DPS system

    Best regards,
    DPS System
    """

    return send_email(ADMIN_EMAIL, subject, body)

def send_admin_notification_new_disease(disease_name, doctor_name, patient_name):
    """Send notification to admin about new disease report"""
    subject = f"New Disease Report - {disease_name}"

    body = f"""
    A new disease has been reported in the system:

    Disease: {disease_name}
    Reported by: Dr. {doctor_name}
    Patient: {patient_name}
    Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    Please log into the admin panel to review this report and consider adding it to the system.

    Admin Panel: Access through the DPS system

    Best regards,
    DPS System
    """

    return send_email(ADMIN_EMAIL, subject, body)

def send_admin_verification_request(username, email):
    """Send verification request to admin from user"""
    subject = f"Verification Request - {username}"

    body = f"""
    A doctor is requesting account verification:

    Username: {username}
    Email: {email}
    Request Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    The user has not received verification and is requesting manual approval.

    Please log into the admin panel to verify this account.

    Admin Panel: Access through the DPS system

    Best regards,
    DPS System
    """

    return send_email(ADMIN_EMAIL, subject, body)

def send_approval_email(email, username):
    """Send approval confirmation to doctor"""
    subject = "Account Approved - Nairobi Hospital Disease Prediction System"

    body = f"""
    Dear Dr. {username},

    Great news! Your account has been approved and verified.

    You can now log into the Disease Prediction System using your credentials:
    - Username: {username}
    - Email: {email}

    System Features Available:
    - Disease Prediction Tools (Diabetes, Heart Disease, Parkinson's, etc.)
    - Patient Management
    - Reports and Analytics
    - New Disease Reporting

    Please log in at your earliest convenience and start using the system.

    If you experience any issues, please contact our support team.

    Best regards,
    Nairobi Hospital DPS Team
    Email: {ADMIN_EMAIL}

    Welcome aboard!
    """

    return send_email(email, subject, body)

def send_verification_link_email(email, username, token):
    """Send verification link email to new user"""
    verification_url = f"http://20.109.17.234:8501/?verify={token}"

    subject = "Verify Your Account - Nairobi Hospital Disease Prediction System"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
            <div style="background-color: #e63946; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>🏥 Nairobi Hospital DPS</h1>
                <h2>Account Verification Required</h2>
            </div>

            <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <p>Dear Dr. <strong>{username}</strong>,</p>

                <p>Thank you for registering with the Nairobi Hospital Disease Prediction System!</p>

                <p>To complete your registration, please click the verification link below:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}"
                       style="background-color: #457b9d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        ✅ Verify My Account
                    </a>
                </div>

                <p><strong>Or copy this link:</strong><br>
                <a href="{verification_url}" style="color: #457b9d;">{verification_url}</a></p>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4>📋 Account Details:</h4>
                    <ul>
                        <li><strong>Username:</strong> {username}</li>
                        <li><strong>Email:</strong> {email}</li>
                        <li><strong>Registration Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                    </ul>
                </div>

                <p><strong>⚠️ Important Notes:</strong></p>
                <ul>
                    <li>This verification link will expire in 24 hours</li>
                    <li><strong>Option 1:</strong> Click the verification link above to verify your email</li>
                    <li><strong>Option 2:</strong> If you cannot verify via this link or don't receive this email, contact admin at {ADMIN_EMAIL} for manual approval</li>
                    <li>Your account will be reviewed by admin after email verification</li>
                    <li>You will receive an approval email once admin approves your account</li>
                </ul>

                <p>If you have any questions, please contact our support team.</p>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666;">
                    <p>Best regards,<br>
                    <strong>Nairobi Hospital DPS Team</strong><br>
                    Email: {ADMIN_EMAIL}</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(email, subject, html_body, is_html=True)

def send_daily_report_to_admin():
    """Send daily report to admin with all predictions and user statistics"""
    users = get_all_users()
    all_predictions = load_predictions()

    # Calculate statistics
    total_users = len(users)
    total_doctors = sum(1 for u in users.values() if u.get('role') == 'doctor')
    total_admins = sum(1 for u in users.values() if u.get('role') == 'admin')
    total_predictions = sum(len(preds) for preds in all_predictions.values())

    # Get predictions from last 24 hours
    yesterday = datetime.now() - timedelta(hours=24)
    recent_predictions = []

    for username, predictions in all_predictions.items():
        for pred in predictions:
            pred_time = datetime.strptime(pred['timestamp'], '%Y-%m-%d %H:%M:%S')
            if pred_time >= yesterday:
                recent_predictions.append({
                    'username': username,
                    'disease': pred['disease'],
                    'result': pred['result'],
                    'timestamp': pred['timestamp'],
                    'patient': pred['features'].get('Patient Name', 'N/A') if isinstance(pred['features'], dict) else 'N/A'
                })

    subject = f"Daily Report - Nairobi Hospital DPS ({datetime.now().strftime('%Y-%m-%d')})"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
            <div style="background-color: #e63946; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>📊 Daily System Report</h1>
                <h2>Nairobi Hospital Disease Prediction System</h2>
                <p>Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">

                <h3>📈 System Statistics</h3>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0;">
                    <div style="background-color: #e63946; color: white; padding: 15px; border-radius: 8px; text-align: center;">
                        <h4>Total Users</h4>
                        <p style="font-size: 24px; font-weight: bold;">{total_users}</p>
                    </div>
                    <div style="background-color: #457b9d; color: white; padding: 15px; border-radius: 8px; text-align: center;">
                        <h4>Total Doctors</h4>
                        <p style="font-size: 24px; font-weight: bold;">{total_doctors}</p>
                    </div>
                    <div style="background-color: #1d3557; color: white; padding: 15px; border-radius: 8px; text-align: center;">
                        <h4>Total Predictions</h4>
                        <p style="font-size: 24px; font-weight: bold;">{total_predictions}</p>
                    </div>
                    <div style="background-color: #2a9d8f; color: white; padding: 15px; border-radius: 8px; text-align: center;">
                        <h4>Recent Predictions</h4>
                        <p style="font-size: 24px; font-weight: bold;">{len(recent_predictions)}</p>
                    </div>
                </div>

                <h3>👥 User Summary</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f8f9fa;">
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Username</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Role</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Email</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Status</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Predictions</th>
                    </tr>
    """

    for username, user_info in users.items():
        predictions_count = len(all_predictions.get(username, []))
        if user_info.get('verified', False):
            status = "✅ Approved"
        elif user_info.get('email_verified', False):
            status = "📧 Email Verified (Pending Admin)"
        else:
            status = "❌ Not Verified"
        html_body += f"""
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 12px;">{username}</td>
                        <td style="border: 1px solid #ddd; padding: 12px;">{user_info.get('role', 'doctor').title()}</td>
                        <td style="border: 1px solid #ddd; padding: 12px;">{user_info.get('email', 'N/A')}</td>
                        <td style="border: 1px solid #ddd; padding: 12px;">{status}</td>
                        <td style="border: 1px solid #ddd; padding: 12px;">{predictions_count}</td>
                    </tr>
        """

    html_body += f"""
                </table>

                <h3>🩺 Recent Predictions (Last 24 Hours)</h3>
    """

    if recent_predictions:
        html_body += """
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f8f9fa;">
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Doctor</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Disease</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Result</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Patient</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Time</th>
                    </tr>
        """

        for pred in recent_predictions:
            html_body += f"""
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 12px;">{pred['username']}</td>
                        <td style="border: 1px solid #ddd; padding: 12px;">{pred['disease']}</td>
                        <td style="border: 1px solid #ddd; padding: 12px;">{pred['result']}</td>
                        <td style="border: 1px solid #ddd; padding: 12px;">{pred['patient']}</td>
                        <td style="border: 1px solid #ddd; padding: 12px;">{pred['timestamp']}</td>
                    </tr>
            """

        html_body += "</table>"
    else:
        html_body += "<p>No predictions made in the last 24 hours.</p>"

    html_body += f"""
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666;">
                    <p>This is an automated daily report from the Nairobi Hospital DPS system.</p>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(ADMIN_EMAIL, subject, html_body, is_html=True)

def send_announcement_to_doctors(announcement_title, announcement_content, admin_username):
    """Send announcement to all verified doctors"""
    users = get_all_users()
    doctor_emails = []

    for username, user_info in users.items():
        if user_info.get('role') == 'doctor' and user_info.get('verified', False) and user_info.get('email'):
            # Validate email format
            email = user_info['email']
            if '@' in email and '.' in email and len(email) > 5:
                doctor_emails.append(email)

    if not doctor_emails:
        return False

    subject = f"Announcement: {announcement_title} - Nairobi Hospital DPS"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
            <div style="background-color: #e63946; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>📢 Important Announcement</h1>
                <h2>Nairobi Hospital Disease Prediction System</h2>
            </div>

            <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3>{announcement_title}</h3>

                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #457b9d;">
                    {announcement_content.replace(chr(10), '<br>')}
                </div>

                <p><strong>From:</strong> Admin {admin_username}</p>
                <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666;">
                    <p>This is an official announcement from the Nairobi Hospital DPS system.</p>
                    <p>If you have any questions, please contact admin at {ADMIN_EMAIL}</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Send to each doctor
    success_count = 0
    for email in doctor_emails:
        if send_email(email, subject, html_body, is_html=True):
            success_count += 1

    return success_count

def send_verification_reminder_email(email, username):
    """Send reminder email to unverified users"""
    subject = "Account Verification Reminder - Nairobi Hospital DPS"

    body = f"""
    Dear Dr. {username},

    This is a reminder that your account is still pending verification.

    Account Details:
    - Username: {username}
    - Email: {email}
    - Registration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    Please contact admin at {ADMIN_EMAIL} if you need assistance with verification.

    Best regards,
    Nairobi Hospital DPS Team
    """

    return send_email(email, subject, body)

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

    # Generate verification token
    token = secrets.token_urlsafe(32)

    users[username] = {
        'password': hash_password(password),
        'role': role,
        'registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'email': email,
        'verified': True if role == 'admin' else False,
        'token': token,
        'verification_sent': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_users(users)

    # Send verification link email to user
    if role == 'doctor' and email:
        send_verification_link_email(email, username, token)
        # Notify admin about new registration
        send_admin_notification_new_user(username, email)
        log_notification(f'New doctor registration: {username} - Verification link email sent', notif_type='registration')

    return True

def authenticate_user(username, password):
    users = load_users()
    if username not in users:
        return False
    if users[username]['password'] != hash_password(password):
        return False
    # Check if doctor is verified
    if users[username].get('role') == 'doctor' and not users[username].get('verified', False):
        return 'unverified'
    return True

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

def verify_user_account(username):
    """Verify a user account and send approval email"""
    users = load_users()
    if username in users:
        users[username]['verified'] = True
        users[username]['verified_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_users(users)

        # Send approval email
        email = users[username].get('email')
        if email:
            send_approval_email(email, username)

        # Update verification request status
        update_verification_request_status(username, 'approved')

        return True
    return False

def verify_user_by_token(token):
    """Verify user account using verification token from email"""
    users = load_users()
    for username, user_info in users.items():
        if user_info.get('token') == token and not user_info.get('verified', False):
            # Mark as email verified but still require admin approval
            users[username]['email_verified'] = True
            users[username]['email_verified_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_users(users)

            # Notify admin about email verification
            email = user_info.get('email')
            if email:
                send_admin_notification_new_user(username, email)

            return username
    return None

def delete_user(username):
    """Delete a user account"""
    users = load_users()
    if username in users and users[username].get('role') != 'admin':
        email = users[username].get('email')
        del users[username]
        save_users(users)

        # Send deletion notification email
        if email:
            subject = "Account Deleted - Nairobi Hospital DPS"
            body = f"""
            Dear {username},

            Your account has been deleted from the Nairobi Hospital Disease Prediction System.

            If you believe this was done in error, please contact admin at {ADMIN_EMAIL}.

            Best regards,
            Nairobi Hospital DPS Team
            """
            send_email(email, subject, body)

        return True
    return False

def resend_verification_email(username):
    """Resend verification email to user"""
    users = load_users()
    if username in users:
        user_info = users[username]
        email = user_info.get('email')
        token = user_info.get('token')

        if email and token:
            # Generate new token
            new_token = secrets.token_urlsafe(32)
            users[username]['token'] = new_token
            users[username]['verification_sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_users(users)

            # Send new verification email
            return send_verification_link_email(email, username, new_token)

    return False

def update_user_details(username, new_email=None, new_password=None, new_role=None):
    """Update user details (email, password, role)"""
    users = load_users()
    if username in users:
        updated = False

        # Update email if provided
        if new_email and new_email != users[username].get('email'):
            old_email = users[username].get('email')
            users[username]['email'] = new_email
            users[username]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated = True

            # Send notification email about email change
            if old_email:
                subject = "Account Email Updated - Nairobi Hospital DPS"
                body = f"""
                Dear {username},

                Your account email has been updated by an administrator.

                Old Email: {old_email}
                New Email: {new_email}
                Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                If you did not request this change, please contact admin immediately.

                Best regards,
                Nairobi Hospital DPS Team
                """
                send_email(old_email, subject, body)

        # Update password if provided
        if new_password:
            users[username]['password'] = hash_password(new_password)
            users[username]['password_updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated = True

            # Send notification email about password change
            email = users[username].get('email')
            if email:
                subject = "Account Password Updated - Nairobi Hospital DPS"
                body = f"""
                Dear {username},

                Your account password has been updated by an administrator.

                Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                You can now log in with your new password.

                If you did not request this change, please contact admin immediately.

                Best regards,
                Nairobi Hospital DPS Team
                """
                send_email(email, subject, body)

        # Update role if provided
        if new_role and new_role != users[username].get('role'):
            old_role = users[username].get('role')
            users[username]['role'] = new_role
            users[username]['role_updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated = True

            # Send notification email about role change
            email = users[username].get('email')
            if email:
                subject = "Account Role Updated - Nairobi Hospital DPS"
                body = f"""
                Dear {username},

                Your account role has been updated by an administrator.

                Old Role: {old_role.title()}
                New Role: {new_role.title()}
                Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                Best regards,
                Nairobi Hospital DPS Team
                """
                send_email(email, subject, body)

        if updated:
            save_users(users)
            return True

    return False

def get_user_details(username):
    """Get detailed user information"""
    users = load_users()
    if username in users:
        user_info = users[username].copy()
        # Remove sensitive information
        user_info.pop('password', None)
        user_info.pop('token', None)
        return user_info
    return None

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
.verification-notice {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    color: #856404;
}
.success-notice {
    background-color: #d1edff;
    border: 1px solid #74b9ff;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    color: #0984e3;
}
</style>
'''
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Ensure default admin user exists ---
def ensure_admin_user():
    users = load_users()
    if 'admin' not in users:
        users['admin'] = {
            'password': hash_password('admin1234#'),
            'role': 'admin',
            'registered': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'email': ADMIN_EMAIL,
            'verified': True
        }
        save_users(users)
ensure_admin_user()

# --- Session State for Auth ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'role' not in st.session_state:
    st.session_state.role = 'doctor'

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.role = 'doctor'

# --- URL Parameter Handling for Email Verification ---
if 'verify' in st.query_params:
    token = st.query_params['verify']
    verified_username = verify_user_by_token(token)
    if verified_username:
        st.success(f'✅ Email verification successful for {verified_username}!')
        st.info('Your email has been verified. Please wait for admin approval to access the system.')
        st.markdown('You can now close this page and log in once your account is approved by admin.')
    else:
        st.error('❌ Invalid or expired verification token.')
        st.info('Please contact admin for assistance.')

    # Clear the URL parameter
    st.query_params.clear()
    st.stop()

# --- Sidebar Navigation ---
with st.sidebar:
    st.image('https://img.icons8.com/color/96/000000/hospital-3.png', width=80)
    st.markdown('<h2 style="color:#fff;">Nairobi Hospital DPS</h2>', unsafe_allow_html=True)

    if st.session_state.logged_in:
        role = get_user_role(st.session_state.username)
        sidebar_options = ['Dashboard', 'Diabetes Prediction', 'Heart Disease Prediction',
                          'Parkinsons Prediction', 'Malaria Prediction', 'Typhoid Prediction',
                          'AIDS Prediction', 'Other Disease', 'Reports', 'Logout', 'About']
        sidebar_icons = ['house', 'activity', 'heart', 'person', 'bug', 'droplet',
                        'alert-triangle', 'plus-circle', 'bar-chart', 'box-arrow-right', 'info-circle']

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

# --- Enhanced Login Page ---
if selected == 'Login':
    st.title('🏥 Login to Disease Prediction System')
    st.markdown('Please log in to access the Disease Prediction System.')

    # Store authentication result in session state
    if 'auth_result' not in st.session_state:
        st.session_state.auth_result = None
    if 'auth_username' not in st.session_state:
        st.session_state.auth_username = None

    with st.form("login_form"):
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit_button = st.form_submit_button('Login')

        if submit_button:
            if not username or not password:
                st.error('Please fill in both username and password.')
            else:
                auth_result = authenticate_user(username, password)
                if auth_result is True:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = get_user_role(username)
                    st.success(f'Welcome, {username}!')
                    log_user_event(username, 'login')
                    st.rerun()
                elif auth_result == 'unverified':
                    st.session_state.auth_result = 'unverified'
                    st.session_state.auth_username = username
                    st.rerun()
                else:
                    st.error('Invalid username or password.')

    # Handle unverified user outside the form
    if st.session_state.auth_result == 'unverified':
        st.error('Your account is not verified. Please complete the verification process.')

        # Show verification request section
        st.markdown('<div class="verification-notice">', unsafe_allow_html=True)
        st.markdown('**🔒 Account Verification Required**')
        st.markdown('Your doctor account needs verification. You have two options:')
        st.markdown('1. **Check your email** for a verification link and click it')
        st.markdown('2. **Contact admin** if you haven\'t received the email or need assistance')
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button('📧 Request Verification from Admin'):
            users = load_users()
            user_email = users.get(st.session_state.auth_username, {}).get('email', '')

            if user_email:
                # Log verification request
                log_verification_request(st.session_state.auth_username, user_email, 'manual')

                # Send email to admin
                if send_admin_verification_request(st.session_state.auth_username, user_email):
                    st.success('✅ Verification request sent to admin successfully!')
                    st.info('You will receive an email once your account is approved.')
                    # Clear the auth result after successful request
                    st.session_state.auth_result = None
                    st.session_state.auth_username = None
                else:
                    st.error('❌ Failed to send verification request. Please try again.')
            else:
                st.error('❌ No email found for your account. Please contact admin directly.')

        # Add a button to clear the verification notice
        if st.button('❌ Clear Notice'):
            st.session_state.auth_result = None
            st.session_state.auth_username = None
            st.rerun()

# --- Enhanced Register Page ---
elif selected == 'Register':
    st.title('🏥 Register for Disease Prediction System')
    st.markdown('Create a new account to access the system.')

    with st.form("register_form"):
        username = st.text_input('Username *')
        password = st.text_input('Password *', type='password')
        confirm_password = st.text_input('Confirm Password *', type='password')
        email = st.text_input('Email Address *', placeholder='your.email@example.com')

        st.markdown('**📧 Email Verification Process:**')
        st.info('''After registration, you will receive a verification email with two options:

        **Option 1:** Click the verification link in your email to verify your account
        **Option 2:** If you don't receive the email or can't verify via link, contact admin for manual approval

        In both cases, you'll need to wait for admin approval before accessing the system.''')

        submit_button = st.form_submit_button('Register')

        if submit_button:
            if not username or not password or not confirm_password or not email:
                st.error('Please fill in all fields.')
            elif password != confirm_password:
                st.error('Passwords do not match.')
            elif not email or '@' not in email:
                st.error('Please enter a valid email address.')
            else:
                success = register_user(username, password, 'doctor', email)
                if success:
                    st.success('✅ Registration successful!')
                    st.info('📧 Please check your email for verification link.')
                    st.markdown('**Next Steps:**')
                    st.markdown('1. **Option 1:** Click the verification link in your email')
                    st.markdown('2. **Option 2:** If no email received, contact admin at ' + ADMIN_EMAIL)
                    st.markdown('3. Wait for admin approval (you\'ll receive an approval email)')
                    st.markdown('4. Log in once approved')
                else:
                    st.error('Username already exists. Please choose a different username.')

# --- Logout ---
elif selected == 'Logout':
    if st.session_state.logged_in:
        log_user_event(st.session_state.username, 'logout')
        logout()
        st.success('You have been logged out successfully.')
    else:
        st.info('You are not logged in.')

# --- Access Control for Protected Pages ---
elif not st.session_state.get('logged_in', False) and selected not in ['About', 'Login', 'Register']:
    st.warning('⚠️ Please log in to access this page.')
    st.info('Use the sidebar to navigate to the Login page.')

# --- Dashboard ---
elif st.session_state.logged_in and selected == 'Dashboard':
    st.markdown('<h1 style="color:#e63946;">🏥 Welcome to Nairobi Hospital Disease Prediction System</h1>', unsafe_allow_html=True)
    st.markdown(f'<h3 style="color:#457b9d;">Hello, {st.session_state.username}!</h3>', unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)

    # Profile section
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image('https://img.icons8.com/color/96/000000/user-male-circle--v2.png', width=80)
    with col2:
        user_role = get_user_role(st.session_state.username)
        st.markdown(f'''<div style="background:#457b9d;color:#fff;padding:1em;border-radius:10px;box-shadow:0 2px 8px #ccc;">
                    <b>Username:</b> {st.session_state.username}<br>
                    <b>Role:</b> {user_role.capitalize()}<br>
                    <b>Login time:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    </div>''', unsafe_allow_html=True)

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
        last_pred = df['timestamp'].max() if total_preds > 0 else '-'
        st.markdown(f'''<div style="background:#1d3557;color:#fff;padding:1.2em 1em;border-radius:12px;box-shadow:0 2px 8px #ccc;text-align:center;">
        <span style="font-size:2em;">⏰</span><br><b>Last Prediction</b><br><span style="font-size:1.2em;">{last_pred}</span></div>''', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # --- Charts ---
    if total_preds > 0:
        # Pie chart: predictions by disease
        pie_fig = px.pie(df, names='disease', title='Predictions by Disease',
                        color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(pie_fig, use_container_width=True)

        # Bar chart: predictions over time (by day)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_counts = df.groupby('date').size().reset_index(name='count')
        bar_fig = px.bar(daily_counts, x='date', y='count', title='Predictions Over Time',
                        color='count', color_continuous_scale=px.colors.sequential.Blues)
        st.plotly_chart(bar_fig, use_container_width=True)

    # --- Recent Activity Timeline ---
    st.markdown('<h4 style="color:#e63946;">Recent Activity</h4>', unsafe_allow_html=True)
    if total_preds > 0:
        recent = df[['timestamp', 'disease', 'result', 'features']].sort_values('timestamp', ascending=False).head(5)
        for _, row in recent.iterrows():
            patient_name = row['features'].get('Patient Name', '-') if isinstance(row['features'], dict) else '-'
            st.markdown(f'''<div style="background:#f1faee;padding:0.7em 1em;margin-bottom:0.5em;border-radius:8px;box-shadow:0 1px 4px #ccc;">
            <span style="color:#e63946;font-weight:bold;">{row['timestamp']}</span> — <b>{row['disease']}</b>: <span style="color:#457b9d;">{row['result']}</span><br>
            <span style="font-size:0.9em;color:#333;">Patient: {patient_name}</span>
            </div>''', unsafe_allow_html=True)
    else:
        st.info('No predictions yet. Use the sidebar to make your first prediction!')

# --- Enhanced Admin Page ---
elif st.session_state.logged_in and selected == 'Admin':
    if get_user_role(st.session_state.username) != 'admin':
        st.error('❌ Access denied. Admin privileges required.')
    else:
        st.title('👑 Admin Dashboard')

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

        # --- Enhanced Verification Requests Section ---
        st.markdown('<h4 style="color:#e63946;">📧 Verification Requests</h4>', unsafe_allow_html=True)

        verification_requests = get_verification_requests()
        pending_requests = [req for req in verification_requests if req['status'] == 'pending']

        if pending_requests:
            st.markdown(f'**{len(pending_requests)} pending verification requests:**')

            for request in pending_requests:
                st.markdown(f'''<div style="background:#fff3cd;padding:1em;border-radius:8px;margin-bottom:0.5em;box-shadow:0 1px 4px #ccc;">
                <b>{request['username']}</b> | Email: {request['email']} | Request Time: {request['timestamp']}<br>
                <span style="color:#e63946;">📧 Verification Request: {request['request_type'].title()}</span>
                </div>''', unsafe_allow_html=True)

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f'✅ Approve Request {request["username"]}', key=f'approve_req_{request["username"]}{request["timestamp"]}'):
                        if verify_user_account(request['username']):
                            st.success(f'Verification request approved for {request["username"]}!')
                            st.rerun()
                        else:
                            st.error('Failed to approve request.')

                with col2:
                    if st.button(f'❌ Deny Request {request["username"]}', key=f'deny_req_{request["username"]}{request["timestamp"]}'):
                        update_verification_request_status(request['username'], 'denied')
                        st.success(f'Verification request denied for {request["username"]}.')
                        st.rerun()
        else:
            st.info('✅ No pending verification requests.')

        # --- Create New User Section ---
        st.markdown('<h4 style="color:#e63946;">👤 Create New User</h4>', unsafe_allow_html=True)
        with st.expander("Create New User", expanded=False):
            with st.form("admin_create_user"):
                new_user = st.text_input('New Username')
                new_pass = st.text_input('New Password', type='password')
                new_email = st.text_input('Email Address')
                new_role = st.selectbox('Role', ['doctor', 'admin'])
                auto_verify = st.checkbox('Auto-verify user', value=True)

                if st.form_submit_button('Create User'):
                    if not new_user or not new_pass:
                        st.error('Please fill in username and password.')
                    elif new_user in users:
                        st.error('Username already exists.')
                    else:
                        success = register_user(new_user, new_pass, new_role, new_email)
                        if success and auto_verify:
                            # Auto-verify the user
                            users = load_users()
                            users[new_user]['verified'] = True
                            save_users(users)

                        if success:
                            st.success(f'User {new_user} created successfully!')
                            st.rerun()
                        else:
                            st.error('Failed to create user.')

        # --- System-wide Charts ---
        if users:
            role_counts = pd.Series([u.get('role', 'doctor') for u in users.values()]).value_counts()
            pie_fig = px.pie(role_counts, names=role_counts.index, values=role_counts.values,
                            title='User Roles', color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(pie_fig, use_container_width=True)

        # --- Unverified Users Management ---
        st.markdown('<h4 style="color:#e63946;">⏳ Unverified Doctors</h4>', unsafe_allow_html=True)
        if unverified:
            for uname in unverified:
                uinfo = users[uname]
                email_status = "📧 Email Verified" if uinfo.get('email_verified', False) else "📧 Email Not Verified"
                st.markdown(f'''<div style="background:#fff3cd;padding:1em;border-radius:8px;margin-bottom:0.5em;box-shadow:0 1px 4px #ccc;">
                <b>{uname}</b> | Email: {uinfo.get('email','-')} | Registered: {uinfo.get('registered','-')}<br>
                <span style="color:#e63946;">⚠️ {email_status} - Pending Admin Approval</span>
                </div>''', unsafe_allow_html=True)

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f'✅ Approve {uname}', key=f'approve_{uname}'):
                        if verify_user_account(uname):
                            st.success(f'Doctor {uname} approved!')
                            st.rerun()
                        else:
                            st.error('Failed to approve user.')

                with col2:
                    if st.button(f'❌ Delete {uname}', key=f'delete_{uname}'):
                        if delete_user(uname):
                            st.success(f'User {uname} deleted!')
                            st.rerun()
                        else:
                            st.error('Failed to delete user.')

                col3, col4 = st.columns([1, 1])
                with col3:
                    if st.button(f'📧 Resend Verification {uname}', key=f'resend_{uname}'):
                        if resend_verification_email(uname):
                            st.success(f'Verification email resent to {uname}!')
                            st.rerun()
                        else:
                            st.error('Failed to resend verification email.')

                with col4:
                    if st.button(f'📧 Send Reminder {uname}', key=f'reminder_{uname}'):
                        email = users[uname].get('email')
                        if email and send_verification_reminder_email(email, uname):
                            st.success(f'Reminder email sent to {uname}!')
                            st.rerun()
                        else:
                            st.error('Failed to send reminder email.')
        else:
            st.info('✅ No unverified doctors.')

        st.markdown('<hr>', unsafe_allow_html=True)

        # --- All Users Table ---
        st.markdown('<h4 style="color:#e63946;">👥 All Users</h4>', unsafe_allow_html=True)
        user_data = []
        for uname, uinfo in users.items():
            user_sessions = get_user_sessions(uname)
            last_login = '-'
            if user_sessions:
                login_sessions = [s for s in user_sessions if s['event'] == 'login']
                if login_sessions:
                    last_login = max(login_sessions, key=lambda x: x['timestamp'])['timestamp']

            # Determine verification status
            if uinfo.get('verified', False):
                status = '✅ Approved'
            elif uinfo.get('email_verified', False):
                status = '📧 Email Verified (Pending Admin)'
            else:
                status = '❌ Not Verified'

            user_data.append({
                'Username': uname,
                'Role': uinfo.get('role', 'doctor'),
                'Email': uinfo.get('email', ''),
                'Status': status,
                'Registered': uinfo.get('registered', ''),
                'Predictions': len(get_user_predictions(uname)),
                'Last Login': last_login
            })

        df_users = pd.DataFrame(user_data)
        st.dataframe(df_users, use_container_width=True)

        st.markdown('<hr>', unsafe_allow_html=True)

        # --- Enhanced User Management Section ---
        st.markdown('<h4 style="color:#e63946;">👤 User Management</h4>', unsafe_allow_html=True)

        # User selection for editing
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_user = st.selectbox(
                'Select User to Manage',
                options=[''] + list(users.keys()),
                format_func=lambda x: f"{x} ({users[x].get('role', 'doctor').title()})" if x else "Choose a user..."
            )

        with col2:
            if selected_user and selected_user != st.session_state.username:
                if st.button('🗑️ Delete User', type='secondary'):
                    if delete_user(selected_user):
                        st.success(f'User {selected_user} deleted successfully!')
                        st.rerun()
                    else:
                        st.error('Failed to delete user.')
            elif selected_user == st.session_state.username:
                st.warning('⚠️ Cannot delete your own account')

        # User editing form
        if selected_user:
            user_info = get_user_details(selected_user)
            if user_info:
                st.markdown(f'**Editing User: {selected_user}**')

                with st.form(f"edit_user_{selected_user}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        current_email = user_info.get('email', '')
                        new_email = st.text_input('Email Address', value=current_email, key=f'email_{selected_user}')

                        current_role = user_info.get('role', 'doctor')
                        new_role = st.selectbox(
                            'Role',
                            options=['doctor', 'admin'],
                            index=0 if current_role == 'doctor' else 1,
                            key=f'role_{selected_user}'
                        )

                    with col2:
                        new_password = st.text_input(
                            'New Password (leave blank to keep current)',
                            type='password',
                            key=f'password_{selected_user}'
                        )

                        # Show current user status
                        if user_info.get('verified', False):
                            status_display = '✅ Verified'
                        elif user_info.get('email_verified', False):
                            status_display = '📧 Email Verified (Pending Admin)'
                        else:
                            status_display = '❌ Not Verified'

                        st.info(f'**Current Status:** {status_display}')

                    # Additional user information
                    st.markdown('**User Information:**')
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.text(f'Registered: {user_info.get("registered", "N/A")}')
                    with col2:
                        st.text(f'Predictions: {len(get_user_predictions(selected_user))}')
                    with col3:
                        if user_info.get('verified_at'):
                            st.text(f'Approved: {user_info.get("verified_at")}')

                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.form_submit_button('💾 Save Changes'):
                            if update_user_details(selected_user, new_email, new_password, new_role):
                                st.success('✅ User details updated successfully!')
                                st.rerun()
                            else:
                                st.error('❌ Failed to update user details.')

                    with col2:
                        if not user_info.get('verified', False):
                            if st.form_submit_button('✅ Approve User'):
                                if verify_user_account(selected_user):
                                    st.success('✅ User approved successfully!')
                                    st.rerun()
                                else:
                                    st.error('❌ Failed to approve user.')
                        else:
                            st.info('✅ User already approved')

                    with col3:
                        if st.form_submit_button('📧 Resend Verification'):
                            if resend_verification_email(selected_user):
                                st.success('✅ Verification email sent!')
                                st.rerun()
                            else:
                                st.error('❌ Failed to send verification email.')

        st.markdown('<hr>', unsafe_allow_html=True)

        # --- New Disease Reports ---
        st.markdown('<h4 style="color:#e63946;">🆕 New Disease Reports</h4>', unsafe_allow_html=True)
        if new_disease_reports:
            df_reports = pd.DataFrame(new_disease_reports)
            st.dataframe(df_reports.sort_values('timestamp', ascending=False), use_container_width=True)

            csv = df_reports.to_csv(index=False).encode('utf-8')
            st.download_button('📥 Download Reports (CSV)', csv, 'new_disease_reports.csv', 'text/csv')
        else:
            st.info('No new disease reports yet.')

        st.markdown('<hr>', unsafe_allow_html=True)

        # --- Bulk User Management ---
        st.markdown('<h4 style="color:#e63946;">📋 Bulk User Operations</h4>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('**🔍 User Statistics:**')
            total_doctors = sum(1 for u in users.values() if u.get('role') == 'doctor')
            total_admins = sum(1 for u in users.values() if u.get('role') == 'admin')
            verified_users = sum(1 for u in users.values() if u.get('verified', False))
            unverified_users = len(users) - verified_users

            st.metric("Total Doctors", total_doctors)
            st.metric("Total Admins", total_admins)
            st.metric("Verified Users", verified_users)
            st.metric("Unverified Users", unverified_users)

        with col2:
            st.markdown('**⚡ Quick Actions:**')

            if st.button('📧 Send Verification Reminders', key='bulk_reminders_1'):
                unverified_users_list = [u for u, info in users.items()
                                       if info.get('role') == 'doctor' and not info.get('verified', False)]
                success_count = 0
                for username in unverified_users_list:
                    email = users[username].get('email')
                    if email and send_verification_reminder_email(email, username):
                        success_count += 1

                if success_count > 0:
                    st.success(f'✅ Verification reminders sent to {success_count} users!')
                else:
                    st.info('No unverified users to send reminders to.')

            if st.button('📧 Resend All Verification Emails', key='bulk_resend_1'):
                unverified_users_list = [u for u, info in users.items()
                                       if info.get('role') == 'doctor' and not info.get('verified', False)]
                success_count = 0
                for username in unverified_users_list:
                    if resend_verification_email(username):
                        success_count += 1

                if success_count > 0:
                    st.success(f'✅ Verification emails resent to {success_count} users!')
                else:
                    st.info('No unverified users to resend emails to.')

            if st.button('✅ Approve All Email-Verified Users', key='bulk_approve_1'):
                email_verified_users = [u for u, info in users.items()
                                      if info.get('email_verified', False) and not info.get('verified', False)]
                success_count = 0
                for username in email_verified_users:
                    if verify_user_account(username):
                        success_count += 1

                if success_count > 0:
                    st.success(f'✅ Approved {success_count} email-verified users!')
                else:
                    st.info('No email-verified users to approve.')

        with col3:
            st.markdown('**📊 Export Options:**')

            # Export user data
            if st.button('📥 Export User Data (CSV)'):
                export_data = []
                for uname, uinfo in users.items():
                    export_data.append({
                        'Username': uname,
                        'Role': uinfo.get('role', 'doctor'),
                        'Email': uinfo.get('email', ''),
                        'Verified': uinfo.get('verified', False),
                        'Email_Verified': uinfo.get('email_verified', False),
                        'Registered': uinfo.get('registered', ''),
                        'Predictions': len(get_user_predictions(uname))
                    })

                df_export = pd.DataFrame(export_data)
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    '📥 Download User Data',
                    csv,
                    'user_data_export.csv',
                    'text/csv'
                )

            # Export predictions data
            if st.button('📥 Export All Predictions (CSV)'):
                all_predictions = load_predictions()
                export_predictions = []

                for username, predictions in all_predictions.items():
                    for pred in predictions:
                        export_predictions.append({
                            'Username': username,
                            'Disease': pred['disease'],
                            'Result': pred['result'],
                            'Timestamp': pred['timestamp'],
                            'Patient': pred['features'].get('Patient Name', 'N/A') if isinstance(pred['features'], dict) else 'N/A'
                        })

                if export_predictions:
                    df_pred_export = pd.DataFrame(export_predictions)
                    csv_pred = df_pred_export.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        '📥 Download Predictions Data',
                        csv_pred,
                        'predictions_export.csv',
                        'text/csv'
                    )
                else:
                    st.info('No predictions to export.')

        st.markdown('<hr>', unsafe_allow_html=True)

        # --- Enhanced Admin Features ---

        # --- Email Management Section ---
        st.markdown('<h4 style="color:#e63946;">📧 Email Management</h4>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('**📊 Daily Reports**')
            if st.button('📧 Send Daily Report Now'):
                if send_daily_report_to_admin():
                    st.success('✅ Daily report sent successfully!')
                else:
                    st.error('❌ Failed to send daily report.')

            st.markdown('**📢 Send Announcement**')
            with st.expander("Send Announcement to All Doctors", expanded=False):
                with st.form("announcement_form"):
                    announcement_title = st.text_input('Announcement Title')
                    announcement_content = st.text_area('Announcement Content', height=150)

                    if st.form_submit_button('📢 Send Announcement'):
                        if announcement_title and announcement_content:
                            success_count = send_announcement_to_doctors(
                                announcement_title, announcement_content, st.session_state.username
                            )
                            if success_count > 0:
                                st.success(f'✅ Announcement sent to {success_count} doctors!')
                            else:
                                st.error('❌ Failed to send announcement.')
                        else:
                            st.error('Please fill in both title and content.')

        with col2:
            st.markdown('**👥 User Management**')

            # Bulk actions
            st.markdown('**Bulk Actions:**')
            if st.button('📧 Send Verification Reminders', key='bulk_reminders_2'):
                users = get_all_users()
                unverified_users = [u for u, info in users.items()
                                  if info.get('role') == 'doctor' and not info.get('verified', False)]

                success_count = 0
                for username in unverified_users:
                    email = users[username].get('email')
                    if email and send_verification_reminder_email(email, username):
                        success_count += 1

                if success_count > 0:
                    st.success(f'✅ Verification reminders sent to {success_count} users!')
                else:
                    st.info('No unverified users to send reminders to.')

            if st.button('📧 Resend All Verification Emails', key='bulk_resend_2'):
                users = get_all_users()
                unverified_users = [u for u, info in users.items()
                                  if info.get('role') == 'doctor' and not info.get('verified', False)]

                success_count = 0
                for username in unverified_users:
                    if resend_verification_email(username):
                        success_count += 1

                if success_count > 0:
                    st.success(f'✅ Verification emails resent to {success_count} users!')
                else:
                    st.info('No unverified users to resend emails to.')

        st.markdown('<hr>', unsafe_allow_html=True)

        # --- System Information ---
        st.markdown('<h4 style="color:#e63946;">⚙️ System Information</h4>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('**📈 Email Statistics:**')
            users = get_all_users()
            total_emails = sum(1 for u in users.values() if u.get('email'))
            verified_emails = sum(1 for u in users.values() if u.get('email') and u.get('verified'))

            st.metric("Total Users with Email", total_emails)
            st.metric("Verified Users with Email", verified_emails)
            st.metric("Email Coverage", f"{(total_emails/len(users)*100):.1f}%" if users else "0%")

        with col2:
            st.markdown('**🔧 System Status:**')
            st.info(f"Admin Email: {ADMIN_EMAIL}")
            st.info(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
            st.info(f"Email Status: {'✅ Configured' if ADMIN_PASSWORD != 'your_app_password_here' else '❌ Not Configured'}")

# Load ML Models
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(os.path.dirname(current_dir), 'models')

# Create models directory if it doesn't exist
if not os.path.exists(models_dir):
    models_dir = os.path.join(current_dir, 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

# Loading the saved models with error handling
try:
    diabetes_model = pickle.load(open(os.path.join(models_dir, 'diabetes_model.sav'), 'rb'))
except Exception as e:
    diabetes_model = None

try:
    heart_disease_model = pickle.load(open(os.path.join(models_dir, 'heart_disease_model.sav'), 'rb'))
except Exception as e:
    heart_disease_model = None

try:
    parkinsons_model = pickle.load(open(os.path.join(models_dir, 'parkinsons_model.sav'), 'rb'))
except Exception as e:
    parkinsons_model = None

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

# --- Prediction Pages ---

# Diabetes Prediction Page
if selected == 'Diabetes Prediction':
    st.title('🩺 Diabetes Prediction using ML')

    if not diabetes_model:
        st.error('❌ Diabetes prediction model not available. Please contact administrator.')
    else:
        with st.form("diabetes_form"):
            patient_name = st.text_input('Patient Name *', placeholder='Enter patient full name')

            col1, col2, col3 = st.columns(3)

            with col1:
                pregnancies = st.number_input('Number of Pregnancies', min_value=0, max_value=20, value=0)
                skin_thickness = st.number_input('Skin Thickness (mm)', min_value=0.0, max_value=100.0, value=20.0)
                diabetes_pedigree = st.number_input('Diabetes Pedigree Function', min_value=0.0, max_value=3.0, value=0.5, step=0.1)

            with col2:
                glucose = st.number_input('Glucose Level (mg/dL)', min_value=0, max_value=300, value=120)
                insulin = st.number_input('Insulin Level (μU/mL)', min_value=0, max_value=900, value=80)
                age = st.number_input('Age (years)', min_value=1, max_value=120, value=25)

            with col3:
                blood_pressure = st.number_input('Blood Pressure (mmHg)', min_value=0, max_value=200, value=70)
                bmi = st.number_input('BMI', min_value=0.0, max_value=70.0, value=25.0, step=0.1)

            submit_diabetes = st.form_submit_button('🔍 Predict Diabetes')

            if submit_diabetes:
                if not patient_name.strip():
                    st.error('❌ Please enter patient name.')
                else:
                    try:
                        input_data = [pregnancies, glucose, blood_pressure, skin_thickness,
                                    insulin, bmi, diabetes_pedigree, age]

                        prediction = diabetes_model.predict([input_data])

                        if prediction[0] == 1:
                            result = 'The person is diabetic'
                            st.error(f'⚠️ {result}')
                            st.markdown('**🏥 Suggested Medicines:**')
                            for med in MEDICINE_SUGGESTIONS['Diabetes']:
                                st.markdown(f'• {med}')
                        else:
                            result = 'The person is not diabetic'
                            st.success(f'✅ {result}')
                            st.info('💡 No medication needed. Regular health checkups recommended.')

                        # Log prediction
                        log_prediction(st.session_state.username, 'Diabetes', result, {
                            'Patient Name': patient_name,
                            'Pregnancies': pregnancies, 'Glucose': glucose, 'Blood Pressure': blood_pressure,
                            'Skin Thickness': skin_thickness, 'Insulin': insulin, 'BMI': bmi,
                            'Diabetes Pedigree Function': diabetes_pedigree, 'Age': age
                        })

                    except Exception as e:
                        st.error(f'❌ Prediction failed: {str(e)}')

# Heart Disease Prediction Page
elif selected == 'Heart Disease Prediction':
    st.title('❤️ Heart Disease Prediction using ML')

    if not heart_disease_model:
        st.error('❌ Heart disease prediction model not available. Please contact administrator.')
    else:
        with st.form("heart_form"):
            patient_name = st.text_input('Patient Name *', placeholder='Enter patient full name')

            col1, col2, col3 = st.columns(3)

            with col1:
                age = st.number_input('Age (years)', min_value=1, max_value=120, value=50)
                cp = st.selectbox('Chest Pain Type', options=[0, 1, 2, 3],
                    format_func=lambda x: ['Typical Angina', 'Atypical Angina', 'Non-anginal Pain', 'Asymptomatic'][x])
                chol = st.number_input('Serum Cholesterol (mg/dl)', min_value=100, max_value=600, value=200)
                thalach = st.number_input('Maximum Heart Rate', min_value=60, max_value=250, value=150)
                slope = st.selectbox('ST Segment Slope', options=[0, 1, 2],
                    format_func=lambda x: ['Upsloping', 'Flat', 'Downsloping'][x])

            with col2:
                sex = st.selectbox('Sex', options=[0, 1], format_func=lambda x: 'Female' if x == 0 else 'Male')
                trestbps = st.number_input('Resting Blood Pressure (mmHg)', min_value=50, max_value=250, value=120)
                fbs = st.selectbox('Fasting Blood Sugar > 120 mg/dl', options=[0, 1],
                    format_func=lambda x: 'No' if x == 0 else 'Yes')
                exang = st.selectbox('Exercise Induced Angina', options=[0, 1],
                    format_func=lambda x: 'No' if x == 0 else 'Yes')
                ca = st.number_input('Major Vessels (0-3)', min_value=0, max_value=3, value=0)

            with col3:
                restecg = st.selectbox('Resting ECG', options=[0, 1, 2],
                    format_func=lambda x: ['Normal', 'ST-T abnormality', 'LV hypertrophy'][x])
                oldpeak = st.number_input('ST Depression', min_value=0.0, max_value=10.0, value=1.0, step=0.1)
                thal = st.selectbox('Thalassemia', options=[1, 2, 3],
                    format_func=lambda x: {1: 'Normal', 2: 'Fixed Defect', 3: 'Reversible Defect'}[x])

            submit_heart = st.form_submit_button('🔍 Predict Heart Disease')

            if submit_heart:
                if not patient_name.strip():
                    st.error('❌ Please enter patient name.')
                else:
                    try:
                        input_data = [age, sex, cp, trestbps, chol, fbs, restecg,
                                    thalach, exang, oldpeak, slope, ca, thal]

                        prediction = heart_disease_model.predict([input_data])

                        if prediction[0] == 1:
                            result = 'The person has heart disease'
                            st.error(f'⚠️ {result}')
                            st.markdown('**🏥 Suggested information:**')
                            for med in MEDICINE_SUGGESTIONS['Heart Disease']:
                                st.markdown(f'• {med}')
                        else:
                            result = 'The person does not have heart disease'
                            st.success(f'✅ {result}')
                            st.info('💡 Heart appears healthy. Maintain healthy lifestyle.')

                        # Log prediction
                        log_prediction(st.session_state.username, 'Heart Disease', result, {
                            'Patient Name': patient_name,
                            'Age': age, 'Sex': sex, 'Chest Pain Type': cp, 'Resting BP': trestbps,
                            'Cholesterol': chol, 'Fasting BS': fbs, 'Resting ECG': restecg,
                            'Max Heart Rate': thalach, 'Exercise Angina': exang, 'ST Depression': oldpeak,
                            'Slope': slope, 'Major Vessels': ca, 'Thalassemia': thal
                        })

                    except Exception as e:
                        st.error(f'❌ Prediction failed: {str(e)}')

# Parkinson's Prediction Page
elif selected == "Parkinsons Prediction":
    st.title("🧠 Parkinson's Disease Prediction using ML")

    if not parkinsons_model:
        st.error("❌ Parkinson's prediction model not available. Please contact administrator.")
    else:
        st.info('📋 All voice measurement parameters are required for accurate prediction.')

        with st.form("parkinsons_form"):
            patient_name = st.text_input('Patient Name *', placeholder='Enter patient full name')

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                fo = st.number_input('MDVP:Fo(Hz)', min_value=0.0, value=197.0, step=0.1)
                RAP = st.number_input('MDVP:RAP', min_value=0.0, value=0.00289, step=0.00001, format="%.5f")
                APQ3 = st.number_input('Shimmer:APQ3', min_value=0.0, value=0.00484, step=0.00001, format="%.5f")
                HNR = st.number_input('HNR', value=21.0, step=0.1)
                D2 = st.number_input('D2', value=2.0, step=0.1)

            with col2:
                fhi = st.number_input('MDVP:Fhi(Hz)', min_value=0.0, value=206.0, step=0.1)
                PPQ = st.number_input('MDVP:PPQ', min_value=0.0, value=0.00166, step=0.00001, format="%.5f")
                APQ5 = st.number_input('Shimmer:APQ5', min_value=0.0, value=0.00557, step=0.00001, format="%.5f")
                RPDE = st.number_input('RPDE', value=0.4, step=0.01)
                PPE = st.number_input('PPE', value=0.2, step=0.01)

            with col3:
                flo = st.number_input('MDVP:Flo(Hz)', min_value=0.0, value=192.0, step=0.1)
                DDP = st.number_input('Jitter:DDP', min_value=0.0, value=0.00867, step=0.00001, format="%.5f")
                APQ = st.number_input('MDVP:APQ', min_value=0.0, value=0.00335, step=0.00001, format="%.5f")
                DFA = st.number_input('DFA', value=0.7, step=0.01)

            with col4:
                jitter_percent = st.number_input('MDVP:Jitter(%)', min_value=0.0, value=0.00289, step=0.00001, format="%.5f")
                shimmer = st.number_input('MDVP:Shimmer', min_value=0.0, value=0.00484, step=0.00001, format="%.5f")
                DDA = st.number_input('Shimmer:DDA', min_value=0.0, value=0.01452, step=0.00001, format="%.5f")
                spread1 = st.number_input('spread1', value=-6.0, step=0.1)

            with col5:
                jitter_abs = st.number_input('MDVP:Jitter(Abs)', min_value=0.0, value=0.000015, step=0.000001, format="%.6f")
                shimmer_db = st.number_input('MDVP:Shimmer(dB)', value=0.426, step=0.001)
                NHR = st.number_input('NHR', value=0.024, step=0.001)
                spread2 = st.number_input('spread2', value=0.2, step=0.01)

            submit_parkinsons = st.form_submit_button("🔍 Predict Parkinson's Disease")

            if submit_parkinsons:
                if not patient_name.strip():
                    st.error('❌ Please enter patient name.')
                else:
                    try:
                        input_data = [fo, fhi, flo, jitter_percent, jitter_abs, RAP, PPQ, DDP,
                                    shimmer, shimmer_db, APQ3, APQ5, APQ, DDA, NHR, HNR, RPDE,
                                    DFA, spread1, spread2, D2, PPE]

                        prediction = parkinsons_model.predict([input_data])

                        if prediction[0] == 1:
                            result = "The person has Parkinson's disease"
                            st.error(f'⚠️ {result}')
                            st.markdown("**🏥 Suggested information:**")
                            for med in MEDICINE_SUGGESTIONS['Parkinsons']:
                                st.markdown(f'• {med}')
                        else:
                            result = "The person does not have Parkinson's disease"
                            st.success(f'✅ {result}')
                            st.info('💡 No signs of Parkinson\'s detected in voice analysis.')

                        # Log prediction
                        log_prediction(st.session_state.username, 'Parkinsons', result, {
                            'Patient Name': patient_name,
                            'MDVP:Fo(Hz)': fo, 'MDVP:Fhi(Hz)': fhi, 'MDVP:Flo(Hz)': flo,
                            'MDVP:Jitter(%)': jitter_percent, 'MDVP:Jitter(Abs)': jitter_abs,
                            'MDVP:RAP': RAP, 'MDVP:PPQ': PPQ, 'Jitter:DDP': DDP,
                            'MDVP:Shimmer': shimmer, 'MDVP:Shimmer(dB)': shimmer_db,
                            'Shimmer:APQ3': APQ3, 'Shimmer:APQ5': APQ5, 'MDVP:APQ': APQ,
                            'Shimmer:DDA': DDA, 'NHR': NHR, 'HNR': HNR, 'RPDE': RPDE,
                            'DFA': DFA, 'spread1': spread1, 'spread2': spread2, 'D2': D2, 'PPE': PPE
                        })

                    except Exception as e:
                        st.error(f'❌ Prediction failed: {str(e)}')

# Other Disease Prediction Pages (Malaria, Typhoid, AIDS)
elif selected == 'Malaria Prediction':
    st.title('🦟 Malaria Prediction using ML')

    with st.form("malaria_form"):
        patient_name = st.text_input('Patient Name *', placeholder='Enter patient full name')

        col1, col2, col3 = st.columns(3)

        with col1:
            fever = st.selectbox('High Fever (>38°C)', ['No', 'Yes'])
            chills = st.selectbox('Chills and Sweating', ['No', 'Yes'])
            headache = st.selectbox('Severe Headache', ['No', 'Yes'])

        with col2:
            nausea = st.selectbox('Nausea/Vomiting', ['No', 'Yes'])
            muscle_pain = st.selectbox('Muscle Pain', ['No', 'Yes'])
            fatigue = st.selectbox('Extreme Fatigue', ['No', 'Yes'])

        with col3:
            travel = st.selectbox('Recent Travel to Malaria Area', ['No', 'Yes'])
            blood_test = st.selectbox('Positive Malaria Blood Test', ['No', 'Yes'])

        submit_malaria = st.form_submit_button('🔍 Predict Malaria')

        if submit_malaria:
            if not patient_name.strip():
                st.error('❌ Please enter patient name.')
            elif malaria_model:
                try:
                    input_data = [int(fever=='Yes'), int(chills=='Yes'), int(headache=='Yes'),
                                int(nausea=='Yes'), int(muscle_pain=='Yes'), int(fatigue=='Yes'),
                                int(travel=='Yes'), int(blood_test=='Yes')]

                    prediction = malaria_model.predict([input_data])

                    if prediction[0] == 1:
                        result = 'The person is likely to have Malaria'
                        st.error(f'⚠️ {result}')
                        st.markdown('**🏥 Suggested treatment information:**')
                        for med in MEDICINE_SUGGESTIONS['Malaria']:
                            st.markdown(f'• {med}')
                    else:
                        result = 'The person is unlikely to have Malaria'
                        st.success(f'✅ {result}')
                        st.info('💡 Symptoms may indicate other conditions. Consult doctor.')

                    log_prediction(st.session_state.username, 'Malaria', result, {
                        'Patient Name': patient_name,
                        'High Fever': fever, 'Chills': chills, 'Headache': headache,
                        'Nausea': nausea, 'Muscle Pain': muscle_pain, 'Fatigue': fatigue,
                        'Travel History': travel, 'Blood Test': blood_test
                    })

                except Exception as e:
                    st.error(f'❌ Prediction failed: {str(e)}')
            else:
                st.warning('⚠️ Malaria prediction model not available.')

elif selected == 'Typhoid Prediction':
    st.title('🦠 Typhoid Prediction using ML')

    with st.form("typhoid_form"):
        patient_name = st.text_input('Patient Name *', placeholder='Enter patient full name')

        col1, col2, col3 = st.columns(3)

        with col1:
            fever = st.selectbox('Prolonged Fever', ['No', 'Yes'])
            abdominal_pain = st.selectbox('Abdominal Pain', ['No', 'Yes'])
            headache = st.selectbox('Headache', ['No', 'Yes'])

        with col2:
            diarrhea = st.selectbox('Diarrhea', ['No', 'Yes'])
            constipation = st.selectbox('Constipation', ['No', 'Yes'])
            rash = st.selectbox('Rose Spots (Rash)', ['No', 'Yes'])

        with col3:
            weakness = st.selectbox('Weakness', ['No', 'Yes'])
            appetite = st.selectbox('Loss of Appetite', ['No', 'Yes'])
            blood_test = st.selectbox('Positive Typhoid Test', ['No', 'Yes'])

        submit_typhoid = st.form_submit_button('🔍 Predict Typhoid')

        if submit_typhoid:
            if not patient_name.strip():
                st.error('❌ Please enter patient name.')
            elif typhoid_model:
                try:
                    input_data = [int(fever=='Yes'), int(abdominal_pain=='Yes'), int(headache=='Yes'),
                                int(diarrhea=='Yes'), int(constipation=='Yes'), int(rash=='Yes'),
                                int(weakness=='Yes'), int(appetite=='Yes'), int(blood_test=='Yes')]

                    prediction = typhoid_model.predict([input_data])

                    if prediction[0] == 1:
                        result = 'The person is likely to have Typhoid'
                        st.error(f'⚠️ {result}')
                        st.markdown('**🏥 Suggested treatment information:**')
                        for med in MEDICINE_SUGGESTIONS['Typhoid']:
                            st.markdown(f'• {med}')
                    else:
                        result = 'The person is unlikely to have Typhoid'
                        st.success(f'✅ {result}')
                        st.info('💡 Symptoms may indicate other conditions. Consult doctor.')

                    log_prediction(st.session_state.username, 'Typhoid', result, {
                        'Patient Name': patient_name,
                        'Prolonged Fever': fever, 'Abdominal Pain': abdominal_pain,
                        'Headache': headache, 'Diarrhea': diarrhea, 'Constipation': constipation,
                        'Rose Spots': rash, 'Weakness': weakness, 'Loss of Appetite': appetite,
                        'Blood Test': blood_test
                    })

                except Exception as e:
                    st.error(f'❌ Prediction failed: {str(e)}')
            else:
                st.warning('⚠️ Typhoid prediction model not available.')

elif selected == 'AIDS Prediction':
    st.title('🩸 AIDS (HIV) Prediction using ML')

    with st.form("aids_form"):
        patient_name = st.text_input('Patient Name *', placeholder='Enter patient full name')

        col1, col2 = st.columns(2)

        with col1:
            weight_loss = st.selectbox('Unexplained Weight Loss', ['No', 'Yes'])
            fever = st.selectbox('Persistent Fever', ['No', 'Yes'])
            night_sweats = st.selectbox('Night Sweats', ['No', 'Yes'])
            fatigue = st.selectbox('Chronic Fatigue', ['No', 'Yes'])

        with col2:
            lymph_nodes = st.selectbox('Swollen Lymph Nodes', ['No', 'Yes'])
            risky_behavior = st.selectbox('History of Risky Behavior', ['No', 'Yes'])
            hiv_test = st.selectbox('Positive HIV Test', ['No', 'Yes'])

        submit_aids = st.form_submit_button('🔍 Predict AIDS Risk')

        if submit_aids:
            if not patient_name.strip():
                st.error('❌ Please enter patient name.')
            elif aids_model:
                try:
                    input_data = [int(weight_loss=='Yes'), int(fever=='Yes'), int(night_sweats=='Yes'),
                                int(fatigue=='Yes'), int(lymph_nodes=='Yes'), int(risky_behavior=='Yes'),
                                int(hiv_test=='Yes')]

                    prediction = aids_model.predict([input_data])

                    if prediction[0] == 1:
                        result = 'The person has high AIDS risk indicators'
                        st.error(f'⚠️ {result}')
                        st.markdown('**🏥 Suggested care information:**')
                        for med in MEDICINE_SUGGESTIONS['AIDS']:
                            st.markdown(f'• {med}')
                        st.warning('🔒 This information is confidential and requires immediate medical attention.')
                    else:
                        result = 'The person has low AIDS risk indicators'
                        st.success(f'✅ {result}')
                        st.info('💡 Regular health monitoring recommended.')

                    log_prediction(st.session_state.username, 'AIDS', result, {
                        'Patient Name': patient_name,
                        'Weight Loss': weight_loss, 'Fever': fever, 'Night Sweats': night_sweats,
                        'Fatigue': fatigue, 'Swollen Lymph Nodes': lymph_nodes,
                        'Risky Behavior': risky_behavior, 'HIV Test': hiv_test
                    })

                except Exception as e:
                    st.error(f'❌ Prediction failed: {str(e)}')
            else:
                st.warning('⚠️ AIDS prediction model not available.')

# Other Disease Reporting Page
elif st.session_state.logged_in and selected == 'Other Disease':
    st.title('📝 Report New/Other Disease')
    st.markdown('''<div style="background-color:#f1faee;padding:1em;border-radius:8px;margin-bottom:1em;">
    📋 If a patient presents with a disease not listed in the system, please fill out this form.
    The admin will be notified and the case will be reviewed for future system updates.
    </div>''', unsafe_allow_html=True)

    with st.form("other_disease_form"):
        patient_name = st.text_input('Patient Name *')
        suspected_disease = st.text_input('Suspected Disease Name *')
        symptoms = st.text_area('Symptoms (describe each symptom)', height=100)
        severity = st.selectbox('Severity Level', ['Mild', 'Moderate', 'Severe', 'Critical'])
        duration = st.text_input('Duration of Symptoms')
        notes = st.text_area('Additional Clinical Notes', height=100)

        submit_report = st.form_submit_button('📤 Submit Report')

        if submit_report:
            if not patient_name or not suspected_disease or not symptoms:
                st.error('❌ Please fill in all required fields (marked with *).')
            else:
                report = {
                    'doctor': st.session_state.username,
                    'patient_name': patient_name,
                    'suspected_disease': suspected_disease,
                    'symptoms': symptoms,
                    'severity': severity,
                    'duration': duration,
                    'notes': notes,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                log_new_disease_report(report)

                # Send email notification to admin about new disease report
                send_admin_notification_new_disease(suspected_disease, st.session_state.username, patient_name)

                log_notification(f'New disease reported: {suspected_disease} (by Dr. {st.session_state.username})',
                               notif_type='new_disease')

                st.success('✅ Report submitted successfully! The admin will be notified via email.')
                st.info('📧 You will receive updates on the status of this report.')

# Reports Page
elif st.session_state.logged_in and selected == 'Reports':
    st.title('📊 Reports & Prediction History')
    st.markdown('📋 **Filter and export your prediction history.**')

    user_preds = get_user_predictions(st.session_state.username)

    if user_preds:
        df = pd.DataFrame(user_preds)

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            patient_filter = st.text_input('🔍 Filter by Patient Name')
        with col2:
            disease_filter = st.selectbox('🏥 Filter by Disease', ['All'] + sorted(df['disease'].unique().tolist()))
        with col3:
            date_from = st.date_input('📅 From Date')

        # Apply filters
        filtered = df.copy()

        if patient_filter:
            filtered = filtered[filtered['features'].apply(
                lambda f: patient_filter.lower() in f.get('Patient Name', '').lower()
                if isinstance(f, dict) else False
            )]

        if disease_filter != 'All':
            filtered = filtered[filtered['disease'] == disease_filter]

        if date_from:
            filtered = filtered[pd.to_datetime(filtered['timestamp']).dt.date >= date_from]

        # Display results
        st.markdown(f'📈 **Showing {len(filtered)} of {len(df)} predictions**')

        # Format display data
        display_data = []
        for _, row in filtered.iterrows():
            patient_name = row['features'].get('Patient Name', 'Unknown') if isinstance(row['features'], dict) else 'Unknown'
            display_data.append({
                'Timestamp': row['timestamp'],
                'Patient': patient_name,
                'Disease': row['disease'],
                'Result': row['result']
            })

        if display_data:
            df_display = pd.DataFrame(display_data)
            st.dataframe(df_display, use_container_width=True)

            # Export options
            col1, col2 = st.columns(2)
            with col1:
                csv = filtered.to_csv(index=False).encode('utf-8')
                st.download_button('📥 Download Filtered Report (CSV)', csv,
                                 'prediction_report.csv', 'text/csv')

            with col2:
                if st.button('🗑️ Clear All History'):
                    predictions = load_predictions()
                    predictions[st.session_state.username] = []
                    save_predictions(predictions)
                    st.success('✅ Prediction history cleared!')
                    st.rerun()
        else:
            st.info('📭 No predictions match your filters.')
    else:
        st.info('📭 No predictions yet. Start by making your first prediction!')

# About Page
elif selected == 'About':
    st.title('ℹ️ About the Disease Prediction System')

    st.markdown(f'''
    ## 🏥 **Nairobi Hospital Disease Prediction System**

    ### 🎓 **Academic Project Information**
    - **Institution**: School of Technology
    - **Program**: Bachelor of Science in Data Science
    - **Student**: Cherotich Laura
    - **Registration**: 23/08450
    - **Supervisor**: Ernest Madara

    ---

    ### 📋 **Project Overview**
    This advanced machine learning system assists healthcare professionals at Nairobi Hospital
    by providing data-driven diagnostic support for multiple diseases including:

    - 🩺 **Diabetes** - Based on glucose levels, BMI, and other factors
    - ❤️ **Heart Disease** - Cardiovascular risk assessment
    - 🧠 **Parkinson's Disease** - Voice pattern analysis
    - 🦟 **Malaria** - Symptom-based prediction
    - 🦠 **Typhoid** - Clinical symptom evaluation
    - 🩸 **AIDS/HIV** - Risk factor assessment

    ### 🎯 **Key Objectives**
    1. **Data Collection**: Gather and prepare comprehensive patient data
    2. **Pattern Recognition**: Identify relationships between symptoms and diseases
    3. **Model Development**: Train and validate machine learning models
    4. **User Interface**: Provide intuitive diagnostic tools
    5. **Accuracy Assessment**: Evaluate system performance and reliability

    ### 🔬 **Methodology**
    - **Data Processing**: Advanced cleaning and preprocessing techniques
    - **Machine Learning**: Multiple algorithm implementation and testing
    - **Interface Design**: User-friendly Streamlit web application
    - **Integration**: Seamless model deployment and testing
    - **Documentation**: Comprehensive system documentation

    ### 👥 **User Roles**
    - **👨‍⚕️ Doctors**: Access prediction tools and patient management
    - **👑 Administrators**: User management and system oversight
    - **📊 Analytics**: Comprehensive reporting and data export

    ### 🔒 **Security Features**
    - **Authentication**: Secure login system
    - **Role-based Access**: Appropriate permission levels
    - **Data Protection**: Patient information confidentiality
    - **Audit Trail**: Complete activity logging

    ### 📧 **Email Verification System**
    - **Automated Verification**: Email verification for new doctor registrations
    - **Admin Notifications**: Instant email alerts for new registrations and disease reports
    - **Manual Requests**: Users can request verification if emails are not received
    - **Professional Templates**: Well-formatted email communications

    ### 📚 **Technical References**
    - Shrestha & Chatterjee (2019) - Disease Prediction Models
    - Srivastava & Singh (2022) - Healthcare ML Applications
    - Jindal et al. (2021) - Diagnostic System Design
    - Heller et al. (1984) - Medical Data Analysis
    - Cáceres & Paccanaro (2019) - Predictive Healthcare Systems

    ### ⚠️ **Important Disclaimers**
    - **Medical Advice**: This system provides diagnostic support only
    - **Professional Consultation**: Always consult qualified medical professionals
    - **Accuracy**: Predictions are based on available data and models
    - **Responsibility**: Final diagnostic decisions rest with healthcare providers

    ### 📞 **Support & Contact**
    For technical support or questions about this system, please contact:
    - **System Administrator**: {ADMIN_EMAIL}
    - **Technical Support**: support@nairobihospital.ke
    - **Student Contact**: cherotich.laura@student.edu

    ---

    ### 🚀 **Version Information**
    - **Version**: 2.0.0 (Enhanced with Email Verification)
    - **Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
    - **Framework**: Streamlit + Scikit-learn + Gmail SMTP
    - **Database**: Pickle-based data storage
    - **Email Service**: Gmail SMTP Integration

    *This system is designed to enhance medical decision-making through data-driven insights
    while maintaining the highest standards of patient care and data security.*
    ''')

# Handle any other unmatched routes
else:
    if st.session_state.logged_in:
        st.warning('⚠️ Page not found. Please use the sidebar to navigate.')
    else:
        st.info('Please login to access the system.')
