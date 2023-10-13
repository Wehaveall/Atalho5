import sqlite3

# Function to create the database and its tables if they don't exist
# Function to create the database and its tables if they don't exist
def initialize_db(db_name="E:/regex.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # Create aTable if it doesn't exist, with an additional column for regex_pattern
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS aTable
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         prefix text, 
         shortcut text, 
         expansion text, 
         regex_pattern text,
         label text, 
         format boolean, 
         "case" text DEFAULT 'Diferenciar Maiúsculas/Minúsculas')
    """
    )
    
    # Create config table if it doesn't exist
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS config
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         requires_delimiter TEXT DEFAULT 'yes', 
         delimiters TEXT DEFAULT 'space,enter')
    """
    )
    
    # Insert default values into config table
    c.execute(
        """
        INSERT OR IGNORE INTO config (id, requires_delimiter, delimiters) 
        VALUES (1, 'yes', 'space,enter')
    """
    )
    
    conn.commit()
    conn.close()

# Function to populate the database with regex rules
def create_regex_database(db_name="E:/regex.db"):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # Database to store regex expressions and their corresponding suffix expansions
    regex_database = [
        ("", "çao", "ção", r"(?<![ã])\bçao\b", "", False, "Diferenciar Maiúsculas/Minúsculas"),
        ("", "mn", "mento", r".mn", "", False, "Diferenciar Maiúsculas/Minúsculas"),
        ("", "ao", "ão", r"ao(?![s])", "", False, "Diferenciar Maiúsculas/Minúsculas"),
        ("", "oes", "ões", r".oes", "", False, "Diferenciar Maiúsculas/Minúsculas"),
    ]
    
    # Insert data into the main table, including the regex pattern
    c.executemany(
        """
        INSERT INTO aTable (prefix, shortcut, expansion, regex_pattern, label, format, "case") 
        VALUES (?,?,?,?,?,?,?)
    """,
        regex_database,
    )
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Initialize the database and its tables
initialize_db()

# Populate the database with regex rules
create_regex_database()
