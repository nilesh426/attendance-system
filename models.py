from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager

class Teacher(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)

    departments = db.relationship('Department', backref='teacher', lazy=True)
    students = db.relationship('Student', backref='teacher', lazy=True)
    attendances = db.relationship('Attendance', backref='teacher', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    students = db.relationship('Student', backref='department', lazy=True)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return Teacher.query.get(int(user_id))
