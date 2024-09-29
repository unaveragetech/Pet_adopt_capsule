from install_requirements import install_requirements
from flask import Flask, request, jsonify, session, redirect, url_for
import bcrypt
import pyotp
import json
import os
# Call the function to install dependencies
install_requirements()

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

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if username in users:
        return jsonify({'error': 'User already exists!'}), 400

    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Generate TOTP secret
    totp_secret = pyotp.random_base32()

    users[username] = {
        'password': hashed.decode('utf-8'),
        'totp_secret': totp_secret
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
    return jsonify({'message': 'Login successful!', 'totp_secret': user['totp_secret']})

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

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
