from flask import Flask, request, redirect, g, render_template_string
import sqlite3
import string
import random

app = Flask(__name__)
DATABASE = 'url_shortener.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>URL Shortener</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f4f4f9;
                }
                .container {
                    text-align: center;
                    background: #fff;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    border-radius: 10px;
                }
                h1 {
                    color: #333;
                }
                form {
                    margin-top: 20px;
                }
                input[type="text"] {
                    padding: 10px;
                    width: 80%;
                    max-width: 400px;
                    margin-bottom: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                button {
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: #fff;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #0056b3;
                }
                .result {
                    margin-top: 20px;
                }
                .result a {
                    color: #007bff;
                    text-decoration: none;
                }
                .result a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>URL Shortener</h1>
                <form action="/shorten" method="post">
                    <input type="text" id="long_url" name="long_url" placeholder="Enter the long URL" required>
                    <button type="submit">Shorten</button>
                </form>
                {% if short_url %}
                    <div class="result">
                        <h2>Shortened URL:</h2>
                        <p><a href="{{ short_url }}" target="_blank">{{ short_url }}</a></p>
                    </div>
                {% endif %}
            </div>
        </body>
        </html>
    ''', short_url=None)

@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form['long_url']
    short_code = generate_short_code()
    db = get_db()
    db.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, short_code))
    db.commit()
    short_url = f"http://localhost:5000/{short_code}"
    return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>URL Shortener</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f4f4f9;
                }
                .container {
                    text-align: center;
                    background: #fff;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    border-radius: 10px;
                }
                h1 {
                    color: #333;
                }
                form {
                    margin-top: 20px;
                }
                input[type="text"] {
                    padding: 10px;
                    width: 80%;
                    max-width: 400px;
                    margin-bottom: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                button {
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: #fff;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #0056b3;
                }
                .result {
                    margin-top: 20px;
                }
                .result a {
                    color: #007bff;
                    text-decoration: none;
                }
                .result a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>URL Shortener</h1>
                <form action="/shorten" method="post">
                    <input type="text" id="long_url" name="long_url" placeholder="Enter the long URL" required>
                    <button type="submit">Shorten</button>
                </form>
                {% if short_url %}
                    <div class="result">
                        <h2>Shortened URL:</h2>
                        <p><a href="{{ short_url }}" target="_blank">{{ short_url }}</a></p>
                    </div>
                {% endif %}
            </div>
        </body>
        </html>
    ''', short_url=short_url)

@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    db = get_db()
    cur = db.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
    result = cur.fetchone()
    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404

if __name__ == '__main__':
    with app.app_context():
        db = get_db()
        db.execute("CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY, long_url TEXT, short_code TEXT)")
        db.commit()
    app.run(debug=True)
