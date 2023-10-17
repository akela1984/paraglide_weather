from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import datetime
import requests
import sqlite3
import bcrypt
import random

app = Flask(__name__)
app.secret_key = '5d2a1f0f7bba42f6a5476c1e1a683376' 

def get_news_from_database():
    try:
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        cursor.execute("SELECT date, title, text FROM news")
        news_data = cursor.fetchall()
        conn.close()
        return news_data
    except sqlite3.Error as e:
        return []
    
questions = [
    {
        "question": "What is the primary source of lift that keeps a paraglider in the air?",
        "answers": ["A) Jet engines", "B) Thermal currents", "C) Propellers", "D) Helium balloons"],
        "correct_answer": "B",
    },
    {
        "question": "What is the main piece of equipment used in paragliding to control direction and speed?",
        "answers": ["A) Harness", "B) Helmet", "C) Parachute", "D) Wing"],
        "correct_answer": "D",
    },
    {
        "question": "What do you call the steering controls on a paraglider?",
        "answers": ["A) Throttle", "B) Brakes", "C) Joystick", "D) Rudder"],
        "correct_answer": "B",
    },
    {
        "question": "In paragliding, what does the term 'wing loading' refer to?",
        "answers": ["A) The weight of the pilot", "B) The wind speed", "C) The type of wing used", "D) The number of flights per day"],
        "correct_answer": "A",
    },
    {
        "question": "Which type of paragliding flight involves flying as high as possible and then gliding back to the ground without using a motor?",
        "answers": ["A) Powered paragliding", "B) Tandem paragliding", "C) Acro paragliding", "D) Cross-country paragliding"],
        "correct_answer": "D",
    },
    {
        "question": "What is the name of the safety device used in paragliding that is designed to slow down or stop a rapid descent?",
        "answers": ["A) Flare", "B) Flap", "C) Flip", "D) Float"],
        "correct_answer": "A",
    },
    {
        "question": "Paragliders often use a weather forecasting tool to find rising air currents. What is this tool called?",
        "answers": ["A) Windsock", "B) Altimeter", "C) GPS", "D) Variometer"],
        "correct_answer": "D",
    },
    {
        "question": "What is the term for a sudden and dangerous loss of altitude in paragliding, often caused by turbulent air?",
        "answers": ["A) Stall", "B) Glide", "C) Collapse", "D) Tumble"],
        "correct_answer": "C",
    },
    {
        "question": "Paragliders wear a safety device that automatically deploys in case of an emergency. What is it called?",
        "answers": ["A) Reserve parachute", "B) Airbag", "C) Radio transmitter", "D) Windsock"],
        "correct_answer": "A",
    },
    {
        "question": "Which famous mountain range is a popular destination for paragliding in Europe?",
        "answers": ["A) The Andes", "B) The Alps", "C) The Rocky Mountains", "D) The Himalayas"],
        "correct_answer": "B",
    },
    # Add more questions here
]

# Shuffle the questions to make the quiz more random
random.shuffle(questions)

current_question = 0
score = 0


@app.route('/')
def index():
    try:
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Fetch the latest 10 news items from the database
        cursor.execute("SELECT date, title, text FROM news ORDER BY date DESC LIMIT 10")
        latest_news = cursor.fetchall()

        conn.close()

        return render_template('index.html', latest_news=latest_news)
    except sqlite3.Error as e:
        flash('An error occurred while fetching news data.', 'danger')
        return render_template('index.html', latest_news=[])


@app.route('/links')
def links():
    return render_template('links.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        license_type = request.form['license_type']

        # Check if the username or email is already registered
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            flash('Username or email is already registered. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert user data into the database
        try:
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, email, license_type) VALUES (?, ?, ?, ?)",
                           (username, hashed_password.decode('utf-8'), email, license_type))
            conn.commit()
            conn.close()
            flash('Registration successful', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash('Registration failed. Please try again.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['login-username']
        password = request.form['login-password']
        
        # Check if the provided username exists in the database
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, admin FROM users WHERE username=?", (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data is not None:
            db_username, hashed_password, admin = user_data
            # Verify the hashed password against the provided password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                session['username'] = username  # Set the username in the session
                session['admin'] = admin  # Set the admin status in the session

                # Flash a success message
                flash('Login successful!', 'success')
                return redirect(url_for('index'))  # Redirect to the index page after successful login
        
        # If the username or password is invalid, Flash an error message
        flash('Invalid credentials. Please try again', 'danger')
        
    return render_template('login.html')


@app.route('/myaccount')
def myaccount():
    if 'username' in session:
        username = session['username']

        # Retrieve the user's details from the database
        try:
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_data = cursor.fetchone()
            conn.close()

            if user_data:
                # user_data contains (id, username, password, email, license_type, admin)
                user_id, username, _, email, license_type, admin = user_data
                return render_template('myaccount.html', username=username, email=email, license_type=license_type, admin=admin)
            else:
                flash('User not found in the database.', 'danger')
                return redirect(url_for('index'))
        except sqlite3.Error as e:
            flash('An error occurred while fetching user data.', 'danger')
            return redirect(url_for('index'))
    else:
        flash('You must be logged in to access this page.', 'danger')
        return redirect(url_for('login'))
@app.route('/update_account', methods=['POST'])
def update_account():
    if 'username' in session:
        username = session['username']
        email = request.form['email']
        license_type = request.form['license_type']
        
        # Update user information in the database
        try:
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET email=?, license_type=? WHERE username=?", (email, license_type, username))
            conn.commit()
            conn.close()
            flash('Account information updated successfully', 'success')
        except sqlite3.Error as e:
            flash('Failed to update account information. Please try again.', 'danger')
    
    return redirect(url_for('myaccount'))

@app.route('/admin_panel')
def admin_panel():
    if 'username' in session:
        username = session['username']
        try:
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            users_data = cursor.fetchall()
            
            # Fetch news data from the database
            news_data = get_news_from_database()
            
            conn.close()

            if users_data:
                # Assuming you want to display all users, you can pass the list of users
                # to the template context.
                return render_template('admin_panel.html', username=username, users=users_data, news=news_data)
            else:
                flash('No users found in the database.', 'danger')
                return redirect(url_for('index'))
        except sqlite3.Error as e:
            flash('An error occurred while fetching data.', 'danger')
            return redirect(url_for('index'))
    else:
        flash('You must be logged in to access this page.', 'danger')
        return redirect(url_for('login'))


@app.route('/add_news', methods=['POST'])
def add_news():
    if request.method == 'POST':
        date = request.form['date']
        title = request.form['title']
        text = request.form['text']

        # Convert the date string to a datetime object
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('sites'))  # Redirect to the sites page

        # Insert news data into the database
        try:
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO news (date, title, text) VALUES (?, ?, ?)",
                           (date_obj, title, text))
            conn.commit()
            conn.close()
            flash('News added successfully', 'success')
        except sqlite3.Error as e:
            flash('Failed to add news. Please try again.', 'danger')

    return redirect(url_for('admin_panel'))  # Redirect to the admin_panel page after adding news

@app.route('/edit_news', methods=['POST'])
def edit_news():
    if 'username' in session:
        title = request.form.get('editTitle')
        text = request.form.get('editText')

        try:
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE news SET text=? WHERE title=?", (text, title))
            conn.commit()
            conn.close()
            flash('News updated successfully', 'success')
        except sqlite3.Error as e:
            flash('Failed to update news. Please try again.', 'danger')

    return redirect(url_for('admin_panel'))


@app.route('/delete_news', methods=['POST'])
def delete_news():
    if 'username' in session:
        try:
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()

            # Get the criteria for deleting news items
            date = request.form.get('date')
            title = request.form.get('title')
            text = request.form.get('text')

            # Delete news items based on the provided criteria
            cursor.execute("DELETE FROM news WHERE date=? AND title=? AND text=?", (date, title, text))
            conn.commit()
            conn.close()
            flash('News deleted successfully', 'success')
            return redirect(url_for('admin_panel'))
        except sqlite3.Error as e:
            flash('An error occurred while deleting news.', 'danger')
            return redirect(url_for('admin_panel'))
    else:
        flash('You must be logged in to delete news.', 'danger')
        return redirect(url_for('login'))


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' in session:
        if request.method == 'POST':
            user_id = request.form.get('user_id')

            try:
                conn = sqlite3.connect('mydatabase.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
                conn.commit()
                conn.close()
                flash('User deleted successfully', 'success')
            except sqlite3.Error as e:
                flash('Failed to delete user. Please try again.', 'danger')
        
        return redirect(url_for('admin_panel'))  
    else:
        flash('You must be logged in to access this page.', 'danger')
        return redirect(url_for('login'))
    
    
@app.route('/news/<string:title>')
def news(title):
    try:
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title, text, date FROM news WHERE title=?", (title,))
        news_data = cursor.fetchone()
        conn.close()

        if news_data:
            news_title, news_text, news_date = news_data
            return render_template('news.html', news_title=news_title, news_text=news_text, news_date=news_date)
        else:
            flash('News not found in the database.', 'danger')
            return redirect(url_for('index'))
    except sqlite3.Error as e:
        flash('An error occurred while fetching news data.', 'danger')
        return redirect(url_for('index'))
    
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    global current_question, score

    if request.method == 'POST':
        user_answer = request.form.get('answer')

        if user_answer == questions[current_question]["correct_answer"]:
            score += 1

        current_question += 1

        if current_question < len(questions):
            return render_template('quiz.html', question=questions[current_question])
        else:
            flash(f"Quiz completed! You scored {score} out of {len(questions)}", 'info')
            current_question = 0
            score = 0
            return redirect(url_for('quiz'))

    if current_question < len(questions):
        return render_template('quiz.html', question=questions[current_question])
    else:
        flash(f"Quiz completed! You scored {score} out of {len(questions)}", 'info')
        current_question = 0
        score = 0
        return render_template('quiz.html', question=None)

@app.route('/logout')
def logout():
    session.pop('username', None) 
    flash('You have successfully logged out', 'success')
    return redirect(url_for('index'))  

@app.route('/sites')
def sites():
    api_url = "https://api.openweathermap.org/data/2.5/forecast?lat=55.59194&lon=-3.66288&units=metric&appid=69129460125ea343f55bb51da80ec507"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()


        forecast_data = data['list'][:4 * 8]
        forecast = []

        
        for item in forecast_data:
            date = item['dt']
            time_str = datetime.utcfromtimestamp(date).strftime('%H:%M')
            
            # Check if the time is between 09:00 and 21:00 - rest of the day is irrelevant for this sport as it can fly in dark
            if '09:00' <= time_str <= '21:00':
                day_of_week = datetime.utcfromtimestamp(date).strftime('%a')
                date_str = datetime.utcfromtimestamp(date).strftime('%d/%m/%Y')
                temperature = round(item['main']['temp'])
                description = item['weather'][0]['description'].capitalize()
  
                wind_direction = get_wind_direction(item['wind']['deg'])
                wind_speed = round(item['wind']['speed'], 1)
                rain = 'rain' in item and item['rain']
                
                # Determine fly conditions for each site
                fly_condition_tinto_south, fly_condition_class_tinto_south = get_fly_condition_tinto_south(wind_direction, description, wind_speed)
                fly_condition_tinto_north, fly_condition_class_tinto_north = get_fly_condition_tinto_north(wind_direction, description, wind_speed)
                fly_condition_abington, fly_condition_class_abington = get_fly_condition_abington_and_dungeval(wind_direction, description, wind_speed)
                fly_condition_dungeval, fly_condition_class_dungeval = get_fly_condition_abington_and_dungeval(wind_direction, description, wind_speed)
           
                descriptionIcon = ''

                if 'clear sky' in description.lower():
                    descriptionIcon = 'fa-sun'  # Icon for clear sky
                elif 'few clouds' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for few clouds
                elif 'scattered clouds' in description.lower():
                    descriptionIcon = 'fa-cloud'  # Icon for scattered clouds
                elif 'broken clouds' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for broken clouds
                elif 'overcast clouds' in description.lower():
                    descriptionIcon = 'fa-cloud'  # Icon for overcast clouds
                elif 'mist' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for mist
                elif 'fog' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for fog
                elif 'haze' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for haze
                elif 'smoke' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for smoke
                elif 'dust' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for dust
                elif 'sand' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for sand
                elif 'dust and sand' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for dust and sand
                elif 'dust and fog' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for dust and fog
                elif 'dust and mist' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for dust and mist
                elif 'dust and haze' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for dust and haze
                elif 'dust and smoke' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for dust and smoke
                elif 'foggy' in description.lower():
                    descriptionIcon = 'fa-cloud-sun'  # Icon for foggy
                elif 'light rain' in description.lower():
                    descriptionIcon = 'fa-cloud-rain'  # Icon for light rain
                elif 'moderate rain' in description.lower():
                    descriptionIcon = 'fa-cloud-showers-heavy'  # Icon for moderate rain
                elif 'heavy rain' in description.lower():
                    descriptionIcon = 'fa-cloud-showers-heavy'  # Icon for heavy rain
                elif 'light snow' in description.lower():
                    descriptionIcon = 'fa-snowflake'  # Icon for light snow
                elif 'moderate snow' in description.lower():
                    descriptionIcon = 'fa-snowflake'  # Icon for moderate snow
                elif 'heavy snow' in description.lower():
                    descriptionIcon = 'fa-snowflake'  # Icon for heavy snow
                elif 'light drizzle' in description.lower():
                    descriptionIcon = 'fa-cloud-rain'  # Icon for light drizzle
                elif 'drizzle' in description.lower():
                    descriptionIcon = 'fa-cloud-showers-heavy'  # Icon for drizzle
                elif 'heavy drizzle' in description.lower():
                    descriptionIcon = 'fa-cloud-showers-heavy'  # Icon for heavy drizzle
                elif 'light rain showers' in description.lower():
                    descriptionIcon = 'fa-cloud-rain'  # Icon for light rain showers
                elif 'rain showers' in description.lower():
                    descriptionIcon = 'fa-cloud-showers-heavy'  # Icon for rain showers
                elif 'heavy rain showers' in description.lower():
                    descriptionIcon = 'fa-cloud-showers-heavy'  # Icon for heavy rain showers
                elif 'light snow showers' in description.lower():
                    descriptionIcon = 'fa-snowflake'  # Icon for light snow showers
                elif 'snow showers' in description.lower():
                    descriptionIcon = 'fa-snowflake'  # Icon for snow showers
                elif 'heavy snow showers' in description.lower():
                    descriptionIcon = 'fa-snowflake'  # Icon for heavy snow showers
                elif 'light thunderstorm' in description.lower():
                    descriptionIcon = 'fa-bolt'  # Icon for light thunderstorm
                elif 'thunderstorm' in description.lower():
                    descriptionIcon = 'fa-bolt'  # Icon for thunderstorm
                elif 'heavy thunderstorm' in description.lower():
                    descriptionIcon = 'fa-bolt'  # Icon for heavy thunderstorm
                elif 'thunderstorm with light rain' in description.lower():
                    descriptionIcon = 'fa-bolt'  # Icon for thunderstorm with light rain
                elif 'thunderstorm with rain' in description.lower():
                    descriptionIcon = 'fa-bolt'  # Icon for thunderstorm with rain
                elif 'thunderstorm with heavy rain' in description.lower():
                    descriptionIcon = 'fa-bolt'  # Icon for thunderstorm with heavy rain
                elif 'thunderstorm with light snow' in description.lower():
                    descriptionIcon = 'fa-bolt'  # Icon for thunderstorm with light snow
                elif 'thunderstorm with snow' in description.lower():
                    descriptionIcon = 'fa-bolt'  # Icon for thunderstorm with snow
                elif 'thunderstorm with heavy snow' in description.lower():
                    descriptionIcon = 'fa-bolt'  # Icon for thunderstorm with heavy snow
                elif 'sleet' in description.lower():
                    descriptionIcon = 'fa-cloud-rain'  # Icon for sleet
                elif 'freezing rain' in description.lower():
                    descriptionIcon = 'fa-cloud-rain'  # Icon for freezing rain
                elif 'freezing drizzle' in description.lower():
                    descriptionIcon = 'fa-cloud-rain'  # Icon for freezing drizzle
                elif 'tornado' in description.lower():
                    descriptionIcon = 'fa-tornado'  # Icon for tornado
                elif 'tropical storm' in description.lower():
                    descriptionIcon = 'fa-wind'  # Icon for tropical storm
                elif 'hurricane' in description.lower():
                    descriptionIcon = 'fa-wind'  # Icon for hurricane
                elif 'cold' in description.lower():
                    descriptionIcon = 'fa-thermometer-empty'  # Icon for cold
                elif 'hot' in description.lower():
                    descriptionIcon = 'fa-thermometer-full'  # Icon for hot
                elif 'windy' in description.lower():
                    descriptionIcon = 'fa-wind'  # Icon for windy
                else:
                    descriptionIcon = 'fa-sun'  # Default icon for other weather conditions (replace with your choice)
                
                forecast.append({
                    'dayOfWeek': day_of_week,
                    'date': date_str,
                    'time': time_str,
                    'temperature': temperature,
                    'description': description,
                    'windDirection': wind_direction,
                    'windSpeed': wind_speed,
                    'rain': rain,
                    'flyConditionTintoSouth': fly_condition_tinto_south,
                    'flyConditionTintoNorth': fly_condition_tinto_north,
                    'flyConditionAbington': fly_condition_abington,
                    'flyConditionDungeval': fly_condition_dungeval,
                    
                     # Add fly condition CSS class
                    'flyConditionClassTintoNorth': fly_condition_class_tinto_north,  
                    'flyConditionClassTintoSouth': fly_condition_class_tinto_south,  
                    'flyConditionClassAbington' : fly_condition_class_abington,
                    'flyConditionClassDungeval' : fly_condition_class_dungeval,
                    'descriptionIcon': descriptionIcon 
                    
                    
                })

        return render_template('sites.html', forecast=forecast)
    else:
        return "Error fetching weather data"

# Helper function to get wind direction
def get_wind_direction(degree):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return directions[round((degree % 360) / 22.5)]

# Helper function to determine fly condition for Tinto South
def get_fly_condition_tinto_south(wind_direction, description, wind_speed):
    if (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and "rain" in description.lower()
    ):
        return "Not flyable due to the rainy conditions.", "rain"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 0 <= wind_speed <= 3
    ):
        return "Ideal conditions for beginners and thermal flying", "ideal"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 3 < wind_speed <= 5
    ):
        return "Good conditions for most pilots", "good"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 5 < wind_speed <= 8
    ):
        return "Challenging conditions for intermediate pilots", "challenging"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 8 < wind_speed <= 11
    ):
        return "Difficult conditions for experienced pilots only", "difficult"
    elif (
        wind_direction in ["S", "SSW", "SSE", "SW", "SE"]
        and 11 < wind_speed <= 15
    ):
        return "Dangerous conditions for all pilots", "dangerous"
    elif wind_direction in ["S", "SSW", "SSE", "SW", "SE"] and wind_speed > 15:
        return "Extreme conditions, not suitable for flying", "extreme"
    else:
        return "The wind direction is not suitable for this site.", "unsuitable"
    

# Helper function to determine fly condition for Tinto North
def get_fly_condition_tinto_north(wind_direction, description, wind_speed):
    if (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and "rain" in description.lower()
    ):
        return "Not flyable due to the rainy conditions.", "rain"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 0 <= wind_speed <= 3
    ):
        return "Ideal conditions for beginners and thermal flying", "ideal"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 3 < wind_speed <= 5
    ):
        return "Good conditions for most pilots", "good"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 5 < wind_speed <= 8
    ):
        return "Challenging conditions for intermediate pilots", "challenging"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 8 < wind_speed <= 11
    ):
        return "Difficult conditions for experienced pilots only", "difficult"
    elif (
        wind_direction in ["N", "NNW", "NNE", "NW", "NE"]
        and 11 < wind_speed <= 15
    ):
        return "Dangerous conditions for all pilots", "dangerous"
    elif wind_direction in ["N", "NNW", "NNE", "NW", "NE"] and wind_speed > 15:
        return "Extreme conditions, not suitable for flying", "extreme"
    else:
        return "The wind direction is not suitable for this site.", "unsuitable"
    
    # Helper function to determine fly condition for Abington
def get_fly_condition_abington_and_dungeval(wind_direction, description, wind_speed):
    if (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and "rain" in description.lower()
    ):
        return "Not flyable due to the rainy conditions.", "rain"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 0 <= wind_speed <= 3
    ):
        return "Ideal conditions for beginners and thermal flying", "ideal"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 3 < wind_speed <= 5
    ):
        return "Good conditions for most pilots", "good"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 5 < wind_speed <= 8
    ):
        return "Challenging conditions for intermediate pilots", "challenging"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 8 < wind_speed <= 11
    ):
        return "Difficult conditions for experienced pilots only", "difficult"
    elif (
        wind_direction in ["W", "WSW", "WNW", "SW", "NW"]
        and 11 < wind_speed <= 15
    ):
        return "Dangerous conditions for all pilots", "dangerous"
    elif wind_direction in ["W", "WSW", "WNW", "Sw", "Nw"] and wind_speed > 15:
        return "Extreme conditions, not suitable for flying", "extreme"
    else:
        return "The wind direction is not suitable for this site.", "unsuitable"

if __name__ == '__main__':
    app.run()
