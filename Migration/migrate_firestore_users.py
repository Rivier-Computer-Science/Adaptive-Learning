"""
Author: Rakesh Madikanti
User Firestore Migration Script

Purpose:
--------
This script migrates existing Firebase Authentication users in the Firestore `users` collection
to ensure their `name`, `email`, and `gender` fields are properly encrypted using the current
Fernet key as configured in the `.env` file. 

Background:
-----------
Earlier versions of the application may have:
- Created users in Firebase Auth but not written encrypted user profile fields to Firestore.
- Used a different Fernet encryption key, resulting in fields that are missing or cannot be decrypted by the app.

Why this matters:
-----------------
- The Adaptive Learning app expects every user document in Firestore to contain `name`, `email`, and `gender` fields,
  encrypted using the current Fernet key.
- Without these fields (or if encrypted with a wrong key), user features like displaying the user’s name or writing
  session JSON will fail or show `"N/A"`.

How this script helps:
----------------------
- Reads a CSV(users_to_migrate.csv) list of user UIDs, names, emails, and genders.
            Example for users_to_migrate.csv:
            uid,name,email,gender
            <paste_uid_here>,John Doe,john@example.com,Male
            
- Encrypts each field with the current Fernet key.
- Updates or creates the appropriate Firestore document for each user.
- Ensures all users (including old ones) can log in and have their profile fields correctly displayed and used by the app.

Usage:
------
1. Update the `.env` file with the correct `FERNET_KEY` and `FIREBASE_SERVICE_ACCOUNT_KEY_PATH`.
2. Prepare a CSV file (`users_to_migrate.csv`) with columns: `uid,name,email,gender`.
3. Run this script.
4. Old users will now have their Firestore docs compatible with the current app.

"""


import os
import csv
from cryptography.fernet import Fernet
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

fernet_key = os.getenv('FERNET_KEY')
if not fernet_key:
    raise Exception("FERNET_KEY not found in .env")
cipher = Fernet(fernet_key.encode())

service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
if not service_account_path:
    raise Exception("FIREBASE_SERVICE_ACCOUNT_KEY_PATH not found in .env")
cred = credentials.Certificate(service_account_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Open and process comma-separated CSV
with open('users_to_migrate.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)  # default delimiter is comma
    for row in reader:
        user_uid = row['uid']
        real_name = row['name']
        real_email = row['email']
        real_gender = row['gender']

        encrypted_name = cipher.encrypt(real_name.encode('utf-8')).decode('utf-8')
        encrypted_email = cipher.encrypt(real_email.encode('utf-8')).decode('utf-8')
        encrypted_gender = cipher.encrypt(real_gender.encode('utf-8')).decode('utf-8')

        user_ref = db.collection('users').document(user_uid)
        user_ref.set({
            'name': encrypted_name,
            'email': encrypted_email,
            'gender': encrypted_gender
        }, merge=True)
        print(f"Updated user: {user_uid}")

print("All users migrated (comma CSV)!")
