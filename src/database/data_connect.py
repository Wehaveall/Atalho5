import sqlite3
import webview
import json


def create_db():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect("my_database.db")

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

    conn = sqlite3.connect("my_database.db")
    c = conn.cursor()

    # Insert a row of data
    c.execute("INSERT INTO my_table VALUES (?, ?, ?)", (shortcut, expansion, label))

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()


def get_data_from_database():
    # Connect to SQLite database
    conn = sqlite3.connect("my_database.db")

    # Create a cursor object
    c = conn.cursor()

    # Execute an SQL command
    c.execute("SELECT * FROM my_table")

    # Fetch all rows from the last executed SQL command
    rows = c.fetchall()

    # Don't forget to close the connection
    conn.close()

    return rows


def inject_data(window):
    data = get_data_from_database()

    for row in data:
        row_html = "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(*row)
        encoded_html = json.dumps(row_html)  # This will escape any special characters
        window.evaluate_js(
            'document.getElementById("myTable").insertAdjacentHTML("beforeend", {});'.format(
                encoded_html
            )
        )
