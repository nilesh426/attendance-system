from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import login_user, logout_user, login_required, current_user
from io import StringIO, BytesIO
import csv
import datetime
from datetime import datetime as dt
import pandas as pd

from models import Teacher, Department, Student, Attendance
from forms import TeacherLoginForm as LoginForm, TeacherRegistrationForm as RegistrationForm, DepartmentForm, StudentForm, AttendanceForm
from extensions import db


def register_routes(app):

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            new_teacher = Teacher(username=form.username.data)
            new_teacher.set_password(form.password.data)
            db.session.add(new_teacher)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            teacher = Teacher.query.filter_by(username=form.username.data).first()
            if teacher and teacher.check_password(form.password.data):
                login_user(teacher)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid credentials.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out successfully.', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        today = datetime.date.today()
        attendance_today = Attendance.query.filter_by(date=today, teacher_id=current_user.id).count()
        student_count = Student.query.filter_by(teacher_id=current_user.id).count()
        department_count = Department.query.filter_by(teacher_id=current_user.id).count()
        return render_template('dashboard.html', attendance_today=attendance_today,
                               student_count=student_count, department_count=department_count)

    @app.route('/departments/add', methods=['GET', 'POST'])
    @login_required
    def add_department():
        form = DepartmentForm()
        if form.validate_on_submit():
            department = Department(department_name=form.department_name.data, teacher_id=current_user.id)
            db.session.add(department)
            db.session.commit()
            flash('Department added successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('add_department.html', form=form)

    @app.route('/students/add', methods=['GET', 'POST'])
    @login_required
    def add_student():
        form = StudentForm()
        form.department_id.choices = [(d.id, d.department_name) for d in Department.query.filter_by(teacher_id=current_user.id).all()]
        if form.validate_on_submit():
            student = Student(
                student_name=form.student_name.data,
                roll_no=form.roll_no.data,
                department_id=form.department_id.data,
                teacher_id=current_user.id
            )
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('add_student.html', form=form)

    @app.route('/attendance/mark', methods=['GET', 'POST'])
    @login_required
    def mark_attendance():
        selected_department_id = request.args.get('department_id', type=int)
        date_str = request.args.get('date', datetime.date.today().strftime('%Y-%m-%d'))
        selected_date = dt.strptime(date_str, '%Y-%m-%d').date()
        departments = Department.query.filter_by(teacher_id=current_user.id).all()
        students = []

        if selected_department_id:
            students = Student.query.filter_by(teacher_id=current_user.id, department_id=selected_department_id).all()

        if request.method == 'POST':
            for student in students:
                status = request.form.get(f'status_{student.id}')
                if status:
                    attendance = Attendance(
                        student_id=student.id,
                        student_name=student.student_name,
                        roll_no=student.roll_no,
                        status=status,
                        date=selected_date,
                        teacher_id=current_user.id
                    )
                    db.session.add(attendance)
            db.session.commit()
            flash('Attendance marked successfully!', 'success')
            return redirect(url_for('view_attendance'))

        return render_template('mark_attendance.html', departments=departments, students=students,
                               selected_department_id=selected_department_id, selected_date=date_str)

    @app.route('/attendance/history')
    @login_required
    def attendance_history():
        departments = Department.query.filter_by(teacher_id=current_user.id).all()
        selected_dept_id = request.args.get('department_id', type=int)

        student_query = Student.query.filter_by(teacher_id=current_user.id)
        if selected_dept_id:
            student_query = student_query.filter_by(department_id=selected_dept_id)

        students = student_query.all()
        history = []
        chart_labels = []
        chart_data = []

        for student in students:
            total_classes = Attendance.query.filter_by(student_id=student.id).count()
            presents = Attendance.query.filter_by(student_id=student.id, status='Present').count()
            percentage = (presents / total_classes * 100) if total_classes > 0 else 0

            history.append({
                'name': student.student_name,
                'roll_no': student.roll_no,
                'department': student.department.department_name,
                'total': total_classes,
                'present': presents,
                'percentage': round(percentage, 2)
            })
            chart_labels.append(student.student_name)
            chart_data.append(round(percentage, 2))

        return render_template('attendance_history.html', history=history,
                               departments=departments, selected_dept_id=selected_dept_id,
                               chart_labels=chart_labels, chart_data=chart_data)

    @app.route('/attendance/history/export')
    @login_required
    def export_attendance_history():
        selected_dept_id = request.args.get('department_id', type=int)
        students_query = Student.query.filter_by(teacher_id=current_user.id)
        if selected_dept_id:
            students_query = students_query.filter_by(department_id=selected_dept_id)

        students = students_query.all()
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['Student Name', 'Roll No', 'Department', 'Total Classes', 'Present', 'Attendance %'])

        for student in students:
            total_classes = Attendance.query.filter_by(student_id=student.id).count()
            presents = Attendance.query.filter_by(student_id=student.id, status='Present').count()
            percentage = (presents / total_classes * 100) if total_classes > 0 else 0

            cw.writerow([
                student.student_name,
                student.roll_no,
                student.department.department_name,
                total_classes,
                presents,
                round(percentage, 2)
            ])

        mem = BytesIO()
        mem.write(si.getvalue().encode('utf-8'))
        mem.seek(0)
        si.close()

        return send_file(mem, mimetype='text/csv', download_name='attendance_history.csv', as_attachment=True)

    @app.route('/defaulters')
    @login_required
    def defaulter_list():
        students = Student.query.filter_by(teacher_id=current_user.id).all()
        defaulters = []

        for student in students:
            total = Attendance.query.filter_by(student_id=student.id).count()
            present = Attendance.query.filter_by(student_id=student.id, status='Present').count()
            percentage = (present / total * 100) if total > 0 else 0
            if percentage < 75:
                defaulters.append({
                    'name': student.student_name,
                    'roll_no': student.roll_no,
                    'department': student.department.department_name,
                    'total': total,
                    'present': present,
                    'percentage': round(percentage, 2)
                })

        return render_template('defaulter_list.html', defaulters=defaulters)

    @app.route('/students/import', methods=['GET', 'POST'])
    @login_required
    def import_students():
        if request.method == 'POST':
            file = request.files.get('file')
            if not file or not file.filename.endswith('.xlsx'):
                flash('Please upload a valid Excel (.xlsx) file.', 'danger')
                return redirect(request.url)

            try:
                df = pd.read_excel(file)
            except Exception as e:
                flash(f'Error reading Excel file: {e}', 'danger')
                return redirect(request.url)

            required_cols = {'Student Name', 'Roll No', 'Department Name'}
            if not required_cols.issubset(df.columns):
                flash('Missing required columns. Include: Student Name, Roll No, Department Name', 'danger')
                return redirect(request.url)

            imported_count = 0
            for _, row in df.iterrows():
                dept_name = row['Department Name']
                department = Department.query.filter_by(department_name=dept_name, teacher_id=current_user.id).first()
                if not department:
                    department = Department(department_name=dept_name, teacher_id=current_user.id)
                    db.session.add(department)
                    db.session.commit()

                student = Student(
                    student_name=row['Student Name'],
                    roll_no=row['Roll No'],
                    department_id=department.id,
                    teacher_id=current_user.id
                )
                db.session.add(student)
                imported_count += 1

            db.session.commit()
            flash(f'{imported_count} students imported successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('import_students.html')
