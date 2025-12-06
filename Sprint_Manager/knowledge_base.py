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
        
        # --- Initial Data Check (For Demo Purposes) ---
        cursor.execute('SELECT COUNT(*) FROM developer_profiles')
        if cursor.fetchone()[0] == 0:
            print("Knowledge Base: Populating initial developer profiles.")
            initial_devs = [
                ('dev_1', 'Alice Johnson', 'Frontend', 0),
                ('dev_2', 'Bob Smith', 'Backend', 0),
                ('dev_3', 'Charlie Brown', 'DevOps', 0),
                ('dev_4', 'Diana Prince', 'FullStack', 0)
            ]
            cursor.executemany('INSERT INTO developer_profiles (developer_id, name, specialization, current_workload) VALUES (?, ?, ?, ?)', initial_devs)
        
        # --- Pre-populate some history for Velocity Calculation Demo ---
        cursor.execute('SELECT COUNT(*) FROM sprint_history')
        if cursor.fetchone()[0] == 0:
             # Simulating last 3 sprints with an average velocity of ~10 issues
            print("Knowledge Base: Populating simulated sprint history.")
            history = [
                (101, '2023-09-01', '2023-09-14', 8, 8.0),
                (102, '2023-09-15', '2023-09-28', 12, 10.0),
                (103, '2023-09-29', '2023-10-12', 10, 10.0)
            ]
            cursor.executemany('INSERT INTO sprint_history (sprint_id, start_date, end_date, completed_points, team_velocity) VALUES (?, ?, ?, ?, ?)', history)

        self.conn.commit()
        print("Knowledge Base: Tables verified and ready.")

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("Knowledge Base connection closed.")

    def get_best_assignee(self, specialization):
        """Finds the developer with the matching specialization and lowest workload."""
        cursor = self.conn.cursor()
        query = "SELECT developer_id, name, current_workload FROM developer_profiles WHERE specialization = ? ORDER BY current_workload ASC LIMIT 1"
        cursor.execute(query, (specialization,))
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

    # --- NEW: B. Data-Driven Intelligence Methods ---

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
        avg_velocity = result[0] if result and result[0] is not None else 0
        print(f"  [KB] Calculated historical average velocity: {avg_velocity:.2f}")
        return avg_velocity

    def get_all_developer_profiles(self):
        """Fetches all developer profiles to analyze workload balance."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT developer_id, name, current_workload FROM developer_profiles')
        return cursor.fetchall()