# 以下の import 行を追加します
from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, MetaData, Column, Integer, String, DateTime
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

metadata = MetaData()

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(50), nullable=False)
    description = db.Column(String(200))
    date = db.Column(DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(Integer, primary_key=True)
    event_id = db.Column(Integer, db.ForeignKey('events.id'), nullable=False)
    user_name = db.Column(String(50), nullable=False)
    attendance_status = db.Column(String(20), nullable=False) # 'attending' or 'not_attending'


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    events = Event.query.all()
    attendances = Attendance.query.all()  # 全ての出席情報を取得します
    return render_template('index.html', events=events, attendances=attendances)  # 出席情報をテンプレートに渡します

@app.route('/events', methods=['POST'])
def create_event():
    data = request.form
    name = data.get('name')
    description = data.get('description')
    date_string = data.get('date')

    # Convert the date string to a datetime object.
    date = datetime.strptime(date_string, "%Y-%m-%d")

    new_event = Event(name=name, description=description, date=date)
    db.session.add(new_event)
    db.session.commit()
    return redirect('/')

@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([{'id': event.id, 'name': event.name, 'description': event.description, 'date': event.date} for event in events]), 200

@app.route('/attendances', methods=['POST'])
def create_attendance():
    data = request.form
    new_attendance = Attendance(event_id=data['event_id'], user_name=data['user_name'], attendance_status=data['attendance'])
    db.session.add(new_attendance)
    db.session.commit()
    return redirect('/')

@app.route('/confirm_attendance/<event_id>', methods=['POST'])
def confirm_attendance(event_id):
    data = request.form
    user_name = data.get('user_name')
    attendance_status = data.get('attendance')
    new_attendance = Attendance(event_id=event_id, user_name=user_name, attendance_status=attendance_status)
    db.session.add(new_attendance)
    db.session.commit()
    return redirect('/')

@app.route('/attendances/<string:user_name>', methods=['GET'])
def get_attendances_for_user(user_name):
    attendances = Attendance.query.filter_by(user_name=user_name).all()
    return jsonify([{'event_id': attendance.event_id, 'user_name': attendance.user_name} for attendance in attendances]), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
