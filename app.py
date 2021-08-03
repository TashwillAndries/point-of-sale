import hmac

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
import sqlite3


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# fetching users from the database
def fetch_users():
    with sqlite3.connect('shopping.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users_data = cursor.fetchall()

        new_data = []

        for data in users_data:
            new_data.append(User(data[0], data[5], data[6]))

        return new_data


# creating table for users
def init_user_table():
    conn = sqlite3.connect('shopping.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "address TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table successfully")
    conn.close()


init_user_table()
users = fetch_users()


# creating table for the products
def init_products_table():
    with sqlite3.connect('shopping.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS cart (product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "item_name TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "quantity TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "type TEXT NOT NULL, "
                     "total TEXT NOT NULL)")
    print("shopping table created successfully")


init_products_table()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'this-is-a-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/user-registration/', methods=['POST'])
def user_registration():
    response = {}

    if request.method == "POST":

        first_name = request.form['first_name']
        surname = request.form['last_name']
        address = request.form['address']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("shopping.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user (first_name,last_name,address,email,username,password) VALUES(?,?,?,?,?,?)",
                           (first_name, surname, address, email, username, password))
            conn.commit()
            response["message"] = 'Success'
            response["status_code"] = 201
        return response


# protected route that creates products
@app.route('/products-create/', methods=['POST'])
@jwt_required()
def products_create():
    response = {}

    if request.method == "POST":

        item_name = request.form['item_name']
        description = request.form['description']
        quantity = request.form['quantity']
        price = request.form['price']
        type = request.form['type']
        total = int(price) * int(quantity)

        with sqlite3.connect('shopping.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cart (item_name, description, quantity,"
                           "price, type, total) VALUES(?, ?, ?, ?, ?, ?)", (item_name, description, quantity, price, type,
                                                                            total))
            conn.commit()
            response['message'] = "item added successfully"
            response['status_code'] = 201
        return response


# route to show all the products
@app.route('/get-products/', methods=['GET'])
def get_products():
    response = {}
    with sqlite3.connect('shopping.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cart")
        carts = cursor.fetchall()

    response['status_code'] = 201
    response['data'] = carts
    return response


# route to delete a product
@app.route("/delete-product/<int:product_id>")
@jwt_required()
def delete_product(product_id):
    response = {}
    with sqlite3.connect("shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE product_id=" + str(product_id))
        conn.commit()
        response['status_code'] = 201
        response['message'] = "product deleted successfully"
    return response


# route to edit products
@app.route('/edit-product/<int:product_id>/', methods=['PUT'])
@jwt_required()
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('shopping.db') as conn:
            cursor = conn.cursor()
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("item_name") is not None:
                put_data["item_name"] = incoming_data.get("item_name")
                with sqlite3.connect('shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET item_name =? WHERE product_id =?", (put_data['item_name'],
                                                                                        product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            if incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")
                with sqlite3.connect('shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET description =? WHERE product_id =?",
                                   (put_data['description'], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            if incoming_data.get("quantity") is not None:
                put_data["quantity"] = incoming_data.get("quantity")
                with sqlite3.connect('shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET quantity =? WHERE product_id =?",
                                   (put_data['quantity'], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            if incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")
                with sqlite3.connect('shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET price =? WHERE product_id =?",
                                       (put_data['price'], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            if incoming_data.get("type") is not None:
                put_data["type"] = incoming_data.get("type")
                with sqlite3.connect('shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET type =? WHERE product_id =?",
                                   (put_data['type'], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            if incoming_data.get("total") is not None:
                put_data["total"] = incoming_data.get("total")
                with sqlite3.connect('shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET total =? WHERE product_id =?",
                                   (put_data['total'], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
                return response


if __name__ == '__main__':
    app.run()