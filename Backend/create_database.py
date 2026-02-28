#!/usr/bin/env python
"""Create PostgreSQL database for college portal"""
import psycopg2
from psycopg2 import sql

try:
    # Connect to default database
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Try to create database
    try:
        cursor.execute("CREATE DATABASE college_portal")
        print("✓ Database 'college_portal' created successfully")
    except psycopg2.errors.DuplicateDatabase:
        print("ℹ Database 'college_portal' already exists")
    
    cursor.close()
    conn.close()
except psycopg2.OperationalError as e:
    print(f"✗ Connection failed: {e}")
    print("\nPlease ensure PostgreSQL is running and password is correct")
