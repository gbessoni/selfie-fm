"""
Migration script to add missing columns to the links table
Adds: ai_generated_script and scraped_content columns
"""
import sqlite3
import os

def get_db_path():
    """Get the database path"""
    # Try multiple locations
    possible_paths = [
        'voicetree.db',
        '../voicetree.db',
        'backend/voicetree.db',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Default to voicetree.db in current directory
    return 'voicetree.db'

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate_database():
    """Add missing columns to links table"""
    db_path = get_db_path()
    
    print(f"Using database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        print("\nSearching for database...")
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == 'voicetree.db':
                    found_path = os.path.join(root, file)
                    print(f"Found database at: {found_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\nChecking for missing columns...")
        
        # Check and add ai_generated_script column
        if not column_exists(cursor, 'links', 'ai_generated_script'):
            print("Adding column: ai_generated_script")
            cursor.execute("ALTER TABLE links ADD COLUMN ai_generated_script TEXT;")
            print("✓ Added ai_generated_script column")
        else:
            print("✓ Column ai_generated_script already exists")
        
        # Check and add scraped_content column
        if not column_exists(cursor, 'links', 'scraped_content'):
            print("Adding column: scraped_content")
            cursor.execute("ALTER TABLE links ADD COLUMN scraped_content TEXT;")
            print("✓ Added scraped_content column")
        else:
            print("✓ Column scraped_content already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the columns were added
        print("\nVerifying links table schema:")
        cursor.execute("PRAGMA table_info(links)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
        print("\n✓ Migration completed successfully!")
        print("Dashboard should now load without errors.")
        return True
        
    except sqlite3.Error as e:
        print(f"\nERROR: Database error occurred: {e}")
        return False
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("VoiceTree Database Migration")
    print("Adding missing columns to links table")
    print("=" * 60)
    migrate_database()
