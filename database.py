import sqlite3

def create_db():
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS StudentGroup (
                        id INTEGER PRIMARY KEY,
                        name TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS GroupInfo (
                        id INTEGER PRIMARY KEY,
                        group_id INTEGER,
                        men INTEGER,
                        women INTEGER,
                        other_regions INTEGER,
                        orphans INTEGER,
                        starosta TEXT,
                        proforg TEXT,
                        FOREIGN KEY (group_id) REFERENCES StudentGroup(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS PersonalSheet (
                        id INTEGER PRIMARY KEY,
                        group_id INTEGER,
                        full_name TEXT,
                        dob TEXT,
                        perm_address TEXT,
                        temp_address TEXT,
                        contact_number TEXT,
                        email TEXT,
                        scholarship TEXT,
                        father_name TEXT,
                        father_work TEXT,
                        father_phone TEXT,
                        mother_name TEXT,
                        mother_work TEXT,
                        mother_phone TEXT,
                        other_data TEXT,
                        FOREIGN KEY (group_id) REFERENCES StudentGroup(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Teacher (
                        id INTEGER PRIMARY KEY,
                        full_name TEXT,
                        phone_number TEXT,
                        department_id INTEGER,
                        FOREIGN KEY (department_id) REFERENCES Department(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Discipline (
                        id INTEGER PRIMARY KEY,
                        name TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Semester (
                        id INTEGER PRIMARY KEY,
                        group_id INTEGER,
                        discipline_id INTEGER,
                        teacher_id INTEGER,
                        semester_number INTEGER,
                        FOREIGN KEY (group_id) REFERENCES StudentGroup(id),
                        FOREIGN KEY (discipline_id) REFERENCES Discipline(id),
                        FOREIGN KEY (teacher_id) REFERENCES Teacher(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS WorkPlan (
                        id INTEGER PRIMARY KEY,
                        event TEXT,
                        venue TEXT,
                        dates TEXT,
                        performers TEXT,
                        result TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Department (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        phone TEXT)''')

    conn.commit()
    conn.close()

create_db()
