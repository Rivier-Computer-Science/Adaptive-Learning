import asyncio
import firebase_admin
from firebase_admin import credentials, db, auth
from concurrent.futures import ThreadPoolExecutor

class Firebase:
    def __init__(self,
                 service_account_key_path='adaptive-learning-rivier-firebase-adminsdk-6u1pl-d8fc406e6f.json',
                 database_url='https://adaptive-learning-rivier-default-rtdb.firebaseio.com/'):
        """
        Initialize the Firebase Admin SDK and the database.
        If the database is empty, initialize it with default entries.
        """
        # Initialize Firebase app
        self.credential = credentials.Certificate(service_account_key_path)
        # Check if an app is already initialized
        if not firebase_admin._apps:
            self.app = firebase_admin.initialize_app(self.credential, {
                'databaseURL': database_url
            })
        else:
            self.app = firebase_admin.get_app()

        # Create a thread pool executor for asynchronous operations
        self.executor = ThreadPoolExecutor(max_workers=5)

        # Initialize the database asynchronously
        asyncio.create_task(self.initialize_database())

    async def initialize_database(self):
        """
        Check if the database is empty and initialize it with default data if needed.
        """
        ref = db.reference('/')
        data = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)

        if data is None:
            # Database is empty, set up initial data
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

    # User Data Management
    async def add_new_user(self, user_id, user_data):
        """
        Add a new user to the database.
        """
        ref = db.reference(f'/users/{user_id}')
        await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, user_data)
        print(f'New user {user_id} added to the database.')

    async def get_user_data(self, user_id):
        """
        Retrieve user data.
        """
        ref = db.reference(f'/users/{user_id}')
        user_data = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
        return user_data

    # Progress Management
    async def update_user_progress(self, user_id, subject_id, lesson_id, progress_data):
        """
        Update the progress of a user for a specific lesson in a subject.
        """
        ref = db.reference(f'/progress/{user_id}/{subject_id}/{lesson_id}')
        await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, progress_data)
        print(f'Progress for user {user_id} on subject {subject_id}, lesson {lesson_id} updated successfully.')

    async def get_user_progress(self, user_id):
        """
        Retrieve the progress data for a specific user.
        """
        ref = db.reference(f'/progress/{user_id}')
        progress = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
        return progress

    # Leaderboard Management
    async def update_leaderboard(self, user_id, username, new_score):
        """
        Update the leaderboard with the user's score if it's higher than the existing score.
        """
        ref = db.reference(f'/leaderboard/{user_id}')

        def transaction_update(current_data):
            current_data = current_data or {}
            current_score = current_data.get('score', 0)
            if new_score > current_score:
                current_data['username'] = username
                current_data['score'] = new_score
            return current_data

        await asyncio.get_event_loop().run_in_executor(self.executor, ref.transaction, transaction_update)
        print(f'Leaderboard updated for user {user_id}.')

    async def get_leaderboard(self, limit=10):
        """
        Retrieve the leaderboard ordered by score in descending order.
        """
        ref = db.reference('/leaderboard')
        snapshot = await asyncio.get_event_loop().run_in_executor(
            self.executor,
            lambda: ref.order_by_child('score').limit_to_last(limit).get()
        )
        leaderboard = []
        # Reverse the order since limit_to_last returns ascending order
        for key, val in reversed(list(snapshot.items())):
            leaderboard.append({
                'user_id': key,
                'username': val.get('username'),
                'score': val.get('score')
            })
        return leaderboard

    # Badges Management
    async def award_badge(self, user_id, badge_id, badge_data):
        """
        Award a badge to a user.
        """
        ref = db.reference(f'/badges/{user_id}/{badge_id}')
        await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, badge_data)
        print(f'Badge {badge_id} awarded to user {user_id}.')

    async def get_user_badges(self, user_id):
        """
        Retrieve all badges earned by a user.
        """
        ref = db.reference(f'/badges/{user_id}')
        badges = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
        return badges

    # Rankings Management
    async def update_rankings(self, ranking_type, user_id, rank_data):
        """
        Update rankings for a specific type (e.g., overall, subject-specific).
        """
        ref = db.reference(f'/rankings/{ranking_type}/{user_id}')
        await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, rank_data)
        print(f'Rankings updated for user {user_id} in {ranking_type}.')

    async def get_rankings(self, ranking_type, limit=10):
        """
        Retrieve rankings for a specific type.
        """
        ref = db.reference(f'/rankings/{ranking_type}')
        snapshot = await asyncio.get_event_loop().run_in_executor(
            self.executor,
            lambda: ref.order_by_child('rank').limit_to_first(limit).get()
        )
        rankings = []
        for key, val in snapshot.items():
            rankings.append({
                'user_id': key,
                'rank_data': val
            })
        return rankings

    # Knowledge Tracing Management
    async def update_knowledge_tracing(self, user_id, subject_id, knowledge_level):
        """
        Update the knowledge tracing level for a user in a specific subject.
        """
        ref = db.reference(f'/knowledge_tracing/{user_id}/{subject_id}')
        data = {'knowledge_level': knowledge_level}
        await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, data)
        print(f'Knowledge tracing level updated for user {user_id} in subject {subject_id}.')

    async def get_knowledge_tracing(self, user_id):
        """
        Retrieve the knowledge tracing levels for a user.
        """
        ref = db.reference(f'/knowledge_tracing/{user_id}')
        knowledge_data = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
        return knowledge_data

    # Mastery Level Management
    async def update_mastery_level(self, user_id, subject_id, mastery_level):
        """
        Update the mastery level for a user in a specific subject.
        """
        ref = db.reference(f'/mastery_levels/{user_id}/{subject_id}')
        data = {'mastery_level': mastery_level}
        await asyncio.get_event_loop().run_in_executor(self.executor, ref.set, data)
        print(f'Mastery level updated for user {user_id} in subject {subject_id}.')

    async def get_mastery_levels(self, user_id):
        """
        Retrieve the mastery levels for a user.
        """
        ref = db.reference(f'/mastery_levels/{user_id}')
        mastery_data = await asyncio.get_event_loop().run_in_executor(self.executor, ref.get)
        return mastery_data

    # Additional Utility Methods
    async def increment_user_score(self, user_id, subject_id, lesson_id, increment):
        """
        Atomically increment a user's score for a specific lesson in a subject.
        """
        ref = db.reference(f'/progress/{user_id}/{subject_id}/{lesson_id}/score')

        def transaction_score(current_value):
            return (current_value or 0) + increment

        await asyncio.get_event_loop().run_in_executor(self.executor, ref.transaction, transaction_score)
        print(f'Score for user {user_id} on subject {subject_id}, lesson {lesson_id} incremented by {increment}.')

    # User Verification
    async def verify_user(self, id_token):
        """
        Verify the user's ID token and return the user ID (uid).
        """
        try:
            decoded_token = await asyncio.get_event_loop().run_in_executor(
                self.executor, auth.verify_id_token, id_token
            )
            uid = decoded_token['uid']
            return uid
        except Exception as e:
            print('Authentication error:', e)
            return None
