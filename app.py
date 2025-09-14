from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "sightings.db"

def get_species_list():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT common_name FROM invasive_plants ORDER BY common_name ASC")
    species = [row[0] for row in c.fetchall()]
    conn.close()
    return species

@app.route('/species')
def species():
    # Returns JSON of all species
    return jsonify(get_species_list())

def get_sightings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT species, lat, lon, notes FROM sightings ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return [
        {"species": r[0], "lat": r[1], "lon": r[2], "notes": r[3]}
        for r in rows
    ]

@app.route('/', methods=['GET', 'POST'])
def home():
    # Get allowed species from your invasive_plants table
    def get_species_list():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT common_name FROM invasive_plants ORDER BY common_name ASC")
        species_list = [row[0] for row in c.fetchall()]
        conn.close()
        return species_list

    allowed_species = get_species_list()

    if request.method == 'POST':
        species = request.form.get('species', '').strip()
        lat = request.form.get('lat', '').strip()
        lon = request.form.get('lon', '').strip()
        notes = request.form.get('notes', '').strip()

        # Required fields
        if not species or not lat or not lon:
            return "Species, latitude, and longitude are required.", 400

        # Species validation
        if species not in allowed_species:
            return "Invalid species selected. Please choose from the provided list.", 400

        # Convert lat/lon and validate ranges
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return "Latitude and longitude must be numbers.", 400

        if not (-90 <= lat <= 90):
            return "Latitude must be between -90 and 90.", 400
        if not (-180 <= lon <= 180):
            return "Longitude must be between -180 and 180.", 400

        # Limit notes length
        if len(notes) > 500:
            return "Notes must be under 500 characters.", 400

        # Insert into database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO sightings (species, lat, lon, notes) VALUES (?, ?, ?, ?)",
            (species, lat, lon, notes)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('index.html', sightings=get_sightings(), allowed_species=allowed_species)


# Only allow this route in development
@app.route('/clear', methods=['POST'])
def clear_sightings():
    if not app.debug:
        abort(403)  # Forbidden in production

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM sightings")
    conn.commit()
    conn.close()

    return "All sightings cleared.", 200

if __name__ == '__main__':
    app.run(debug=True)
