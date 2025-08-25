import sqlite3

class KnowledgeBase:
    def __init__(self, db_path='data/sprint_data.db'):
        """Initializes the connection to the SQLite database."""
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._setup_database()
        print("Knowledge Base initialized and connected.")

    def _connect(self):
        """Establishes the database connection."""
        self.conn = sqlite3.connect(self.db_path)

    def _setup_database(self):
        """Creates the necessary tables if they don't already exist."""
        cursor = self.conn.cursor()
        
        # Create sprint_history table as per the plan
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sprint_history (
                sprint_id INTEGER PRIMARY KEY,
                start_date TEXT,
                end_date TEXT,
                completed_points INTEGER,
                team_velocity REAL
            )
        ''')

        # Create developer_profiles table as per the plan
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS developer_profiles (
                developer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                specialization TEXT,
                current_workload INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
        print("Knowledge Base: Tables verified and ready.")

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("Knowledge Base connection closed.")