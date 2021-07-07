#mysql config info
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
#MYSQL_USERNAME = "rstaakir_mysql"
MYSQL_USERNAME = "mysql"
#MYSQL_PASSWORD = "Vi8Um-i(2*v;"
MYSQL_PASSWORD = "123fes"

#postgresql config info
POSTGRESQL_HOST = "localhost"
POSTGRESQL_PORT = 5432
#POSTGRESQL_USERNAME = "rstaakir_postgres"
POSTGRESQL_USERNAME = "postgres"
#POSTGRESQL_PASSWORD = "KcND(o!3hP4;"
POSTGRESQL_PASSWORD = "123fes"

#mongodb config info
#MONGODB_HOST = "91.98.96.173"
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
#MONGODB_USERNAME = "rstaakir_mongo"
MONGODB_USERNAME = "mongo"
#MONGODB_PASSWORD = "McKC(o!4hP3;"
MONGODB_PASSWORD = "123fes"
authMechanism = "SCRAM-SHA-256"

MYSQL_DB_NAME = "rstaakir_rostaak"
POSTGRESQL_DB_NAME = "rstaakir_rousta"
MONGO_DB_NAME = "rousta"
MONGO_CHAT_DB_NAME = "rstaakir_chat"

#ippanel (sms sender) config info
IPPANEL_API_KEY = "at8ETrykancq8AY8ktJjbXD1z42wWiHBosVOEa3OUOA="
SMS_PATTERN_CODE = "gxq3go11wa"
SMS_ORIGINATOR = "+983000505"

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
#IMAGE_FILE_FOLDER = '/home/rstaakir/ROUSTA/static/img'
#IMAGE_URL_PATH = 'http://rstaak.ir/static/img'
IMAGE_FILE_FOLDER = 'E:/projects/ROUSTA/rousta/static/img'
ATTACHED_FILE_FOLDER = '/root/vestano/static/attachments'

LOCATION_QUERY = ['ostan', 'shahrestan', 'bakhsh', 'shahr', 'dehestan', 'abadi', 'dehshahr']
REGEX_QUERY = ['locationRegex', 'adRegex']

HTML_STATUS_CODE = {
'Success': 200,
'NotAcceptable': 406,
'NotFound': 404,
'Duplicate': 409,
'SeeOther': 303,
'NoContent': 204,
'NotImplemented': 501
}

productsConstantValues = ['_sa_instance_state', 'productId', 'createdDatetime',
'owner', 'byer', 'ordered', 'viewList', 'likeList']
shopsConstantValues = ['_sa_instance_state', 'shopId', 'createdDatetime',
'owner', 'productsList', 'customersList', 'viewList', 'likeList', 'shopLink']
categoriesConstantValues = ['categoryId', 'createdDatetime',
'childCategories', 'productsList']