# SK Application Test Suite

This directory contains comprehensive tests for the main functionality of the SK application.

## Test File: `tests.py`

### Overview
The test suite covers five main areas of functionality with 25 total tests:

### 1. URL Routing Tests (`URLRoutingTest`)
- **Purpose**: Validates URL configuration and routing
- **Tests (5)**:
  - Admin URL resolution
  - Secure admin login URL resolution  
  - Secure admin logout URL resolution
  - Robots.txt URL resolution
  - App URLs inclusion verification

### 2. Secure Admin Views Tests (`SecureAdminViewsTest`)
- **Purpose**: Tests secure admin login/logout functionality
- **Tests (5)**:
  - GET request to secure admin login
  - POST with valid credentials (sets session flag)
  - POST with invalid credentials
  - Secure admin logout (clears session flag)
  - Login with 'next' parameter redirection

### 3. Security Middleware Tests (`SecurityMiddlewareTest`)
- **Purpose**: Tests detection of malicious/suspicious requests
- **Tests (5)**:
  - PHP file detection
  - WordPress path detection
  - Legitimate request allowance
  - Config file access detection
  - Case-insensitive detection

### 4. Secure Admin Middleware Tests (`SecureAdminMiddlewareTest`)
- **Purpose**: Tests admin access protection
- **Tests (5)**:
  - Admin login page access allowance
  - Unauthenticated user blocking
  - Authenticated user without flag blocking
  - Authenticated user with flag allowance
  - Non-admin URL access allowance

### 5. Robots.txt View Tests (`RobotsTxtViewTest`)
- **Purpose**: Tests robots.txt serving functionality
- **Tests (5)**:
  - Content-Type header verification
  - Admin disallow rules presence
  - Secure admin disallow rules presence
  - File reading when exists
  - Cache header presence

## Running the Tests

To run all SK application tests:
```bash
python manage.py test sk.tests
```

To run with verbose output:
```bash
python manage.py test sk.tests -v 2
```

To run a specific test class:
```bash
python manage.py test sk.tests.URLRoutingTest
```

## Test Coverage

The test suite provides comprehensive coverage of:
- ✅ URL routing and configuration
- ✅ Authentication and session management
- ✅ Security middleware functionality
- ✅ Admin access protection
- ✅ Static file serving (robots.txt)

All tests use Django's built-in testing framework and include proper setup/teardown, mocking where necessary, and comprehensive assertions.
