
from flask import Flask
from flask.globals import request
from flask.templating import render_template

from pymongo import MongoClient
from werkzeug.debug import console

client = MongoClient()

client = MongoClient('localhost', 27017)

app = Flask(__name__)

db = client['DB-Project']

collection = db.users


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test1')
def hello_world():
    db.users.insert({'name':{'firstname' : request.values['firstname'] , 'lastname' : request.values['lastname']}})
    return render_template('page2.html', firstname = request.values['firstname'], lastname = request.values['lastname'])

@app.route('/sign-up')
def sign_up():
    return render_template('sign-up.html')


@app.route('/sign-up-submit')
def sign_up_submit():
    name = request.values['name']
    username = request.values['username']
    email = request.values['email']
    password = request.values['password']
    point = 0
    image = request.values['image']

    favorite = request.values.getlist('favorite')

    temp = db.users.find({'$or':[{'username' : username},{'email': email}]})

    for i in temp:
        return "not OK"
    else:
        db.users.insert({'name': name, 'username': username, 'email': email, 'password': password, 'point': point, 'image': image, 'favorite': favorite})
        return "OK"

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login-submit')
def login_submit():
    person = db.users.find({'username' : request.values['username']})

    for i in person:
        if (request.values['password'] == i['password']):
            return 'correct password'
        else:
            return 'uncorrect password'

    return 'incorrect username'

@app.route('/new-problem')
def new_problem():
    return render_template('new-problem.html')

@app.route('/new-problem-submit')
def new_problem_submit():
    problem = request.values['problem']
    keys = request.values['keys'].split(" ")
    answers = {'text' : "", 'comment' : [], 'point':0, 'creator': ''}
    comment = []
    creator = ''

    db.problems.insert({'problem': problem, 'keys': keys, 'answers': answers, 'comment': comment, 'creator': creator})

    return "problem added"

@app.route('/search-problem')
def search_problem():
    return render_template('search-problem.html')

@app.route('/search-problem-submit')
def search_problem_submit():
    # keywordList = db.problems.find({'keys' : { '$in' : request.values['search'].split(" ")}})
    #
    # temp= "ali"
    # for i in keywordList:
    #     temp  = i['problem']
    # db.problems.create_index({'keys': "text"})
    db.problems.create_index('keys')

    keywordList = db.problems.find({ '$text': { '$search': request.values['search']}},{'score': { '$meta': "textScore"}}).sort([('score', { '$meta': "textScore"})])

    temp = "not"
    for i in keywordList:
        temp  = i['problem']
        print(temp)


if __name__ == '__main__':
    # print(db.problems.ensureIndex())
    app.debug = True
    app.run()


 # 'firstname':request.values['firstname'] , 'lastname': request.values['lastname']
