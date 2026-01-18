import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import os

class MySQLDatabase:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                database=os.getenv('MYSQL_DATABASE', 'medical_reports'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', '')
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
    
    def create_tables(self):
        """Create necessary tables"""
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        
        # Reports table
        reports_table = """
        CREATE TABLE IF NOT EXISTS reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255),
            extracted_text TEXT,
            lab_values JSON,
            explanation JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Lab values table
        lab_values_table = """
        CREATE TABLE IF NOT EXISTS lab_values (
            id INT AUTO_INCREMENT PRIMARY KEY,
            report_id INT,
            test_name VARCHAR(100),
            test_value DECIMAL(10,2),
            normal_range VARCHAR(100),
            status ENUM('normal', 'high', 'low'),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES reports(id)
        )
        """
        
        try:
            cursor.execute(reports_table)
            cursor.execute(lab_values_table)
            self.connection.commit()
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()
    
    def save_report(self, filename, extracted_text, lab_values, explanation):
        """Save report analysis to database"""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor()
        
        try:
            # Insert report
            insert_report = """
            INSERT INTO reports (filename, extracted_text, lab_values, explanation)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_report, (
                filename,
                extracted_text,
                json.dumps(lab_values),
                json.dumps(explanation)
            ))
            
            report_id = cursor.lastrowid
            
            # Insert individual lab values
            for test_name, value in lab_values.items():
                if isinstance(value, (int, float)):
                    insert_lab_value = """
                    INSERT INTO lab_values (report_id, test_name, test_value)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(insert_lab_value, (report_id, test_name, value))
            
            self.connection.commit()
            return report_id
            
        except Error as e:
            print(f"Error saving report: {e}")
            return None
        finally:
            cursor.close()
    
    def get_report(self, report_id):
        """Get report by ID"""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
            report = cursor.fetchone()
            
            if report:
                report['lab_values'] = json.loads(report['lab_values'])
                report['explanation'] = json.loads(report['explanation'])
            
            return report
            
        except Error as e:
            print(f"Error getting report: {e}")
            return None
        finally:
            cursor.close()
    
    def get_recent_reports(self, limit=10):
        """Get recent reports"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT id, filename, created_at 
                FROM reports 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error getting recent reports: {e}")
            return []
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()