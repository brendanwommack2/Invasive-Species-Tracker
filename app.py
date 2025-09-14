from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_PATH = "sightings.db"

def get_sightings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT species, lat, lon, notes FROM sightings ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    # Convert to list of dicts for Leaflet
    return [
        {"species": r[0], "lat": r[1], "lon": r[2], "notes": r[3]}
        for r in rows
    ]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        species = request.form.get('species')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        notes = request.form.get('notes')

        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return "Invalid latitude or longitude.", 400

        # Save to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO sightings (species, lat, lon, notes) VALUES (?, ?, ?, ?)",
            (species, lat, lon, notes)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('index.html', sightings=get_sightings())

if __name__ == '__main__':
    app.run(debug=True)
