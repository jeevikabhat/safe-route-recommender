from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to SQLite
def get_db_connection():
    conn = sqlite3.connect('safe_routes.db')
    conn.row_factory = sqlite3.Row
    return conn

# GET routes with safety score
@app.route('/routes', methods=['GET'])
def get_routes():
    start = request.args.get('start')
    end = request.args.get('end')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        r.id,
        r.route_name,
        IFNULL(AVG(lighting_score * 0.4 + crowd_score * 0.4 - incident_flag * 2), 3) AS safety_score
    FROM Routes r
    LEFT JOIN SafetyReports s ON r.id = s.id
    WHERE r.start_loc = ? AND r.end_loc = ?
    GROUP BY r.id;
    """

    cursor.execute(query, (start, end))
    rows = cursor.fetchall()

    conn.close()

    result = [dict(row) for row in rows]

    return jsonify(result)


# POST safety report
@app.route('/report', methods=['POST'])
def add_report():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO SafetyReports (id, lighting_score, crowd_score, incident_flag)
    VALUES (?, ?, ?, ?)
    """

    cursor.execute(query, (
        data['id'],
        data['lighting_score'],
        data['crowd_score'],
        data['incident_flag']
    ))

    conn.commit()
    conn.close()

    return {"message": "Report added successfully"}


if __name__ == '__main__':
    app.run(debug=True)