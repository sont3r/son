from app import create_app, db
from app.models import User, OpenDay, Event, Building, SubjectArea, Registration, UserAgenda, Feedback, Course

app = create_app()

with app.app_context():
    # Check all tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"All tables in database: {tables}")
    
    # Count records in each table
    print("\nRecord counts:")
    print(f"Users: {User.query.count()}")
    print(f"Subject Areas: {SubjectArea.query.count()}")
    print(f"Buildings: {Building.query.count()}")
    print(f"Open Days: {OpenDay.query.count()}")
    print(f"Events: {Event.query.count()}")
    print(f"Courses: {Course.query.count()}")
    
    # Display some sample data
    print("\nSample Subject Areas:")
    for area in SubjectArea.query.all():
        print(f"- {area.name}")
    
    print("\nSample Open Days:")
    for day in OpenDay.query.all():
        print(f"- {day.title} on {day.event_date}")