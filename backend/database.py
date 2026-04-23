"""
Database operations for Biological Sprinkler
SQLite database for storing analysis history
"""
import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH

class Database:
    def __init__(self):
        """Initialize database connection"""
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create analysis history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_name TEXT NOT NULL,
                crop_type TEXT NOT NULL,
                disease_name TEXT NOT NULL,
                severity INTEGER NOT NULL,
                confidence REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database initialized")
    
    def insert_analysis(self, image_name, crop_type, disease_name, severity, confidence):
        """
        Insert a new analysis record
        
        Args:
            image_name: Name of uploaded image
            crop_type: Crop type (Tomato/Potato)
            disease_name: Detected disease name
            severity: Severity percentage
            confidence: Model confidence score
        
        Returns:
            ID of inserted record
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history 
            (image_name, crop_type, disease_name, severity, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (image_name, crop_type, disease_name, severity, confidence))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_recent_analyses(self, limit=10):
        """
        Get recent analysis records
        
        Args:
            limit: Number of records to retrieve
        
        Returns:
            List of analysis records
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, image_name, crop_type, disease_name, severity, confidence, timestamp
            FROM analysis_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        records = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0],
                'image_name': r[1],
                'crop_type': r[2],
                'disease_name': r[3],
                'severity': r[4],
                'confidence': r[5],
                'timestamp': r[6]
            }
            for r in records
        ]
    
    def get_statistics(self):
        """
        Get overall statistics
        
        Returns:
            Dictionary with statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute('SELECT COUNT(*) FROM analysis_history')
        total_analyses = cursor.fetchone()[0]
        
        # Diseased vs healthy count
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN disease_name = 'Healthy' THEN 1 ELSE 0 END) as healthy_count,
                SUM(CASE WHEN disease_name != 'Healthy' THEN 1 ELSE 0 END) as diseased_count
            FROM analysis_history
        ''')
        result = cursor.fetchone()
        healthy_count = result[0] or 0
        diseased_count = result[1] or 0
        
        # Average severity
        cursor.execute('SELECT AVG(severity) FROM analysis_history')
        avg_severity = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_analyses': total_analyses,
            'healthy_count': healthy_count,
            'diseased_count': diseased_count,
            'average_severity': round(avg_severity, 2)
        }

# Create global database instance
db = Database()
