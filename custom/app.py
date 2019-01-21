import os

import stripe
from flask import Flask, jsonify, render_template, request, abort


app = Flask(__name__)

stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

products = [
    {
        'id': 1,
        'name': 'Something Special',
        'description': 'Something really, really special',
        'amount': 600
    },
    {
        'id': 2,
        'name': 'More Special',
        'description': 'Something even more special',
        'amount': 700
    },
]


def get_product(product_id):
    for product in products:
        if product['id'] == product_id:
            return product
    return False


@app.route('/hello')
def hello_world():
    return jsonify('hello, world!')


@app.route('/products/<int:product_id>')
def product(product_id):
    product = get_product(product_id)
    if product:
        product['amount_in_dollars'] = product['amount'] / 100
        return render_template(
            'index.html',
            key=stripe_keys['publishable_key'],
            product=product
        )
    return abort(404)


@app.route('/charge', methods=['POST'])
def charge():
    response = jsonify('error')
    response.status_code = 500
    product = get_product(int(request.json['product']))
    if product:
        try:
            product = get_product(int(request.json['product']))
            customer = stripe.Customer.create(
                email='sample@customer.com',
                source=request.json['token']
            )
            stripe.Charge.create(
                customer=customer.id,
                amount=product['amount'],
                currency='usd',
                description=product['description']
            )
            response = jsonify('success')
            response.status_code = 202
        except stripe.error.StripeError:
            return response
    return response


if __name__ == '__main__':
    app.run()
