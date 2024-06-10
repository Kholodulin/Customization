import sqlite3

def save_student_group(student_group):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO StudentGroup (name) VALUES (?)', (student_group.name,))
    conn.commit()
    conn.close()

def save_group_info(group_info):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO GroupInfo (group_id, men, women, other_regions, orphans, starosta, proforg) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (group_info.group_id, group_info.men, group_info.women, group_info.other_regions, group_info.orphans, group_info.starosta, group_info.proforg))
    conn.commit()
    conn.close()

def save_personal_sheet(personal_sheet):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO PersonalSheet (group_id, full_name, dob, perm_address, temp_address, contact_number, email, scholarship, father_name, father_work, father_phone, mother_name, mother_work, mother_phone, other_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (personal_sheet.group_id, personal_sheet.full_name, personal_sheet.dob, personal_sheet.perm_address, personal_sheet.temp_address, personal_sheet.contact_number, personal_sheet.email, personal_sheet.scholarship, personal_sheet.father_name, personal_sheet.father_work, personal_sheet.father_phone, personal_sheet.mother_name, personal_sheet.mother_work, personal_sheet.mother_phone, personal_sheet.other_data))
    conn.commit()
    conn.close()

def save_teacher(teacher):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Teacher (full_name, phone_number, department_id) VALUES (?, ?, ?)',
                   (teacher.full_name, teacher.phone_number, teacher.department_id))
    conn.commit()
    conn.close()

def save_discipline(discipline):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Discipline (name) VALUES (?)', (discipline.name,))
    conn.commit()
    conn.close()

def save_semester(semester):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Semester (group_id, discipline_id, teacher_id, semester_number) VALUES (?, ?, ?, ?)',
                   (semester.group_id, semester.discipline_id, semester.teacher_id, semester.semester_number))
    conn.commit()
    conn.close()

def save_work_plan(work_plan):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO WorkPlan (event, venue, dates, performers, result) VALUES (?, ?, ?, ?, ?)',
                   (work_plan.event, work_plan.venue, work_plan.dates, work_plan.performers, work_plan.result))
    conn.commit()
    conn.close()

def save_department(department):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Department (name, phone) VALUES (?, ?)', (department.name, department.phone))
    conn.commit()
    conn.close()

def view_data(table_name, group_id=None, semester_number=None):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    if group_id and table_name in ['GroupInfo', 'PersonalSheet', 'Semester']:
        if table_name == 'Semester' and semester_number:
            cursor.execute(f'SELECT * FROM {table_name} WHERE group_id=? AND semester_number=?', (group_id, semester_number))
        else:
            cursor.execute(f'SELECT * FROM {table_name} WHERE group_id=?', (group_id,))
    else:
        cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_data(table_name, record_id):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {table_name} WHERE id=?', (record_id,))
    conn.commit()
    conn.close()

def get_groups():
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM StudentGroup')
    groups = cursor.fetchall()
    conn.close()
    return groups

def update_group_info(group_id, group_info):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE GroupInfo
                      SET men = ?, women = ?, other_regions = ?, orphans = ?, starosta = ?, proforg = ?
                      WHERE group_id = ?''',
                   (group_info['men'], group_info['women'], group_info['other_regions'], group_info['orphans'], group_info['starosta'], group_info['proforg'], group_id))
    conn.commit()
    conn.close()

def get_group_name_by_id(group_id):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM StudentGroup WHERE id=?', (group_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_department_name_by_id(department_id):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM Department WHERE id=?', (department_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_discipline_name_by_id(discipline_id):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM Discipline WHERE id=?', (discipline_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_teacher_name_by_id(teacher_id):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT full_name FROM Teacher WHERE id=?', (teacher_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def view_data_with_names(table_name, group_id=None, semester_number=None):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    if group_id and table_name in ['GroupInfo', 'PersonalSheet', 'Semester']:
        if table_name == 'Semester' and semester_number:
            cursor.execute(f'SELECT * FROM {table_name} WHERE group_id=? AND semester_number=?', (group_id, semester_number))
        else:
            cursor.execute(f'SELECT * FROM {table_name} WHERE group_id=?', (group_id,))
    else:
        cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    
    if table_name == 'PersonalSheet':
        rows = [(row[0], get_group_name_by_id(row[1]), *row[2:]) for row in rows]
    elif table_name == 'Teacher':
        rows = [(row[0], *row[1:3], get_department_name_by_id(row[3])) for row in rows]
    elif table_name == 'Semester':
        rows = [(row[0], get_group_name_by_id(row[1]), get_discipline_name_by_id(row[2]), get_teacher_name_by_id(row[3]), row[4]) for row in rows]

    conn.close()
    return rows

def delete_group_and_related_data(group_id):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM PersonalSheet WHERE group_id=?', (group_id,))
    cursor.execute('DELETE FROM GroupInfo WHERE group_id=?', (group_id,))
    cursor.execute('DELETE FROM Semester WHERE group_id=?', (group_id,))
    cursor.execute('DELETE FROM StudentGroup WHERE id=?', (group_id,))
    conn.commit()
    conn.close()

def get_general_info(group_id):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT g.name, gi.men, gi.women, gi.other_regions, gi.orphans, gi.starosta, gi.proforg
                      FROM GroupInfo gi
                      JOIN StudentGroup g ON gi.group_id = g.id
                      WHERE gi.group_id = ?''', (group_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_students_info(group_id):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT s.full_name, s.dob, s.perm_address, s.temp_address, s.contact_number, s.email,
                             s.scholarship, s.father_name, s.father_work, s.father_phone, s.mother_name, 
                             s.mother_work, s.mother_phone, s.other_data
                      FROM PersonalSheet s
                      WHERE s.group_id = ?''', (group_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_teachers_info():
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT t.full_name, t.phone_number, d.name as department_name
                      FROM Teacher t
                      JOIN Department d ON t.department_id = d.id''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_work_plan():
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT event, venue, dates, performers, result FROM WorkPlan')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_semester_info(group_id):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT s.semester_number, d.name as discipline_name, t.full_name as teacher_name, t.phone_number as department_phone
                      FROM Semester s
                      JOIN Discipline d ON s.discipline_id = d.id
                      JOIN Teacher t ON s.teacher_id = t.id
                      WHERE s.group_id = ?''', (group_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_data(table_name, record_id, column_name, new_value):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE {table_name} SET {column_name} = ? WHERE id = ?', (new_value, record_id))
    conn.commit()
    conn.close()


def update_personal_sheet(record_id, column, value):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE PersonalSheet SET {column} = ? WHERE id = ?', (value, record_id))
    conn.commit()
    conn.close()

def update_teacher(record_id, column, value):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE Teacher SET {column} = ? WHERE id = ?', (value, record_id))
    conn.commit()
    conn.close()

def update_discipline(record_id, column, value):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE Discipline SET {column} = ? WHERE id = ?', (value, record_id))
    conn.commit()
    conn.close()

def update_semester(record_id, column, value):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE Semester SET {column} = ? WHERE id = ?', (value, record_id))
    conn.commit()
    conn.close()

def update_work_plan(record_id, column, value):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE WorkPlan SET {column} = ? WHERE id = ?', (value, record_id))
    conn.commit()
    conn.close()

def update_department(record_id, column, value):
    conn = sqlite3.connect('curator.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE Department SET {column} = ? WHERE id = ?', (value, record_id))
    conn.commit()
    conn.close()