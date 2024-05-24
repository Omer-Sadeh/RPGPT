from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from backend.Game.Game import Game
from backend.Utility import build_error_response, build_success_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, \
    set_access_cookies


# ----------------------------------------------------- #
# ---------------------- App Setup -------------------- #
# ----------------------------------------------------- #


def check_inputs(input_data, required_fields):
    for f_name, f_type in required_fields.items():
        if f_name not in input_data:
            return build_error_response(f"{f_name} not provided.")
        if type(input_data[f_name]) is not f_type:
            return build_error_response(f"{f_name} must be a {f_type}, got {type(input_data[f_name])} instead.")
    return None


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'your_strong_secret_key'
app.config["JWT_SECRET_KEY"] = 'your_jwt_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

db = SQLAlchemy(app)
bcrypt = Bcrypt()
jwt = JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


@app.route('/login', methods=['POST'])
def login():
    input_data = request.get_json()
    error = check_inputs(input_data, {
        "username": str,
        "password": str
    })
    if error:
        return error

    username = input_data['username']
    password = input_data['password']

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return build_success_response(access_token)
    else:
        return build_error_response("Invalid username or password")


@app.route('/register', methods=['POST'])
def register():
    input_data = request.get_json()
    error = check_inputs(input_data, {
        "username": str,
        "password": str
    })
    if error:
        return error

    username = input_data['username']
    password = input_data['password']

    if len(username.split()) > 1:
        return build_error_response("Username must not contain spaces.")
    if len(password) < 8:
        return build_error_response("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        return build_error_response("Password must contain at least one digit.")
    if not any(char.isupper() for char in password):
        return build_error_response("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in password):
        return build_error_response("Password must contain at least one lowercase letter.")
    if not any(char in "!@#$%^&*()-+" for char in password):
        return build_error_response("Password must contain at least one special character.")

    user = User.query.filter_by(username=username).first()

    if user:
        return build_error_response("Username already exists!")

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return build_success_response("User created successfully!")


def run_app():
    with app.app_context():
        db.create_all()
        app.run()


# ----------------------------------------------------- #
# ---------------------- Endpoint --------------------- #
# ----------------------------------------------------- #

API = Game()


@app.route('/startup', methods=['GET'])
def startup():
    return API.system_startup()


@app.route('/saves_list', methods=['GET'])
@jwt_required()
def saves():
    username = User.query.filter_by(id=get_jwt_identity()).first().username
    return API.get_saves_list(username)


@app.route('/themes', methods=['GET'])
def themes():
    return API.get_available_themes()


@app.route('/load', methods=['POST'], endpoint='load')
@jwt_required()
def load():
    input_data = request.get_json()
    error = check_inputs(input_data, {
        "save_name": str
    })

    username = User.query.filter_by(id=get_jwt_identity()).first().username

    if error:
        return error
    return API.load_save(username, input_data["save_name"], request.headers['images'] == 'True')


@app.route('/fetch', methods=['POST'], endpoint='fetch')
@jwt_required()
def fetch():
    input_data = request.get_json()
    error = check_inputs(input_data, {
        "save_name": str
    })

    username = User.query.filter_by(id=get_jwt_identity()).first().username

    if error:
        return error
    return API.fetch_save(username, input_data["save_name"])


@app.route('/new_save', methods=['POST'], endpoint='new_save')
@jwt_required()
def new_save():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "theme": str,
        "background": dict
    })

    if error:
        return error
    return API.new_save(username, input_data["theme"], input_data["background"])


@app.route('/delete', methods=['POST'], endpoint='delete')
@jwt_required()
def delete():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "save_name": str
    })

    if error:
        return error
    return API.delete_save(username, input_data["save_name"])


@app.route('/goals', methods=['POST'], endpoint='goals')
@jwt_required()
def goals():
    username = User.query.filter_by(id=get_jwt_identity()).first().username
    input_data = request.get_json()

    error = check_inputs(input_data, {
        "regen": bool,
        "save_name": str
    })

    if error:
        return error

    return API.get_goals(username, input_data["save_name"], input_data["regen"])


@app.route('/new_story', methods=['POST'], endpoint='new_story')
@jwt_required()
def new_story():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "save_name": str
    })

    if error:
        return error
    return API.new_story(username, input_data["save_name"], input_data["goal"] if "goal" in input_data else None)


@app.route('/advance', methods=['POST'], endpoint='advance')
@jwt_required()
def advance():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "action": str,
        "save_name": str
    })

    if error:
        return error
    return API.advance_story(username, input_data["save_name"], input_data["action"], request.headers['images'] == 'True')


@app.route('/new_option', methods=['POST'], endpoint='new_option')
@jwt_required()
def new_option():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "new_action": str,
        "save_name": str
    })

    if error:
        return error
    return API.create_new_option(username, input_data["save_name"], input_data["new_action"])


@app.route('/spend', methods=['POST'], endpoint='spend')
@jwt_required()
def spend():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "skill": str,
        "save_name": str
    })

    if error:
        return error
    return API.spend_action_point(username, input_data["save_name"], input_data["skill"])


@app.route('/shop', methods=['POST'], endpoint='shop')
@jwt_required()
def shop():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "save_name": str
    })

    if error:
        return error
    return API.get_shop(username, input_data["save_name"], request.headers['images'] == 'True')


@app.route('/buy', methods=['POST'], endpoint='buy')
@jwt_required()
def buy():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "item_name": str,
        "save_name": str
    })

    if error:
        return error
    return API.buy_item(username, input_data["save_name"], input_data["item_name"])


@app.route('/sell', methods=['POST'], endpoint='sell')
@jwt_required()
def sell():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "item_name": str,
        "save_name": str
    })

    if error:
        return error
    return API.sell_item(username, input_data["save_name"], input_data["item_name"])


@app.route('/end_story', methods=['POST'], endpoint='end_story')
@jwt_required()
def end():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "save_name": str
    })

    if error:
        return error
    return API.end_game(username, input_data["save_name"], request.headers['images'] == 'True')


@app.route('/image', methods=['POST'], endpoint='image')
@jwt_required()
def image():
    username = User.query.filter_by(id=get_jwt_identity()).first().username

    input_data = request.get_json()
    error = check_inputs(input_data, {
        "save_name": str
    })

    if error:
        return error
    return API.get_image(username, input_data["save_name"])


if __name__ == '__main__':
    run_app()
