from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import pooling

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'hkwaishing.com',  # e.g., 'localhost'
    'user': 'waishing_trendy',  # e.g., 'root'
    'password': 'Socool666',  # your database password
    'database': 'waishing_binance'  # your database name
}




# Create a connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **db_config
)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    rows_per_page = 20
    offset = (page - 1) * rows_per_page
    search = request.args.get('search', '')
    column = request.args.get('column', 'PRODUCT_ID')

    # Validate the column input
    valid_columns = ['PRODUCT_ID', 'SHEET_NAME']
    if column not in valid_columns:
        column = 'PRODUCT_ID'  # Fallback to a default column

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Build the base query
        query = "SELECT TITLE, STATUS, URL, COST, PHOTO, CREATED_DATE, UPDATED_DATE FROM PRODUCT"
        count_query = "SELECT COUNT(*) FROM PRODUCT"
        params = []

        # If searching, add conditions
        if search:
            query += f" WHERE {column} LIKE %s"
            count_query += f" WHERE {column} LIKE %s"
            params.append(f'%{search}%')

        # Execute the count query first to get the total rows
        cursor.execute(count_query, params if search else None)
        total_rows = cursor.fetchone()[0]

        # Add pagination to the main query
        query += " LIMIT %s OFFSET %s"
        params.extend([rows_per_page, offset])

        # Execute the main query
        cursor.execute(query, params)
        results = cursor.fetchall()

    except mysql.connector.Error as e:
        return f"Error: {e}"
    finally:
        cursor.close()
        connection.close()

    # Process the results to extract the first photo
    for index, row in enumerate(results):
        if row[4]:  # If the PHOTO column is not empty
            photos = row[4].split(',')  # Split by comma
            results[index] = (row[0], row[1], row[2], row[3], photos[0].strip(),row[5],row[6])  # Include URL and COST

    return render_template('index.html', results=results, total_rows=total_rows, page=page, rows_per_page=rows_per_page)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)