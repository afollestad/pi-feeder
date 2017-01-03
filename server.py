#/usr/bin/python3

"""The main HTTP server."""
from flask import Flask, render_template, jsonify, session, escape, redirect, url_for, request
from motor_util import MotorUtil
from datetime import timedelta
from discovery import init_visibility
from exceptions import InvalidRequestData
import scheduling
import auth
from constants import MOTOR_DEFAULT_DURATION
import prefs

app = Flask(__name__, static_url_path='/static')

@app.errorhandler(InvalidRequestData)
def handle_invalid_request_data(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.before_request
def intercept_login():
    """Intercepts every request and checks if the user is logged in."""
    if 'username' not in session and request.endpoint is not None and request.endpoint != 'login' and request.endpoint != 'api_login' and request.endpoint != 'static':

        token = request.headers.get('token')
        if token is None:
            token = request.args.get('token') 
        if token is None:
            return redirect(url_for('login'))
        else:
            api_user = auth.validate_token(token)
            if api_user is None:
                raise InvalidRequestData('Invalid authentication token.', status_code=401)
            return
    
    # Sessions last for 30 minutes before having to login again
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    return

@app.route('/')
def home():
    """The homepage, after logging in."""
    show_activate_now = request.args.get('token') is None
    return render_template('index.j2', show_menu=True, show_refresh=True, show_activate_now=show_activate_now)

@app.route('/add_recurrence', methods=['POST'])
def add_recurrence():
    """API: adds an occurrence to the recurrence schedule."""
    content = request.get_json(silent=True)
    day_id = content['day_id']
    hour = content['hour']
    minute = content['minute']

    if not scheduling.add_occurrence(day_id, hour, minute):
        raise InvalidRequestData('Cannot add a duplicate occurrence')

    response = {'status': 'success'}
    return jsonify(**response)

@app.route('/remove_recurrence', methods=['POST'])
def remove_recurrence():
    """API: removes an occurrence from the recurrence schedule."""
    content = request.get_json(silent=True)
    day_id = content['day_id']
    hour = content['hour']
    minute = content['minute']
    scheduling.remove_recurrence(day_id, hour, minute)
    response = {'status': 'success'}
    return jsonify(**response)

@app.route('/add_onetime_occurrence', methods=['GET', 'POST'])
@app.route('/add_onetime_occurrence/<error>', methods=['GET', 'POST'])
def add_onetime_occurrence(error=None):
    """API: the modal for adding a one-time occurrence to the schedule."""
    if request.method == 'POST':
        content = request.get_json(silent=True)
        year = content['year']
        month = content['month']
        day = content['day']
        hour = content['hour']
        minute = content['minute']
        
        if not scheduling.add_onetime_occurrence(year, month, day, hour, minute):
            raise InvalidRequestData('Cannot add a duplicate occurrence.')

        response = {'status': 'success'}
        return jsonify(**response)
    else:
        return render_template('onetimemodal.j2', error_message=error)

@app.route('/remove_onetime_occurrence', methods=['POST'])
def remove_onetime_occurrence():
    """API: removes an occurrence from the recurrence schedule."""
    content = request.get_json(silent=True)
    year = content['year']
    month = content['month']
    day = content['day']
    hour = content['hour']
    minute = content['minute']
    scheduling.remove_onetime_occurrence(year, month, day, hour, minute)
    response = {'status': 'success'}
    return jsonify(**response)

@app.route('/schedule')
def schedule():
    """API: retrieves the full reoccurrence schedule."""
    date = scheduling.get_next_occurrence()
    nextOccurrence = -1
    if date is not None:
        nextOccurrence = int(date.timestamp() * 1000)

    schedule = scheduling.get_recurrence_schedule()
    recurrences = []
    for recur in schedule:
        recurrences.append({'day_id': recur[0], 'hour': recur[1], 'minute': recur[2]})

    onetimeschedule = scheduling.get_onetime_occurrence_schedule()
    occurrences = []
    for recur in onetimeschedule:
        occurrences.append({'year': recur[0], 'month': recur[1], 'day': recur[2], 'hour': recur[3], 'minute': recur[4]})

    response = {'status': 'success', 'next_occurrence': nextOccurrence, 'schedule': recurrences, 'onetimes': occurrences}
    return jsonify(**response)

@app.route('/activate', methods=['POST'])
def activate():
    """Triggers the feeder now."""
    MotorUtil().turn_motor_async()
    response = {'status': 'success', 'duration': MOTOR_DEFAULT_DURATION}
    return jsonify(**response)

@app.route('/api_login', methods=['POST'])
def api_login(error=None):
    content = request.get_json(silent=True)
    username = content.get('username')
    password = content.get('password')
    if auth.try_login(username, password):
        new_token = auth.generate_token(username)
        response = {'status': 'success', 'token': new_token}
        return jsonify(**response)
    else:
        raise InvalidRequestData('Invalid username or password.')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/<error>', methods=['GET', 'POST'])
def login(error=None):
    """Loads the login page or performs login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if auth.try_login(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login', error='Wrong username or password.'))
    else:
        if 'username' in session:
            return redirect(url_for('home'))
        return render_template('login.j2', error_message=error, show_menu=False, show_refresh=False)

@app.route('/settings', methods=['GET', 'POST'])
@app.route('/settings/<error>', methods=['GET', 'POST'])
def settings(error=None):
    """Loads the settings page or saves settings.."""
    if request.method == 'POST':
        username = session['username']
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        try_result = auth.try_change_password(username, current_password, new_password, confirm_password)
        if try_result is not None:
            return render_template('settings.j2', error_message=try_result, show_menu=True, show_refresh=False)    
        return redirect(url_for('home'))
    else:
        return render_template('settings.j2', error_message=error, show_menu=True, show_refresh=False)

@app.route('/mobile_config', methods=['GET', 'POST'])
def mobile_config(error=None):
    phones = prefs.get_phones()
    if request.method == 'POST':
        content = request.get_json(silent=True)
        phone = content.get('phone')
        remove = content.get('remove')
        if remove:
            phones.remove(phone)
        elif phone not in phones:
            phones.append(phone)
        prefs.set_phones(phones)
    response = {'status': 'success', 'phones': phones}
    return jsonify(**response)

@app.route('/logout')
def logout():
    """Nullifies the session."""
    session.pop('username', None)
    return redirect(url_for('home'))

@app.after_request
def disable_caching(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = 0
    return response

if __name__ == '__main__':
    scheduling.init_scheduler()
    auth.init_auth()
    init_visibility()
    app.secret_key = 'a3ddad8e-2288-414e-9d7d-c5dd9018fef0'
    app.run(debug=True, host='0.0.0.0', port=80, use_reloader=False)
    