from rousta import db, manager
from flask_migrate import MigrateCommand
import models

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()


#for run this script:

#for first time:
#python manage.py db init

#then for each upgrading models:
#python manage.py db migrate
#python manage.py db upgrade