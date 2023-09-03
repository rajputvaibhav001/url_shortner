from flask import Flask, render_template, request, redirect, flash
import sqlite3
import random
import string
from secrets import SECRET_KEY






app = Flask(__name__)
app.secret_key = SECRET_KEY


# Function to generate a random short URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))
    return short_url

# Initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY, original_url TEXT, short_url TEXT)')
    conn.commit()
    conn.close()

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        if not original_url.startswith(('http://', 'https://')):
            flash('Invalid URL. Make sure it starts with http:// or https://', 'error')
        else:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT short_url FROM urls WHERE original_url = ?', (original_url,))
            result = cursor.fetchone()
            if result:
                short_url = result[0]
            else:
                short_url = generate_short_url()
                cursor.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
                conn.commit()
            conn.close()
            return render_template('index.html', short_url=short_url)

    return render_template('index.html')

# Redirect route for short URLs
@app.route('/<short_url>')
def redirect_to_original(short_url):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
    result = cursor.fetchone()
    conn.close()
    if result:
        original_url = result[0]
        return redirect(original_url)
    else:
        flash('URL not found', 'error')
        return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
