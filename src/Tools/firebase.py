# File: src/Tools/firebase.py

import asyncio
import aiohttp
import os
import firebase_admin
from firebase_admin import credentials, auth, firestore, initialize_app, _apps
from dotenv import load_dotenv

load_dotenv()
SERVICE_ACCOUNT_KEY_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred)

print("DEBUG at import: FIREBASE_SERVICE_ACCOUNT_KEY_PATH =", os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH"))
db = firestore.client()


load_dotenv()
SERVICE_ACCOUNT_KEY_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

class Firebase:
    def __init__(self,
                 service_account_key_path=None,
                 database_url=None,
                 api_key=None):
        """
        Initialize the Firebase Admin SDK and set up asynchronous operations.

        :param service_account_key_path: Path to the Firebase service account key JSON file.
                                         If not provided, it will be fetched from environment variable.
        :param database_url: URL of the Firebase Realtime Database.
                             If not provided, it will be fetched from environment variable.
        :param api_key: Firebase API key for REST API calls.
                        If not provided, it will be fetched from environment variable.
        """
        # Fetch configurations from environment variables if not provided
        service_account_key_path = service_account_key_path or os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
        database_url = database_url or os.getenv('FIREBASE_DATABASE_URL')
        self.api_key = api_key or os.getenv('FIREBASE_API_KEY')

        if not service_account_key_path:
            raise ValueError("Service account key path must be provided either as a parameter or via 'FIREBASE_SERVICE_ACCOUNT_KEY_PATH' environment variable.")
        if not database_url:
            raise ValueError("Database URL must be provided either as a parameter or via 'FIREBASE_DATABASE_URL' environment variable.")
        if not self.api_key:
            raise ValueError("Firebase API key must be provided either as a parameter or via 'FIREBASE_API_KEY' environment variable.")

        # Initialize Firebase app
        self.credential = credentials.Certificate(service_account_key_path)
        if not firebase_admin._apps:
            self.app = firebase_admin.initialize_app(self.credential, {
                'databaseURL': database_url
            })
        else:
            self.app = firebase_admin.get_app()

        # Create a thread pool executor for running blocking operations asynchronously
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Initialize an aiohttp session for making asynchronous HTTP requests
        self.session = aiohttp.ClientSession()

        # Event to signal that the database has been initialized
        self.initialized = asyncio.Event()

        # Start asynchronous database initialization
        asyncio.create_task(self.initialize_database())

    async def initialize_database(self):
        """
        Check if the database is empty and initialize it with default data if needed.
        Sets the 'initialized' event upon completion.
        """
        ref = db.reference('/')
        try:
            data = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
            if data is None:
                initial_data = {
                    'leaderboard': {},
                    'progress': {},
                    'users': {},
                    'badges': {},
                    'rankings': {},
                    'knowledge_tracing': {},
                    'mastery_levels': {}
                }
                await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, initial_data)
                print('Database initialized with default entries.')
            else:
                print('Database already contains data. Initialization not required.')
        except Exception as e:
            print(f'Error initializing database: {e}')
        finally:
            self.initialized.set()

    async def wait_until_initialized(self):
        """
        Wait until the database initialization is complete.
        """
        await self.initialized.wait()

    # -----------------------
    # User Data Management
    # -----------------------

    async def add_new_user_data(self, user_id, user_data):
        """
        Add a new user's data to the database.

        :param user_id: The user's unique ID.
        :param user_data: A dictionary containing user information.
        """
        ref = db.reference(f'/users/{user_id}')
        try:
            await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, user_data)
            print(f'New user data for UID {user_id} added successfully.')
        except Exception as e:
            print(f'Error adding user data for UID {user_id}: {e}')

    async def get_user_data(self, user_id):
        """
        Retrieve user data.

        :param user_id: The user's unique ID.
        :return: A dictionary containing the user's data or None if not found.
        """
        ref = db.reference(f'/users/{user_id}')
        try:
            user_data = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
            return user_data
        except Exception as e:
            print(f'Error retrieving user data for UID {user_id}: {e}')
            return None

    # -----------------------
    # User Account Management
    # -----------------------

    async def sign_up(self, email, password):
        """
        Sign up a new user using Firebase Authentication REST API.

        :param email: The user's email address.
        :param password: The user's password.
        :return: The response data or None if failed.
        """
        url = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}'
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        try:
            async with self.session.post(url, json=payload) as response:
                data = await response.json()
                if response.status == 200:
                    print('User signed up successfully via REST API.')
                    print('ID Token:', data.get('idToken'))
                    return data
                else:
                    print('Error signing up via REST API:', data)
                    return None
        except Exception as e:
            print(f'Exception during sign up via REST API: {e}')
            return None

    async def sign_in(self, email, password):
        """
        Sign in an existing user using Firebase Authentication REST API.

        :param email: The user's email address.
        :param password: The user's password.
        :return: The response data or None if failed.
        """
        url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}'
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        try:
            async with self.session.post(url, json=payload) as response:
                data = await response.json()
                if response.status == 200:
                    print('User signed in successfully via REST API.')
                    print('ID Token:', data.get('idToken'))
                    return data
                else:
                    print('Error signing in via REST API:', data)
                    return None
        except Exception as e:
            print(f'Exception during sign in via REST API: {e}')
            return None

    async def refresh_id_token(self, refresh_token):
        """
        Refresh the ID token using the refresh token.

        :param refresh_token: The user's refresh token.
        :return: The new ID token data or None if failed.
        """
        url = f'https://securetoken.googleapis.com/v1/token?key={self.api_key}'
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        try:
            async with self.session.post(url, data=payload) as response:
                data = await response.json()
                if response.status == 200:
                    print('ID Token refreshed successfully.')
                    print('New ID Token:', data.get('id_token'))
                    return data
                else:
                    print('Error refreshing ID token:', data)
                    return None
        except Exception as e:
            print(f'Exception during token refresh: {e}')
            return None

    async def create_user(self, email, password):
        """
        Create a new user with the given email and password using Firebase Admin SDK.

        :param email: The user's email address.
        :param password: The user's password.
        :return: The created user's UID or None if creation failed.
        """
        try:
            user = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: auth.create_user(
                    email=email,
                    password=password
                )
            )
            print(f'User created successfully via Admin SDK. UID: {user.uid}')
            return user.uid
        except firebase_admin.auth.EmailAlreadyExistsError:
            print(f'User with email {email} already exists.')
            try:
                user = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    lambda: auth.get_user_by_email(email)
                )
                print(f'Retrieved existing user. UID: {user.uid}')
                return user.uid
            except Exception as e:
                print(f'Error retrieving existing user: {e}')
                return None
        except Exception as e:
            print(f'Error creating user via Admin SDK: {e}')
            return None

    async def delete_user(self, user_id):
        """
        Delete the user with the given UID.

        :param user_id: The user's unique ID.
        """
        try:
            await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: auth.delete_user(user_id)
            )
            print(f'User {user_id} deleted successfully via Admin SDK.')
        except Exception as e:
            print(f'Error deleting user {user_id} via Admin SDK: {e}')

    async def verify_user(self, id_token):
        """
        Verify the user's ID token and return the user ID (uid).

        :param id_token: The Firebase ID token obtained after user authentication.
        :return: User ID (uid) if verification is successful, None otherwise.
        """
        try:
            decoded_token = await asyncio.get_event_loop().run_in_executor(
                self.executor, auth.verify_id_token, id_token
            )
            uid = decoded_token['uid']
            print(f'ID Token verified. UID: {uid}')
            return uid
        except Exception as e:
            print('Authentication error:', e)
            return None

    # -----------------------
    # Progress Management
    # -----------------------

    async def update_user_progress(self, user_id, subject_id, lesson_id, progress_data):
        """
        Update the progress of a user for a specific lesson in a subject.

        :param user_id: The user's unique ID.
        :param subject_id: The subject's unique ID.
        :param lesson_id: The lesson's unique ID.
        :param progress_data: A dictionary containing progress information.
        """
        ref = db.reference(f'/progress/{user_id}/{subject_id}/{lesson_id}')
        try:
            await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, progress_data)
            print(f'Progress for user {user_id} on subject "{subject_id}", lesson "{lesson_id}" updated successfully.')
        except Exception as e:
            print(f'Error updating progress for user {user_id}, subject "{subject_id}", lesson "{lesson_id}": {e}')

    async def get_user_progress(self, user_id):
        """
        Retrieve the progress data for a specific user.

        :param user_id: The user's unique ID.
        :return: A dictionary containing the user's progress data or None if not found.
        """
        ref = db.reference(f'/progress/{user_id}')
        try:
            progress = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
            return progress
        except Exception as e:
            print(f'Error retrieving progress for user {user_id}: {e}')
            return None

    # -----------------------
    # Leaderboard Management
    # -----------------------

    async def update_leaderboard(self, user_id, username, new_score):
        """
        Update the leaderboard with the user's score if it's higher than the existing score.

        :param user_id: The user's unique ID.
        :param username: The user's username.
        :param new_score: The new score to compare against the existing score.
        """
        ref = db.reference(f'/leaderboard/{user_id}')

        def transaction_update(current_data):
            current_data = current_data or {}
            current_score = current_data.get('score', 0)
            if new_score > current_score:
                current_data['username'] = username
                current_data['score'] = new_score
            return current_data

        try:
            await asyncio.get_event_loop().run_in_executor(self.executor, ref.transaction, transaction_update)
            print(f'Leaderboard updated for user {user_id}.')
        except Exception as e:
            print(f'Error updating leaderboard for user {user_id}: {e}')

    async def get_leaderboard(self, limit=10):
        """
        Retrieve the leaderboard ordered by score in descending order.

        :param limit: The maximum number of top scores to retrieve.
        :return: A list of dictionaries containing user IDs, usernames, and scores.
        """
        ref = db.reference('/leaderboard')
        try:
            snapshot = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: ref.order_by_child('score').limit_to_last(limit).get()
            )
            leaderboard = []
            # Reverse the order since limit_to_last returns ascending order
            if snapshot:
                for key, val in reversed(list(snapshot.items())):
                    leaderboard.append({
                        'user_id': key,
                        'username': val.get('username'),
                        'score': val.get('score')
                    })
            return leaderboard
        except Exception as e:
            print(f'Error retrieving leaderboard: {e}')
            return []

    # -----------------------
    # Badges Management
    # -----------------------

    async def award_badge(self, user_id, badge_id, badge_data):
        """
        Award a badge to a user.

        :param user_id: The user's unique ID.
        :param badge_id: The badge's unique ID.
        :param badge_data: A dictionary containing badge information.
        """
        ref = db.reference(f'/badges/{user_id}/{badge_id}')
        try:
            await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, badge_data)
            print(f'Badge "{badge_id}" awarded to user {user_id}.')
        except Exception as e:
            print(f'Error awarding badge "{badge_id}" to user {user_id}: {e}')

    async def get_user_badges(self, user_id):
        """
        Retrieve all badges earned by a user.

        :param user_id: The user's unique ID.
        :return: A dictionary of badges earned by the user or None if not found.
        """
        ref = db.reference(f'/badges/{user_id}')
        try:
            badges = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
            return badges
        except Exception as e:
            print(f'Error retrieving badges for user {user_id}: {e}')
            return None

    # -----------------------
    # Rankings Management
    # -----------------------

    async def update_rankings(self, ranking_type, user_id, rank_data):
        """
        Update rankings for a specific type (e.g., overall, subject-specific).

        :param ranking_type: The type of ranking (e.g., 'overall', 'subject_math').
        :param user_id: The user's unique ID.
        :param rank_data: A dictionary containing ranking information.
        """
        ref = db.reference(f'/rankings/{ranking_type}/{user_id}')
        try:
            await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, rank_data)
            print(f'Rankings updated for user {user_id} in "{ranking_type}".')
        except Exception as e:
            print(f'Error updating rankings for user {user_id} in "{ranking_type}": {e}')

    async def get_rankings(self, ranking_type, limit=10):
        """
        Retrieve rankings for a specific type.

        :param ranking_type: The type of ranking.
        :param limit: The maximum number of top rankings to retrieve.
        :return: A list of dictionaries containing user IDs and ranking data.
        """
        ref = db.reference(f'/rankings/{ranking_type}')
        try:
            snapshot = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: ref.order_by_child('rank').limit_to_first(limit).get()
            )
            rankings = []
            if snapshot:
                for key, val in snapshot.items():
                    rankings.append({
                        'user_id': key,
                        'rank_data': val
                    })
            return rankings
        except Exception as e:
            print(f'Error retrieving rankings for "{ranking_type}": {e}')
            return []

    # -----------------------
    # Knowledge Tracing Management
    # -----------------------

    async def update_knowledge_tracing(self, user_id, subject_id, knowledge_level):
        """
        Update the knowledge tracing level for a user in a specific subject.

        :param user_id: The user's unique ID.
        :param subject_id: The subject's unique ID.
        :param knowledge_level: A float representing the knowledge level (e.g., 0.0 to 1.0).
        """
        ref = db.reference(f'/knowledge_tracing/{user_id}/{subject_id}')
        data = {'knowledge_level': knowledge_level}
        try:
            await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, data)
            print(f'Knowledge tracing level updated for user {user_id} in subject "{subject_id}".')
        except Exception as e:
            print(f'Error updating knowledge tracing for user {user_id} in subject "{subject_id}": {e}')

    async def get_knowledge_tracing(self, user_id):
        """
        Retrieve the knowledge tracing levels for a user.

        :param user_id: The user's unique ID.
        :return: A dictionary of subjects and their knowledge levels or None if not found.
        """
        ref = db.reference(f'/knowledge_tracing/{user_id}')
        try:
            knowledge_data = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
            return knowledge_data
        except Exception as e:
            print(f'Error retrieving knowledge tracing for user {user_id}: {e}')
            return None

    # -----------------------
    # Mastery Level Management
    # -----------------------

    async def update_mastery_level(self, user_id, subject_id, mastery_level):
        """
        Update the mastery level for a user in a specific subject.

        :param user_id: The user's unique ID.
        :param subject_id: The subject's unique ID.
        :param mastery_level: A string representing the mastery level (e.g., 'Beginner', 'Intermediate', 'Advanced').
        """
        ref = db.reference(f'/mastery_levels/{user_id}/{subject_id}')
        data = {'mastery_level': mastery_level}
        try:
            await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, data)
            print(f'Mastery level updated for user {user_id} in subject "{subject_id}".')
        except Exception as e:
            print(f'Error updating mastery level for user {user_id} in subject "{subject_id}": {e}')

    async def get_mastery_levels(self, user_id):
        """
        Retrieve the mastery levels for a user.

        :param user_id: The user's unique ID.
        :return: A dictionary of subjects and their mastery levels or None if not found.
        """
        ref = db.reference(f'/mastery_levels/{user_id}')
        try:
            mastery_data = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
            return mastery_data
        except Exception as e:
            print(f'Error retrieving mastery levels for user {user_id}: {e}')
            return None

    # -----------------------
    # Additional Utility Methods
    # -----------------------

    async def increment_user_score(self, user_id, subject_id, lesson_id, increment):
        """
        Atomically increment a user's score for a specific lesson in a subject.

        :param user_id: The user's unique ID.
        :param subject_id: The subject's unique ID.
        :param lesson_id: The lesson's unique ID.
        :param increment: The amount to increment the score by.
        """
        ref = db.reference(f'/progress/{user_id}/{subject_id}/{lesson_id}/score')

        def transaction_score(current_value):
            return (current_value or 0) + increment

        try:
            await asyncio.get_event_loop().run_in_executor(self.executor, ref.transaction, transaction_score)
            print(f'Score for user {user_id} on subject "{subject_id}", lesson "{lesson_id}" incremented by {increment}.')
        except Exception as e:
            print(f'Error incrementing score for user {user_id} on subject "{subject_id}", lesson "{lesson_id}": {e}')
            
    # -----------------------
    # Cleanup Method
    # -----------------------

    async def close(self):
        """
        Close the aiohttp session and shutdown the executor.
        """
        try:
            await self.session.close()
            self.executor.shutdown(wait=True)
            print('Firebase resources have been cleaned up.')
        except Exception as e:
            print(f'Error during cleanup: {e}')

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    # --------------------------------------------------------
    # Firestore Integration for Session Sync - Author: Rakesh
    # --------------------------------------------------------

def get_firestore_client(service_account_key_path=None, database_url=None):
    """
    Returns a Firestore client, initializing the Firebase app if needed.
    Uses the same parameter/env variable fallback pattern as the Firebase class.
    """
    # Fetch from arguments first, else from environment variables
    service_account_key_path = service_account_key_path or os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
    database_url = database_url or os.getenv('FIREBASE_DATABASE_URL')

    # DEBUG: Show what's being used (remove or comment)
    #print("DEBUG: Firestore client init with service_account_key_path =", service_account_key_path)
    #print("DEBUG: Firestore client init with database_url =", database_url)

    if not service_account_key_path:
        raise ValueError("Service account key path must be provided either as a parameter or via 'FIREBASE_SERVICE_ACCOUNT_KEY_PATH' environment variable.")
    if not database_url:
        raise ValueError("Database URL must be provided either as a parameter or via 'FIREBASE_DATABASE_URL' environment variable.")

    # Initialize Firebase app if not already done
    if not _apps:
        cred = credentials.Certificate(service_account_key_path)
        initialize_app(cred, {'databaseURL': database_url})

    return firestore.client()

    # ----------------------------------------------
    # Save session to firebases  - Author: Rakesh
    # ----------------------------------------------

# def save_session_to_firestore(session_data, user_uid):
#     """
#     Save the chat session data to Firestore under the user's UID.
#     """
#     # Save to users/{user_uid}/sessions/{session_id}
#     print(f"Saving to Firestore for user_uid: {user_id}")
#     user_id = user_uid or session_data.get('user_id')
#     session_id = session_data.get('session_id')
#     if not user_id or not session_id:
#         print("Missing user ID or session ID for Firestore save.")
#         return
#     try:
#         # Reference: users/{user_id}/sessions/{session_id}
#         doc_ref = db.collection("users").document(user_id).collection("sessions").document(session_id)
#         doc_ref.set(session_data)
#         print(f"Session data saved to Firestore at users/{user_id}/sessions/{session_id}")
#     except Exception as e:
#         print(f"Error saving session to Firestore: {e}")

def save_session_to_firestore(session_data, user_uid):
    """
    Save the chat session data to Firestore under the user's UID.
    """
    user_id = user_uid or session_data.get('user_uid')
    session_id = session_data.get('session_uid')
    if not user_id or not session_id:
        print("Missing user ID or session ID for Firestore save.")
        print("DEBUG: user_id =", user_id)
        print("DEBUG: session_id =", session_id)
        print("DEBUG: session_data keys:", list(session_data.keys()))
        return
    try:
        # Only Firestore syntax!
        doc_ref = db.collection("users").document(user_id).collection("sessions").document(session_id)
        doc_ref.set(session_data)
        print(f"Session data saved to Firestore at users/{user_id}/sessions/{session_id}")
    except Exception as e:
        print(f"Error saving session to Firestore: {e}")
