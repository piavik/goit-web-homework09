from mongoengine import connect
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

# ----- Mongo -----
mongo_user = config.get('MONGO', 'user')
mongodb_pass = config.get('MONGO', 'pass')
db_name = config.get('MONGO', 'db_name')
domain = config.get('MONGO', 'domain')

# ----- mongo connect -----
connect(host=f"""mongodb+srv://{mongo_user}:{mongodb_pass}@{domain}/{db_name}?retryWrites=true&w=majority""", ssl=True)
