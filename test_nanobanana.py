import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Mock sys.modules for Streamlit and google.genai before importing nanobanana_app
sys.modules['streamlit'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()

import db
import nanobanana_app

class TestDB(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for testing DB module
        # Note: ':memory:' creates a new database per connection,
        # so we need to use a temporary file instead to share state across connections
        self.test_db_path = 'test_staging_app.db'
        db.DB_PATH = self.test_db_path
        db.init_db()

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_init_db_creates_users(self):
        user = db.get_user('admin')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'admin')
        self.assertTrue(user['is_admin'])

        user2 = db.get_user('testuser')
        self.assertIsNotNone(user2)
        self.assertEqual(user2['username'], 'testuser')

    def test_get_user_with_password(self):
        user = db.get_user('testuser', 'testpass')
        self.assertIsNotNone(user)

        bad_user = db.get_user('testuser', 'wrongpass')
        self.assertIsNone(bad_user)

    def test_increment_quota(self):
        user = db.get_user('testuser')
        user_id = user['id']

        # Initial is 0
        self.assertEqual(user['used_quota'], 0)

        # Increment once
        success = db.increment_quota(user_id)
        self.assertTrue(success)

        user_updated = db.get_user('testuser')
        self.assertEqual(user_updated['used_quota'], 1)

    def test_increment_quota_limit(self):
        user = db.get_user('testuser')
        user_id = user['id']

        # Set quota limit to 1
        conn = db.get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE users SET monthly_quota = 1 WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

        # Increment 1st time (success)
        success = db.increment_quota(user_id)
        self.assertTrue(success)

        # Increment 2nd time (fail)
        success2 = db.increment_quota(user_id)
        self.assertFalse(success2)


class TestAppFunctions(unittest.TestCase):
    def test_format_style_option(self):
        self.assertEqual(nanobanana_app.format_style_option(0), "モダン")
        self.assertEqual(nanobanana_app.format_style_option(1), "北欧風")

    @patch('nanobanana_app.Image')
    def test_add_watermark_failure_returns_original(self, mock_image):
        # Mock Image.open to raise an exception to test failure path
        mock_image.open.side_effect = Exception("Mocked PIL Error")

        original_bytes = b"original_image_data"
        result_bytes = nanobanana_app.add_watermark(original_bytes, "Test Mansion")

        # Should return original if error occurs
        self.assertEqual(result_bytes, original_bytes)

    @patch('nanobanana_app.os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_image(self, mock_open, mock_makedirs):
        img_bytes = b"fake_img"
        path = nanobanana_app.save_image(img_bytes, "test_dir", "prefix")

        mock_makedirs.assert_called_once_with("test_dir", exist_ok=True)
        self.assertTrue(path.startswith("test_dir/prefix_"))
        self.assertTrue(path.endswith(".png"))
        mock_open.assert_called_once_with(path, "wb")
        mock_open().write.assert_called_once_with(img_bytes)

if __name__ == '__main__':
    unittest.main()
