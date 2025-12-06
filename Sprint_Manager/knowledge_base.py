# Sprint_Manager/knowledge_base.py
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sprint_history (
                sprint_id INTEGER PRIMARY KEY,
                start_date TEXT,
                end_date TEXT,
                completed_points INTEGER,
                team_velocity REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS developer_profiles (
                developer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                specialization TEXT,
                current_workload INTEGER DEFAULT 0
            )
        ''')
        
        # --- CONFIGURATION: PASTE YOUR REAL JIRA ACCOUNT ID BELOW ---
        # Get this from your Jira Profile URL: /people/557058:be4...
        # --- CONFIGURATION: PASTE YOUR REAL JIRA ACCOUNT ID BELOW ---
        MY_JIRA_ID = "712020:487fb3e9-57ff-4d9c-99c3-178179399a4f" 
        # -----------------------------------------------------------
        # -----------------------------------------------------------

        # Populates the DB with YOU as the default "FullStack" engineer
        cursor.execute('SELECT COUNT(*) FROM developer_profiles')
        if cursor.fetchone()[0] == 0:
            print("Knowledge Base: Populating initial developer profiles.")
            initial_devs = [
                (MY_JIRA_ID, 'Admin (Me)', 'FullStack', 0)
            ]
            cursor.executemany('INSERT INTO developer_profiles (developer_id, name, specialization, current_workload) VALUES (?, ?, ?, ?)', initial_devs)
        
        self.conn.commit()
        print("Knowledge Base: Tables verified and ready.")

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("Knowledge Base connection closed.")

    def get_best_assignee(self, specialization):
        """
        Finds the developer with the matching specialization.
        SAFETY NET: If no exact match is found, falls back to 'FullStack' (You) 
        so the system never crashes on assignment.
        """
        cursor = self.conn.cursor()
        
        # 1. Try to find an exact specialist (e.g., Frontend)
        query = "SELECT developer_id, name, current_workload FROM developer_profiles WHERE specialization = ? ORDER BY current_workload ASC LIMIT 1"
        cursor.execute(query, (specialization,))
        result = cursor.fetchone()
        
        if result:
            return result
            
        # 2. Fallback: Return the 'FullStack' dev (You) if no specialist exists
        print(f"  [KB] No specific '{specialization}' dev found. Fallback to FullStack.")
        cursor.execute("SELECT developer_id, name, current_workload FROM developer_profiles WHERE specialization = 'FullStack' ORDER BY current_workload ASC LIMIT 1")
        return cursor.fetchone()

    def update_developer_workload(self, developer_id, new_workload):
        """Updates the current_workload for a given developer_id."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE developer_profiles SET current_workload = ? WHERE developer_id = ?', (new_workload, developer_id))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_average_velocity(self, last_n=3):
        """Calculates the average completed issues (velocity) from the last N sprints."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT AVG(completed_points) FROM (
                SELECT completed_points FROM sprint_history
                ORDER BY end_date DESC
                LIMIT ?
            )
        ''', (last_n,))
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0

    def get_all_developer_profiles(self):
        """Fetches all developer profiles to analyze workload balance."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT developer_id, name, current_workload FROM developer_profiles')
        return cursor.fetchall()