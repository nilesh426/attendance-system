from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from models import Teacher

class TeacherLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TeacherRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        teacher = Teacher.query.filter_by(username=username.data).first()
        if teacher:
            raise ValidationError('Username already exists.')

class DepartmentForm(FlaskForm):
    department_name = StringField('Department Name', validators=[DataRequired()])
    submit = SubmitField('Add Department')

class StudentForm(FlaskForm):
    student_name = StringField('Student Name', validators=[DataRequired()])
    roll_no = StringField('Roll Number', validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Student')

class AttendanceForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent')], validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Mark Attendance')
