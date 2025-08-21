from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Simple database setup
DATABASE = 'surveys.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables"""
    conn = get_db_connection()
    
    # Create surveys table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Create questions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT DEFAULT 'text',
            is_required BOOLEAN DEFAULT 0,
            question_order INTEGER NOT NULL,
            checkbox_options TEXT,
            FOREIGN KEY (survey_id) REFERENCES surveys (id)
        )
    ''')
    
    # Add checkbox_options column if it doesn't exist (for existing databases)
    try:
        conn.execute('ALTER TABLE questions ADD COLUMN checkbox_options TEXT')
        conn.commit()
    except:
        # Column already exists, ignore error
        pass
    
    # Create responses table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            responses_data TEXT NOT NULL,
            FOREIGN KEY (survey_id) REFERENCES surveys (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database when app starts
init_db()

@app.route('/')
def home():
    """Home page route - displays the main landing page with hero section"""
    conn = get_db_connection()
    survey_count = conn.execute('SELECT COUNT(*) FROM surveys').fetchone()[0]
    response_count = conn.execute('SELECT COUNT(*) FROM responses').fetchone()[0]
    conn.close()
    return render_template("index.html", title="Home", survey_count=survey_count, response_count=response_count)

@app.route('/surveys')
def survey_selection():
    """Survey creation page route - displays the survey creation form"""
    return render_template("survey.html", title="Create Survey")

@app.route('/surveys/create', methods=['POST'])
def create_survey():
    """Handle simple survey creation from the form"""
    try:
        # Get survey basic info
        survey_title = request.form.get('survey_title', '').strip()
        survey_description = request.form.get('survey_description', '').strip()
        
        if not survey_title:
            return "Survey title is required", 400
        
        conn = get_db_connection()
        
        # Insert the new survey
        cursor = conn.execute(
            'INSERT INTO surveys (title, description) VALUES (?, ?)',
            (survey_title, survey_description)
        )
        survey_id = cursor.lastrowid
        
        # Add questions (up to 5)
        for i in range(1, 6):
            question_text = request.form.get(f'question_text_{i}', '').strip()
            if question_text:  # Only add non-empty questions
                question_type = request.form.get(f'question_type_{i}', 'text')
                is_required = 1 if request.form.get(f'required_{i}') else 0
                checkbox_options = request.form.get(f'checkbox_options_{i}', '').strip()
                
                conn.execute(
                    'INSERT INTO questions (survey_id, question_text, question_type, is_required, question_order, checkbox_options) VALUES (?, ?, ?, ?, ?, ?)',
                    (survey_id, question_text, question_type, is_required, i, checkbox_options)
                )
        
        conn.commit()
        conn.close()
        
        # Redirect to surveys list
        return redirect(url_for('list_surveys'))
        
    except Exception as e:
        print(f"Error creating survey: {e}")
        return "Error creating survey", 500

@app.route('/surveys/list')
def list_surveys():
    """Show all created surveys"""
    conn = get_db_connection()
    surveys = conn.execute(
        'SELECT * FROM surveys ORDER BY id DESC'
    ).fetchall()
    conn.close()
    return render_template("survey_list.html", title="All Surveys", surveys=surveys)

@app.route('/surveys/<int:survey_id>')
def view_survey(survey_id):
    """View a specific survey"""
    conn = get_db_connection()
    survey = conn.execute(
        'SELECT * FROM surveys WHERE id = ?', (survey_id,)
    ).fetchone()
    
    if not survey:
        return "Survey not found", 404
    
    questions = conn.execute(
        'SELECT * FROM questions WHERE survey_id = ? ORDER BY question_order',
        (survey_id,)
    ).fetchall()
    conn.close()
    
    return render_template("view_survey.html", title=survey['title'], survey=survey, questions=questions)

@app.route('/surveys/<int:survey_id>/take')
def take_survey(survey_id):
    """Take/fill out a survey"""
    conn = get_db_connection()
    survey = conn.execute(
        'SELECT * FROM surveys WHERE id = ?', (survey_id,)
    ).fetchone()
    
    if not survey:
        return "Survey not found", 404
    
    questions = conn.execute(
        'SELECT * FROM questions WHERE survey_id = ? ORDER BY question_order',
        (survey_id,)
    ).fetchall()
    conn.close()
    
    return render_template("take_survey.html", title=f"Take Survey: {survey['title']}", survey=survey, questions=questions)

@app.route('/surveys/<int:survey_id>/submit', methods=['POST'])
def submit_survey_response(survey_id):
    """Submit survey response and redirect to thank you page"""
    try:
        # Collect all responses
        responses = {}
        
        for key, value in request.form.items():
            if key.startswith('question_'):
                responses[key] = value
        
        # Handle multiple selections (checkbox dropdown)
        for key in request.form.keys():
            if key.startswith('question_'):
                values = request.form.getlist(key)
                if len(values) > 1:
                    responses[key] = ', '.join(values)
                elif len(values) == 1:
                    responses[key] = values[0]
        
        # Save to database
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO responses (survey_id, responses_data) VALUES (?, ?)',
            (survey_id, json.dumps(responses))
        )
        conn.commit()
        conn.close()
        
        # Redirect to thank you page
        return redirect(url_for('survey_thank_you'))
        
    except Exception as e:
        print(f"Error submitting response: {e}")
        return "Error submitting response", 500

@app.route('/surveys/thank-you')
def survey_thank_you():
    """Thank you page after survey submission"""
    return render_template("survey_thank_you.html", title="Thank You")

@app.route('/surveys/<int:survey_id>/results')
def survey_results(survey_id):
    """View survey results/responses"""
    conn = get_db_connection()
    survey = conn.execute(
        'SELECT * FROM surveys WHERE id = ?', (survey_id,)
    ).fetchone()
    
    if not survey:
        return "Survey not found", 404
    
    questions = conn.execute(
        'SELECT * FROM questions WHERE survey_id = ? ORDER BY question_order',
        (survey_id,)
    ).fetchall()
    
    responses = conn.execute(
        'SELECT * FROM responses WHERE survey_id = ?',
        (survey_id,)
    ).fetchall()
    
    # Parse response data
    parsed_responses = []
    for response in responses:
        response_data = json.loads(response['responses_data'])
        parsed_responses.append(response_data)
    
    conn.close()
    
    return render_template("survey_results.html", title=f"Results: {survey['title']}", 
                         survey=survey, questions=questions, responses=parsed_responses)

@app.route('/surveys/<int:survey_id>/delete', methods=['POST'])
def delete_survey(survey_id):
    """Delete a survey and all its questions and responses"""
    try:
        conn = get_db_connection()
        
        # Delete responses first (foreign key constraint)
        conn.execute('DELETE FROM responses WHERE survey_id = ?', (survey_id,))
        
        # Delete questions
        conn.execute('DELETE FROM questions WHERE survey_id = ?', (survey_id,))
        
        # Delete survey
        conn.execute('DELETE FROM surveys WHERE id = ?', (survey_id,))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('list_surveys'))
        
    except Exception as e:
        print(f"Error deleting survey: {e}")
        return "Error deleting survey", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)