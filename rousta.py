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

@app.route('/badrequest400')
def bad_request():
    return abort(403)

@app.route('/api/v1.0/initiation/post', methods=['POST'])
def app_initiation_api():
    data = request.get_json() if request.get_json() else {}
    if not utils.initiation_validator(data)[0]:
        return jsonify(utils.initiation_validator(data)[1])
    cellNumber = data['cellNumber']
    registerCode = str(random2.randint(10000, 99999))
    sms_result = utils.send_sms(cellNumber, registerCode)
    user = models.User.query.filter_by(cellNumber = cellNumber).first()
    if user:
        return jsonify({
            'status': 303,
            'message': {'phone number': cellNumber,
            'register code': registerCode,
            'userId': user.userId}
            })
    return jsonify({
        'status': config.HTML_STATUS_CODE['Success'],
        'message': {'phone number': cellNumber,
        'register code': registerCode}
        })

@app.route('/api/v1.0/phoneNumber-approvement/post', methods=['POST'])
def cellNumber_approvement_api():
    data = request.get_json() if request.get_json() else {}
    if not utils.initiation_validator(data)[0]:
        return jsonify(utils.initiation_validator(data)[1])
    cellNumber = data['cellNumber']
    if db.session.query(models.User).filter(models.User.cellNumber == cellNumber).count():
        return jsonify({
            'status': config.HTML_STATUS_CODE['NotAcceptable'],
            'message': {'error': 'Duplicated phone number!'}
            })
    userId = str(uuid.uuid4())
    shop = utils.make_record({'title': "فروشگاه من"}, 'shop', {'owner': userId})
    models.Shop.create(**shop)
    shopList = []
    shopList.append(shop)
    models.User.create(
        cellNumber=cellNumber,
        userId=userId,
        shopList=shopList,
        createdDatetime=jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        )
    return jsonify({
        'status': config.HTML_STATUS_CODE['Success'],
        'message': {'phone number': cellNumber, 'userId': userId}
        })

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
        shop_result = db.session.query(models.Shop).filter_by(shopId = record['shopId']).first()
        products_list = copy.deepcopy(shop_result.productsList)
        products_list.append(record['productId'])
        shop_result.productsList = products_list
        db.session.commit()
        message = {'productId': record['productId']}
    elif 'shop' in object_type:
        models.Shop.create(**record)
        message = {'shopId': record['shopId']}
    return jsonify({
        'status': config.HTML_STATUS_CODE['Success'],
        'message': message})

@app.route('/api/v1.0/<query_type>-query/get', methods=['POST'])
def query_api(query_type):
    data = request.get_json() if request.get_json() else {}
    (l1, l2) = utils.query_range(data)
    result_list = utils.query_result(data, query_type, l1, l2)
    return jsonify({
        'status': config.HTML_STATUS_CODE['Success'],
        'message': {'result': result_list},
        'found records': len(result_list)
        })

#like and view products
@app.route('/api/v1.0/<action_type>-product/put', methods=['PUT'])
def like_view_api(action_type):
    data = request.get_json() if request.get_json() else {}
    if not utils.like_view_validator(data)[0]:
        return jsonify(utils.like_view_validator(data)[1])
    action_result = utils.like_view_action(data, action_type)
    if not action_result[0]:
        return jsonify(action_result[1])
    (len1, len2) = action_result[1]
    return jsonify({
        'status': config.HTML_STATUS_CODE['Success'],
        'message': {'productId': data['productId'], 'viewedNumber': len1, 'likedNumber': len2}
        })

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)