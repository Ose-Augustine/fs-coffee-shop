from hashlib import new
import os
from pdb import post_mortem
from flask import Flask, flash, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def retrieve_summary_of_drinks():
    drinks = Drink.query.all()[0]
    formatted_drinks = drinks.short()
    
    return jsonify({
        'success':True,
       "drinks":formatted_drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrive_details_of_drinks():
    drinks = Drink.query.all()[0]
    formatted_drinks = drinks.long()
    return jsonify({
        "success":True,
        "drinks":formatted_drinks
    })



@app.route('/drinks', methods= ['POST'])
@requires_auth('post:drinks')
def new_drink():
    body = request.get_json()
    title = body.get("title",None)
    recipe = body.get("recipe",None)
    new_drink = Drink(title=title,recipe=recipe)
    try:
        new_drink.insert()
    except:
        abort(400)
    return jsonify({
        'success':True,
    })

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_existing_drink(id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    body = request.get_json()
    title = body.get('title',None)
    recipe = body.get('recipe',None)
    #conditions depending on state of json body
    if title:
        drink.title = title
        drink.update()
    if recipe:
        drink.recipe = recipe 
        drink.update()
    #run the query a seocnd time to get new state of drink
    updated_drink = Drink.query.get_or_404(id)
    formatted_drink = updated_drink.long()
    return jsonify({
        'success':True,
        'dirnks':formatted_drink

    })


@app.route('/drinks/<int:id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def remove_drink(id):
    drink = Drink.query.get_or_404(id)
    id = drink.id
    drink.delete()
    return jsonify({
        'success':True,
        'deleted':id
        })

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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found():
    return jsonify({
        "success":False,
        "message":"Resource not found"
    })

@app.errorhandler(405)
def unsupported_method():
    return jsonify({
        "success":False,
        "message":"Method not allowed for the url requested"
    })
@app.errorhandler(403)
def permission_denied():
    return jsonify({
        "success":False,
        "message":"Permission not granted for request"
    })

@app.errorhandler(AuthError)
def auth_errors(error):
    return error.error 

if __name__ == "__main__":
    app.debug = True
    app.run()
