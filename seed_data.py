from app import create_app, db
from app.models import User, OpenDay, Event, Building, SubjectArea, Course
from datetime import datetime, time, date, timedelta
import os

app = create_app()

def seed_database():
    with app.app_context():
        # Create admin user
        if not User.query.filter_by(email='admin@wlv.ac.uk').first():
            admin = User(
                email='admin@wlv.ac.uk',
                password='Admin123!',
                full_name='Admin User',
                is_admin=True
            )
            db.session.add(admin)
            print("Added admin user")

        # Create subject areas
        subject_areas = [
            ('Business and Management', 'Business, entrepreneurship, management, and leadership courses'),
            ('Computing and Computer Science', 'Programming, data science, cybersecurity, and digital technologies'),
            ('Education and Teaching', 'Teacher training, educational leadership, and childhood studies'),
            ('Engineering', 'Mechanical, electrical, civil, and aerospace engineering'),
            ('Health and Social Care', 'Nursing, midwifery, paramedic science, and social work'),
            ('Law', 'Legal studies, criminology, and policing'),
            ('Science', 'Biology, chemistry, physics, and forensic science'),
            ('Arts and Humanities', 'Art, design, media, English, and history')
        ]

        for name, desc in subject_areas:
            if not SubjectArea.query.filter_by(name=name).first():
                area = SubjectArea(name=name, description=desc)
                db.session.add(area)
                print(f"Added subject area: {name}")

        # Create buildings
        buildings = [
            ('MC Building', 'MC', 'Main campus building with lecture halls and student services', 'City Campus', 52.5874, -2.1273),
            ('Science Centre', 'SC', 'Modern science and research facilities', 'City Campus', 52.5872, -2.1264),
            ('Performance Hub', 'PH', 'Performing arts and music facilities', 'Walsall Campus', 52.5801, -1.9909),
            ('Student Centre', 'FS', 'Student support and services hub', 'City Campus', 52.5882, -2.1298)
        ]

        for name, code, desc, campus, lat, lng in buildings:
            if not Building.query.filter_by(name=name).first():
                building = Building(
                    name=name, code=code, description=desc,
                    campus=campus, latitude=lat, longitude=lng
                )
                db.session.add(building)
                print(f"Added building: {name}")

        # Create open days
        today = date.today()
        open_days = [
            ('Undergraduate Open Day', 'Explore our undergraduate courses and campus facilities', 
             today + timedelta(days=30), '09:00', '16:00', 'City Campus'),
            ('Postgraduate Open Evening', 'Learn about our postgraduate programs and research opportunities', 
             today + timedelta(days=45), '16:00', '20:00', 'City Campus'),
            ('Virtual Open Day', 'Online event with virtual tours and live Q&A sessions', 
             today + timedelta(days=60), '10:00', '15:00', None, True)
        ]

        for title, desc, event_date, start, end, location, is_virtual in (
                open_days + [(o[0], o[1], o[2], o[3], o[4], o[5], False) for o in open_days[:2]]):
            if not OpenDay.query.filter_by(title=title, event_date=event_date).first():
                open_day = OpenDay(
                    title=title,
                    description=desc,
                    event_date=event_date,
                    start_time=datetime.strptime(start, '%H:%M').time(),
                    end_time=datetime.strptime(end, '%H:%M').time(),
                    location=location,
                    is_virtual=is_virtual if 'is_virtual' in locals() else False
                )
                db.session.add(open_day)
                print(f"Added open day: {title} on {event_date}")

        db.session.commit()
        print("Database seeded with basic data")

        # Create events after committing the open days
        if OpenDay.query.count() > 0 and Event.query.count() == 0:
            # Get first open day and buildings
            open_day = OpenDay.query.first()
            buildings = Building.query.all()
            subject_areas = SubjectArea.query.all()
            
            if open_day and buildings and subject_areas:
                events = [
                    ('Welcome Talk', 'Introduction to the University of Wolverhampton', 'Talk', 
                     '09:30', '10:00', buildings[0].id, 'LT1', 100, None, 'Prof. Jane Smith'),
                    ('Computer Science Showcase', 'Demonstrations of student projects', 'Workshop', 
                     '10:30', '11:30', buildings[1].id, 'Lab 3', 30, subject_areas[1].id, 'Dr. Alan Turing'),
                    ('Campus Tour', 'Guided tour of the City Campus facilities', 'Tour', 
                     '12:00', '13:00', None, None, 20, None, 'Student Ambassadors'),
                    ('Business School Q&A', 'Meet faculty and ask questions', 'Talk', 
                     '14:00', '15:00', buildings[0].id, 'Room 202', 50, subject_areas[0].id, 'Dr. Richard Branson')
                ]
                
                for title, desc, event_type, start, end, building_id, room, capacity, subject_id, presenter in events:
                    event = Event(
                        open_day_id=open_day.id,
                        title=title,
                        description=desc,
                        event_type=event_type,
                        start_time=datetime.strptime(start, '%H:%M').time(),
                        end_time=datetime.strptime(end, '%H:%M').time(),
                        building_id=building_id,
                        room=room,
                        capacity=capacity,
                        subject_area_id=subject_id,
                        presenter=presenter
                    )
                    db.session.add(event)
                    print(f"Added event: {title}")
                
                db.session.commit()
                print("Events created successfully")

if __name__ == '__main__':
    seed_database()