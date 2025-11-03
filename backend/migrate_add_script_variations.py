"""
Database Migration: Add script variation fields to Link model
Adds fields for 3 script variations (brief, standard, conversational) and selected_script
"""
import sqlite3
import os

def migrate():
    """Add script variation fields to links table"""
    db_path = os.path.join(os.path.dirname(__file__), 'voicetree.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add script variation fields
        cursor.execute("""
            ALTER TABLE links 
            ADD COLUMN script_brief TEXT
        """)
        print("✓ Added script_brief column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("✓ script_brief column already exists")
        else:
            raise
    
    try:
        cursor.execute("""
            ALTER TABLE links 
            ADD COLUMN script_standard TEXT
        """)
        print("✓ Added script_standard column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("✓ script_standard column already exists")
        else:
            raise
    
    try:
        cursor.execute("""
            ALTER TABLE links 
            ADD COLUMN script_conversational TEXT
        """)
        print("✓ Added script_conversational column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("✓ script_conversational column already exists")
        else:
            raise
    
    try:
        cursor.execute("""
            ALTER TABLE links 
            ADD COLUMN selected_script TEXT
        """)
        print("✓ Added selected_script column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("✓ selected_script column already exists")
        else:
            raise
    
    conn.commit()
    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
