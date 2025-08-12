# Database Configuration Guide

This guide explains the PostgreSQL-first database configuration with SQLite fallback for your Django application.

## Configuration Overview

The application uses a smart database configuration strategy:

- **Primary**: PostgreSQL (both development and production)
- **Fallback**: SQLite (automatic fallback if PostgreSQL is unavailable)

This ensures consistency between development and production environments while maintaining flexibility.

## Database Selection Logic

The application automatically selects the database in this priority order:

1. **`DATABASE_URL`** (if set) → Uses PostgreSQL with dj-database-url (production)
2. **PostgreSQL** (default) → Uses manual PostgreSQL configuration
3. **SQLite** (fallback) → Automatic fallback if PostgreSQL is unavailable

## Development Setup

### Option 1: PostgreSQL (Recommended)

**Install PostgreSQL locally:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

**Create development database:**

```bash
# Switch to postgres user and create database
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE sk_website;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE sk_website TO postgres;
ALTER USER postgres CREATEDB;
\q
```

**Your .env file is already configured for PostgreSQL:**
```bash
DB_NAME=sk_website
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### Option 2: SQLite Fallback (Automatic)

If PostgreSQL is not available or fails to connect, the application will automatically fall back to SQLite. No configuration needed!

## Production Setup (PostgreSQL)

### Using Render (Recommended)
The `render.yaml` file is configured for PostgreSQL:

1. **Database**: Automatically creates a PostgreSQL database
2. **Connection**: Uses `DATABASE_URL` environment variable
3. **No manual setup required!**

### Manual PostgreSQL Configuration
If not using Render or need custom configuration:

```bash
# Production environment variables
DATABASE_URL=postgresql://user:password@host:port/database

# Or use manual configuration:
DB_NAME=your_production_db
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_HOST=your_db_host
DB_PORT=5432
```

## Database Commands

### With PostgreSQL
```bash
# Install dependencies first
uv sync

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Check database connection
python manage.py check --database default
```

### With SQLite Fallback
```bash
# If PostgreSQL is unavailable, these commands will use SQLite automatically
python manage.py migrate
python manage.py createsuperuser

# Reset SQLite database (if needed)
rm db.sqlite3
python manage.py migrate
```

## Benefits of PostgreSQL-First Approach

1. **Environment Consistency**: Same database engine in development and production
2. **Feature Parity**: Access to PostgreSQL-specific features during development
3. **Data Type Compatibility**: No surprises when deploying to production
4. **Flexibility**: Automatic SQLite fallback for quick setup or CI environments

## Dependencies

The following packages are automatically installed:

- `psycopg2-binary`: PostgreSQL adapter for Python
- `dj-database-url`: Parse database URLs

## Environment Variables Reference

| Variable | Description | Development Default | Production |
|----------|-------------|---------------------|------------|
| `DATABASE_URL` | Full database connection string | Not set | `postgresql://...` |
| `DB_NAME` | Database name | `sk_website` | Your production DB name |
| `DB_USER` | Database user | `postgres` | Your production user |
| `DB_PASSWORD` | Database password | `postgres` | Secure production password |
| `DB_HOST` | Database host | `localhost` | Your production host |
| `DB_PORT` | Database port | `5432` | `5432` (usually) |

## Checking Current Database

To see which database is currently being used:

```bash
python manage.py shell -c "
from django.conf import settings
db = settings.DATABASES['default']
print(f'Database Engine: {db[\"ENGINE\"]}')
if 'NAME' in db:
    print(f'Database Name: {db[\"NAME\"]}')
"
```

## Troubleshooting

### PostgreSQL Connection Issues:

1. **Service not running**:
   ```bash
   # Check if PostgreSQL is running
   sudo systemctl status postgresql  # Linux
   brew services list | grep postgres  # macOS
   ```

2. **Authentication failed**:
   - Check username and password in .env
   - Verify PostgreSQL user permissions
   - Check `pg_hba.conf` authentication settings

3. **Database doesn't exist**:
   ```bash
   # Create the database
   sudo -u postgres createdb sk_website
   ```

4. **Connection timeout**:
   - Check host and port settings
   - Verify firewall settings
   - Ensure PostgreSQL accepts connections

### SQLite Fallback Activation:

The application will automatically fall back to SQLite if:
- PostgreSQL is not installed
- PostgreSQL service is not running
- Database connection fails
- psycopg2 library is not available

### Useful Commands:

```bash
# Test PostgreSQL connection directly
psql -h localhost -U postgres -d sk_website

# Check Django database settings
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES)"

# Run database shell
python manage.py dbshell

# Check for PostgreSQL processes
ps aux | grep postgres
```

## Migration Between Databases

If you need to switch from SQLite to PostgreSQL or vice versa:

1. **Export existing data**:
   ```bash
   python manage.py dumpdata > data_backup.json
   ```

2. **Update database configuration** (change .env or install PostgreSQL)

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Import data** (if needed):
   ```bash
   python manage.py loaddata data_backup.json
   ```

Your application now provides the best of both worlds: PostgreSQL consistency with SQLite flexibility!
