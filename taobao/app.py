from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from mysql.connector import pooling
import download_photo2


app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'hkwaishing.com',
    'user': 'waishing_trendy',
    'password': 'Socool666',  # Use an environment variable for security
    'database': 'waishing_binance'
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
    rows_per_page = request.args.get('per_page', 20, type=int)  # Get rows_per_page from URL
    offset = (page - 1) * rows_per_page
    selected_sheet = request.args.get('sheet_name', '')
    product_id = request.args.get('product_id', '')

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Fetch unique SHEET_NAMEs for the dropdown
        cursor.execute("SELECT DISTINCT SHEET_NAME FROM PRODUCT")
        sheet_names = cursor.fetchall()

        # Build the base query
        query = "SELECT product_id, title, status, url, cost, body, photo, tags, created_date, updated_date, type_id FROM PRODUCT"
        count_query = "SELECT COUNT(*) FROM PRODUCT"
        params = []

        if product_id:
            query += " WHERE product_id LIKE %s"
            count_query += " WHERE product_id LIKE %s"
            params.append(f'%{product_id}%')
        elif selected_sheet:
            query += " WHERE SHEET_NAME = %s"
            count_query += " WHERE SHEET_NAME = %s"
            params.append(selected_sheet)

        # Fetch total rows
        cursor.execute(count_query, params if params else None)
        total_rows = cursor.fetchone()[0]

        # Ensure page number is valid
        if page < 1:
            page = 1

        # Add LIMIT and OFFSET to the query
        query += " LIMIT %s OFFSET %s"
        params.extend([rows_per_page, offset])

        cursor.execute(query, params)
        results = cursor.fetchall()

        total_pages = (total_rows + rows_per_page - 1) // rows_per_page

    except mysql.connector.Error as e:
        return f"Error: {e}"
    finally:
        cursor.close()
        connection.close()

    return render_template('index.html', results=results, total_rows=total_rows, page=page, rows_per_page=rows_per_page, sheet_names=sheet_names, current_page=page, total_pages=total_pages, selected_sheet=selected_sheet, product_id=product_id)
@app.route('/update', methods=['POST'])
def update_product():
    print("Received POST request to update products.")
    print("Form data:", request.form)  # Print all form data for debugging

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        update_query = """
        UPDATE PRODUCT
        SET title = %s, cost = %s, body = %s, tags = %s, type_id = %s
        WHERE product_id = %s
        """

        for key in request.form.keys():
            if key.startswith("id-"):
                product_id = request.form.get(key)

                title = request.form.get(f"title-{product_id}")
                price = request.form.get(f"price-{product_id}")
                body = request.form.get(f"body-{product_id}")
                tags = request.form.get(f"tags-{product_id}")
                type_id = request.form.get(f"type_id-{product_id}")

                print(f"Updating Product ID: {product_id}, Title: {title}, Price: {price}, Body: {body}, Tags: {tags} ")
                cursor.execute(update_query, (title, price, body, tags, type_id,  product_id))

        connection.commit()
        print("All products updated successfully.")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return f"Error: {e}"
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('index'))

@app.route('/check_update')
def check_update():
    page = request.args.get('page', 1, type=int)
    rows_per_page = 20
    offset = (page - 1) * rows_per_page
    selected_sheet = request.args.get('sheet_name', '')
    product_id = request.args.get('product_id', '')

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Fetch unique SHEET_NAMEs for the dropdown
        cursor.execute("SELECT DISTINCT SHEET_NAME FROM PRODUCT")
        sheet_names = cursor.fetchall()

        # Build the base query including TAGS
        query = """
        SELECT product_id, title, status, url, cost, body, photo, tags, created_date, updated_date , type_id
        FROM PRODUCT 
        """
        count_query = "SELECT COUNT(*) FROM PRODUCT"
        params = []

        if product_id:
            query += " WHERE product_id LIKE %s"
            count_query += " WHERE product_id LIKE %s"
            params.append(f'%{product_id}%')
        elif selected_sheet:
            query += " WHERE SHEET_NAME = %s"
            count_query += " WHERE SHEET_NAME = %s"
            params.append(selected_sheet)



        cursor.execute(count_query, params if params else None)
        total_rows = cursor.fetchone()[0]

        if page < 1:
            page = 1

        query += " LIMIT %s OFFSET %s  order by updated_date desc"
        params.extend([rows_per_page, offset])

        cursor.execute(query, params)
        results = cursor.fetchall()

    except mysql.connector.Error as e:
        return f"Error: {e}"
    finally:
        cursor.close()
        connection.close()

    return render_template('update.html', results=results, total_rows=total_rows, page=page, rows_per_page=rows_per_page, sheet_names=sheet_names)


@app.route('/fetch_brands', methods=['GET'])
def fetch_brands():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT DISTINCT BRAND_NAME FROM PRODUCT_TYPE")  # Adjust as necessary
        brands = cursor.fetchall()

        # Convert to a list of dictionaries for easier access in JavaScript
        brands_list = [{'name': row[0]} for row in brands]

        return jsonify(brands_list)

    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/fetch_catas', methods=['GET'])
def fetch_catas():
    brand_name = request.args.get('brand_name')
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT DISTINCT CATA FROM PRODUCT_TYPE WHERE BRAND_NAME = %s", (brand_name,))
        catas = cursor.fetchall()

        return jsonify([{'name': row[0]} for row in catas])  # Adjusted to return only CATA names

    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/fetch_types', methods=['GET'])
def fetch_types():
    brand_name = request.args.get('brand_name')  # Get BRAND_NAME
    cata = request.args.get('cata')  # Get CATA

    print(f"Brand Name: {brand_name}, CATA: {cata}")  # Log received parameters

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Query to fetch TYPE_NAME where BRAND_NAME and CATA match
        cursor.execute("""
            SELECT ID, TYPE_NAME 
            FROM PRODUCT_TYPE 
            WHERE BRAND_NAME = %s AND CATA = %s
        """, (brand_name, cata))

        types = cursor.fetchall()

        print(f"Fetched Types: {types}")  # Log fetched types

        return jsonify([{'id': row[0], 'name': row[1]} for row in types])

    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/update_db', methods=['GET'])
def update_db():
    sheet_id = request.args.get('id')
    try:
        print('Start update db ', sheet_id)

        download_photo2.update_product_status(sheet_id)
        print('End update db ')
    except error as e:
        print(e)


    return redirect(url_for('index'))


@app.route('/fetch_type_details', methods=['GET'])
def fetch_type_details():
    type_id = request.args.get('id')

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        # Fetch ID, TITLE, BODY, TAGS, and PHOTO from PRODUCT_TYPE
        cursor.execute("SELECT ID, TITLE, BODY, TAGS, PHOTO FROM PRODUCT_TYPE WHERE ID = %s", (type_id,))
        result = cursor.fetchone()

        if result:
            return jsonify({
                'id': result[0],
                'title': result[1],
                'body': result[2],
                'tags': result[3],
                'photo': result[4]  # Include PHOTO in the response
            })
        else:
            return jsonify({'error': 'Type not found'}), 404

    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)