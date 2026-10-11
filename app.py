from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'event_registration_secret_key_2026'

DATABASE = 'registrations.db'


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with the registrations table."""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            organization TEXT,
            event_type TEXT NOT NULL,
            dietary_preference TEXT,
            comments TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    """Render the registration form."""
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    """Handle form submission."""
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    organization = request.form.get('organization', '').strip()
    event_type = request.form.get('event_type', '').strip()
    dietary_preference = request.form.get('dietary_preference', '').strip()
    comments = request.form.get('comments', '').strip()

    # Validation
    if not full_name or not email or not phone or not event_type:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('index'))

    try:
        conn = get_db()
        conn.execute(
            '''INSERT INTO registrations 
               (full_name, email, phone, organization, event_type, dietary_preference, comments)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (full_name, email, phone, organization, event_type, dietary_preference, comments)
        )
        conn.commit()
        conn.close()
        flash('Registration successful! We look forward to seeing you at the event.', 'success')
        return redirect(url_for('success'))
    except sqlite3.IntegrityError:
        flash('This email is already registered. Please use a different email.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/success')
def success():
    """Render the success page."""
    return render_template('success.html')


@app.route('/registrations')
def registrations():
    """Display all registrations (admin view)."""
    conn = get_db()
    rows = conn.execute('SELECT * FROM registrations ORDER BY registered_at DESC').fetchall()
    conn.close()
    return render_template('registrations.html', registrations=rows)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
