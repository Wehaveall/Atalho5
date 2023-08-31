import sqlite3


# for the collapsible
import os



from sqlalchemy import create_engine, select, MetaData, Table
from sqlalchemy import inspect  # Importe o Inspector
from sqlalchemy.orm import Session





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


# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------

# No SQLAlchemy, o "engine" é a fonte comum para todas as operações de banco de dados.
# Ao criar um engine, o SQLAlchemy também pode criar um pool de conexões,
# gerenciando automaticamente a abertura e fechamento de conexões para você.
# No entanto, criar um novo engine para cada operação pode ser ineficiente e
# pode levar a problemas se muitas instâncias forem criadas rapidamente.
# Em vez disso, você pode criar um único engine e reutilizá-lo.
# Aqui está uma forma de refatorar a função lookup_word_in_all_databases para criar e reutilizar um único engine:
# Crie o engine uma vez e reutilize-o.
# Use a abordagem de "context manager" (with) para garantir que as conexões sejam fechadas após o uso.


from sqlalchemy import create_engine, select, inspect, MetaData, Table
from sqlalchemy.orm import Session


# Crie uma função para obter um engine com base no caminho do banco de dados
def get_engine(db_path):
    return create_engine(f"sqlite:///{db_path}", echo=True)


def lookup_word_in_all_databases(word):
    db_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "groups")
    
    # Lista para armazenar os arquivos de banco de dados
    db_files = []
    
    # Use os.walk para percorrer todos os subdiretórios de db_directory
    for root, dirs, files in os.walk(db_directory):
        for file in files:
            if file.endswith('.db'):
                db_files.append(os.path.join(root, file))

  

    # Crie uma instância de MetaData uma vez
    metadata = MetaData()

    for db_file in db_files:
        engine = get_engine(db_file)  # Obtenha o engine
        
        # Use o Inspector para obter os nomes das tabelas
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        # Selecione a tabela que não é 'sqlite_sequence'
        target_table_name = next((name for name in table_names if name != "sqlite_sequence"), None)

        if target_table_name:
            table = Table(target_table_name, metadata, autoload_with=engine)
            s = select(table).where(table.c.shortcut == word)

            # Use a abordagem de "context manager"
            with Session(engine) as session:
                result = session.execute(s).first()
                if result:
                    return result.expansion

    # Se nenhum resultado foi encontrado em nenhum banco de dados, retorne None
    return None