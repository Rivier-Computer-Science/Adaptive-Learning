import unittest
import os
from io import BytesIO
from flask import Flask
from werkzeug.datastructures import FileStorage
from src.web_app import app, dashboard

class WebAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True
        # Ensure the uploads directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    def setUp(self):
        # Create a test file
        self.test_csv = 'test_data.csv'
        with open(self.test_csv, 'w') as f:
            f.write("student_id,accuracy,time_taken,improvement\n")
            f.write("1,90.5,5,15\n")
            f.write("2,85.0,7,10\n")

    def tearDown(self):
        # Remove test file
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        
        # Remove files from uploads directory
        upload_folder = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Remove uploads directory
        if os.path.exists(upload_folder):
            os.rmdir(upload_folder)

    def test_file_upload(self):
        with open(self.test_csv, 'rb') as f:
            data = {
                'file': (BytesIO(f.read()), self.test_csv)
            }
            response = self.app.post('/', content_type='multipart/form-data', data=data)
            self.assertEqual(response.status_code, 302)  # Should redirect to /report

    def test_report_generation(self):
        with open(self.test_csv, 'rb') as f:
            data = {
                'file': (BytesIO(f.read()), self.test_csv)
            }
            self.app.post('/', content_type='multipart/form-data', data=data)
            response = self.app.get('/report')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<img src="data:image/png;base64,', response.data)  # Check if image is rendered

if __name__ == '__main__':
    unittest.main()
