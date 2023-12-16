import sqlite3
import datetime
db_name = 'meet_bot_db.sql'
name_max_length = 255
# Review 11.07.2023
def create_tables_if_not_exists():
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute(
            f'''
            CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            tg_id int NOT NULL, 
            photo_name text,
            photo_path text,
            name varchar({name_max_length}),
            description text,
            type varchar(255) NOT NULL);
            '''
        )
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS match (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_tg_id int NOT NULL,
            second_tg_id int NOT NULL,
            time timestamp NOT NULL);
            ''')
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if conn:
            conn.close()
            print('Соединение с SQLite закрыто')
def user_exists_in_db(user_id):
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        res = cur.execute(
            f'''
            SELECT id, tg_id FROM user
            WHERE tg_id == {user_id}
            ORDER BY id DESC
            '''
        )
        result = res.fetchall()
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if conn:
            conn.close()
            print('Соединение с SQLite закрыто')

    if len(result) == 0:
        return False
    return True

async def save_form_to_db(user_id, name, photo_name, photo_path, description):
    if name == None:
        name_str = "NULL"
    else:
        name_str = f'''"{name}"'''
    if photo_name == None:
        photo_name_str = "NULL"
    else:
        photo_name_str = f'''"{photo_name}"'''
    if photo_path == None:
        photo_path_str = "NULL"
    else:
        photo_path_str = f'''"{photo_path}"'''
    if description == None:
        description_str = "NULL"
    else:
        description_str = f'''"{description}"'''

    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute(
            f'''
            INSERT INTO user (tg_id, name, photo_name, photo_path, description, type)
            VALUES ({user_id}, {name_str}, {photo_name_str}, {photo_path_str}, {description_str}, "user");
            '''
        )
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if conn:
            conn.close()
            print('Соединение с SQLite закрыто')

async def get_name_from_db(user_id):
    result = None
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        res = cur.execute(
            f'''
            SELECT name, tg_id FROM user
            WHERE tg_id == {user_id}
            ORDER BY id DESC
            LIMIT 1
            '''
        )
        result = res.fetchall()
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if conn:
            conn.close()
            print('Соединение с SQLite закрыто')

    if result is not None:
        return result[0][0]
    else:
        return None

async def get_photo_from_db(user_id):
    result = None
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        res = cur.execute(
            f'''
            SELECT photo_path, tg_id FROM user
            WHERE tg_id == {user_id}
            ORDER BY id DESC
            LIMIT 1
            '''
        )
        result = res.fetchall()
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if conn:
            conn.close()
            print('Соединение с SQLite закрыто')

    if result is not None:
        with open(result[0][0], 'rb') as new_file:
            return new_file.read()
    else:
        return None




async def get_description_from_db(user_id):
    result = None
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        res = cur.execute(
            f'''
            SELECT description, tg_id FROM user
            WHERE tg_id == {user_id}
            ORDER BY id DESC
            LIMIT 1
            '''
        )
        result = res.fetchall()
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if conn:
            conn.close()
            print('Соединение с SQLite закрыто')

    if result is not None:
        return result[0][0]
    else:
        return None

async def get_user_id_coffee_from_db(user_id):
    result = None
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        res = cur.execute(
            f'''
            SELECT first_tg_id, second_tg_id FROM match
            WHERE first_tg_id == {user_id} OR second_tg_id == {user_id}
            '''
        )
        result = res.fetchall()
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if conn:
            conn.close()
            print('Соединение с SQLite закрыто')

    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        res = cur.execute(
            f'''
            SELECT id, tg_id FROM user
            '''
        )
        all_users = res.fetchall()
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if conn:
            conn.close()
            print('Соединение с SQLite закрыто')

    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        res = cur.execute(
            f'''
            SELECT COUNT(*) FROM user
            '''
        )
        count = res.fetchall()
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if conn:
            conn.close()
            print('Соединение с SQLite закрыто')

    indexes = set()
    if result is not None:
        for i in result:
            if i[0] == user_id:
                indexes = indexes.union(set([i[1]]))
            # if i[1] == user_id:
            #     indexes = indexes.union(set([i[0]]))
    print(f'indexes: {indexes}')
    print(f'count: {count}')
    for i in range(count[0][0]):
        print(f'count {i}')
        print(f'all_users[i][1]: {all_users[i][1]}')
        if all_users[i][1] not in indexes and all_users[i][1] != user_id:
            print('test2')
            return all_users[i][1]
    return None

async def add_match_to_db(user_id, match_id):
    print("test1")
    try:
        sqliteConnection = sqlite3.connect(db_name,
                                           detect_types=sqlite3.PARSE_DECLTYPES |
                                                        sqlite3.PARSE_COLNAMES)
        cur = sqliteConnection.cursor()
        print("Connected to SQLite")
        sqlite_insert_with_param = """
                                    INSERT INTO match ('first_tg_id', 'second_tg_id', 'time')
                                    VALUES (?, ?, ?);
                                    """

        data_tuple = (user_id, match_id, datetime.datetime.now())
        cur.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('Соединение с SQLite закрыто')

async def get_time_next_match_from_db(user_id):
    result = None
    try:
        sqliteConnection = sqlite3.connect(db_name,
                                           detect_types=sqlite3.PARSE_DECLTYPES |
                                                        sqlite3.PARSE_COLNAMES)
        cur = sqliteConnection.cursor()

        res = cur.execute(
            f'''
            SELECT id, time FROM match
            WHERE first_tg_id == {user_id}
            ORDER BY id DESC
            LIMIT 1
            '''
        )
        result = res.fetchall()
        sqliteConnection.commit()
        cur.close()
    except sqlite3.Error as error:
        print('Ошибка при работе с SQLite', error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('Соединение с SQLite закрыто')
    if result is None or len(result) == 0:
        return datetime.timedelta(0)
    print(f"Aaaaaaaaaaa: {datetime.timedelta(days=7) - (datetime.datetime.now() - result[0][1])}")
    return datetime.timedelta(seconds=10) - (datetime.datetime.now() - result[0][1])


