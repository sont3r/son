from app import create_app, db
from app.models import User, OpenDay, Event, Building, SubjectArea

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'OpenDay': OpenDay, 
        'Event': Event, 
        'Building': Building, 
        'SubjectArea': SubjectArea
    }

if __name__ == '__main__':
    app.run(debug=True)