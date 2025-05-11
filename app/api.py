from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app import db
from app.models import (
    User, OpenDay, Event, Building, SubjectArea,
    Registration, UserAgenda, Feedback, Course, FAQ
)
from app.utils import validate_email, validate_password
from datetime import datetime, time
import json

# Create Blueprint
api_bp = Blueprint('api', __name__)


# ==================== AUTH ROUTES ====================

@api_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate input
    if not all(k in data for k in ['email', 'password', 'full_name']):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if email is valid
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400

    # Check if password is strong enough
    if not validate_password(data['password']):
        return jsonify(
            {'error': 'Password must be at least 8 characters and include a number and special character'}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Create new user
    try:
        user = User(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            phone=data.get('phone')
        )
        db.session.add(user)
        db.session.commit()

        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200


@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_user():
    identity = get_jwt_identity()
    user = User.query.get(identity)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict()}), 200


# ==================== OPEN DAYS ROUTES ====================

@api_bp.route('/opendays', methods=['GET'])
def get_open_days():
    open_days = OpenDay.query.order_by(OpenDay.event_date).all()
    return jsonify({
        'open_days': [open_day.to_dict() for open_day in open_days]
    }), 200


@api_bp.route('/opendays/<int:open_day_id>', methods=['GET'])
def get_open_day(open_day_id):
    open_day = OpenDay.query.get(open_day_id)

    if not open_day:
        return jsonify({'error': 'Open day not found'}), 404

    return jsonify({'open_day': open_day.to_dict()}), 200


@api_bp.route('/opendays', methods=['POST'])
@jwt_required()
def create_open_day():
    # Check if user is admin
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Validate required fields
    required_fields = ['title', 'event_date', 'start_time', 'end_time']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Convert string dates to Python date objects
        event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()

        # Convert string times to Python time objects
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()

        # Convert registration_deadline if provided
        registration_deadline = None
        if 'registration_deadline' in data and data['registration_deadline']:
            registration_deadline = datetime.strptime(data['registration_deadline'], '%Y-%m-%d').date()

        open_day = OpenDay(
            title=data['title'],
            description=data.get('description'),
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            location=data.get('location'),
            is_virtual=data.get('is_virtual', False),
            registration_deadline=registration_deadline
        )

        db.session.add(open_day)
        db.session.commit()

        return jsonify({
            'message': 'Open day created successfully',
            'open_day': open_day.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== EVENTS ROUTES ====================

@api_bp.route('/events', methods=['GET'])
def get_events():
    # Get query parameters for filtering
    open_day_id = request.args.get('open_day_id', type=int)
    event_type = request.args.get('event_type')
    subject_area_id = request.args.get('subject_area_id', type=int)
    building_id = request.args.get('building_id', type=int)

    # Build query
    query = Event.query

    if open_day_id:
        query = query.filter(Event.open_day_id == open_day_id)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if subject_area_id:
        query = query.filter(Event.subject_area_id == subject_area_id)
    if building_id:
        query = query.filter(Event.building_id == building_id)

    # Sort by start time
    events = query.order_by(Event.start_time).all()

    return jsonify({
        'events': [event.to_dict() for event in events]
    }), 200


@api_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get(event_id)

    if not event:
        return jsonify({'error': 'Event not found'}), 404

    return jsonify({'event': event.to_dict()}), 200


@api_bp.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    # Check if user is admin
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Validate required fields
    required_fields = ['open_day_id', 'title', 'event_type', 'start_time', 'end_time']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if open day exists
    open_day = OpenDay.query.get(data['open_day_id'])
    if not open_day:
        return jsonify({'error': 'Open day not found'}), 404

    try:
        # Convert string times to Python time objects
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()

        event = Event(
            open_day_id=data['open_day_id'],
            title=data['title'],
            description=data.get('description'),
            event_type=data['event_type'],
            start_time=start_time,
            end_time=end_time,
            building_id=data.get('building_id'),
            room=data.get('room'),
            capacity=data.get('capacity'),
            subject_area_id=data.get('subject_area_id'),
            presenter=data.get('presenter')
        )

        db.session.add(event)
        db.session.commit()

        return jsonify({
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== REGISTRATIONS ROUTES ====================

@api_bp.route('/register/openday/<int:open_day_id>', methods=['POST'])
@jwt_required()
def register_for_open_day(open_day_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    # Check if open day exists
    open_day = OpenDay.query.get(open_day_id)
    if not open_day:
        return jsonify({'error': 'Open day not found'}), 404

    # Check if already registered
    existing = Registration.query.filter_by(user_id=user_id, open_day_id=open_day_id).first()
    if existing:
        return jsonify({'message': 'Already registered for this open day', 'registration': existing.to_dict()}), 200

    try:
        registration = Registration(
            user_id=user_id,
            open_day_id=open_day_id,
            interest_area=data.get('interest_area'),
            receive_updates=data.get('receive_updates', False)
        )

        db.session.add(registration)
        db.session.commit()

        return jsonify({
            'message': 'Successfully registered for open day',
            'registration': registration.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/registrations', methods=['GET'])
@jwt_required()
def get_user_registrations():
    user_id = get_jwt_identity()

    registrations = Registration.query.filter_by(user_id=user_id).all()

    return jsonify({
        'registrations': [registration.to_dict() for registration in registrations]
    }), 200


# ==================== AGENDA ROUTES ====================

@api_bp.route('/agenda', methods=['GET'])
@jwt_required()
def get_user_agenda():
    user_id = get_jwt_identity()
    open_day_id = request.args.get('open_day_id', type=int)

    # Get user agenda items
    query = UserAgenda.query.filter_by(user_id=user_id)

    # Filter by open day if provided
    if open_day_id:
        query = query.join(Event).filter(Event.open_day_id == open_day_id)

    agenda_items = query.join(Event).order_by(Event.start_time).all()

    # Format response
    result = []
    for item in agenda_items:
        event_data = item.event.to_dict()
        event_data['attended'] = item.attended
        event_data['added_at'] = item.added_at.isoformat() if item.added_at else None
        result.append(event_data)

    return jsonify({
        'agenda': result
    }), 200


@api_bp.route('/agenda/add/<int:event_id>', methods=['POST'])
@jwt_required()
def add_to_agenda(event_id):
    user_id = get_jwt_identity()

    # Check if event exists
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    # Check if already in agenda
    existing = UserAgenda.query.filter_by(user_id=user_id, event_id=event_id).first()
    if existing:
        return jsonify({'message': 'Event already in agenda'}), 200

    # Add to agenda
    try:
        agenda_item = UserAgenda(user_id=user_id, event_id=event_id)
        db.session.add(agenda_item)
        db.session.commit()

        return jsonify({
            'message': 'Event added to agenda successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/agenda/remove/<int:event_id>', methods=['DELETE'])
@jwt_required()
def remove_from_agenda(event_id):
    user_id = get_jwt_identity()

    # Check if item exists in user's agenda
    agenda_item = UserAgenda.query.filter_by(user_id=user_id, event_id=event_id).first()

    if not agenda_item:
        return jsonify({'error': 'Event not in agenda'}), 404

    # Remove from agenda
    try:
        db.session.delete(agenda_item)
        db.session.commit()

        return jsonify({
            'message': 'Event removed from agenda successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== MAPS ROUTES ====================

@api_bp.route('/maps/buildings', methods=['GET'])
def get_buildings():
    campus = request.args.get('campus')

    query = Building.query

    if campus:
        query = query.filter(Building.campus == campus)

    buildings = query.all()

    return jsonify({
        'buildings': [building.to_dict() for building in buildings]
    }), 200


@api_bp.route('/maps/campuses', methods=['GET'])
def get_campuses():
    # Get unique campus names
    campuses = db.session.query(Building.campus).distinct().all()
    campus_list = [campus[0] for campus in campuses if campus[0]]

    return jsonify({
        'campuses': campus_list
    }), 200


# ==================== COURSES ROUTES ====================

@api_bp.route('/courses', methods=['GET'])
def get_courses():
    subject_area_id = request.args.get('subject_area_id', type=int)

    query = Course.query

    if subject_area_id:
        query = query.filter(Course.subject_area_id == subject_area_id)

    courses = query.all()

    return jsonify({
        'courses': [course.to_dict() for course in courses]
    }), 200


@api_bp.route('/courses/subject-areas', methods=['GET'])
def get_subject_areas():
    subject_areas = SubjectArea.query.all()

    return jsonify({
        'subject_areas': [subject_area.to_dict() for subject_area in subject_areas]
    }), 200


# ==================== FEEDBACK ROUTES ====================

@api_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    if not all(k in data for k in ['open_day_id', 'rating']):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate rating
    if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

    # Check if open day exists
    open_day = OpenDay.query.get(data['open_day_id'])
    if not open_day:
        return jsonify({'error': 'Open day not found'}), 404

    # Check if user already submitted feedback for this open day
    existing = Feedback.query.filter_by(user_id=user_id, open_day_id=data['open_day_id']).first()
    if existing:
        return jsonify({'error': 'You have already submitted feedback for this open day'}), 409

    try:
        feedback = Feedback(
            user_id=user_id,
            open_day_id=data['open_day_id'],
            rating=data['rating'],
            useful_aspects=data.get('useful_aspects', []),
            improvement_suggestions=data.get('improvement_suggestions'),
            additional_comments=data.get('additional_comments')
        )

        db.session.add(feedback)
        db.session.commit()

        return jsonify({
            'message': 'Feedback submitted successfully',
            'feedback': feedback.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== CONTACT ROUTES ====================

@api_bp.route('/contact', methods=['POST'])
def submit_contact_form():
    data = request.get_json()

    # Validate required fields
    if not all(k in data for k in ['name', 'email', 'message']):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate email
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400

    try:
        # Here you would typically save to database and/or send an email
        # For simplicity, we'll just return a success message
        return jsonify({
            'message': 'Your message has been sent. We will get back to you soon.',
            'contact': {
                'name': data['name'],
                'email': data['email'],
                'subject': data.get('subject', 'Open Day Inquiry'),
                'message': data['message']
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== FAQ ROUTES ====================

@api_bp.route('/faqs', methods=['GET'])
def get_faqs():
    faqs = FAQ.query.order_by(FAQ.created_at.desc()).all()
    return jsonify({'faqs': [faq.to_dict() for faq in faqs]}), 200


@api_bp.route('/faqs/<int:faq_id>', methods=['GET'])
def get_faq(faq_id):
    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({'error': 'FAQ not found'}), 404
    return jsonify({'faq': faq.to_dict()}), 200


@api_bp.route('/faqs', methods=['POST'])
@jwt_required()
def create_faq():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    if not all(k in data for k in ['question', 'answer']):
        return jsonify({'error': 'Missing required fields'}), 400

    faq = FAQ(question=data['question'], answer=data['answer'], category=data.get('category'))
    try:
        db.session.add(faq)
        db.session.commit()
        return jsonify({'message': 'FAQ created successfully', 'faq': faq.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/faqs/<int:faq_id>', methods=['PUT'])
@jwt_required()
def update_faq(faq_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({'error': 'FAQ not found'}), 404

    data = request.get_json()
    faq.question = data.get('question', faq.question)
    faq.answer = data.get('answer', faq.answer)
    faq.category = data.get('category', faq.category)

    try:
        db.session.commit()
        return jsonify({'message': 'FAQ updated successfully', 'faq': faq.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/faqs/<int:faq_id>', methods=['DELETE'])
@jwt_required()
def delete_faq(faq_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({'error': 'FAQ not found'}), 404

    try:
        db.session.delete(faq)
        db.session.commit()
        return jsonify({'message': 'FAQ deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
