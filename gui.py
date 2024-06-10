import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QInputDialog, QLineEdit, QFormLayout, QDialog, QDialogButtonBox, QScrollArea, QComboBox, QLabel, QListWidget, QStackedWidget, QSplitter, QSpinBox, QFileDialog, QTableView, QHeaderView
from PyQt5.QtCore import Qt, QModelIndex, QVariant
from PyQt5.QtGui import QStandardItemModel
from database import create_db
from crud_operations import save_student_group, save_group_info, save_personal_sheet, save_teacher, save_discipline, save_semester, save_work_plan, save_department, view_data_with_names, delete_data, get_groups, update_group_info, delete_group_and_related_data, get_general_info, get_students_info, get_teachers_info, get_work_plan, get_semester_info
import pandas as pd

from models import Department, Discipline, GroupInfo, PersonalSheet, Semester, StudentGroup, Teacher, WorkPlan, StudentGroup

class InputDialog(QDialog):
    def __init__(self, inputs, combo_options1=None, combo_options2=None, parent=None, fixed_size=(400, 300)):
        super().__init__(parent)
        self.inputs = inputs
        self.combo_options1 = combo_options1
        self.combo_options2 = combo_options2
        self.fixed_size = fixed_size
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Новая запись')
        self.setFixedSize(*self.fixed_size)
        layout = QFormLayout(self)
        self.input_fields = {}

        for i, label in enumerate(self.inputs):
            if label in ["Кафедра", "Дисциплина", "Преподаватель"] and (self.combo_options1 or self.combo_options2):
                combo_box = QComboBox(self)
                if label == "Кафедра":
                    combo_box.addItems(self.combo_options1)
                elif label == "Дисциплина":
                    combo_box.addItems(self.combo_options1)
                elif label == "Преподаватель":
                    combo_box.addItems(self.combo_options2)
                layout.addRow(label, combo_box)
                self.input_fields[label] = combo_box
            else:
                input_field = QLineEdit(self)
                layout.addRow(label, input_field)
                self.input_fields[label] = input_field

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.button(QDialogButtonBox.Ok).setObjectName("okButton")
        self.buttons.button(QDialogButtonBox.Cancel).setObjectName("cancelButton")
        self.buttons.accepted.connect(self.validate_inputs)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def validate_inputs(self):
        if all(isinstance(field, QLineEdit) and field.text().strip() == "" for field in self.input_fields.values()):
            QMessageBox.warning(self, "Ошибка", "Заполните хотя бы одно поле.")
        else:
            self.accept()

    def getInputs(self):
        return {label: (field.currentText() if isinstance(field, QComboBox) else field.text()) for label, field in self.input_fields.items()}

class GroupInfoDialog(QDialog):
    def __init__(self, group_id, parent=None):
        super().__init__(parent)
        self.group_id = group_id
        self.is_new = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Информация о группе")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout(self)

        self.form_layout = QFormLayout()

        self.fields = {
            "Мужчин": QLineEdit(self),
            "Женщин": QLineEdit(self),
            "Из других регионов": QLineEdit(self),
            "Дети-сироты": QLineEdit(self),
            "Староста": QLineEdit(self),
            "Профорг": QLineEdit(self),
        }

        for label, field in self.fields.items():
            self.form_layout.addRow(label, field)

        layout.addLayout(self.form_layout)

        self.populate_group_info(self.group_id)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.save_group_info)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def populate_group_info(self, group_id):
        data = view_data_with_names('GroupInfo', group_id)
        if data:
            row = data[0]
            self.fields["Мужчин"].setText(str(row[2]))
            self.fields["Женщин"].setText(str(row[3]))
            self.fields["Из других регионов"].setText(str(row[4]))
            self.fields["Дети-сироты"].setText(str(row[5]))
            self.fields["Староста"].setText(str(row[6]))
            self.fields["Профорг"].setText(str(row[7]))
        else:
            self.is_new = True

    def save_group_info(self):
        group_info = {
            "men": int(self.fields["Мужчин"].text()),
            "women": int(self.fields["Женщин"].text()),
            "other_regions": int(self.fields["Из других регионов"].text()),
            "orphans": int(self.fields["Дети-сироты"].text()),
            "starosta": self.fields["Староста"].text(),
            "proforg": self.fields["Профорг"].text(),
        }
        if self.is_new:
            save_group_info(GroupInfo(
                group_id=self.group_id,
                men=group_info["men"],
                women=group_info["women"],
                other_regions=group_info["other_regions"],
                orphans=group_info["orphans"],
                starosta=group_info["starosta"],
                proforg=group_info["proforg"]
            ))
        else:
            update_group_info(self.group_id, group_info)
        self.accept()

class EditableStandardItemModel(QStandardItemModel):
    def __init__(self, rows=0, columns=0, parent=None):
        super().__init__(rows, columns, parent)

    def setData(self, index: QModelIndex, value: QVariant, role: int = Qt.EditRole) -> bool:
        if role == Qt.EditRole:
            self.dataChanged.emit(index, index, [role])
        return super().setData(index, value, role)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Журнал Куратора")
        self.setGeometry(100, 100, 1200, 800)

        self.current_group_id = None
        self.current_group_name = None
        self.current_table_name = None
        self.current_semester_number = 1

        layout = QHBoxLayout()

        # Left navigation panel with fixed width
        nav_layout = QVBoxLayout()
        nav_container = QWidget()
        nav_container.setLayout(nav_layout)
        nav_container.setFixedWidth(250)  # Set fixed width for the left panel

        self.group_selector = QComboBox(self)
        self.group_selector.currentIndexChanged.connect(self.update_current_group)
        nav_layout.addWidget(QLabel("Выберите группу:"))
        nav_layout.addWidget(self.group_selector)

        button_layout = QHBoxLayout()

        group_info_button = QPushButton("Информация о группе")
        group_info_button.clicked.connect(self.show_group_info)
        button_layout.addWidget(group_info_button)

        add_group_button = QPushButton("+")
        add_group_button.setFixedWidth(30)  # Make the button small
        add_group_button.clicked.connect(self.add_new_group)
        button_layout.addWidget(add_group_button)

        delete_group_button = QPushButton("-")
        delete_group_button.setFixedWidth(30)  # Make the button small
        delete_group_button.clicked.connect(self.delete_current_group)
        button_layout.addWidget(delete_group_button)
        
        nav_layout.addLayout(button_layout)

        self.nav_list = QListWidget()
        self.nav_list.addItem("Личные листки студентов")
        self.nav_list.addItem("Список Преподавателей")
        self.nav_list.addItem("Список Дисциплин")
        self.nav_list.addItem("Учебный план на семестр")
        self.nav_list.addItem("Мероприятия")
        self.nav_list.addItem("Список кафедр")
        self.nav_list.currentRowChanged.connect(self.display_current_table)
        nav_layout.addWidget(self.nav_list)

        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_record)
        nav_layout.addWidget(add_button)

        generate_report_button = QPushButton("Сгенерировать отчет")
        generate_report_button.clicked.connect(self.generate_report)
        nav_layout.addWidget(generate_report_button)
        # Right panel with table and delete button
        right_layout = QVBoxLayout()
        right_container = QWidget()
        right_container.setLayout(right_layout)

        self.semester_selector = QSpinBox(self)
        self.semester_selector.setMinimum(1)
        self.semester_selector.setMaximum(12)
        self.semester_selector.valueChanged.connect(self.update_current_semester)
        self.pick_semestr = QLabel(self)
        self.pick_semestr.setText("Выберите семестр:")
        right_layout.addWidget(self.pick_semestr)
        right_layout.addWidget(self.semester_selector)
        self.semester_selector.hide()
        self.pick_semestr.hide()

        self.stack = QStackedWidget(self)
        self.personal_sheet_table = QTableView()
        self.teacher_table = QTableView()
        self.discipline_table = QTableView()
        self.semester_table = QTableView()
        self.work_plan_table = QTableView()
        self.department_table = QTableView()
        
        self.stack.addWidget(self.personal_sheet_table)
        self.stack.addWidget(self.teacher_table)
        self.stack.addWidget(self.discipline_table)
        self.stack.addWidget(self.semester_table)
        self.stack.addWidget(self.work_plan_table)
        self.stack.addWidget(self.department_table)

        self.personal_sheet_table.resizeColumnsToContents()
        self.teacher_table.resizeColumnsToContents()
        self.discipline_table.resizeColumnsToContents()
        self.semester_table.resizeColumnsToContents()
        self.work_plan_table.resizeColumnsToContents()
        self.department_table.resizeColumnsToContents()

        self.personal_sheet_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.teacher_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.discipline_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.semester_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.work_plan_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.department_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        right_layout.addWidget(self.stack)

        # Move Delete button here under the table
        delete_button = QPushButton("Удалить выбранную запись")
        delete_button.clicked.connect(self.delete_selected_row)
        right_layout.addWidget(delete_button)

        # Splitter to divide left and right panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(nav_container)
        splitter.addWidget(right_container)

        layout.addWidget(splitter)

        container = QWidget()
        container.setLayout(layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        self.setCentralWidget(scroll)

        create_db()
        self.populate_group_selector()

        # Install event filter to capture key press events
        self.installEventFilter(self)

    def populate_group_selector(self):
        self.group_selector.clear()
        groups = get_groups()
        for group in groups:
            self.group_selector.addItem(group[1], group[0])  # Display group name, store group ID

    def update_current_group(self):
        self.current_group_id = self.group_selector.currentData()
        self.current_group_name = self.group_selector.currentText()
        self.setWindowTitle(f"Журнал Куратора - Текущая группа: {self.current_group_name}")
        if self.current_table_name:
            self.update_table_if_needed(self.current_table_name)

    def update_current_semester(self):
        self.current_semester_number = self.semester_selector.value()
        if self.current_table_name == 'Semester':
            self.update_table_if_needed('Semester')

    def add_new_group(self):
        group_name, ok = QInputDialog.getText(self, "Добавить группу", "Введите название новой группы:")
        if ok and group_name:
            new_group = StudentGroup(group_name)
            save_student_group(new_group)
            self.populate_group_selector()
            QMessageBox.information(self, "Информация", "Группа добавлена успешно.")

    def show_group_info(self):
        if not self.current_group_id:
            QMessageBox.warning(self, "Ошибка", "Выберите группу перед просмотром информации.")
            return
        dialog = GroupInfoDialog(self.current_group_id, self)
        dialog.exec()

    def delete_current_group(self):
        if not self.current_group_id:
            QMessageBox.warning(self, "Ошибка", "Выберите группу перед удалением.")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить эту группу и всю связанную с ней информацию?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_group_and_related_data(self.current_group_id)
            self.populate_group_selector()
            QMessageBox.information(self, "Информация", "Группа и вся связанная с ней информация удалены успешно.")
            self.current_group_id = None
            self.current_group_name = None
            self.setWindowTitle("Журнал Куратора")

    def display_current_table(self, index):
        self.stack.setCurrentIndex(index)
        table_mapping = {
            0: ('PersonalSheet', ["ID", "Группа", "Ф.И.О.", "Дата рождения", "Постоянная регистрация", "Временная регистрация", "Контактный телефон", "Email", "Получение стипендии", "Отец (Ф.И.О.)", "Место работы, должность отца", "Телефон отца", "Мать (Ф.И.О.)", "Место работы, должность матери", "Телефон матери", "Другие данные"]),
            1: ('Teacher', ["ID", "Полное имя", "Номер телефона", "Кафедра"]),
            2: ('Discipline', ["ID", "Название дисциплины"]),
            3: ('Semester', ["ID", "Группа", "Дисциплина", "Преподаватель", "Номер семестра"]),
            4: ('WorkPlan', ["ID", "Мероприятие", "Место проведения", "Сроки", "Исполнители", "Результат"]),
            5: ('Department', ["ID", "Название кафедры", "Телефон"])
        }
        self.current_table_name, headers = table_mapping[index]
        self.view_data(self.current_table_name, headers)

        if self.current_table_name == 'Semester':
            self.semester_selector.show()
            self.pick_semestr.show()
        else:
            self.semester_selector.hide()
            self.pick_semestr.hide()

    def add_record(self):
        index = self.nav_list.currentRow()
        add_funcs = {
            0: self.input_personal_sheets,
            1: self.input_teachers,
            2: self.input_disciplines,
            3: self.input_semesters,
            4: self.input_work_plan,
            5: self.input_departments
        }
        add_func = add_funcs.get(index)
        if add_func:
            add_func()

    def input_personal_sheets(self):
        if not self.current_group_id:
            QMessageBox.warning(self, "Ошибка", "Выберите группу перед добавлением информации.")
            return
        dialog = InputDialog([
            "Ф.И.О.", "Дата рождения", "Постоянная регистрация", "Временная регистрация", "Контактный телефон", "Email", "Получение стипендии (да/нет)",
            "Отец (Ф.И.О.)", "Место работы, должность отца", "Телефон отца", "Мать (Ф.И.О.)", "Место работы, должность матери", "Телефон матери", "Другие данные"
        ], fixed_size=(500, 560))
        if dialog.exec() == QDialog.Accepted:
            inputs = dialog.getInputs()
            personal_sheet = PersonalSheet(
                self.current_group_id,
                inputs["Ф.И.О."],
                inputs["Дата рождения"],
                inputs["Постоянная регистрация"],
                inputs["Временная регистрация"],
                inputs["Контактный телефон"],
                inputs["Email"],
                inputs["Получение стипендии (да/нет)"],
                inputs["Отец (Ф.И.О.)"],
                inputs["Место работы, должность отца"],
                inputs["Телефон отца"],
                inputs["Мать (Ф.И.О.)"],
                inputs["Место работы, должность матери"],
                inputs["Телефон матери"],
                inputs["Другие данные"]
            )
            save_personal_sheet(personal_sheet)
            self.update_table_if_needed('PersonalSheet')

    def input_teachers(self):
        departments = self.get_department_names()
        department_names = [dept[1] for dept in departments]
        dialog = InputDialog(["Полное имя", "Номер телефона", "Кафедра"], department_names)
        if dialog.exec() == QDialog.Accepted:
            inputs = dialog.getInputs()
            department_id = next(dept[0] for dept in departments if dept[1] == inputs["Кафедра"])
            teacher = Teacher(
                inputs["Полное имя"],
                inputs["Номер телефона"],
                department_id
            )
            save_teacher(teacher)
            self.update_table_if_needed('Teacher')

    def input_disciplines(self):
        dialog = InputDialog(["Название дисциплины"])
        if dialog.exec() == QDialog.Accepted:
            inputs = dialog.getInputs()
            discipline = Discipline(inputs["Название дисциплины"])
            save_discipline(discipline)
            self.update_table_if_needed('Discipline')

    def input_semesters(self):
        if not self.current_group_id:
            QMessageBox.warning(self, "Ошибка", "Выберите группу перед добавлением информации.")
            return
        disciplines = self.get_discipline_names()
        discipline_names = [disc[1] for disc in disciplines]
        teachers = self.get_teacher_names()
        teacher_names = [teacher[1] for teacher in teachers]

        dialog = InputDialog(["Дисциплина", "Преподаватель"], discipline_names, teacher_names)
        if dialog.exec() == QDialog.Accepted:
            inputs = dialog.getInputs()
            discipline_id = next(disc[0] for disc in disciplines if disc[1] == inputs["Дисциплина"])
            teacher_id = next(teacher[0] for teacher in teachers if teacher[1] == inputs["Преподаватель"])
            semester = Semester(
                self.current_group_id,
                discipline_id,
                teacher_id,
                self.current_semester_number
            )
            save_semester(semester)
            self.update_table_if_needed('Semester')

    def input_work_plan(self):
        dialog = InputDialog(["Мероприятие", "Место проведения", "Сроки", "Исполнители", "Результат"])
        if dialog.exec() == QDialog.Accepted:
            inputs = dialog.getInputs()
            work_plan = WorkPlan(
                inputs["Мероприятие"],
                inputs["Место проведения"],
                inputs["Сроки"],
                inputs["Исполнители"],
                inputs["Результат"]
            )
            save_work_plan(work_plan)
            self.update_table_if_needed('WorkPlan')

    def input_departments(self):
        dialog = InputDialog(["Название кафедры", "Телефон"])
        if dialog.exec() == QDialog.Accepted:
            inputs = dialog.getInputs()
            department = Department(
                inputs["Название кафедры"],
                inputs["Телефон"]
            )
            save_department(department)
            self.update_table_if_needed('Department')

    def view_data(self, table_name, headers):
        if table_name in ['PersonalSheet', 'Semester'] and self.current_group_id:
            if table_name == 'Semester':
                data = view_data_with_names(table_name, self.current_group_id, self.current_semester_number)
            else:
                data = view_data_with_names(table_name, self.current_group_id)
        else:
            data = view_data_with_names(table_name)
        
        current_table = self.stack.currentWidget()
        model = EditableStandardItemModel(len(data), len(headers))
        model.setHorizontalHeaderLabels(headers)
        
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                model.setData(model.index(i, j), QVariant(str(item)))

        current_table.setModel(model)
        current_table.setColumnHidden(0, True)  # Hide the column
        if table_name in ['PersonalSheet', 'Semester']:
            current_table.setColumnHidden(1, True)
        

        model.dataChanged.connect(self.save_data)

    def save_data(self, topLeft, bottomRight, roles):
        if Qt.EditRole in roles:
            model = topLeft.model()
            record_id = int(model.data(model.index(topLeft.row(), 0)))
            table_name = self.current_table_name

            if table_name == 'PersonalSheet':
                column_names = ["id", "group_id", "full_name", "dob", "perm_address", "temp_address", "contact_number", "email", "scholarship", "father_name", "father_work", "father_phone", "mother_name", "mother_work", "mother_phone", "other_data"]
            elif table_name == 'Teacher':
                column_names = ["id", "full_name", "phone_number", "department_id"]
            elif table_name == 'Discipline':
                column_names = ["id", "name"]
            elif table_name == 'Semester':
                column_names = ["id", "group_id", "discipline_id", "teacher_id", "semester_number"]
            elif table_name == 'WorkPlan':
                column_names = ["id", "event", "venue", "dates", "performers", "result"]
            elif table_name == 'Department':
                column_names = ["id", "name", "phone"]

            values = [model.data(model.index(topLeft.row(), i)) for i in range(len(column_names))]
            update_query = f"UPDATE {table_name} SET " + ", ".join([f"{col} = ?" for col in column_names[1:]]) + " WHERE id = ?"
            self.update_database(update_query, values[1:] + [record_id])

    def update_database(self, query, values):
        conn = sqlite3.connect('curator.db')
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def delete_selected_row(self):
        current_table = self.stack.currentWidget()
        model = current_table.model()
        current_row = current_table.currentIndex().row()
        if current_row >= 0:
            record_id = int(model.data(model.index(current_row, 0)))
            delete_data(self.current_table_name, record_id)
            model.removeRow(current_row)
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления.")

    def update_table_if_needed(self, table_name):
        if self.current_table_name == table_name:
            self.view_data(table_name, self.get_headers_for_table(table_name))

    def get_headers_for_table(self, table_name):
        headers = {
            'StudentGroup': ["ID", "Название группы"],
            'GroupInfo': ["ID", "Группа", "Мужчин", "Женщин", "Из других регионов", "Дети-сироты", "Староста", "Профорг"],
            'PersonalSheet': ["ID", "Группа", "Ф.И.О.", "Дата рождения", "Постоянная регистрация", "Временная регистрация", "Контактный телефон", "Email", "Получение стипендии", "Отец (Ф.И.О.)", "Место работы, должность отца", "Телефон отца", "Мать (Ф.И.О.)", "Место работы, должность матери", "Телефон матери", "Другие данные"],
            'Teacher': ["ID", "Полное имя", "Номер телефона", "Кафедра"],
            'Discipline': ["ID", "Название дисциплины"],
            'Semester': ["ID", "Группа", "Дисциплина", "Преподаватель", "Номер семестра"],
            'WorkPlan': ["ID", "Мероприятие", "Место проведения", "Сроки", "Исполнители", "Результат"],
            'Department': ["ID", "Название кафедры", "Телефон"]
        }
        return headers.get(table_name, [])

    def get_department_names(self):
        departments = view_data_with_names('Department')
        return [(dept[0], dept[1]) for dept in departments]

    def get_discipline_names(self):
        disciplines = view_data_with_names('Discipline')
        return [(disc[0], disc[1]) for disc in disciplines]

    def get_teacher_names(self):
        teachers = view_data_with_names('Teacher')
        return [(teacher[0], teacher[1]) for teacher in teachers]

    def generate_report(self):
        if not self.current_group_id:
            QMessageBox.warning(self, "Ошибка", "Выберите группу перед созданием отчета.")
            return

        general_info = get_general_info(self.current_group_id)
        students_info = get_students_info(self.current_group_id)
        teachers_info = get_teachers_info()
        work_plan = get_work_plan()
        semester_info = get_semester_info(self.current_group_id)

        # Создаем DataFrame для каждого раздела отчета
        df_general_info = pd.DataFrame([general_info], columns=["Группа", "Мужчин", "Женщин", "Из других регионов", "Дети-сироты", "Староста", "Профорг"])

        df_students = pd.DataFrame(students_info, columns=["Ф.И.О.", "Дата рождения", "Постоянная регистрация", 
                                                           "Временная регистрация", "Контактный телефон", "Email", 
                                                           "Получение стипендии", "Отец (Ф.И.О.)", "Место работы отца", 
                                                           "Телефон отца", "Мать (Ф.И.О.)", "Место работы матери", 
                                                           "Телефон матери", "Другие данные"])
        
        df_teachers = pd.DataFrame(teachers_info, columns=["Полное имя", "Телефон", "Кафедра"])

        df_work_plan = pd.DataFrame(work_plan, columns=["Мероприятие", "Место проведения", "Сроки", 
                                                        "Исполнители", "Результат"])

        df_semester_info = pd.DataFrame(semester_info, columns=["Семестр", "Дисциплина", "Преподаватель", "Телефон кафедры"])

        # Записываем в CSV
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "", "CSV Files (*.csv)")
        if file_path:
            df_general_info.to_csv(file_path, index=False, mode='w', encoding='utf-8-sig')
            df_students.to_csv(file_path, index=False, mode='a', encoding='utf-8-sig')
            df_teachers.to_csv(file_path, index=False, mode='a', encoding='utf-8-sig')
            df_work_plan.to_csv(file_path, index=False, mode='a', encoding='utf-8-sig')
            df_semester_info.to_csv(file_path, index=False, mode='a', encoding='utf-8-sig')
            
            QMessageBox.information(self, "Информация", f"Отчет сохранен: {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
