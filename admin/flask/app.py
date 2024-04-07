from flask import Flask

from home import home_bp
from contact import contact_bp

app = Flask(__name__)

app.register_blueprint(home_bp, url_prefix='/home')
app.register_blueprint(contact_bp, url_prefix='/contact')

app.logger.debug('This is a DEBUG message')
app.logger.info('This is an INFO message')
app.logger.warning('This is a WARNING message')
app.logger.error('This is an ERROR message')

@app.before_request
def before():
    print("This is executed BEFORE each request.")
    
@app.route('/hello/')
def hello():
    return "Hello World!"

@app.route('/<int:number>/')
def incrementer(number):
    return "Incremented number is " + str(number+1)


@app.route('/person/')
def person():
    return jsonify({
        'name':'Taiwo',
        'address': 'WI'
    })

@app.route('/numbers/')
def print_list():
    return jsonify(list(range(5)))


@app.route('/teapot/')
def teapot():
    return "Would you like some tea?", 418

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)