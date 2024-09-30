from pipin import install_requirements
from flask import Flask, request, jsonify, session
import bcrypt
import pyotp
import json
import os
import threading
import requests
import qrcode
import io
from base64 import b64encode
import random
import string
import webbrowser

# Call the function to install dependencies
install_requirements()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Secure key should be set via environment

# Load user data
if os.path.exists('users.json'):
    with open('users.json') as f:
        users = json.load(f)
else:
    users = {}

# Save user data
def save_users():
    with open('users.json', 'w') as f:
        json.dump(users, f)

# Function to send email via FormSubmit with response handling
def send_email(email, subject, message):
    form_data = {
        'name': 'User',
        'email': email,
        'subject': subject,
        'message': message
    }
    try:
        response = requests.post(f'https://formsubmit.co/{email}', data=form_data)
        print(f"Email sent to {email}. Status code: {response.status_code}")
        if response.ok:
            print("Email sent successfully!")
            return True
        else:
            print("Failed to send email.")
            print("Response:", response.text)
            return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False

# Function to send password to user
def send_password_email(email, username, password):
    subject = 'Your Account Information'
    message = f'Hello {username},\n\nYour password is: {password}\nPlease keep this information secure.'
    if send_email(email, subject, message):
        # Open a browser window after sending the email
        webbrowser.open(f"https://formsubmit.co/{email}")

# Function to send verification code via email
def send_verification_code(email, username, code):
    subject = 'Password Reset Verification Code'
    message = f'Hello {username},\n\nYour verification code is: {code}\nPlease use this code to reset your password.'
    if send_email(email, subject, message):
        # Open a browser window after sending the email
        webbrowser.open(f"https://formsubmit.co/{email}")

# Registration Route
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email', None)  # Optional recovery email

    if username in users:
        return jsonify({'error': 'User already exists!'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    totp_secret = pyotp.random_base32()

    users[username] = {
        'password': hashed.decode('utf-8'),
        'totp_secret': totp_secret,
        'email': email,
        'role': 'user',
        'first_login': True,
        'failed_attempts': 0,
        'locked': False
    }
    save_users()

    # Send password to the email if provided
    if email:
        email_sent = send_password_email(email, username, password)
        if not email_sent:
            return jsonify({'error': 'Failed to send the password to the provided email!'}), 500

    # Generate QR code for TOTP setup
    totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(name=username, issuer_name="YourApp")
    qr = qrcode.make(totp_uri)
    buffered = io.BytesIO()
    qr.save(buffered, format="PNG")
    qr_code_str = b64encode(buffered.getvalue()).decode('utf-8')

    return jsonify({'message': 'User registered successfully!', 'qr_code': qr_code_str})

# Login Route
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = users.get(username)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        if user:
            user['failed_attempts'] += 1
            if user['failed_attempts'] >= 3:
                user['locked'] = True
                save_users()
                return jsonify({'error': 'Account is locked due to multiple failed login attempts!'}), 403
        return jsonify({'error': 'Invalid credentials!'}), 400

    if user['locked']:
        return jsonify({'error': 'Account is locked due to multiple failed login attempts!'}), 403

    session['username'] = username
    user['failed_attempts'] = 0  # Reset attempts on successful login

    # On first login, send password again to recovery email
    if user['first_login'] and user['email']:
        email_sent = send_password_email(user['email'], username, password)
        if not email_sent:
            return jsonify({'error': 'Failed to send password to the recovery email!'}), 500
        users[username]['first_login'] = False
        save_users()

    return jsonify({'message': 'Login successful!', 'totp_secret': user['totp_secret']})

# Verify TOTP Route
@app.route('/verify_totp', methods=['POST'])
def verify_totp():
    username = session.get('username')
    if not username:
        return jsonify({'error': 'User not logged in!'}), 403

    user = users[username]
    totp = request.json.get('totp')

    # Verify TOTP
    totp_gen = pyotp.TOTP(user['totp_secret'])
    if totp_gen.verify(totp):
        return jsonify({'message': '2FA verification successful!'})
    return jsonify({'error': 'Invalid TOTP!'}), 400

# Logout Route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully!'})

# Thread for running Flask app
def run_flask():
    app.run(debug=True, use_reloader=False)

# Generate a random verification code
def generate_verification_code(length=6):
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# CLI Functionality
def cli_interface():
    while True:
        print("\nWelcome to the CLI interface. Choose an option:")
        print("1. List all users")
        print("2. Reset a password")
        print("3. Login as Admin")
        print("4. Register a new user")
        print("5. Quit")
        choice = input("Enter your choice: ")

        if choice == '1':
            print(json.dumps(users, indent=4))
        elif choice == '2':
            username = input("Enter the username to reset the password for: ")
            if username not in users:
                print("User does not exist.")
            else:
                email = users[username]['email']
                verification_code = generate_verification_code()
                send_verification_code(email, username, verification_code)

                user_code = input("Enter the verification code sent to your email: ")
                if user_code == verification_code:
                    new_password = input("Enter the new password: ")
                    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    users[username]['password'] = hashed.decode('utf-8')
                    save_users()
                    print(f"Password for {username} has been reset.")
                else:
                    print("Invalid verification code.")
        elif choice == '3':
            admin_username = input("Enter admin username: ")
            admin_password = input("Enter admin password: ")

            if admin_username == 'admin' and admin_password == 'admin_password':  # Replace with secure checks
                print("Admin login successful!")
                while True:
                    print("\nAdmin Menu:")
                    print("1. View all users")
                    print("2. Lock a user account")
                    print("3. Unlock a user account")
                    print("4. Return to main menu")
                    admin_choice = input("Choose an option: ")

                    if admin_choice == '1':
                        print(json.dumps(users, indent=4))
                    elif admin_choice == '2':
                        user_to_lock = input("Enter username to lock: ")
                        if user_to_lock in users:
                            users[user_to_lock]['locked'] = True
                            save_users()
                            print(f"User {user_to_lock} has been locked.")
                        else:
                            print("User does not exist.")
                    elif admin_choice == '3':
                        user_to_unlock = input("Enter username to unlock: ")
                        if user_to_unlock in users:
                            users[user_to_unlock]['locked'] = False
                            save_users()
                            print(f"User {user_to_unlock} has been unlocked.")
                        else:
                            print("User does not exist.")
                    elif admin_choice == '4':
                        break
                    else:
                        print("Invalid choice.")
        elif choice == '4':
            username = input("Enter username: ")
            password = input("Enter password: ")
            email = input("Enter email (optional): ")

            if username not in users:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                totp_secret = pyotp.random_base32()
                users[username] = {
                    'password': hashed.decode('utf-8'),
                    'totp_secret': totp_secret,
                    'email': email,
                    'role': 'user',
                    'first_login': True,
                    'failed_attempts': 0,
                    'locked': False
                }
                save_users()
                print(f"User {username} registered successfully.")
            else:
                print("User already exists.")
        elif choice == '5':
            break
        else:
            print("Invalid choice.")

# Run the Flask app and CLI in separate threads
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    cli_interface()
