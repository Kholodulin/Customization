class StudentGroup:
    def __init__(self, name):
        self.name = name

class GroupInfo:
    def __init__(self, group_id, men, women, other_regions, orphans, starosta, proforg):
        self.group_id = group_id
        self.men = men
        self.women = women
        self.other_regions = other_regions
        self.orphans = orphans
        self.starosta = starosta
        self.proforg = proforg

class PersonalSheet:
    def __init__(self, group_id, full_name, dob, perm_address, temp_address, contact_number, email, scholarship, father_name, father_work, father_phone, mother_name, mother_work, mother_phone, other_data):
        self.group_id = group_id
        self.full_name = full_name
        self.dob = dob
        self.perm_address = perm_address
        self.temp_address = temp_address
        self.contact_number = contact_number
        self.email = email
        self.scholarship = scholarship
        self.father_name = father_name
        self.father_work = father_work
        self.father_phone = father_phone
        self.mother_name = mother_name
        self.mother_work = mother_work
        self.mother_phone = mother_phone
        self.other_data = other_data

class FamilyInfo:
    def __init__(self, father_name, father_work, father_phone, mother_name, mother_work, mother_phone, other_data):
        self.father_name = father_name
        self.father_work = father_work
        self.father_phone = father_phone
        self.mother_name = mother_name
        self.mother_work = mother_work
        self.mother_phone = mother_phone
        self.other_data = other_data

class Teacher:
    def __init__(self, full_name, phone_number, department_id):
        self.full_name = full_name
        self.phone_number = phone_number
        self.department_id = department_id

class Discipline:
    def __init__(self, name):
        self.name = name

class Semester:
    def __init__(self, group_id, discipline_id, teacher_id, semester_number):
        self.group_id = group_id
        self.discipline_id = discipline_id
        self.teacher_id = teacher_id
        self.semester_number = semester_number

class WorkPlan:
    def __init__(self, event, venue, dates, performers, result):
        self.event = event
        self.venue = venue
        self.dates = dates
        self.performers = performers
        self.result = result

class Department:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone
