#!/usr/bin/env python3

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    """Setup MySQL database and tables"""
    
    # Database connection parameters
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database_name = os.getenv('MYSQL_DATABASE', 'medical_reports')
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"✅ Database '{database_name}' created/verified")
        
        # Use the database
        cursor.execute(f"USE {database_name}")
        
        # Create reports table
        reports_table = """
        CREATE TABLE IF NOT EXISTS reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255),
            extracted_text TEXT,
            lab_values JSON,
            explanation JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_created_at (created_at)
        )
        """
        
        # Create lab_values table
        lab_values_table = """
        CREATE TABLE IF NOT EXISTS lab_values (
            id INT AUTO_INCREMENT PRIMARY KEY,
            report_id INT,
            test_name VARCHAR(100),
            test_value DECIMAL(10,2),
            normal_range VARCHAR(100),
            status ENUM('normal', 'high', 'low') DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
            INDEX idx_report_id (report_id),
            INDEX idx_test_name (test_name)
        )
        """
        
        cursor.execute(reports_table)
        cursor.execute(lab_values_table)
        
        connection.commit()
        print("✅ Tables created successfully")
        
        # Show table structure
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Tables in database: {[table[0] for table in tables]}")
        
    except Error as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

if __name__ == "__main__":
    print("🏥 Setting up Medical Report Simplifier Database...")
    
    if setup_database():
        print("✅ Database setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Update your .env file with correct MySQL credentials")
        print("2. Run: python app.py")
    else:
        print("❌ Database setup failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL server is running")
        print("2. Check your MySQL credentials in .env file")
        print("3. Ensure MySQL user has CREATE DATABASE privileges")