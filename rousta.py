#coding: utf-8
from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify
from flask import Response, logging, Markup, abort, after_this_request, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate
from passlib.hash import sha256_crypt
from functools import wraps
from cerberus import Validator
from werkzeug.utils import secure_filename
import requests
import random2
import uuid
import os
import subprocess
import sys
import jwt
import datetime
import jdatetime
import pdfkit
import copy
import json
import base64
import config


app = Flask(__name__)

app.secret_key = 'secret@rousta@password_hash@840'
app.config['IMAGE_FILE_FOLDER'] = config.IMAGE_FILE_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}/{}'.format(
    config.POSTGRESQL_USERNAME, config.POSTGRESQL_PASSWORD, config.POSTGRESQL_HOST, config.DB_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)

import models, utils

#Config mongodb
#mongo_cursor = utils.config_mongodb()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'loged_in' not in session:
            flash(u'لطفا ابتدا وارد شوید!', 'danger')
            return redirect(url_for('logout'))

        if 'access-token' in request.headers['Cookie']:
            Token = request.headers['Cookie'].split(' ')
            token = Token[0][13:-1]

        if not token:
            flash('Token is missing!', 'danger')
            return redirect(request.referrer)

        try:
            data = jwt.decode(token, app.secret_key)
        except:
            return redirect(url_for('token_logout'))            

        result = cursor.users.find_one({"user_id": data['user_id']})
        if result:
            if 'username' not in session:
                username = result['username']
                session['username'] = username
                session['message'] = result['name']
                session['jdatetime'] = jdatetime.datetime.today().strftime('%d / %m / %Y')
                flash(result['name'] + u' عزیز خوش آمدید', 'success-login')
        
        else:
            flash('Token is not valid!', 'danger')
            return redirect(request.referrer)

        return f(*args, **kwargs)
    return decorated

@app.route('/badrequest400')
def bad_request():
    return abort(403)

@app.route('/api/v1.0/connect/token', methods=['POST'])
def token_api():
    print('here')
    #api_key = str(request.args.get('API_KEY'))
    if not data:
        status = 401  #unauthorized
        message = {'error': 'There is no API key!'}
        return jsonify({'status': status, 'message': message})
    api_key = str(data['API_KEY'])
    #if cursor.apiKey_pool.find_one({'apiKey':api_key}):
    if api_key == '123':
        TOKEN = jwt.encode({'API_KEY':api_key,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=20)},
            app.secret_key, algorithm='HS256')
        token = TOKEN.decode('UTF-8')
        status = 200  #success
        message =  {'access token': token, 'expires in': 120, "token_type": "Bearer"}
    else:
        status = 401  #unauthorized
        message = {'error': 'Not valid API key!'}
    return jsonify({'status': status, 'message': message})

@app.route('/api/v1.0/register/post', methods=['POST'])
def register_to_app_api():
    auth = str(request.headers.get('Authorization')).split(' ')[1]
    jwt_data = jwt.decode(auth, app.secret_key, algorithm='HS256')
    #if cursor.apiKey_pool.find_one({'apiKey':str(data['API_KEY'])}):
    if jwt_data['API_KEY'] == '123':
        #defaul status and message if there was proplems in interance data
        status = 406  #Not Acceptable
        message = {'error': 'There is some problems in your data!'}

        if 'data' not in request.form:
            return jsonify({'status': status, 'message': message})

        data = json.loads(request.form['data'])
        if 'cellNumber' not in data.keys():
            return jsonify({'status': status, 'message': "cellNumber is missed!"})
        elif 'password' not in data.keys():
            return jsonify({'status': status, 'message': "password is missed!"})
        cellNumber = str(data['cellNumber'])
        app_password = str(data['password'])
        name = str(data['name']) if 'name' in data.keys() else None
        family = str(data['family']) if 'family' in data.keys() else None

        #app_user_result = cursor.app_users.find_one({"username": app_username})
        if db.session.query(models.User).filter(models.User.cellNumber == cellNumber).count():
            status = 406  #Not Acceptable
            message = {'error': 'Duplicated phone number!'}
            return jsonify({'status': status, 'message': message})
        hash_password = sha256_crypt.hash(app_password)
        rec = models.User(cellNumber, hash_password, name, family, str(uuid.uuid4()))
        register_code = str(random2.randint(10000, 99999))
        sms_result = utils.send_sms(cellNumber, register_code)
        userSmsValidator_restApi
        print(sms_result)
        db.session.add(rec)
        db.session.commit()
        status = 200  #success
        message = {'data': {'phone number': cellNumber}}
    else:
        status = 401  #unauthorized
        message = {'error': 'Not authorized request!'}
    return jsonify({'status': status, 'message': message})

@app.route('/api/v1.0/initiation/post', methods=['POST'])
def app_initiation_api():
    status = 406  #Not Acceptable
    message = {'error': 'There is some problems in your data!'}

    data = request.get_json()
    if not data:
    #if 'data' not in request.form:
        return jsonify({'status': status, 'message': message})

    if 'cellNumber' not in data.keys():
        return jsonify({'status': status, 'message': "cellNumber is missed!"})
    cellNumber = str(data['cellNumber'])
    registerCode = str(random2.randint(10000, 99999))
    sms_result = utils.send_sms(cellNumber, registerCode)
    if db.session.query(models.User).filter(models.User.cellNumber == cellNumber).count():
        return jsonify({
            'status': 303,
            'data': {'message': cellNumber + " is registered before!", 'register code': registerCode}
            })
    status = 200  #success
    message = {'data': {
    'phone number': cellNumber,
    'register code': registerCode
    }}
    return jsonify({'status': status, 'message': message})

@app.route('/api/v1.0/phoneNumber-approvement/post', methods=['POST'])
def cellNumber_approvement_api():
    status = 406  #Not Acceptable
    message = {'error': 'There is some problems in your data!'}

    data = request.get_json()
    if not data:
        return jsonify({'status': status, 'message': message})

    if 'cellNumber' not in data.keys():
        return jsonify({'status': status, 'message': "cellNumber is missed!"})
    cellNumber = str(data['cellNumber'])
    if db.session.query(models.User).filter(models.User.cellNumber == cellNumber).count():

        #delete a record
        #models.User.delete(models.User.query.filter_by(cellNumber = cellNumber).first())

        #update a record
        #record = db.session.query(models.User).filter_by(cellNumber = cellNumber)
        #record[0].name = "محمدرضا"
        #record[0].family = "بابالو"
        #record[0].fullName = record[0].name + ' ' + record[0].family
        #db.session.commit()
        status = 406  #Not Acceptable
        message = {'error': 'Duplicated phone number!'}
        return jsonify({'status': status, 'message': message})
    shopList = {'1':'a', '2':'b'}

    #create a record
    models.User.create(
        cellNumber=cellNumber,
        userId=str(uuid.uuid4()),
        createdDatetime=jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        )
    #data = models.User(cellNumber=cellNumber, userId=str(uuid.uuid4()),
        #createdDatetime=jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
    #db.session.add(data)
    #db.session.commit()
    status = 200  #success
    message = {'data': {'phone number': cellNumber}}
    return jsonify({'status': status, 'message': message})

@app.route('/api/v1.0/new-<object_type>/post', methods=['POST'])
def create_object_api(object_type):
    data = request.get_json()
    if not utils.validating_request(data, object_type)[0]:
        return jsonify(utils.validating_request(data, object_type)[1])
    owner = utils.validating_request(data, object_type)[1]
    record = utils.make_record(data, object_type, owner)
    if not record:
        return jsonify({
            'status': config.HTML_STATUS_CODE['NotAcceptable'],
            'message': "The image can not be saved!"
            })
    if 'product' in object_type:
        models.Product.create(**record)
        message = {'productId': record['productId']}
    elif 'shop' in object_type:
        models.Shop.create(**record)
        message = {'shopId': record['shopId']}
    return jsonify({
        'status': config.HTML_STATUS_CODE['Success'],
        'message': message})

@app.route('/api/v1.0/<query_type>-query/post', methods=['POST'])
def query_api(query_type):
    data = request.get_json() if request.get_json() else {}
    (l1, l2) = utils.query_range(data)
    result_list = utils.query_result(data, query_type, l1, l2)
    return jsonify({
        'status': config.HTML_STATUS_CODE['Success'],
        'message': {'result': result_list},
        'found records': len(result_list)
        })

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)