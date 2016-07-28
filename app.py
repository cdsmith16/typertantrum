import os
import base64
import json
import requests
import urllib2
from flask import Flask, render_template, send_from_directory, request, url_for, session, redirect

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = False,
)
app.secret_key = 'd\xbfrFfl\xf0\x93\x82+'

CLEVER_APP_ID = 'df335c6ac80a8b80a343'
CLEVER_APP_SECRET = '0965310be8fccc31d511e9b781c153712d6acbb7'
    
#for convenience, keeping necessary constants here
REDIRECT_URI = 'https://typertantrum.herokuapp.com/oauth'
CLEVER_OAUTH_URL = 'https://clever.com/oauth/tokens'
CLEVER_API_BASE = 'https://api.clever.com'


@app.route("/oauth", methods=['GET'])
#@oauth.authorize_handler
def oauth():
    code = request.args.get('code')
    scope = request.args.get('scope')

    """ Getting the same code back twice indicates a server error or someone trying to force their way in
    with a code they retrieved.  TyperTantrum opts to forbid these users.
    #Verify 'code' isn't a repeat; existence placeholder for now
    if(not code):
        print 'Code is a repeat'
        return render_template(403.html)"""

    """ This block verifies "state" but this parameter is not passed back by the developer auth portal.
    #Verify 'state' Nonce value matches; just 'foo' for demo
    state = request.args.get('state')
    if(not state == 'foo'):
        print 'Aborting; request from unidentified sender/no state passed back'
        return render_template(401.html)"""

    #If the application scope does not include read-student access, deem the user unauthorized.
    if('read:student' not in scope and 'read:sis' not in scope):
        print 'Not authorized to read student info'
        return render_template('401.html')

    payload = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }

    base64string = base64.encodestring('%s:%s' % (CLEVER_APP_ID, CLEVER_APP_SECRET)).replace('\n', '')
    
    headers = {
        'Authorization': ('Basic %s' % (base64string)),
        'Content-Type': 'application/json',
    }

    response = requests.post(CLEVER_OAUTH_URL, data=json.dumps(payload), headers=headers).json()
    #print response
    
    next_url = url_for('index')
    if (not response) or ('access_token' not in response):
        return redirect(next_url)
    token = response['access_token']

    bearer_headers = {
        'Authorization': ('Bearer %s' % (token))
    }

    # Don't forget to handle 4xx and 5xx errors!
    result = requests.get(CLEVER_API_BASE + '/me', headers=bearer_headers).json()

    """The result for the /me api contains information resembling the following:
    {  
    "links":[  
        {  
            "uri":"/me",
            "rel":"self"
        },
        {  
            "uri":"/v1.1/students/56e8c7375a748be67800dd3e",
            "rel":"canonical"
        },
        {  
            "uri":"/v1.1/districts/56e8c2fe5ea018010000018c",
            "rel":"district"
        }
    ],
    "data":{  
        "id":"56e8c7375a748be67800dd3e",
        "district":"56e8c2fe5ea018010000018c",
        "type":"student"
    },
    "type":"student"
    }
    This information will be utilized to flesh out the behavior of your application."""
    
    print result

    session['logged_in'] = True
    session['clever_token'] = token
    
    #for live applications, you may want different experiences for different types e.g. non-students
    session['type'] = result['type']

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
    return render_template('401.html'), 401

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.route("/")
def index():
    return render_template('index.html')

#remember to get rid of old student info is the session ends or a someone logs out
def pop_login_session():
    #print session['logged_in']
    session.pop('logged_in', None)
    session.pop('type', None)
    session.pop('clever_token', None)
    session.pop('id', None)
    session.pop('district', None)

@app.route("/logout")
def logout():
    #print 'you logged out!'
    pop_login_session()
    return redirect(url_for('index'))

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)