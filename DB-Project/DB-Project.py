
from flask import make_response,Flask
from flask.globals import request
from flask.templating import render_template
import pymongo
from pymongo import MongoClient
from werkzeug.debug import console
from bson import ObjectId

client = MongoClient()

client = MongoClient('localhost', 27017)

app = Flask(__name__)

db = client['DB-Project']

collection = db.users

db.problems.insert({'id' : 0})

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
            resp = make_response(render_template('search-after-login.html', username = request.values['username']))
            resp.set_cookie('username', request.values['username'])

            return resp
        else:
            return 'uncorrect password'

    return 'incorrect username'



@app.route('/new-problem')
def new_problem():
    return render_template('new-problem.html')

@app.route('/new-problem-submit')
def new_problem_submit():
    idTemp = db.problems.find().sort([("id", pymongo.ASCENDING)])
    for i in idTemp:
        idTemp = i['id']
    idTemp += 1
    id = idTemp
    problem = request.values['problem']
    keys = request.values['keys'].split(" ")
    answers = []
    comments = []
    creator = request.cookies['username']

    db.problems.insert({'problem': problem, 'keys': keys, 'answers': answers, 'comments': comments, 'creator': creator, 'id': id})

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

    db.problems.create_index([('keys',pymongo.TEXT)])
    keywordList = db.problems.find({'$text': {'$search': request.values['search']}}, {'score' : {'$meta' : 'textScore'}}).sort([('score' , {'$meta' : 'textScore'})])

    text = ""
    i=0
    text += "<a href=" + "search-problem>" + "go to search page" + "</a>"
    for iterator in keywordList:
        i += 1
        text = text + "<a" + " href=/" + "full-problem/" + str(iterator['id']) + ">" + "<p name=" + "\"" + "P" + str(i) + "\"" + ">" + iterator['problem'] + "</p>" + "</a>"

    return text

@app.route('/full-problem/<i>')
def full_problem(i):
    # return str(i)
    a = int(i)

    question = db.problems.find({'id': a})

    for j in question:
        thisProblem = j['problem']
        thisComments = j['comments']
        thisCreator = j['creator']
        thisAnswer = j['answers']

    text = ""

    text += "<a href=" + "/search-problem>" + "go to search page" + "</a>"

    text += '<br><br>'

    text += 'Problem : '
    text += thisProblem

    if (request.cookies['username'] == thisCreator):
        text += " <a href=" + "/delete-problem/" + str(i) + ">" + "delete" + "</a>"


    text += '<br><br>'

    text += 'Comment:'

    text += '<br><br>'

    for iterator in thisComments:
        text += str(iterator) + '<br>'

    text += '<br><br>'
    text += 'Answer:'

    text += '<br><br>'

    temp = "no answer"
    j = 0
    for iterator in thisAnswer:
        if (j==0):
            temp=""
            j+=1
        temp += str(iterator['text'])
        if (iterator['creator'] == request.cookies['username']):
            temp += " <a href=" + "/delete-answer>" + "delete" + "</a>" + '<br>'

    text += temp



    text += "<form action=/answer-submit/" + str(i) + ">" + "<input type=\"text\" name=\"answer\"> <br>" + "<input type=\"submit\" value=\"Submit\">" + "</form>"



    return text

@app.route('/delete-problem/<i>')
def delete_problem(i):
    a = int(i)

    question = db.problems.remove({'id': a})

    return render_template("search-problem.html")


@app.route('/delete-answer/<i>')
def delete_answer(i):
    a = int(i)

    question = db.problems.find({'id': a})

    return "x"

@app.route('/answer-submit/<i>')
def answer_sumbit(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for i in question:
        question = i

    question['answers'].append({'text' : request.values['answer'], 'comments' : [], 'creator': request.cookies['username']})

    db.problems.update({'id': a}, {'$set' : {'answers' : question['answers']}})



    return "answer added"



if __name__ == '__main__':
    # print(db.problems.ensureIndex())
    app.debug = True
    app.run()


 # 'firstname':request.values['firstname'] , 'lastname': request.values['lastname']
