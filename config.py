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

#DB_NAME = "rstaakir_rousta"
DB_NAME = "rousta"

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