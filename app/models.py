from app import db, bcrypt
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY


# Users
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, password, full_name, phone=None, is_admin=False):
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.full_name = full_name
        self.phone = phone
        self.is_admin = is_admin

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_admin': self.is_admin
        }


# Subject Areas
class SubjectArea(db.Model):
    __tablename__ = 'subject_areas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


# Open Days
class OpenDay(db.Model):
    __tablename__ = 'open_days'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(255))
    is_virtual = db.Column(db.Boolean, default=False)
    registration_deadline = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'location': self.location,
            'is_virtual': self.is_virtual,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Buildings
class Building(db.Model):
    __tablename__ = 'buildings'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50))
    description = db.Column(db.Text)
    campus = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'campus': self.campus,
            'latitude': self.latitude,
            'longitude': self.longitude
        }


# Events
class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    open_day_id = db.Column(db.Integer, db.ForeignKey('open_days.id'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'))
    room = db.Column(db.String(50))
    capacity = db.Column(db.Integer)
    subject_area_id = db.Column(db.Integer, db.ForeignKey('subject_areas.id'))
    presenter = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    open_day = db.relationship('OpenDay', backref='events')
    building = db.relationship('Building', backref='events')
    subject_area = db.relationship('SubjectArea', backref='events')

    def to_dict(self):
        return {
            'id': self.id,
            'open_day_id': self.open_day_id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'building': self.building.to_dict() if self.building else None,
            'room': self.room,
            'capacity': self.capacity,
            'subject_area': self.subject_area.to_dict() if self.subject_area else None,
            'presenter': self.presenter,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Registrations
class Registration(db.Model):
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    open_day_id = db.Column(db.Integer, db.ForeignKey('open_days.id'))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    interest_area = db.Column(db.Integer, db.ForeignKey('subject_areas.id'))
    attendance_status = db.Column(db.String(50), default='registered')
    receive_updates = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship('User', backref='registrations')
    open_day = db.relationship('OpenDay', backref='registrations')
    subject = db.relationship('SubjectArea', backref='interested_registrations')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'open_day_id': self.open_day_id,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'interest_area': self.interest_area,
            'attendance_status': self.attendance_status,
            'receive_updates': self.receive_updates,
            'open_day': self.open_day.to_dict() if self.open_day else None
        }


# User Agenda
class UserAgenda(db.Model):
    __tablename__ = 'user_agenda'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    attended = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship('User', backref='agenda_items')
    event = db.relationship('Event', backref='agenda_items')

    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='user_event_unique'),)


# Feedback
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    open_day_id = db.Column(db.Integer, db.ForeignKey('open_days.id'))
    rating = db.Column(db.Integer)
    useful_aspects = db.Column(ARRAY(db.String))
    improvement_suggestions = db.Column(db.Text)
    additional_comments = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='feedback')
    open_day = db.relationship('OpenDay', backref='feedback')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'open_day_id': self.open_day_id,
            'rating': self.rating,
            'useful_aspects': self.useful_aspects,
            'improvement_suggestions': self.improvement_suggestions,
            'additional_comments': self.additional_comments,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }


# Courses
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    subject_area_id = db.Column(db.Integer, db.ForeignKey('subject_areas.id'))
    faculty = db.Column(db.String(255))
    duration = db.Column(db.String(50))
    ucas_code = db.Column(db.String(50))
    level = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subject_area = db.relationship('SubjectArea', backref='courses')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject_area': self.subject_area.to_dict() if self.subject_area else None,
            'faculty': self.faculty,
            'duration': self.duration,
            'ucas_code': self.ucas_code,
            'level': self.level
        }


# FAQs
class FAQ(db.Model):
    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'category': self.category,
        }
