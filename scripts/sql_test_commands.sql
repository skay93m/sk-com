-- SQL commands to test database functionality
-- Run these in Django dbshell: uv run manage.py dbshell

-- 1. Check database connection and basic info
SELECT version();

-- 2. List all tables
\dt

-- 3. Check Django's built-in tables
SELECT COUNT(*) as user_count FROM auth_user;
SELECT COUNT(*) as session_count FROM django_session;

-- 4. Test basic CRUD with a simple table query
-- Check the structure of auth_user table
\d auth_user

-- 5. Create a test entry (we'll clean it up)
INSERT INTO auth_user (username, email, password, is_staff, is_active, is_superuser, date_joined, first_name, last_name) 
VALUES ('sql_test_user', 'sqltest@example.com', 'pbkdf2_sha256$260000$dummy', false, true, false, NOW(), '', '');

-- 6. Read the entry
SELECT id, username, email, date_joined FROM auth_user WHERE username = 'sql_test_user';

-- 7. Update the entry
UPDATE auth_user SET email = 'updated_sqltest@example.com' WHERE username = 'sql_test_user';

-- 8. Verify update
SELECT id, username, email FROM auth_user WHERE username = 'sql_test_user';

-- 9. Delete the entry
DELETE FROM auth_user WHERE username = 'sql_test_user';

-- 10. Verify deletion
SELECT COUNT(*) FROM auth_user WHERE username = 'sql_test_user';

-- 11. Test transaction (this will be rolled back)
BEGIN;
INSERT INTO auth_user (username, email, password, is_staff, is_active, is_superuser, date_joined, first_name, last_name) 
VALUES ('transaction_test', 'trans@example.com', 'pbkdf2_sha256$260000$dummy', false, true, false, NOW(), '', '');
SELECT username FROM auth_user WHERE username = 'transaction_test';
ROLLBACK;

-- 12. Verify rollback worked
SELECT COUNT(*) FROM auth_user WHERE username = 'transaction_test';
