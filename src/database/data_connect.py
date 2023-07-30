import sqlite3
import json

# for the collapsible
import os
import glob
import psutil


def process_all_databases():
    db_files = get_db_files_in_directory(get_database_path())
    for db_file in db_files:
        with sqlite3.connect(db_file) as conn:
            # Now you can use the 'conn' object to execute queries on the specific database.
            pass  # Your database processing code here


def get_database_path(group_name, db_name):
    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )  # directory of the current script
    if not db_name.endswith(".db"):
        db_name += ".db"
    db_path = os.path.join(base_dir, "groups", group_name, db_name)
    forward_slash_db_path = db_path.replace("\\", "/")
    # print(f"Connecting to database at {forward_slash_db_path}")
    return forward_slash_db_path


def create_db():
    with sqlite3.connect(get_database_path()) as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS my_table
            (shortcut TEXT, expansion TEXT, label TEXT)
        """
        )
        # conn.commit() is not necessary when using sqlite3.connect() as a context manager


def insert_into_db(shortcut, expansion, label):
    if len(shortcut) > 25:
        raise ValueError("Shortcut exceeds 25 characters limit.")
    if len(label) > 40:
        raise ValueError("Label exceeds 40 characters limit.")

    with sqlite3.connect(get_database_path()) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO my_table VALUES (?, ?, ?)", (shortcut, expansion, label))


def get_db_files_in_directory(directory):
    if not os.path.exists(directory):
        raise ValueError(f"Directory '{directory}' does not exist.")

    db_files = []
    # os.walk returns a generator, that creates a tuple of values
    # (current_path, directories in current_path, files in current_path).
    for dirpath, dirnames, filenames in os.walk(directory):
        for file in filenames:
            if file.endswith(".db"):
                db_files.append(os.path.join(dirpath, file))

    return db_files


def load_db_into_memory(database_path):
    # Connect to the file-based database
    src = sqlite3.connect(database_path)

    # Connect to a new in-memory database
    dest = sqlite3.connect(":memory:")

    # Copy data from src to dest
    src.backup(dest)

    return src, dest


def save_db_from_memory(dest, database_path):
    # Connect to the file-based database
    src = sqlite3.connect(database_path)

    # Copy data from dest (in-memory database) to src (file-based database)
    dest.backup(src)


# ----------------------------------------------------Olhar listeners nos bds


def close_db_in_memory(src, dest):
    # Close the in-memory database
    dest.close()

    # Close the file-based database
    src.close()


def lookup_word_in_all_databases(word):
    # Get the list of all database files
    db_files = get_db_files_in_directory(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "groups")
    )
    print(f"Database files found: {db_files}")

    for db_file in db_files:
        file_size_in_bytes = os.path.getsize(db_file)
        file_size_in_megabytes = file_size_in_bytes / (1024 * 1024)
        print(f"File size of {db_file}: {file_size_in_megabytes} MB")

        mem = psutil.virtual_memory()
        available_memory_in_megabytes = mem.available / (1024 * 1024)
        print(f"Available memory: {available_memory_in_megabytes} MB")

        if (
            file_size_in_megabytes < 100
            and file_size_in_megabytes < available_memory_in_megabytes
        ):
            # Load the database into memory
            src, conn = load_db_into_memory(db_file)
        else:
            # Connect to the file-based database
            conn = sqlite3.connect(db_file)

        # Create a cursor
        c = conn.cursor()

        # Get the names of all tables in the database
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = c.fetchall()
        print(f"Table names in {db_file}: {table_names}")

        # For each table, try to find the word
        for table_name in table_names:
            # Execute the query
            c.execute(
                f"SELECT expansion FROM {table_name[0]} WHERE shortcut=?", (word,)
            )

            # Fetch the result
            result = c.fetchone()
            print(f"Result for {word} in {table_name[0]}: {result}")

            # If a result was found, return it
            if result is not None:
                if (
                    file_size_in_megabytes < 100
                    and file_size_in_megabytes < available_memory_in_megabytes
                ):
                    close_db_in_memory(src, conn)
                return result[0]

        if (
            file_size_in_megabytes < 100
            and file_size_in_megabytes < available_memory_in_megabytes
        ):
            close_db_in_memory(src, conn)

    # If no result was found in any database, return None
    return None
