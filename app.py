#Task 1
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError
from password import my_password

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/e_commerce_db'
                                                                

db = SQLAlchemy(app)
ma = Marshmallow(app)

class customerschema(ma.Schema):
    name = fields.String(required = True) 
    email = fields.String(required = True) 
    phone = fields.String(required = True)
    

    class Meta:
        fields = ('name', 'email', 'phone', 'id')

customer_schema = customerschema()
customers_schema = customerschema(many=True)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref = 'customers')


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

class orderschema(ma.Schema):
    date = fields.Date(required = True) 
    customer_id = fields.Integer(required = True)
    

    class Meta:
        fields = ('date', 'customer_id', 'id')

order_schema = orderschema()
orders_schema = orderschema(many=True)



class CustomerAccount(db.Model):
    __tablename__ = 'customeraccounts'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = db.relationship('Customer', backref = 'customer_account', uselist = False) 

class customeraccountchema(ma.Schema):
    username = fields.String(required = True) 
    password = fields.String(required = True) 
    customer_id = fields.String(required = True)
    

    class Meta:
        fields = ('username', 'password', 'customer_id', 'id')

account_schema = customeraccountchema()
accounts_schema = customeraccountchema(many=True)


order_product = db.Table('Order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key = True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key = True)
)

class product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    price = db.Column(db.String(10), nullable = False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    orders = db.relationship('Order', secondary = order_product, backref = db.backref('products'))

class productschema(ma.Schema):
    name = fields.String(required = True) 
    price = fields.String(required = True) 
    order_id = fields.Integer(required = True)
    

    class Meta:
        fields = ('name', 'price', 'order_id', 'id')

product_schema = productschema()
products_schema = productschema(many=True)


with app.app_context():
    db.create_all() 

if __name__ == '__main__':
    app.run(debug=True)


#Customer management
@app.route('/customers', methods = ['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers', methods = ['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(name = customer_data['name'], email = customer_data['email'], phone = customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({'message': "New customer added successfully"}), 201


@app.route('/customers/<int:id>', methods = ['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()

    return jsonify({'message': 'Customer details updated succesfully'}), 200

@app.route('/customers/<int:id>', methods = ['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": 'Customer deleted successfully'}), 200


#CustomerAccount management
@app.route('/customeraccounts', methods = ['GET'])
def get_accounts():
    customers = CustomerAccount.query.all()
    return accounts_schema.jsonify(customers)

@app.route('/customeraccounts', methods = ['POST'])
def add_customeraccount():
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_account = CustomerAccount(username = account_data['username'], password = account_data['password'], customer_id = account_data['customer_id'])
    db.session.add(new_account)
    db.session.commit()

    return jsonify({'message': "New account added successfully"}), 201


@app.route('/customeraccounts/<int:id>', methods = ['PUT'])
def update_account(id):
    account = CustomerAccount.query.get_or_404(id)
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    account.username = account_data['username']
    account.password = account_data['password']
    account.customer_id = account_data['customer_id']
    db.session.commit()

    return jsonify({'message': 'Account details updated succesfully'}), 200


@app.route('/customeraccounts/<int:id>', methods = ['DELETE'])
def delete_account(id):
    account = CustomerAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()

    return jsonify({"message": 'Account deleted successfully'}), 200


#Product management

@app.route('/products', methods = ['GET'])
def get_products():
    products = product.query.all()
    return products_schema.jsonify(products)


@app.route('/products', methods = ['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = product(name = product_data['name'], price = product_data['price'], order_id = product_data['order_id'])
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': "New product added successfully"}), 201


@app.route('/products/<int:id>', methods = ['PUT'])
def update_product(id):
    products = product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    products.name = product_data['name']
    products.price = product_data['price']
    products.order_id = product_data['order_id']
    db.session.commit()

    return jsonify({'message': 'Product details updated succesfully'}), 200


@app.route('/products/<int:id>', methods = ['DELETE'])
def delete_product(id):
    products = product.query.get_or_404(id)
    db.session.delete(products)
    db.session.commit()

    return jsonify({"message": 'Product deleted successfully'}), 200



#Order management

@app.route('/orders', methods = ['GET'])
def get_orders():
    orders = Order.query.all()
    return orders_schema.jsonify(orders)


@app.route('/orders', methods = ['POST'])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_order = Order(date = order_data['date'], customer_id = order_data['customer_id'])
    db.session.add(new_order)
    db.session.commit()

    return jsonify({'message': "New order added successfully"}), 201


@app.route('/orders/<int:id>', methods = ['PUT'])
def update_order(id):
    orders = Order.query.get_or_404(id)
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    orders.date = order_data['date']
    orders.customer_id = order_data['customer_id']
    db.session.commit()

    return jsonify({'message': 'Order details updated succesfully'}), 200


@app.route('/orders/<int:id>', methods = ['DELETE'])
def delete_order(id):
    orders = Order.query.get_or_404(id)
    db.session.delete(orders)
    db.session.commit()

    return jsonify({"message": 'Order deleted successfully'}), 200