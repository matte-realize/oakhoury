import os
import psycopg2
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Helper funcion to close connections
def close_resources(conn, cur):
    if cur:
        cur.close()
    if conn:
        conn.close()

def get_db_connection():
    """Connects to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USERNAME"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")

@app.route('/api/test')
def test_connection():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT version();')
            db_version = cur.fetchone()
            close_resources(conn, cur)
            return jsonify({"message": "Database connection successful!", "version": db_version})
        except Exception as e:
             if conn: conn.close()
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

## ---TASKS.SQL---
# Get all tree requests for a specific resident_id
@app.route('/api/tree-requests')
def get_tree_requests():
    resident_id = request.args.get('resident_id')
    if not resident_id:
        return jsonify({"error": "Missing resident_id parameter"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT id, submission_timestamp, approved FROM tree_requests tr WHERE tr.resident_id = %s ORDER BY tr.submission_timestamp DESC;', (resident_id,))
            rows = cur.fetchall()
            close_resources(conn, cur)

            tree_requests = []
            for row in rows:
                tree_requests.append({
                    'id': row[0],
                    'submission_timestamp': row[1],
                    'approved': row[2]
                })

            return jsonify(tree_requests)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Get information on a speficic tree request
@app.route('/api/details')
def get_tree_request_details():
    resident_id = request.args.get('resident_id')
    tree_request_id = request.args.get('tree_request_id')
    if not tree_request_id:
        return jsonify({"error": "Missing tree_request_id parameter"}), 500
    if not resident_id:
        return jsonify({"error": "Missing resident_id parameter"}), 500


    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
	SELECT 
			t.common_name,
			t.scientific_name,
        	get_tree_request_status(tr.id)               AS status,
        	CURRENT_DATE - submission_timestamp::DATE AS days_since_planting,
            p.status AS permit_status
		FROM tree_requests tr
		INNER JOIN trees t ON tr.tree_id = t.id
        INNER JOIN permits p ON tr.id = p.tree_request_id
		WHERE tr.id = %s AND tr.resident_id = %s;
''', (tree_request_id, resident_id,))
            row = cur.fetchone()
            close_resources(conn, cur)

            if not row:
                return jsonify({"error": "Tree request not found"}), 404
            tree_request = {
                'common_name': row[0],
                'scientific_name': row[1],
                'status': row[2],
                'days_since_planting': row[3],
                'permit_status': row[4]
            }
            return jsonify(tree_request)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Logs in a resident
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    email = data.get('email')

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT id, password, first_name, last_name, is_volunteer, street, zip_code, neighborhood FROM residents WHERE email = %s', (email,))
            row = cur.fetchone()
            close_resources(conn, cur)
            if not row:
                return jsonify({"error": "Invalid credentials"}), 404
            resident = {
                'id': row[0],
                'password': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'is_volunteer': row[4],
                'street': row[5],
                'zip_code': row[6],
                'neighborhood': row[7]
            }
            return jsonify(resident)
        except Exception as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Registers a resident
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    email = data.get('email')
    password = data.get('password') # Hashed
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    street = data.get('street')
    zip_code = data.get('zip_code')
    neighborhood = data.get('neighborhood')
    if not (email and first_name and last_name and password and street and zip_code and neighborhood):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO residents (email, password, first_name, last_name, street, zip_code, is_volunteer, neighborhood)
                VALUES (%s, %s, %s, %s, %s, %s, false, %s)
                RETURNING id
                         ''', (email, password, first_name, last_name, street, zip_code, neighborhood,))
            row = cur.fetchone()
            resident_id = row[0]
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"id": resident_id})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e.pgcode}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500
  
# Check if a user is an organization member
@app.route('/api/is_organization_member', methods=['GET'])
def is_organization_member():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT resident_id FROM organization_members WHERE resident_id = %s', (user_id,))
            row = cur.fetchone()
            close_resources(conn, cur)

            if row:
                return jsonify({"is_organization_member": True})
            else:
                return jsonify({"is_organization_member": False})
        except Exception as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Get all tree requests (admin only).
@app.route('/api/all-tree-requests')
def get_all_tree_requests():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                SELECT tr.id,
                       tr.submission_timestamp,
                       tr.approved,
                       get_tree_request_status(tr.id) AS status,
                       t.common_name,
                       t.scientific_name
                FROM tree_requests tr
                         INNER JOIN trees t ON tr.tree_id = t.id
                ORDER BY tr.submission_timestamp DESC;
            ''')
            rows = cur.fetchall()
            close_resources(conn, cur)
            tree_requests = []
            for row in rows:
                tree_requests.append({
                    'id': row[0],
                    'submission_timestamp': row[1],
                    'approved': row[2],
                    'status': row[3],
                    'common_name': row[4],
                    'scientific_name': row[5]
                })
            return jsonify(tree_requests)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500
  
# Get in-depth details for tree request (admin only)
@app.route('/api/tree-request-details-admin')
def get_tree_request_details_admin():
    tree_request_id = request.args.get('tree_request_id')
    if not tree_request_id:
        return jsonify({"error": "Missing tree_request_id parameter"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Get tree request details
            cur.execute('''
                SELECT t.common_name,
                       t.scientific_name,
                       t.inventory,
                       tr.site_description,
                       r.street,
                       r.zip_code,
                       r.neighborhood,
                       get_tree_request_status(tr.id) AS status
                FROM tree_requests tr
                         INNER JOIN trees t ON tr.tree_id = t.id
                         INNER JOIN residents r ON tr.resident_id = r.id
                WHERE tr.id = %s;
            ''', (tree_request_id,))
            row = cur.fetchone()
            if not row:
                close_resources(conn, cur)
                return jsonify({"error": "Tree request not found"}), 404
            tree_request_details = {
                'tree_common_name': row[0],
                'tree_scientific_name': row[1],
                'tree_inventory': row[2],
                'site_description': row[3],
                'resident_street': row[4],
                'resident_zip_code': row[5],
                'resident_neighborhood': row[6],
                'status': row[7]
            }
            # Get scheduled visits, check if outcome has already been recorded
            cur.execute('''
              SELECT sv.event_id,
                       sv.event_timestamp,
                       sv.cancelled,
                       sv.notes,
                       sv.organization_member_id,
                       CASE WHEN ve.scheduled_visit_id IS NOT NULL THEN true ELSE false END AS outcome_recorded
                FROM scheduled_visits sv
                LEFT JOIN visit_events ve ON sv.event_id = ve.scheduled_visit_id
                WHERE sv.tree_request_id = %s
                ORDER BY sv.event_timestamp DESC
            ''', (tree_request_id,))
            rows = cur.fetchall()
            scheduled_visits = []
            for row in rows:
                 scheduled_visits.append({
                    'event_id': row[0],
                    'event_timestamp': row[1],
                    'cancelled': row[2],
                    'notes': row[3],
                    'organization_member_id': row[4],
                    'outcome_recorded': row[5]
                })
            tree_request_details['scheduled_visits'] = scheduled_visits
            # Get scheduled plantings, check if outcome has already been recorded
            cur.execute('''
                SELECT event_id,
                       event_timestamp,
                       cancelled,
                       notes,
                       CASE WHEN pe.scheduled_planting_id IS NOT NULL THEN true ELSE false END AS outcome_recorded
                FROM scheduled_plantings sp
                LEFT JOIN planting_events pe ON sp.event_id = pe.scheduled_planting_id
                WHERE tree_request_id = %s;
            ''', (tree_request_id,))
            rows = cur.fetchall()
            scheduled_plantings = []
            for row in rows:
                scheduled_plantings.append({
                    'event_id': row[0],
                    'event_timestamp': row[1],
                    'cancelled': row[2],
                    'notes': row[3],
                    'outcome_recorded': row[4]
                })
            tree_request_details['scheduled_plantings'] = scheduled_plantings
            close_resources(conn, cur)
            return jsonify(tree_request_details)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500     

# Get all trees
@app.route('/api/trees')
def get_trees():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT id, common_name, scientific_name, inventory FROM trees ORDER BY common_name;')
            rows = cur.fetchall()
            close_resources(conn, cur)

            trees = []
            for row in rows:
                trees.append({
                    'id': row[0],
                    'common_name': row[1],
                    'scientific_name': row[2],
                    'inventory': row[3]
                })

            return jsonify(trees)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Get all tree requests for a specific resident_id
@app.route('/api/tree-request', methods=['POST'])
def create_tree_request():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    resident_id = data.get('resident_id')
    tree_id = data.get('tree_id')
    site_description = data.get('site_description')
    if not (resident_id and tree_id and site_description):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO tree_requests (resident_id, tree_id, site_description, submission_timestamp, approved)
                VALUES (%s, %s, %s, NOW(), NULL)
                RETURNING id
                         ''', (resident_id, tree_id, site_description,))
            tree_request = cur.fetchone()
            new_tree_request_id = tree_request[0]
            print(f"New tree request ID: {new_tree_request_id}")
            cur.execute('''
                INSERT INTO permits (resident_id, tree_request_id, status, decision_date)
                VALUES (%s, %s, 'pending', NULL)
                         ''', (resident_id, new_tree_request_id,))
            # row = cur.fetchone()
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"id": new_tree_request_id})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Get all neighborhoods
@app.route('/api/neighborhoods')
def get_neighborhoods():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT name FROM neighborhoods ORDER BY name;')
            rows = cur.fetchall()
            close_resources(conn, cur)

            neighborhoods = []
            for row in rows:
                neighborhoods.append(row[0])

            return jsonify(neighborhoods)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Update permit status
@app.route('/api/update-permit-status', methods=['PATCH'])
def update_permit_status():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    tree_request_id = data.get('tree_request_id')
    status = data.get('status')
    if not (tree_request_id and status):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                UPDATE permits
                SET status = %s, decision_date = NOW()
                WHERE tree_request_id = %s
                         ''', (status, tree_request_id,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Permit status updated successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Submit a volunteer request. body is {user_id, notes}
@app.route('/api/volunteer-requests', methods=['POST'])
def create_volunteer_request():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    user_id = data.get('user_id')
    notes = data.get('notes')
    if not (user_id):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO volunteer_applications (resident_id, created, approved, notes)
                VALUES (%s, NOW(), NULL, %s)
                         ''', (user_id, notes,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Volunteer request submitted successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Schedule a visit
@app.route('/api/schedule-visit', methods=['POST'])
def schedule_visit():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    tree_request_id = data.get('tree_request_id')
    timestamp = data.get('timestamp')
    notes = data.get('notes')
    organization_member_id = data.get('organization_member_id')
    if not (tree_request_id and timestamp and organization_member_id):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO scheduled_visits (tree_request_id, event_timestamp, cancelled, notes, organization_member_id)
                VALUES (%s, %s, false, %s, %s)
                         ''', (tree_request_id, timestamp, notes, organization_member_id,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Visit scheduled successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Approve a request for a tree
@app.route('/api/accept-tree-request', methods=['PATCH'])
def accept_tree_request():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    tree_request_id = data.get('tree_request_id')
    if not tree_request_id:
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                UPDATE tree_requests
                SET approved = true
                WHERE id = %s
                         ''', (tree_request_id,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Tree request accepted successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Deny a request for a tree
@app.route('/api/deny-tree-request', methods=['PATCH'])
def deny_tree_request():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    tree_request_id = data.get('tree_request_id')
    if not tree_request_id:
        return jsonify({"error": "Missing tree_request_id parameter"}), 400 # Changed status code to 400

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                UPDATE tree_requests
                SET approved = false
                WHERE id = %s
                         ''', (tree_request_id,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Tree request denied successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             # Use e.pgcode for specific DB errors if needed, otherwise a generic 500
             return jsonify({"error": "Database error occurred"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

@app.route('/api/cancel-visit', methods=['PATCH'])
def cancel_visit():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    event_id = data.get('event_id')
    if not event_id:
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                UPDATE scheduled_visits
                SET cancelled = true
                WHERE id = %s
                         ''', (event_id,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Visit cancelled successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Record info gathered from a visit
@app.route('/api/visit-events', methods=['POST'])
def create_visit_event():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    scheduled_visit_id = data.get('scheduled_visit_id')
    observations = data.get('observations')
    photo_library_link = data.get('photo_library_link')
    additional_visit_required = data.get('additional_visit_required', False)

    if not scheduled_visit_id:
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO visit_events (scheduled_visit_id, observations, photo_library_link, additional_visit_required)
                VALUES (%s, %s, %s, %s)
                         ''', (scheduled_visit_id, observations, photo_library_link, additional_visit_required,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Visit event created successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Schedule a planting (without any org members or volunteers yet)
@app.route('/api/schedule-planting', methods=['POST'])
def schedule_planting():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    tree_request_id = data.get('tree_request_id')
    timestamp = data.get('timestamp')
    notes = data.get('notes')
    if not (tree_request_id and timestamp):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO scheduled_plantings (tree_request_id, event_timestamp, cancelled, notes)
                VALUES (%s, %s, false, %s)
                         ''', (tree_request_id, timestamp, notes,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Planting scheduled successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Add an org member to a scheduled planting
@app.route('/api/add-org-member-to-planting', methods=['POST'])
def add_org_member_to_planting():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    organization_member_id = data.get('organization_member_id')
    scheduled_planting_id = data.get('scheduled_planting_id')
    if not (organization_member_id and scheduled_planting_id):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO organization_members_lead_scheduled_plantings (organization_member_id, scheduled_planting_id)
                VALUES (%s, %s)
                         ''', (organization_member_id, scheduled_planting_id,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Organization member added to planting successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Add a volunteer to a scheduled planting
@app.route('/api/add-volunteer-to-planting', methods=['POST'])
def add_volunteer_to_planting():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    volunteer_id = data.get('volunteer_id')
    planting_event_id = data.get('planting_event_id')
    if not (volunteer_id and planting_event_id):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO scheduled_plantings_have_volunteers (volunteer_id, planting_event_id)
                VALUES (%s, %s)
                         ''', (volunteer_id, planting_event_id,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Volunteer added to planting successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Record info after a scheduled planting
@app.route('/api/new-planting-event', methods=['POST'])
def create_planting_event():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    scheduled_planting_id = data.get('scheduled_planting_id')
    observations = data.get('observations')
    before_photos_library_link = data.get('before_photos_library_link')
    after_photos_library_link = data.get('after_photos_library_link')
    successful = data.get('successful', False)
    if not (scheduled_planting_id):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
             # Insert into planting_events
            cur.execute('''
                INSERT INTO planting_events (scheduled_planting_id, observations, successful, before_photos_library_link, after_photos_library_link)
                VALUES (%s, %s, %s, %s, %s)
                         ''', (scheduled_planting_id, observations, successful, before_photos_library_link, after_photos_library_link,))

            # If successful, decrement inventory
            if successful:
                # Find the tree_id associated with this scheduled planting
                cur.execute('''
                    SELECT tr.tree_id
                    FROM scheduled_plantings sp
                    JOIN tree_requests tr ON sp.tree_request_id = tr.id
                    WHERE sp.event_id = %s;
                ''', (scheduled_planting_id,))
                tree_id_row = cur.fetchone()
                tree_id = tree_id_row[0]
                # Decrement inventory for that tree_id
                cur.execute('''
                    UPDATE trees
                    SET inventory = inventory - 1
                    WHERE id = %s AND inventory > 0;
                ''', (tree_id,))

            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Planting event created successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Add a volunteer that actually participated
@app.route('/api/add-volunteer-to-planting-event', methods=['POST'])
def add_volunteer_to_planting_event():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    volunteer_id = data.get('volunteer_id')
    planting_event_id = data.get('planting_event_id')
    if not (volunteer_id and planting_event_id):
        return jsonify({"error": "Missing some parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO planting_events_have_volunteers (planting_event_id, volunteer_id)
                VALUES (%s, %s)
                         ''', (planting_event_id, volunteer_id,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Volunteer added to planting event successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Update the inventory for a tree
@app.route('/api/update-tree-inventory', methods=['PATCH'])
def update_tree_inventory():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    tree_id = data.get('tree_id')
    inventory = data.get('inventory')
    if tree_id is None or inventory is None:
        return jsonify({"error": "Missing 'tree_id' or 'inventory' parameter"}), 400

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                UPDATE trees
                SET inventory = %s
                WHERE id = %s
                         ''', (inventory, tree_id,))
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Tree inventory updated successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error: {e}")
             return jsonify({"error": e.pgcode}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# --- QUERY REPORTS ---
# Task 1
# For all requests to plant a tree that have not yet completed, show its status, and the number of
# days that has transpired since it was first submitted.
@app.route('/api/tree-requests-status')
def get_tree_requests_status():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                SELECT id,
                       get_tree_request_status(id)               AS status,
                       CURRENT_DATE - submission_timestamp::DATE AS days_since_submission
                FROM tree_requests tr
                WHERE get_tree_request_status(id) <> 'completed';
            ''')
            rows = cur.fetchall()
            close_resources(conn, cur)

            tree_requests = []
            for row in rows:
                tree_requests.append({
                    'id': row[0],
                    'status': row[1],
                    'days_since_submission': row[2]
                })

            return jsonify(tree_requests)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Task 2
# Find all trees planted within a selection of Oakland neighborhoods specified by a
# user in the app. Parameterized neighbor value to allow for user input.
@app.route('/api/trees-planted')
def get_trees_planted():
    neighborhood = request.args.get('neighborhood')
    if not neighborhood:
        return jsonify({"error": "Missing neighborhood parameter"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                SELECT t.common_name,
                       COUNT(*) AS number_of_trees
                FROM neighborhoods n
                         INNER JOIN residents r
                                    ON n.name = r.neighborhood
                         INNER JOIN tree_requests tr
                                    ON r.id = tr.resident_id
                         INNER JOIN scheduled_plantings sp
                                    ON tr.id = sp.tree_request_id
                         INNER JOIN planting_events pe
                                    ON sp.event_id = pe.scheduled_planting_id
                                        AND pe.successful = TRUE
                         INNER JOIN trees t
                                    ON tr.tree_id = t.id
                WHERE n.name = %s
                GROUP BY t.common_name;
            ''', (neighborhood,))
            rows = cur.fetchall()
            close_resources(conn, cur)

            trees_planted = []
            for row in rows:
                trees_planted.append({
                    'common_name': row[0],
                    'number_of_trees': row[1]
                })

            return jsonify(trees_planted)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Task 3
# For every species of trees, find the number of trees planted and some basic statistics on when
# trees were planted: the number of years since the first tree of the species was planted, the
# number of years since the most recent tree of the species was planted. In addition, include the
# year that had the most trees of the species planted and the number of trees planted.
# https://www.scaler.com/topics/datediff-in-postgresql/
@app.route('/api/tree-species-statistics')
def get_tree_species_statistics():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                SELECT t.common_name,
                       COUNT(pe)                                                                       AS number_of_trees_planted,
                       MIN(EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM sp.event_timestamp::TIMESTAMP)) AS years_since_planting,
                       (SELECT
                            EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
                        FROM
                            trees AS t2
                                INNER JOIN tree_requests ON t2.id = tree_requests.tree_id
                                INNER JOIN scheduled_plantings sp2 ON tree_requests.id = sp2.tree_request_id
                                INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
                        WHERE
                              t2.id = t.id
                            AND pe2.successful = TRUE
                        GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
                        ORDER BY COUNT(*) DESC
                        LIMIT 1)                                                                          AS year_most_planted,
                       (SELECT
                            COUNT(*)
                        FROM
                            trees AS t2
                                INNER JOIN tree_requests ON t2.id = tree_requests.tree_id
                                INNER JOIN scheduled_plantings sp2 ON tree_requests.id = sp2.tree_request_id
                                INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
                        WHERE
                              t2.id = t.id
                            AND pe2.successful = TRUE
                        GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
                        ORDER BY COUNT(*) DESC
                        LIMIT 1)                                                                          AS num_planted_in_peak_year
                FROM trees t
                    INNER JOIN tree_requests tr ON t.id = tr.tree_id
                    INNER JOIN scheduled_plantings sp ON tr.id = sp.tree_request_id
                    INNER JOIN planting_events pe ON sp.event_id = pe.scheduled_planting_id
                WHERE pe.successful = TRUE
                GROUP BY t.common_name, t.id;
            ''')
            rows = cur.fetchall()
            close_resources(conn, cur)

            tree_species_statistics = []
            for row in rows:
                tree_species_statistics.append({
                    'common_name': row[0],
                    'number_of_trees_planted': row[1],
                    'years_since_planting': row[2],
                    'year_most_planted':
                        row[3],
                    'num_planted_in_peak_year': row[4]
                })
            return jsonify(tree_species_statistics)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Task 4
# For each Oakland neighborhood, create a report that summarizes the requests, their progress
# (pending, in-process, completed, ec), the trees planted, etc. This is an opportunity for your
# team to demonstrate your skills, so it's expected that you'll demonstrate sophisticated database
# querying skills
@app.route('/api/neighborhood-report')
def get_neighborhood_report():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
SELECT n.name AS neighborhood_name,
       COUNT (spe) AS num_of_planted_trees,
       COUNT(tr) AS num_of_requests,
       COUNT(ctr) AS num_of_completed_requests,
       COUNT(wfptr) AS num_of_requests_waiting_for_planting,
       COUNT(wfvtr) AS num_of_requests_waiting_for_visit,
       COUNT(nptr) AS num_of_requests_needs_permit,
       COUNT(dtr) AS num_of_denied_requests,
       COUNT(patr) AS num_of_requests_pending_approval
FROM neighborhoods n
    INNER JOIN residents r
               ON n.name = r.neighborhood
    INNER JOIN tree_requests tr
               ON r.id = tr.resident_id
    LEFT OUTER JOIN scheduled_plantings sp
                ON tr.id = sp.tree_request_id
    LEFT OUTER JOIN planting_events spe
                        ON sp.event_id = spe.scheduled_planting_id
                               AND spe.successful = TRUE
    INNER JOIN trees t
               ON tr.tree_id = t.id
    LEFT OUTER JOIN tree_requests ctr ON tr.id = ctr.id
        AND get_tree_request_status(ctr.id) = 'completed'
    LEFT OUTER JOIN tree_requests wfptr ON tr.id = wfptr.id
        AND get_tree_request_status(wfptr.id) = 'waiting for planting'
    LEFT OUTER JOIN tree_requests wfvtr ON tr.id = wfvtr.id
        AND get_tree_request_status(wfvtr.id) = 'waiting for visit'
    LEFT OUTER JOIN tree_requests nptr ON tr.id = nptr.id
        AND get_tree_request_status(nptr.id) = 'needs permit'
    LEFT OUTER JOIN tree_requests dtr ON tr.id = dtr.id
        AND get_tree_request_status(dtr.id) = 'denied'
    LEFT OUTER JOIN tree_requests patr ON tr.id = patr.id
        AND get_tree_request_status(patr.id) = 'pending approval'
GROUP BY neighborhood_name
ORDER BY neighborhood_name ASC;
            ''')
            rows = cur.fetchall()
            close_resources(conn, cur)

            neighborhood_report = []
            for row in rows:
                neighborhood_report.append({
                    'neighborhood_name': row[0],
                    'num_of_planted_trees': row[1],
                    'num_of_requests': row[2],
                    'num_of_completed_requests': row[3],
                    'num_of_requests_waiting_for_planting': row[4],
                    'num_of_requests_waiting_for_visit': row[5],
                    'num_of_requests_needs_permit': row[6],
                    'num_of_denied_requests': row[7],
                    'num_of_requests_pending_approval': row[8]
                })
            return jsonify(neighborhood_report)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Custom report 1
# -- The following link helped me figure out how to extract that year from a timestamp
# -- https://www.commandprompt.com/education/how-to-extract-year-from-date-in-postgresql/#:~:text=To%20extract%20a%20year%20from%20a%20date%2C%20the%20built%2Din,dateField'%20FROM%20TIMESTAMP%20%7C%20INTERVAL%20)%3B
# -- The following link taught me about the LIMIT keyword
# -- https://razorsql.com/articles/postgresql_select_top_syntax.html#:~:text=Postgres%20does%20have%20a%20way,limit%20keyword%20must%20be%20used.&text=PostgreSQL%20also%20gives%20the%20ability,limit%20N%20offset%20Y%20syntax.

# -- The following query gets us a report about the most active volunteers, this is important because it helps the organization
# -- keep track of the impact that each volunteer has helped cause. Year has been parameterized so that the user can query
# -- data for whichever year they desire, this parameterization allows for the organization to track the impact and activity
# -- of  of each volunteer more clearly.
@app.route('/api/custom-report-1')
def get_custom_report_1():
    year = request.args.get('year')
    if not year:
        return jsonify({"error": "Missing year parameter"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
SELECT
    r.first_name || ' ' || r.last_name AS volunteer_name,
    MIN(sp.event_timestamp)            AS first_planting,
    MAX(sp.event_timestamp)            AS most_recent_planting,
    COUNT(pev)                         AS trees_planted,
    (SELECT
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     FROM
         planting_events_have_volunteers AS pev2
             INNER JOIN planting_events AS p2 ON pev2.planting_event_id = p2.scheduled_planting_id
             INNER JOIN scheduled_plantings AS sp2 ON p2.scheduled_planting_id = sp2.event_id
     WHERE
         pev2.volunteer_id = r.id
     GROUP BY
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)                          AS peak_year,
    (SELECT
         COUNT(*)
     FROM
         planting_events_have_volunteers pev2
             INNER JOIN planting_events AS p2 ON pev2.planting_event_id = p2.scheduled_planting_id
             INNER JOIN scheduled_plantings AS sp2 ON p2.scheduled_planting_id = sp2.event_id
     WHERE
         pev2.volunteer_id = r.id
     GROUP BY
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)                          AS trees_planted_in_peak_year
FROM
    residents AS r
        INNER JOIN planting_events_have_volunteers AS pev ON r.id = pev.volunteer_id
        INNER JOIN planting_events AS pe ON pev.planting_event_id = pe.scheduled_planting_id
        INNER JOIN scheduled_plantings AS sp ON pe.scheduled_planting_id = sp.event_id
WHERE
      r.is_volunteer = TRUE
  AND pe.successful = TRUE
  AND EXTRACT(YEAR FROM sp.event_timestamp::TIMESTAMP) = %s
GROUP BY r.first_name, r.last_name, r.id
ORDER BY trees_planted DESC, trees_planted_in_peak_year DESC;

                                    ''', (year,))
            rows = cur
            rows = cur.fetchall()
            close_resources(conn, cur)
            custom_report_1 = []
            for row in rows:    
                custom_report_1.append({
                    'volunteer_name': row[0],
                    'first_planting': row[1],
                    'most_recent_planting': row[2],
                    'trees_planted': row[3],
                    'peak_year': row[4],
                    'trees_planted_in_peak_year': row[5]
                })
            return jsonify(custom_report_1)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500
# Custom report 2
# -- The following query gives us a report regarding the organization members that lead plantings and attend visits; it
# -- displays the amount of plantings they've led, visits they've attended, their peak years and activity for both plantings
# -- and visits. This information is important for the higher up organization members so that they can make any necessary
# -- changes to lower level organization members. Year has been parameterized so that the user can query data for whichever
# -- year they desire, this parameterization allows for the organization to track the activity and success of each organization
# -- member more clearly.
@app.route('/api/custom-report-2')
def get_custom_report_2():
    year = request.args.get('year')
    if not year:
        return jsonify({"error": "Missing year parameter"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
              SELECT
    r.first_name || ' ' || r.last_name AS org_member_name,
    COUNT(sp) AS plantings_led,
    COUNT(pe) AS successful_plantings_led,
    (SELECT
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     FROM
         organization_members_lead_scheduled_plantings AS ompe2
             INNER JOIN scheduled_plantings sp2 ON ompe2.scheduled_planting_id = sp2.event_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
             ompe2.organization_member_id = om.resident_id
         AND pe2.successful = TRUE
     GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)   AS plantings_led_peak_year,
    (SELECT
         COUNT(*)
     FROM
         organization_members_lead_scheduled_plantings AS ompe2
             INNER JOIN scheduled_plantings sp2 ON ompe2.scheduled_planting_id = sp2.event_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
             ompe2.organization_member_id = om.resident_id
         AND pe2.successful = TRUE
     GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)   AS plantings_led_in_peak_year,
    COUNT(sv)   AS visits_attended,
    (SELECT
         EXTRACT(YEAR FROM sv2.event_timestamp::TIMESTAMP)
     FROM
         scheduled_visits AS sv2
     WHERE
             sv2.organization_member_id = om.resident_id
         AND sv2.cancelled = FALSE
     GROUP BY EXTRACT(YEAR FROM sv2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)   AS visits_attended_peak_year,
    (SELECT
         COUNT(*)
     FROM
         scheduled_visits AS sv2
     WHERE
           sv2.organization_member_id = om.resident_id
       AND sv2.cancelled = FALSE
     GROUP BY EXTRACT(YEAR FROM sv2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)   AS visits_attended_in_peak_year
FROM
    organization_members AS om
        INNER JOIN residents AS r ON om.resident_id = r.id
        LEFT OUTER JOIN organization_members_lead_scheduled_plantings AS ompe ON om.resident_id = ompe.organization_member_id
        LEFT OUTER JOIN scheduled_visits AS sv ON om.resident_id = sv.organization_member_id
                                                      AND sv.cancelled = FALSE
                                                      AND EXTRACT(YEAR FROM sv.event_timestamp::TIMESTAMP) = %s
        INNER JOIN scheduled_plantings AS sp ON ompe.scheduled_planting_id = sp.event_id
        LEFT OUTER JOIN planting_events AS pe ON sp.event_id = pe.scheduled_planting_id AND pe.successful = TRUE
WHERE
        sp.cancelled = FALSE
    AND EXTRACT(YEAR FROM sp.event_timestamp::TIMESTAMP) = %s
GROUP BY r.first_name, r.last_name, r.id, om.resident_id
ORDER BY plantings_led DESC, visits_attended DESC;
            ''', (year, year))
            rows = cur.fetchall()
            close_resources(conn, cur)
            custom_report_2 = []
            for row in rows:
                custom_report_2.append({
                    'org_member_name': row[0],
                    'plantings_led': row[1],
                    'successful_plantings_led': row[2],
                    'plantings_led_peak_year': row[3],
                    'plantings_led_in_peak_year': row[4],
                    'visits_attended': row[5],
                    'visits_attended_peak_year': row[6],
                    'visits_attended_in_peak_year': row[7]
                })
            return jsonify(custom_report_2)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Custom report 3
# -- The following query gives us a report regarding the total number of trees planted in neighborhood where they have been
# -- planted previously, the number planted in said neighborhood this year, as well as the peak year of planting in that
# -- neighborhood and the number planted during this year. This data is important for the organization so they can keep
# -- track of where the planted trees have gone, and monitor the amount that gets planted in each neighborhood. The query
# -- is parameterized via the common name of the tree, so that data can be accessed and looked through efficiently.
@app.route('/api/custom-report-3')
def get_custom_report_3():
    common_name = request.args.get('common_name')
    if not common_name:
        return jsonify({"error": "Missing common name parameter"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
            SELECT
    t.common_name,
    r.neighborhood,
    (SELECT
         COUNT(*)
     FROM
         tree_requests AS tr2
             INNER JOIN residents AS r2 ON tr2.resident_id = r2.id
             INNER JOIN scheduled_plantings sp2 ON tr2.id = sp2.tree_request_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
           r2.neighborhood = r.neighborhood
       AND tr2.tree_id = t.id
       AND pe2.successful = TRUE) AS num_in_neighborhood,
    (SELECT
         COUNT(*)
     FROM    tree_requests AS tr2
                 INNER JOIN residents AS r2 ON tr2.resident_id = r2.id
                 INNER JOIN scheduled_plantings AS sp2 ON tr2.id = sp2.tree_request_id
                 INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
           r2.neighborhood = r.neighborhood
       AND pe2.successful = TRUE
       AND EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP) = EXTRACT(YEAR FROM CURRENT_DATE::DATE)) AS num_planted_this_year,
    (SELECT
         EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     FROM
         tree_requests AS tr2
             INNER JOIN residents AS r2 ON tr2.resident_id = r2.id
             INNER JOIN scheduled_plantings AS sp2 ON tr2.id = sp2.tree_request_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
           r2.neighborhood = r.neighborhood
       AND pe2.successful = TRUE
     GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)                   AS plantings_peak_year,
    (SELECT
         COUNT(*)
     FROM
         tree_requests AS tr2
             INNER JOIN residents AS r2 ON tr2.resident_id = r2.id
             INNER JOIN scheduled_plantings AS sp2 ON tr2.id = sp2.tree_request_id
             INNER JOIN planting_events pe2 ON sp2.event_id = pe2.scheduled_planting_id
     WHERE
           r2.neighborhood = r.neighborhood
       AND pe2.successful = TRUE
     GROUP BY EXTRACT(YEAR FROM sp2.event_timestamp::TIMESTAMP)
     ORDER BY COUNT(*) DESC
     LIMIT 1)                   AS plantings_in_peak_year
FROM
    trees AS t
        INNER JOIN public.tree_requests tr ON t.id = tr.tree_id
        INNER JOIN residents r ON tr.resident_id = r.id
        INNER JOIN scheduled_plantings sp ON tr.id = sp.tree_request_id
        INNER JOIN planting_events pe ON sp.event_id = pe.scheduled_planting_id
WHERE
        pe.successful = TRUE
    AND t.common_name = %s
GROUP BY t.common_name, r.neighborhood, t.id
ORDER BY t.common_name ASC;
            ''', (common_name,))
            rows = cur.fetchall()
            close_resources(conn, cur)
            custom_report_3 = []
            for row in rows:
                custom_report_3.append(
                    {
                        'neighborhood_name': row[0],
                        'total_trees_planted': row[1],
                        'trees_planted_this_year': row[2],
                        'peak_year': row[3],
                        'trees_planted_in_peak_year': row[4]
                    }
                )
            return jsonify(custom_report_3)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Custom report 4
# -- The following query is to help users figure out which tree that they would like to order, the user provides minimum
# -- and maximum values for both height and width, providing the top 5 trees (based on how many are left in inventory).
# -- This query is important to help less informed users figure out which tree they want to plant. It prioritizes high
# -- inventory so that rarer trees can be left for those who are more passionate about trees. This data is important
# -- because it increases the user experience for many users.
@app.route('/api/custom-report-4')
def get_custom_report_4():
    min_height = request.args.get('min_height')
    max_height = request.args.get('max_height')
    min_width = request.args.get('min_width')
    max_width = request.args.get('max_width')

    if not (min_height and max_height and min_width and max_width):
        return jsonify({"error": "Missing height or width parameters"}), 500

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
  WITH valid_trees AS (SELECT
                            t.id,
                            t.common_name,
                            t.inventory
                        FROM trees t
                            INNER JOIN tree_requests tr
                                        ON t.id = tr.tree_id
                        WHERE
                                LOWER(t.height_range) >= %s
                            AND UPPER(t.height_range) <= %s
                            AND LOWER(t.height_range) >= %s
                            AND UPPER(t.height_range) <= %s
                        GROUP BY t.id, t.common_name, t.inventory
                        HAVING t.inventory - COUNT(tr) > 0)
SELECT t.common_name, COUNT(pe) AS num_planted
FROM valid_trees t
    INNER JOIN tree_requests tr ON t.id = tr.tree_id
    LEFT OUTER JOIN scheduled_plantings sp ON tr.id = sp.tree_request_id
    LEFT OUTER JOIN planting_events pe ON sp.event_id = pe.scheduled_planting_id AND pe.successful = TRUE
GROUP BY t.common_name, t.inventory
HAVING (SELECT COUNT(*)
        FROM valid_trees t2
        WHERE t2.inventory >= t.inventory) <= 4;
            ''', (min_height, max_height, min_width, max_width))
            rows = cur.fetchall()
            close_resources(conn, cur)
            custom_report_4 = []
            for row in rows:
                custom_report_4.append({
                    'common_name': row[0],
                    'num_planted': row[1]
                })
            return jsonify(custom_report_4)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Custom report 5
# 
# For each volunteer, show how many unique tree plantings they've participated in, 
# how many different species they've helped plant, how many plantings they've missed, 
# the success rate of the plantings that they have attended
#
@app.route('/api/custom-report-5')
def get_custom_report_5():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''

WITH scheduled_volunters AS (SELECT
    r.first_name || ' ' || r.last_name AS volunteer_name,
    COUNT(sp) AS num_plantings_scheduled_for
FROM residents r
     INNER JOIN scheduled_plantings_have_volunteers sphv ON r.id = sphv.volunteer_id
     LEFT OUTER JOIN scheduled_plantings sp ON sphv.planting_event_id = sp.event_id AND sp.cancelled = FALSE
WHERE is_volunteer = TRUE
GROUP BY r.first_name, r.last_name),
attended_volunteers AS (SELECT
    r.first_name || ' ' || r.last_name AS volunteer_name,
    COUNT(pehv) AS num_plantings_attended,
    COUNT(spe) AS num_successful_plantings_attended
FROM residents r
         INNER JOIN planting_events_have_volunteers pehv ON r.id = pehv.volunteer_id
         LEFT OUTER JOIN planting_events spe ON pehv.planting_event_id = spe.scheduled_planting_id AND spe.successful = TRUE
WHERE is_volunteer = TRUE
GROUP BY r.first_name, r.last_name)
SELECT sv.volunteer_name,
       av.num_plantings_attended,
       (sv.num_plantings_scheduled_for - av.num_plantings_attended) AS num_plantings_missed,
       (av.num_successful_plantings_attended::FLOAT / av.num_plantings_attended::FLOAT) AS success_rate_of_attended_plantings
FROM scheduled_volunters sv
    LEFT OUTER JOIN attended_volunteers av ON sv.volunteer_name = av.volunteer_name
GROUP BY sv.volunteer_name, sv.num_plantings_scheduled_for, av.num_plantings_attended, av.num_successful_plantings_attended
ORDER BY success_rate_of_attended_plantings ASC, num_plantings_missed DESC;
                        ''', )
            rows = cur.fetchall()
            close_resources(conn, cur)
            custom_report_5 = []
            for row in rows:
                custom_report_5.append({
                    'volunteer_name': row[0],
                    'num_plantings_attended': row[1],
                    'num_plantings_missed': row[2],
                    'success_rate_of_attended_plantings': row[3]
                })
            return jsonify(custom_report_5)
        except Exception as e:
             close_resources(conn, cur)
             return jsonify({"error": f"Database query failed: {e}"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500


# Get pending volunteer applications (admin only)
@app.route('/api/pending-volunteer-applications', methods=['GET'])
def get_pending_volunteer_applications():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                SELECT va.resident_id, va.created, va.notes, r.first_name, r.last_name, r.email
                FROM volunteer_applications va
                JOIN residents r ON va.resident_id = r.id
                WHERE va.approved IS NULL
                ORDER BY va.created ASC;
            ''')
            rows = cur.fetchall()
            close_resources(conn, cur)
            applications = []
            for row in rows:
                applications.append({
                    'resident_id': row[0],
                    'created': row[1],
                    'notes': row[2],
                    'first_name': row[3],
                    'last_name': row[4],
                    'email': row[5]
                })
            return jsonify(applications)
        except Exception as e:
             close_resources(conn, cur)
             print(f"Error fetching pending volunteer applications: {e}")
             return jsonify({"error": "Database query failed"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Approve a volunteer application (admin only)
@app.route('/api/approve-volunteer', methods=['PATCH'])
def approve_volunteer():
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    resident_id = data.get('resident_id')

    if not resident_id:
        return jsonify({"error": "Missing resident_id"}), 400

    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Update volunteer_applications table
            cur.execute('''
                UPDATE volunteer_applications
                SET approved = true
                WHERE resident_id = %s AND approved IS NULL;
            ''', (resident_id,))
            if cur.rowcount == 0:
                 close_resources(conn, cur)
                 return jsonify({"error": "Volunteer application not found or already approved"}), 404

            # Update residents table
            cur.execute('''
                UPDATE residents
                SET is_volunteer = true
                WHERE id = %s;
            ''', (resident_id,))

            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Volunteer approved successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error approving volunteer: {e}")
             return jsonify({"error": "Database error occurred"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Get details for a specific scheduled planting, including assigned people
@app.route('/api/scheduled-planting-details/<int:planting_event_id>', methods=['GET'])
def get_scheduled_planting_details(planting_event_id):
    conn = get_db_connection()
    details = {}
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                SELECT 
                        sp.event_id,
                        sp.tree_request_id,
                        sp.event_timestamp,
                        sp.cancelled,
                        sp.notes,
                        tr.site_description,
                        CASE WHEN pe.scheduled_planting_id IS NOT NULL THEN true ELSE false END AS outcome_recorded
                FROM scheduled_plantings sp
                LEFT JOIN planting_events pe ON sp.event_id = pe.scheduled_planting_id
                INNER JOIN tree_requests tr ON sp.tree_request_id = tr.id
                WHERE sp.event_id = %s;
            ''', (planting_event_id,))
            planting_info_row = cur.fetchone()

            if not planting_info_row:
                close_resources(conn, cur)
                return jsonify({"error": "Scheduled planting not found"}), 404
            details = {
                'event_id': planting_info_row[0],
                'tree_request_id': planting_info_row[1],
                'event_timestamp': planting_info_row[2],
                'cancelled': planting_info_row[3],
                'notes': planting_info_row[4],
                'site_description': planting_info_row[5],
                'outcome_recorded': planting_info_row[6]
            }

            # Get outcome details
            if details['outcome_recorded']:
                cur.execute('''
                    SELECT successful, observations
                    FROM planting_events
                    WHERE scheduled_planting_id = %s;
                ''', (planting_event_id,))
                outcome_row = cur.fetchone()
                if outcome_row:
                    details['outcome_successful'] = outcome_row[0]
                    details['outcome_observations'] = outcome_row[1]

                # Fetch attended volunteers for the recorded event
                cur.execute('''
                    SELECT r.id, r.first_name, r.last_name
                    FROM planting_events_have_volunteers pehv
                    JOIN residents r ON pehv.volunteer_id = r.id
                    WHERE pehv.planting_event_id = %s;
                ''', (planting_event_id,))
                attended_rows = cur.fetchall()
                attended_volunteers = []
                for row in attended_rows:
                    attended_volunteers.append({
                        'id': row[0],
                        'first_name': row[1],
                        'last_name': row[2]
                    })
                details['attended_volunteers'] = attended_volunteers

            # Get assigned volunteers
            cur.execute('''
                SELECT r.id, r.first_name, r.last_name
                FROM scheduled_plantings_have_volunteers spv
                JOIN residents r ON spv.volunteer_id = r.id
                WHERE spv.planting_event_id = %s;
            ''', (planting_event_id,))
            assigned_volunteers_rows = cur.fetchall()
            assigned_volunteers = []
            for row in assigned_volunteers_rows:
                assigned_volunteers.append({
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2]
                })
            details['assigned_volunteers'] = assigned_volunteers

            # Get assigned (leading) org members
            cur.execute('''
                SELECT r.id, r.first_name, r.last_name
                FROM organization_members_lead_scheduled_plantings omsp
                JOIN residents r ON omsp.organization_member_id = r.id
                WHERE omsp.scheduled_planting_id = %s;
            ''', (planting_event_id,))
            assigned_org_members_rows = cur.fetchall()
            assigned_org_members = []
            for row in assigned_org_members_rows:
                 assigned_org_members.append({
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2]
                })
            details['assigned_org_members'] = assigned_org_members

            close_resources(conn, cur)
            return jsonify(details)

        except Exception as e:
             if cur: cur.close()
             if conn: conn.close()
             print(f"Error fetching planting details: {e}")
             return jsonify({"error": "Database query failed"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Get list of available (approved) volunteers
@app.route('/api/available-volunteers', methods=['GET'])
def get_available_volunteers():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                SELECT id, first_name, last_name
                FROM residents
                WHERE is_volunteer = true
                ORDER BY last_name, first_name;
            ''')
            rows = cur.fetchall()
            close_resources(conn, cur)
            volunteers = []
            for row in rows:
                volunteers.append({
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2]
                })
            return jsonify(volunteers)
        except Exception as e:
             if cur: cur.close()
             if conn: conn.close()
             print(f"Error fetching available volunteers: {e}")
             return jsonify({"error": "Database query failed"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Get list of available org members
@app.route('/api/available-org-members', methods=['GET'])
def get_available_org_members():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                SELECT r.id, r.first_name, r.last_name
                FROM organization_members om
                JOIN residents r ON om.resident_id = r.id
                ORDER BY r.last_name, r.first_name;
            ''')
            rows = cur.fetchall()
            close_resources(conn, cur)
            members = []
            for row in rows:
                members.append({
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2]
                })
            return jsonify(members)
        except Exception as e:
             close_resources(conn, cur)
             print(f"Error fetching available org members: {e}")
             return jsonify({"error": "Database query failed"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Cancel a scheduled planting
@app.route('/api/cancel-planting/<int:planting_event_id>', methods=['PATCH'])
def cancel_planting(planting_event_id):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                UPDATE scheduled_events
                SET cancelled = true
                WHERE event_id = %s;
            ''', (planting_event_id,))
            if cur.rowcount == 0:
                 close_resources(conn, cur)
                 return jsonify({"error": "Planting event not found or already cancelled"}), 404
            conn.commit()
            close_resources(conn, cur)
            return jsonify({"message": "Planting cancelled successfully"})
        except psycopg2.Error as e:
             close_resources(conn, cur)
             print(f"Error cancelling planting: {e}")
             return jsonify({"error": "Database error occurred"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

# Get basic details for a visit, including the tree_request_id
@app.route('/api/visit-details/<int:visit_event_id>', methods=['GET'])
def get_visit_details(visit_event_id):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                SELECT tree_request_id
                FROM scheduled_events
                WHERE event_id = %s;
            ''', (visit_event_id,))
            row = cur.fetchone()
            close_resources(conn, cur)
            if not row:
                return jsonify({"error": "Visit event not found"}), 404
            return jsonify({"tree_request_id": row[0]})
        except Exception as e:
             if cur: cur.close()
             if conn: conn.close()
             print(f"Error fetching visit details: {e}")
             return jsonify({"error": "Database query failed"}), 500
    else:
        return jsonify({"error": "Could not connect to database"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)