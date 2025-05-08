from flask import Flask, request, jsonify
import mysql.connector
import logging
import os
from dotenv import load_dotenv
from flask_cors import CORS

# ✅ Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# ✅ Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ MySQL Connection Function
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=int(os.getenv("MYSQL_PORT", 3306))
        #       host="localhost",
        # user="root",
        # password="manoj",
        # database="college_predictor"
        )
    except Exception as e:
        logging.error(f"❌ Database Connection Error: {e}")
        return None

# ✅ Home Route
@app.route("/")
def home():
    return "✅ Flask App is Running on Clever Cloud!", 200

@app.route('/predict', methods=['POST'])
def predict_colleges():
    try:
        data = request.json
        logging.info(f"🔍 Received Request: {data}")

        min_cutoff = data.get("min_cutoff")
        max_cutoff = data.get("max_cutoff")
        category = data.get("category")
        branch = data.get("branch", "")
        district = data.get("district", "")

        if min_cutoff is None or max_cutoff is None or not category:
            return jsonify({"error": "Missing required fields: min_cutoff, max_cutoff, category"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                college_name, 
                college_code, 
                branchname AS branch, 
                district, 
                community AS category, 
                MIN(average_cutoff) AS min_cutoff, 
                MAX(average_cutoff) AS max_cutoff, 
                COUNT(*) AS college_count 
            FROM colleges 
            WHERE average_cutoff BETWEEN %s AND %s 
            AND LOWER(community) = LOWER(%s)
        """

        params = [min_cutoff, max_cutoff, category]

        if branch:
            query += " AND LOWER(branchname) LIKE LOWER(%s)"
            params.append(f"%{branch}%")
        if district:
            query += " AND LOWER(district) LIKE LOWER(%s)"
            params.append(f"%{district}%")

        query += " GROUP BY college_name, college_code, branchname, district, community"

        cursor.execute(query, tuple(params))
        result = cursor.fetchall()

        cursor.close()
        conn.close()
        logging.info(f"🔍 Predicted data: {result}")

        return jsonify({"predicted_colleges": result})

    except Exception as e:
        logging.error(f"❌ Error in /predict: {str(e)}")
        return jsonify({"error": "An error occurred while predicting colleges."}), 500


@app.route('/colleges', methods=['GET'])
def get_colleges():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Branch LIMIT 10")
        colleges = cursor.fetchall()
        conn.close()
        return jsonify(colleges)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Fetch Categories
@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT community FROM colleges")
        categories = [row['community'] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"categories": categories})
    except Exception as e:
        logging.error(f"Error in /categories: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ✅ Fetch Districts
@app.route('/districts', methods=['GET'])
def get_districts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT college_district FROM college_location")
        districts = [row['college_district'] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"districts": districts})
    except Exception as e:
        logging.error(f"❌ Error in /districts: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ✅ Fetch Branches
@app.route('/branches', methods=['GET'])
def get_branches():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT branchname FROM colleges WHERE branchname IS NOT NULL")
        branches = [row['branchname'] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"branches": branches})
    except Exception as e:
        logging.error(f"Error in /branches: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ✅ Fetch All Colleges with Locations
@app.route('/all-colleges', methods=['GET'])
def get_all_colleges():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM college_location")
        result = cursor.fetchall()
        conn.close()
        return jsonify({"colleges": result})
    except Exception as e:
        logging.error(f"Error in /all-colleges: {str(e)}")
        return jsonify({"error": "An error occurred while fetching colleges."}), 500

# ✅ Fetch Filters
@app.route('/filters', methods=['GET'])
def get_filters():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT DISTINCT college_district FROM college_location")
        districts = [row['college_district'] for row in cursor.fetchall()] or []

        cursor.execute("SELECT DISTINCT code FROM college_location")
        college_codes = [row['code'] for row in cursor.fetchall()] or []

        conn.close()

        return jsonify({"districts": districts, "college_codes": college_codes})
    except Exception as e:
        logging.error(f"Error in /filters: {str(e)}")
        return jsonify({"districts": [], "college_codes": [], "error": str(e)}), 500

# ✅ Register User
@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        required_fields = ['name', 'age', 'gender', 'school', 'dob', 'mobile', 'email']
        
        if not all(data.get(field) for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "INSERT INTO users (name, age, gender, school, dob, mobile, email) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, tuple(data[field] for field in required_fields))

        conn.commit()
        conn.close()

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        logging.error(f"Error in /register: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ✅ Run the App
if __name__ == '__main__':
    logging.info(f"Starting Flask App on http://127.0.0.1:5000 🚀")

    logging.info(f"MYSQL_USER: {os.getenv('MYSQL_USER')}")
    logging.info(f"MYSQL_DATABASE: {os.getenv('MYSQL_DATABASE')}")
    
    app.run(debug=True)
