import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tech_nova.db")

def get_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database and create tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT,
        location TEXT,
        medical_history TEXT,
        medications TEXT,
        family_history TEXT,
        neurological_conditions TEXT,
        previous_screening TEXT,
        created_at TEXT
    )
    """)
    
    # Create screenings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        screening_date TEXT,
        symptom_score REAL,
        voice_score REAL,
        writing_score REAL,
        gait_score REAL,
        final_score REAL,
        risk_category TEXT,
        contributing_factors TEXT,
        recommendation TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
    )
    """)
    
    conn.commit()
    conn.close()

def save_patient(patient_data):
    """Save or update a patient profile."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT OR REPLACE INTO patients (
        patient_id, name, age, gender, location, 
        medical_history, medications, family_history, 
        neurological_conditions, previous_screening, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_data.get("patient_id"),
        patient_data.get("name"),
        patient_data.get("age"),
        patient_data.get("gender"),
        patient_data.get("location"),
        patient_data.get("medical_history"),
        patient_data.get("medications"),
        patient_data.get("family_history"),
        patient_data.get("neurological_conditions"),
        patient_data.get("previous_screening"),
        patient_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ))
    
    conn.commit()
    conn.close()

def save_screening(screening_data):
    """Save a screening record."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO screenings (
        patient_id, screening_date, symptom_score, voice_score, 
        writing_score, gait_score, final_score, risk_category, 
        contributing_factors, recommendation
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        screening_data.get("patient_id"),
        screening_data.get("screening_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        screening_data.get("symptom_score"),
        screening_data.get("voice_score"),
        screening_data.get("writing_score"),
        screening_data.get("gait_score"),
        screening_data.get("final_score"),
        screening_data.get("risk_category"),
        json.dumps(screening_data.get("contributing_factors", [])),
        screening_data.get("recommendation")
    ))
    
    conn.commit()
    conn.close()

def get_patient(patient_id):
    """Retrieve patient details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_screening_history(patient_id):
    """Retrieve all screening records for a specific patient sorted by date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM screenings 
        WHERE patient_id = ? 
        ORDER BY datetime(screening_date) ASC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        d = dict(row)
        d["contributing_factors"] = json.loads(d["contributing_factors"])
        history.append(d)
    return history

def get_all_patients():
    """Retrieve all patient records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
