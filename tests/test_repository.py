import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import jwt
from fastapi import HTTPException
from src.repository.auth import Hash, create_access_token, get_current_user, SECRET_KEY, ALGORITHM


class TestHash(unittest.TestCase):
    def setUp(self):
        self.hasher = Hash()
        self.plain_password = "plainpassword"
        self.hashed_password = self.hasher.get_password_hash(self.plain_password)

    def test_verify_password(self):
        self.assertTrue(self.hasher.verify_password(self.plain_password, self.hashed_password))
        self.assertFalse(self.hasher.verify_password("wrongpassword", self.hashed_password))

    def test_get_password_hash(self):
        self.assertNotEqual(self.plain_password, self.hashed_password)
        self.assertTrue(self.hasher.verify_password(self.plain_password, self.hashed_password))

class TestTokenFunctions(unittest.TestCase):
    @patch('your_module.datetime')
    @patch('your_module.jwt.encode')
    def test_create_access_token(self, mock_jwt_encode, mock_datetime):
        mock_jwt_encode.return_value = "testtoken"
        mock_datetime.now.return_value = datetime(2023, 1, 1)

        data = {"sub": "test@example.com"}
        expires_delta = 600

        token = create_access_token(data, expires_delta)

        self.assertEqual(token, "testtoken")
        mock_jwt_encode.assert_called_once()
        args, kwargs = mock_jwt_encode.call_args
        self.assertIn("exp", kwargs['to_encode'])
        self.assertEqual(kwargs['algorithm'], 'HS256')

    @patch('your_module.jwt.decode')
    @patch('your_module.get_db')
    @patch('your_module.oauth2_scheme')
    def test_get_current_user(self, mock_oauth2_scheme, mock_get_db, mock_jwt_decode):
        mock_jwt_decode.return_value = {"sub": "test@example.com"}
        mock_oauth2_scheme.return_value = "testtoken"
        
        db_session = MagicMock()
        mock_get_db.return_value = db_session

        user = MagicMock()
        db_session.query().filter().first.return_value = user

        token = "testtoken"

        current_user = get_current_user(token, db=db_session)

        self.assertEqual(current_user, user)
        mock_jwt_decode.assert_called_once_with(token, SECRET_KEY, algorithms=[ALGORITHM])
        db_session.query().filter().first.assert_called_once()

        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError
        with self.assertRaises(HTTPException):
            get_current_user(token, db=db_session)

if __name__ == '__main__':
    unittest.main()
