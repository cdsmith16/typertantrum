import os
import base64
import json
import requests
import urllib
from flask import Flask, render_template, send_from_directory

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = False,
)

"""Code retrieved from Aashay sample.  Requests to & fro Clever API"""
CLEVER_APP_ID = 'df335c6ac80a8b80a343'
CLEVER_APP_SECRET = '0965310be8fccc31d511e9b781c153712d6acbb7'

REDIRECT_URI = 'https://typertantrum.herokuapp.com/clever_authorized'
CLEVER_OAUTH_URL = 'https://clever.com/oauth/tokens'
CLEVER_API_BASE = 'https://api.clever.com'

"""
# Our OAuth 2.0 redirect URI location corresponds to what we've set above as our REDIRECT_URI
# When this route is executed, we will retrieve the "code" parameter and exchange it for a Clever access token.
# After receiving the access token, we use it with api.clever.com/me to determine its owner,
# save our session state, and redirect our user to our application.
@route('/oauth')
def oauth():
    code = request.query.code

    payload = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }

    headers = {
    	'Authorization': 'Basic {base64string}'.format(base64string =
            base64.b64encode(CLIENT_APP_ID + ':' + CLIENT_APP_SECRET)),
        'Content-Type': 'application/json',
    }

    # Don't forget to handle 4xx and 5xx errors!
    response = requests.post(CLEVER_OAUTH_URL, data=json.dumps(payload), headers=headers).json()
    token = response['access_token']

    bearer_headers = {
        'Authorization': 'Bearer {token}'.format(token=token)
    }

    # Don't forget to handle 4xx and 5xx errors!
    result = requests.get(CLEVER_API_BASE + '/me', headers=bearer_headers).json()
    data = result['data']
    print data

    next_url = request.args.get('next') or url_for('index')

    session['logged_in'] = True
    session['clever_token'] = token


    return redirect(next_url)


    # Only handle student logins for our app (other types include teachers and districts)
    if data['type'] != 'student':
        return template ("You must be a student to log in to this app but you are a {{type}}.", type=data['type'])
    else:
        if 'name' in data: #SIS scope
            nameObject = data['name']            
        else:
            
            #For student scopes, we'll have to take an extra step to get name data.
            studentId = data['id']
            student = requests.get(CLEVER_API_BASE + '/v1.1/students/{studentId}'.format(studentId=studentId), 
                headers=bearer_headers).json()
            
            nameObject = student['data']['name']
        
        session = request.environ.get('beaker.session')
        session['nameObject'] = nameObject

        redirect('/app')
"""

@app.route("/oauth")
#@oauth.authorize_handler
def oauth(resp):
    print resp
    code = request.query.code
    scope = request.query.scope

    #Verify 'state' Nonce value matches; just 'foo' for demo
    state = request.query.state
    if(not state == 'foo'):
        print 'Aborting; request from unidentified sender'
        return

    payload = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }

    headers = {
        'Authorization': 'Basic {base64string}'.format(base64string =
            base64.b64encode(CLIENT_APP_ID + ':' + CLIENT_APP_SECRET)),
        'Content-Type': 'application/json',
    }

    response = requests.post(CLEVER_OAUTH_URL, data=json.dumps(payload), headers=headers).json()
    token = response['access_token']

    bearer_headers = {
        'Authorization': 'Bearer {token}'.format(token=token)
    }

    # Don't forget to handle 4xx and 5xx errors!
    result = requests.get(CLEVER_API_BASE + '/me', headers=bearer_headers).json()
    data = result['data']
    print data

    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'token' not in resp:
        return redirect(next_url)

    session['logged_in'] = True
    session['clever_token'] = (resp['access_token'], '')


    return redirect(next_url)


"""Samples from Flask setup guide"""
# controllers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

""" Other error handlers """
@app.errorhandler(401)
def page_not_found(e):
    return render_template('404.html'), 401

@app.errorhandler(403)
def page_not_found(e):
    return render_template('404.html'), 403

@app.errorhandler(500)
def page_not_found(e):
    return render_template('404.html'), 500

@app.route("/")
def index():
    print 'is this printing shit working?'
    return render_template('index.html')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('clever_token', None)

@app.route("/clever_login")
def clever_login():
    auth_payload = {
        'response_type': 'code',
        'client_id': CLEVER_APP_ID,
        'redirect_uri': REDIRECT_URI
    }
    #make request to clever with above params, in case one button login not plausible
    #pass bearer token and response to /oauth
    """return clever.authorize(callback=url_for('oauth',
        next=request.args.get('next'), _external=True))"""
    return True

@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)