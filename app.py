from dotmap import DotMap
from flask import Flask, request, make_response, redirect, session, render_template, abort, jsonify, url_for

app = Flask(__name__)

# Generate a secret key (via LastPass or something similar).
app.secret_key = '@7*popsc9xKCUdiZDC5ue46q'

app.config.update(
    SESSION_COOKIE_SECURE=True
)

@app.before_request
def pre_req_require_login():
    if not request.endpoint:
        abort(404)

    # TODO: Check API routes for auth somehow.
    if request.endpoint.startswith('api'):
        return

    # Anonymous users can hit these route handlers.
    anon_route_handlers = [
        'web_get_login'
      , 'web_post_login'
      , 'web_get_register'
      , 'web_post_register'
    ]

    # If hitting a session-requiring endpoint and there isn't a session.
    if request.endpoint not in anon_route_handlers and 'id' not in session:
        print('endpoint: ', request.endpoint)
        print('session: ', session)
        return redirect(url_for('web_get_login'))

@app.route('/logout')
def web_get_logout():
    del session['id']
    return redirect('/')

@app.route('/')
def index():
    return 'ok'

@app.route('/login', methods=['GET'])
def web_get_login():
    # User is already logged-in, don't let them create another session.
    if 'id' in session:
        return redirect('/')

    return render_template('login.html')

@app.route('/login', methods=['POST'])
def web_post_login():
    # User is already logged-in, don't let them create another session.
    if 'id' in session:
        return redirect('/')

    form = DotMap(request.form)

    if not form.email or not form.password:
        resp = "The following fields must be provided: "
        missing_fields = []

        if not form.email:
            missing_fields.append("email")

        if not form.password:
            missing_fields.append("password")

        resp += ', '.join(missing_fields)
        return resp, 400

    if form.email == 'test@example.com' and form.password == 'abc123':
        session['id'] = 'uxyZ81'
        return "You're logged in!"

    return 'invalid credentials', 400

@app.route('/api/login', methods=['POST'])
def api_post_login():
    json = request.get_json()
    if not json:
        return jsonify({
            'ok': False
          , 'err': "message"
          , 'message': "POSTed data must be JSON"
        }), 404

    json = DotMap(json)

    if not json.email or not json.password:
        resp = DotMap({
            'ok': False
          , 'err': 'fields'
          , 'fields': []
        })

        if not json.email:
            resp.fields.append({
                'name': 'email'
              , 'message': 'must be provided'
            })

        if not json.password:
            resp.fields.append({
                'name': 'password'
              , 'message': 'must be provided'
            })

        return jsonify(resp), 400

    if json.email == 'test@example.com' and json.password == 'abc123':
        # TODO: Generate tokens.
        return jsonify({
            'ok': True
          , 'access_token': 'TODO'
          , 'refresh_token': 'TODO'
        })

    return jsonify({
        'ok': False
      , 'err': "message"
      , 'message': "Account does not exist or credentials were invalid"
    }), 400