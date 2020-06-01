from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
import json
import os.path
from werkzeug.utils import secure_filename

app = Flask(__name__) # current module
app.secret_key = 's0m3__rand06_k3y'

@app.route('/')
def home():
    return render_template('home.html', codes=session.keys()) # looks in templates

@app.route('/your-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':
        urls = {}

        if os.path.exists('urls.json'):
            with open('urls.json') as url_file:
                urls = json.load(url_file)

        if request.form['code'] in urls.keys():
            flash('That short name has already been taken. Please select another name.')
            return redirect(url_for('home'))

        if 'url' in request.form.keys():
            urls[request.form['code']] = {'url': request.form['url']}
        else:
            # save user file and append shortcut to json
            f = request.files['file']
            full_name = request.form['code'] + secure_filename(f.filename)
            f.save(os.path.join(os.getcwd(), 'static/user_files/', full_name))
            urls[request.form['code']] = {'file': full_name}

        with open('urls.json', 'w') as url_file:
            json.dump(urls, url_file)
            session[request.form['code']] = True # save into cookie. Could do timestamp value to make more meaningful than boolean

        return render_template('your_url.html', urlcode=request.form['code'])
    else:
        return redirect(url_for('home')) #url for home function

# put anything after / into a variable called code
@app.route('/<string:code>')
def redirect_to_url(code):
    """
    Redirect to url or serve user file depending on what the code was created as
    """
    if os.path.exists('urls.json'):
        with open('urls.json') as urls_file:
            urls = json.load(urls_file)
            if code in urls.keys():
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    return redirect(url_for('static', filename='user_files/' + urls[code]['file']))
    return abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/api')
def session_api():
    return jsonify(list(session.keys()))
