#!/bin/bash

# Reset the database by removing the existing SQLite file
rm db.sqlite3

# Remove old migrations so they get regenerated fresh
rm -rf ./digestapi/migrations

# Run initial Django migrations for built-in tables (auth, admin, etc.)
python3 manage.py migrate

# Generate new migrations based on your current models
python3 manage.py makemigrations digestapi

# Apply those new migrations to the database
python3 manage.py migrate digestapi

# Load seed data fixtures in order
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python3 manage.py loaddata books
python3 manage.py loaddata categories