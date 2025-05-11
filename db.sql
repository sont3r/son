-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Open Days Table
CREATE TABLE open_days (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    location VARCHAR(255),
    is_virtual BOOLEAN DEFAULT FALSE,
    registration_deadline DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subject Areas Table
CREATE TABLE subject_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

-- Courses Table
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subject_area_id INTEGER REFERENCES subject_areas(id),
    faculty VARCHAR(255),
    duration VARCHAR(50),
    ucas_code VARCHAR(50),
    level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Buildings Table
CREATE TABLE buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    description TEXT,
    campus VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Events Table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    open_day_id INTEGER REFERENCES open_days(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL, -- talk, tour, workshop, etc.
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    building_id INTEGER REFERENCES buildings(id),
    room VARCHAR(50),
    capacity INTEGER,
    subject_area_id INTEGER REFERENCES subject_areas(id),
    presenter VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Registrations Table
CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    open_day_id INTEGER REFERENCES open_days(id),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interest_area INTEGER REFERENCES subject_areas(id),
    attendance_status VARCHAR(50) DEFAULT 'registered',
    receive_updates BOOLEAN DEFAULT FALSE
);

-- User Agenda Items Table
CREATE TABLE user_agenda (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_id INTEGER REFERENCES events(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attended BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, event_id)
);

-- Feedback Table
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    open_day_id INTEGER REFERENCES open_days(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    useful_aspects TEXT[], -- Storing as array
    improvement_suggestions TEXT,
    additional_comments TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications Table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50), -- event_update, reminder, general, etc.
    related_event_id INTEGER REFERENCES events(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Notifications Table (for tracking read status)
CREATE TABLE user_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    notification_id INTEGER REFERENCES notifications(id),
    is_read BOOLEAN DEFAULT FALSE,
    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, notification_id)
);

-- Contact Messages Table
CREATE TABLE contact_messages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded BOOLEAN DEFAULT FALSE,
    responded_at TIMESTAMP
);