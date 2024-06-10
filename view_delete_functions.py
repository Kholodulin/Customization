from crud_operations import view_data, delete_data

def view_student_groups():
    rows = view_data('StudentGroup')
    for row in rows:
        print(row)

def delete_student_group(record_id):
    delete_data('StudentGroup', record_id)

def view_group_info():
    rows = view_data('GroupInfo')
    for row in rows:
        print(row)

def delete_group_info(record_id):
    delete_data('GroupInfo', record_id)

def view_personal_sheets():
    rows = view_data('PersonalSheet')
    for row in rows:
        print(row)

def delete_personal_sheet(record_id):
    delete_data('PersonalSheet', record_id)

def view_teachers():
    rows = view_data('Teacher')
    for row in rows:
        print(row)

def delete_teacher(record_id):
    delete_data('Teacher', record_id)

def view_disciplines():
    rows = view_data('Discipline')
    for row in rows:
        print(row)

def delete_discipline(record_id):
    delete_data('Discipline', record_id)

def view_group_discipline_teacher():
    rows = view_data('GroupDisciplineTeacher')
    for row in rows:
        print(row)

def delete_group_discipline_teacher(record_id):
    delete_data('GroupDisciplineTeacher', record_id)

def view_work_plan():
    rows = view_data('WorkPlan')
    for row in rows:
        print(row)

def delete_work_plan(record_id):
    delete_data('WorkPlan', record_id)
