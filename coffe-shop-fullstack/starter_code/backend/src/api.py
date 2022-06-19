import os
from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''

 implemented endpoint
    GET /drinks
        it returns a public endpoint
        it contains only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])

def get_drinks():
    drinks=Drink.query.order_by(Drink.id).all()
    try:
        return jsonify({
        'success':True,
        'drinks':[drink.short() for drink in drinks]
        })
    except:
        
        abort(404)
'''
implemented endpoint
    GET /drinks-detail
        it require the 'get:drinks-detail' permission
        it contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(jwt):
    drinks=Drink.query.all()
    return jsonify({
    'success':True,
    'drinks':[drink.long() for drink in drinks]
    }),200

'''
implemented endpoint
    POST /drinks
        it  create a new row in the drinks table
        it require the 'post:drinks' permission
        it  contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    body= request.get_json()

    if 'title' and 'recipe' not in body:
        abort(422)
    try: 
        body= request.get_json() 
        title = body['title']
        recipe = json.dumps(body['recipe'])
    
        
        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception:
        abort(422)       

'''
 implemented endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it  respond with a 404 error if <id> is not found
        it update the corresponding row for <id>
        it require the 'patch:drinks' permission
        it contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt,drink_id):
    drink = Drink.query.get(drink_id)
    body = request.get_json()

    if drink is None:
        abort(404)

    
    if 'title' and 'recipe'in body :
        drink.title = body['title']
        drink.recipe = json.dumps(body['recipe'])

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
 implemented endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it respond with a 404 error if <id> is not found
        it  delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drinks = Drink.query.filter(Drink.id == drink_id ).one_or_none()
    if drinks is  None :
        abort(404)
    try:
        drinks.delete()

        return jsonify({
            'success': True,
            'delete': drinks.id
        })

    except Exception:
        abort(422)   

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
implemented error handler for 404
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
implemented error handler for AuthError
'''

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
