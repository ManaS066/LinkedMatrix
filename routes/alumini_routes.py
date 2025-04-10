from flask import flash, render_template, request, session, redirect, url_for, jsonify
from app import app, alumini_collection, universities_collection
from bson.objectid import ObjectId


@app.route('/alumni_register', methods=['GET'])
def alumni_register_page():
    universities = list(universities_collection.find({}))
    
    return render_template('alumni_register.html', universities=universities)

@app.route('/register_alumni', methods=['POST'])
def register_alumni():
    university_id = request.form.get('universityId')
    department = request.form.get('department')
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    graduation_year = request.form.get('graduation_year')
    degree = request.form.get('degree')
    mobile_no = request.form.get('Mobile')
    current_company = request.form.get('current_company')
    current_location = request.form.get('current_location')
    
    # Get the new fields
    gpa = request.form.get('gpa', '')
    technical_skills = request.form.get('technical_skills', '')
    soft_skills = request.form.get('soft_skills', '')
    mentorship_bio = request.form.get('mentorship_bio', 'Feel free to reach out for career guidance or mentorship opportunities.')
    
    # Process experiences (multiple entries)
    experiences = []
    experience_companies = request.form.getlist('experience_company[]')
    experience_positions = request.form.getlist('experience_position[]')
    experience_start_dates = request.form.getlist('experience_start_date[]')
    experience_end_dates = request.form.getlist('experience_end_date[]')
    experience_descriptions = request.form.getlist('experience_description[]')
    
    for i in range(len(experience_companies)):
        if experience_companies[i]:  # Only add if company name is provided
            experiences.append({
                'company': experience_companies[i],
                'position': experience_positions[i] if i < len(experience_positions) else '',
                'start_date': experience_start_dates[i] if i < len(experience_start_dates) else '',
                'end_date': experience_end_dates[i] if i < len(experience_end_dates) else '',
                'description': experience_descriptions[i] if i < len(experience_descriptions) else ''
            })
    
    # Process achievements (multiple entries)
    achievements = []
    achievement_titles = request.form.getlist('achievement_title[]')
    achievement_years = request.form.getlist('achievement_year[]')
    achievement_descriptions = request.form.getlist('achievement_description[]')
    
    for i in range(len(achievement_titles)):
        if achievement_titles[i]:  # Only add if title is provided
            achievements.append({
                'title': achievement_titles[i],
                'year': achievement_years[i] if i < len(achievement_years) else '',
                'description': achievement_descriptions[i] if i < len(achievement_descriptions) else ''
            })
    
    # Process advanced degrees (multiple entries)
    advanced_degrees = []
    degree_titles = request.form.getlist('advanced_degree_title[]')
    degree_institutions = request.form.getlist('advanced_degree_institution[]')
    degree_fields = request.form.getlist('advanced_degree_field[]')
    degree_years = request.form.getlist('advanced_degree_year[]')
    
    for i in range(len(degree_titles)):
        if degree_titles[i]:  # Only add if title is provided
            advanced_degrees.append({
                'title': degree_titles[i],
                'institution': degree_institutions[i] if i < len(degree_institutions) else '',
                'field': degree_fields[i] if i < len(degree_fields) else '',
                'year': degree_years[i] if i < len(degree_years) else ''
            })
    
    # Check if all required fields are provided
    if not all([university_id, department, name, email, password, graduation_year, mobile_no]):
        return jsonify({"message": "All required fields are required"}), 400
    
    # Get university name
    university = universities_collection.find_one({"_id": ObjectId(university_id)})
    university_name = university["name"] if university else "Unknown University"
    
    # Insert the alumni record
    alumni_id = alumini_collection.insert_one({
        "university_name": university_name,
        "department": department,
        "name": name,
        "email": email,
        "password": password,  # Note: In a production environment, this should be hashed
        "graduation_year": graduation_year,
        "degree": degree,
        "mobile_no": mobile_no,
        "current_company": current_company,
        "current_location": current_location,
        "gpa": gpa,
        "technical_skills": technical_skills,
        "soft_skills": soft_skills,
        "experiences": experiences,
        "achievements": achievements,
        "advanced_degrees": advanced_degrees,
        "mentorship_bio": mentorship_bio,
        "approved": True  # Mark as pending approval
    }).inserted_id
    
    return redirect(url_for('login'))
@app.route('/alumni_login', methods=['GET', 'POST'])
def alumni_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        alumni = alumini_collection.find_one({"email": email, "password": password})

        if alumni:
            if not alumni.get('approved', False):
                flash("Your registration is pending for approval.", "warning")
                return render_template('login.html')
                
            session['alumni_id'] = str(alumni['_id'])
            session['alumni_name'] = alumni['name']
            return redirect(url_for('alumni_dashboard'))
        else:
            return render_template('login.html', error="Invalid Email or Password")

    return render_template('login.html', error="Invalid Email or Password")

@app.route('/alumni_dashboard')
def alumni_dashboard():
    if 'alumni_id' not in session:
        return redirect(url_for('login'))

    alumni = alumini_collection.find_one({"_id": ObjectId(session['alumni_id'])})

    if not alumni:
        return redirect(url_for('login'))

    return render_template('alumni_dashboard.html', alumni=alumni)

# @app.route('/save_alumni_education', methods=['POST'])