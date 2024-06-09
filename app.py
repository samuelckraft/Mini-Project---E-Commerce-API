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
    orders = db.relationship('order', backref = 'customer')


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))



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
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key = True)
)

class product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    price = db.Column(db.Float, nullable = False)
    orders = db.relationship('orders', secondary = order_product, backref = db.backref('products'))


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