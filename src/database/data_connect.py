import sqlite3
import json

# for the colapsible
import os
import glob


def process_all_databases():
    db_files = get_db_files_in_directory(get_database_path())
    for db_file in db_files:
        conn = sqlite3.connect(db_file)
        # Now you can use the 'conn' object to execute queries on the specific database.
        # ...
        conn.close()


def get_database_path(group_name, db_name):
    base_dir = os.path.dirname(__file__)
    if not db_name.endswith(".db"):
        db_name += ".db"
    db_path = os.path.join(base_dir, "groups", group_name, db_name)
    forward_slash_db_path = db_path.replace("\\", "/")
    print(f"Connecting to database at {forward_slash_db_path}")
    return forward_slash_db_path


def create_db():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(get_database_path())

    # Create a cursor object
    c = conn.cursor()

    # Create table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS my_table
        (shortcut TEXT, expansion TEXT, label TEXT)
    """
    )

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()


def insert_into_db(shortcut, expansion, label):
    if len(shortcut) > 25:
        raise ValueError("Shortcut exceeds 25 characters limit.")
    if len(label) > 40:
        raise ValueError("Label exceeds 40 characters limit.")

    conn = sqlite3.connect(get_database_path())
    c = conn.cursor()

    # Insert a row of data
    c.execute("INSERT INTO my_table VALUES (?, ?, ?)", (shortcut, expansion, label))

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()


def inject_data(window):
    # Get all subdirectories in ./src/database/groups/
    subdirectories = [
        f.path for f in os.scandir("./src/database/groups/") if f.is_dir()
    ]

    for subdirectory in subdirectories:
        db_files = get_db_files_in_directory(subdirectory)
        encoded_directory = json.dumps(os.path.basename(subdirectory))
        encoded_db_files = json.dumps(db_files)  # encode the whole list of db files

        window.evaluate_js(
            f"createCollapsible({encoded_directory}, {encoded_db_files});"
        )


# Get the db files
def get_db_files_in_directory(directory):
    # Check if directory exists
    if not os.path.exists(directory):
        raise ValueError(f"Directory '{directory}' does not exist.")

    # Get all .db files in the directory
    db_files = glob.glob(os.path.join(directory, "*.db"))

    # Extract the base name (file name) for each .db file
    db_file_names = [os.path.basename(db_file) for db_file in db_files]

    return db_file_names
