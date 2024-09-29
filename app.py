import json
import os
import bcrypt
import pyotp
import time
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this for production

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

# User Input Validation
def is_valid_username(username):
    return username.isalnum() and len(username) > 3

def is_valid_password(password):
    return len(password) >= 8

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if not is_valid_username(username):
        return jsonify({'error': 'Username must be alphanumeric and at least 4 characters long!'}), 400
    if not is_valid_password(password):
        return jsonify({'error': 'Password must be at least 8 characters long!'}), 400

    if username in users:
        return jsonify({'error': 'User already exists!'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    totp_secret = pyotp.random_base32()

    users[username] = {
        'password': hashed.decode('utf-8'),
        'totp_secret': totp_secret,
        'last_active': time.time()
    }
    save_users()
    return jsonify({'message': 'User registered successfully!'})

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = users.get(username)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials!'}), 400

    session['username'] = username
    users[username]['last_active'] = time.time()  # Update last active time
    return jsonify({'message': 'Login successful!', 'totp_secret': user['totp_secret']})

@app.route('/verify_totp', methods=['POST'])
def verify_totp():
    username = session.get('username')
    if not username or (time.time() - users[username]['last_active'] > 300):
        return jsonify({'error': 'Session expired or user not logged in!'}), 403

    user = users[username]
    totp = request.json.get('totp')
    
    totp_gen = pyotp.TOTP(user['totp_secret'])
    if totp_gen.verify(totp):
        return jsonify({'message': '2FA verification successful!'})
    return jsonify({'error': 'Invalid TOTP!'}), 400

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully!'})

@app.route('/reset_password', methods=['POST'])
def reset_password():
    username = request.json.get('username')
    new_password = request.json.get('new_password')

    if username not in users:
        return jsonify({'error': 'User does not exist!'}), 404
    
    if not is_valid_password(new_password):
        return jsonify({'error': 'New password must be at least 8 characters long!'}), 400

    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    users[username]['password'] = hashed.decode('utf-8')
    save_users()
    return jsonify({'message': 'Password reset successfully!'})

@app.route('/admin/users', methods=['GET'])
def admin_users():
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True)
