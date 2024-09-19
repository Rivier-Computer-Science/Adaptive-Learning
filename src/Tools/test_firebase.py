# File: src/Tools/test_firebase.py

import asyncio
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),  # Default to INFO if LOG_LEVEL not set
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import the Firebase class
from src.Tools.firebase import Firebase  # Adjust the import path as necessary

async def main():

    # Log Current Working Directory
    current_dir = Path.cwd()
    logger.info(f"Current Working Directory: {current_dir}")

    # Retrieve Environment Variables
    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
    database_url = os.getenv('FIREBASE_DATABASE_URL')
    api_key = os.getenv('FIREBASE_API_KEY')

    # Log Environment Variables
    logger.info(f"FIREBASE_SERVICE_ACCOUNT_KEY_PATH: {service_account_path}")
    logger.info(f"FIREBASE_DATABASE_URL: {database_url}")
    # Mask the API key for security
    if api_key and len(api_key) > 4:
        masked_api_key = f"{'*' * (len(api_key) - 4)}{api_key[-4:]}"
    else:
        masked_api_key = "Not Set"
    logger.info(f"FIREBASE_API_KEY: {masked_api_key}")

    # Verify Service Account File Exists
    service_account_file = Path(service_account_path)
    if service_account_file.is_file():
        logger.info(f"Service account file found at: {service_account_file.resolve()}")
    else:
        logger.error(f"Service account file NOT found at: {service_account_file.resolve()}")
        return  # Exit if the service account file is missing


    # Initialize the Firebase class with environment variables
    try:
        firebase = Firebase(
            service_account_key_path=os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH'),
            database_url=os.getenv('FIREBASE_DATABASE_URL'),
            api_key=os.getenv('FIREBASE_API_KEY')
        )
    except ValueError as ve:
        logger.error(f'Initialization Error: {ve}')
        return
    except Exception as e:
        logger.error(f'Unexpected Initialization Error: {e}')
        return

    try:
        # Wait until the database is initialized
        await firebase.wait_until_initialized()

        # User credentials
        email = 'john@glossner.org'
        password = 'SecurePassw0rd!'

        logger.info("\n=== Creating User Account via Admin SDK ===")
        # Create a new user via Admin SDK
        user_id = await firebase.create_user(email, password)
        if not user_id:
            logger.error("Failed to create or retrieve user via Admin SDK. Exiting test.")
            return

        logger.info("\n=== Populating User Data ===")
        # User data to populate
        user_data = {
            'username': 'John Glossner',
            'email': email,
            'created_at': '2024-04-27T12:00:00Z'
        }
        await firebase.add_new_user_data(user_id, user_data)

        # Populate Progress
        progress_data_lesson1 = {
            'completed': True,
            'score': 88,
            'timestamp': '2024-04-27T12:30:00Z'
        }
        progress_data_lesson2 = {
            'completed': False,
            'score': None,
            'timestamp': '2024-04-27T13:00:00Z'
        }
        await firebase.update_user_progress(user_id, 'math', 'lesson1', progress_data_lesson1)
        await firebase.update_user_progress(user_id, 'math', 'lesson2', progress_data_lesson2)

        # Populate Badges
        badge_data = {
            'name': 'Math Starter',
            'description': 'Completed the first math lesson.',
            'awarded_at': '2024-04-27T12:35:00Z'
        }
        await firebase.award_badge(user_id, 'badge_math_starter', badge_data)

        logger.info("\n=== Retrieving and Printing User Data ===")
        # Retrieve and print user data
        retrieved_user_data = await firebase.get_user_data(user_id)
        logger.info(f"User Data for {email}: {retrieved_user_data}")

        # Retrieve and print user progress
        retrieved_progress = await firebase.get_user_progress(user_id)
        logger.info(f"User Progress for {email}: {retrieved_progress}")

        # Retrieve and print user badges
        retrieved_badges = await firebase.get_user_badges(user_id)
        logger.info(f"User Badges for {email}: {retrieved_badges}")

        # Retrieve and print leaderboard
        logger.info("\n=== Retrieving Leaderboard ===")
        leaderboard = await firebase.get_leaderboard(limit=10)
        logger.info("Leaderboard:")
        for entry in leaderboard:
            logger.info(f"Username: {entry['username']}, Score: {entry['score']}")

        # Optionally, update leaderboard with user's score
        logger.info("\n=== Updating Leaderboard ===")
        await firebase.update_leaderboard(user_id, 'John Glossner', 1500)

        # Retrieve and print updated leaderboard
        updated_leaderboard = await firebase.get_leaderboard(limit=10)
        logger.info("Updated Leaderboard:")
        for entry in updated_leaderboard:
            logger.info(f"Username: {entry['username']}, Score: {entry['score']}")

        # Clean up: Delete the user account via Admin SDK
        logger.info("\n=== Deleting User Account via Admin SDK ===")
        await firebase.delete_user(user_id)
        logger.info(f"User account {email} has been deleted.")

    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
    finally:
        # Ensure that resources are cleaned up
        try:
            await firebase.close()
        except Exception as e:
            logger.error(f'Error during cleanup: {e}')

if __name__ == '__main__':
    asyncio.run(main())





# import asyncio
# from aiohttp import web
# from src.Tools.firebase import Firebase

# async def handle_request(request):
#     # Extract the ID token from the request
#     data = await request.json()
#     id_token = data.get('idToken')

#     # Initialize Firebase instance
#     firebase = Firebase()

#     # Verify the user
#     user_id = await firebase.verify_user(id_token)

#     if user_id:
#         # Proceed with authenticated actions
#         progress_data = {
#             'completed': True,
#             'score': 95
#         }
#         await firebase.update_user_progress(user_id, 'math', 'lesson1', progress_data)

#         return web.json_response({'status': 'success'})
#     else:
#         return web.json_response({'status': 'error', 'message': 'Invalid ID token'}, status=401)

# app = web.Application()
# app.router.add_post('/update-progress', handle_request)

# if __name__ == '__main__':
#     web.run_app(app, port=8080)


# async def main():
#     firebase = Firebase()
#     # ... your code ...
#     firebase.executor.shutdown(wait=True)

# import asyncio

# async def main():
#     # Initialize the Firebase class
#     firebase = Firebase()

#     # Simulated ID token from client authentication
#     simulated_id_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6Ijc2OTY...'

#     # Verify the user
#     user_id = await firebase.verify_user(simulated_id_token)

#     if user_id:
#         # Add new user data if not already present
#         user_data = await firebase.get_user_data(user_id)
#         if user_data is None:
#             user_data = {
#                 'username': 'Alice',
#                 'email': 'alice@example.com'
#             }
#             await firebase.add_new_user(user_id, user_data)

#         # Update user progress
#         progress_data = {
#             'completed': True,
#             'score': 95
#         }
#         await firebase.update_user_progress(user_id, 'math', 'lesson1', progress_data)

#         # Retrieve user progress
#         user_progress = await firebase.get_user_progress(user_id)
#         print('User Progress:', user_progress)

#         # Award a badge
#         badge_data = {
#             'name': 'Math Whiz',
#             'description': 'Completed all math lessons.'
#         }
#         await firebase.award_badge(user_id, 'badge_math_whiz', badge_data)

#         # Retrieve badges
#         badges = await firebase.get_user_badges(user_id)
#         print('Badges:', badges)

#         # Update knowledge tracing level
#         await firebase.update_knowledge_tracing(user_id, 'math', 0.85)

#         # Retrieve knowledge tracing data
#         knowledge_data = await firebase.get_knowledge_tracing(user_id)
#         print('Knowledge Tracing:', knowledge_data)

#         # Update mastery level
#         await firebase.update_mastery_level(user_id, 'math', 'Intermediate')

#         # Retrieve mastery levels
#         mastery_levels = await firebase.get_mastery_levels(user_id)
#         print('Mastery Levels:', mastery_levels)

#         # Update leaderboard
#         await firebase.update_leaderboard(user_id, 'Alice', 1500)

#         # Retrieve leaderboard
#         leaderboard = await firebase.get_leaderboard()
#         print('Leaderboard:')
#         for entry in leaderboard:
#             print(f"Username: {entry['username']}, Score: {entry['score']}")
#     else:
#         print('User verification failed.')

# # Run the main function in the event loop
# asyncio.run(main())

