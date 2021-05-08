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