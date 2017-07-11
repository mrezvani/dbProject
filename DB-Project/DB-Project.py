
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

@app.route('/new-problem-search')
def new_problem_search():


    text = ""
    text += "<a href=" + "/search-problem>" + "go to search page" + "</a>"
    text += "your question is: <br>"
    text += '<p name="problemtitle">' + request.values['problem'] + '</p>'
    text += "<br><br><br>"


    db.problems.create_index([('keys',pymongo.TEXT)])
    keywordList = db.problems.find({'$text': {'$search': request.values['keys']}}, {'score' : {'$meta' : 'textScore'}}).sort([('score' , {'$meta' : 'textScore'})])


    text += "Did you mean...? <br><br>"
    i=0

    for iterator in keywordList:
        i += 1
        text +=  "<a" + " href=/" + "full-problem/" + str(iterator['id']) + ">" + "<p name=" + "\"" + "P" + str(i) + "\"" + ">" + iterator['problem'] + "</p>" + "</a>"
    text += """<form action="/new-problem-submit">
    <input type="hidden" name="problem"  value=%s>
    <input type="hidden" name="keys"  value=%s>
     <input type="submit" value="No">
     </form>""" % (request.values['problem'],request.values['keys'])

    return text


@app.route('/new-problem-submit')
def new_problem_submit():

    idTemp = db.problems.find().sort([("id", pymongo.ASCENDING)])
    for i in idTemp:
        idTemp = i['id']
    idTemp += 1
    id = idTemp
    problem = request.values['problem']


    keys = request.values['keys'].split(" ")
    answers = [{'id' : 0 , 'text' : 'first_id', 'creator' : 'admin', 'likedBy':[], 'dislikeBy':[]}]
    comments = [{'id' : 0 , 'text' : 'first_id', 'creator' : 'admin', 'likedBy':[], 'dislikeBy':[]}]
    creator = request.cookies['username']
    likedBy = []
    dislikedBy = []

    db.problems.insert({'problem': problem, 'keys': keys, 'answers': answers, 'comments': comments, 'creator': creator, 'id': id, 'likedBy': likedBy, 'dislikedBy': dislikedBy })

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
        thisLikedBy = j['likedBy']
        thisdisLikedBy = j['dislikedBy']

    text = ""

    text += "<a href=" + "/search-problem>" + "go to search page" + "</a>"

    text += '<br><br>'

    text += 'Problem : '
    text += thisProblem

    if (request.cookies['username'] == thisCreator):
        text += " <a href=" + "/delete-problem/" + str(i) + ">" + "delete" + "</a>"
        text += " <a href=" + "/edit-problem/" + str(i) + ">" + "edit" + "</a>"
        text += " <a href=" + "/like-problem/" + str(i) + ">" + "like" + "</a>"
        text += " <a href=" + "/dislike-problem/" + str(i) + ">" + "dislike" + "</a>"
        if request.cookies['username'] in thisLikedBy:
            text += "   |  liked by you"
        elif request.cookies['username'] in thisdisLikedBy:
            text += "   |  disliked by you"



    text += '<br><br>'

    text += 'Comment:'

    text += '<br><br>'


    temp = "no comment"
    j = 0
    for iterator in thisComments:
        if (j == 0):
            temp = ""
            j += 1
        temp += str(iterator['text'])
        if (iterator['creator'] == request.cookies['username']):
            temp += " <a href=" + "/delete-comment/" + str(i) + "/" + str(iterator['id']) + ">" + "delete" + "</a>"
            temp += " <a href=" + "/edit-comment/" + str(i) + "/" + str(iterator['id']) + ">" + "edit" + "</a>"
            temp += " <a href=" + "/like-comment/" + str(i) + "/" + str(iterator['id']) + ">" + "like" + "</a>"
            temp += " <a href=" + "/dislike-comment/" + str(i) + "/" + str(iterator['id']) + ">" + "dislike" + "</a>"
            if request.cookies['username'] in iterator['likedBy']:
                temp += "   |  liked by you"
            elif request.cookies['username'] in iterator['dislikedBy']:
                temp += "   |  disliked by you"
        temp += '<br>'

    text += temp

    text += "<form action=/comment-submit/" + str(i) + ">" + "<input type=\"text\" name=\"comment\"> <br>" + "<input type=\"submit\" value=\"Submit\">" + "</form>"

    text += '<br><br>'
    text += 'Answer:'



    text += '<br><br>'

    temp = "no answer"
    j = 0
    for iterator in thisAnswer:
        if (j == 0):
            temp=""
            j += 1
        temp += str(iterator['text'])
        if (iterator['creator'] == request.cookies['username']):
            temp += " <a href=" + "/delete-answer/" + str(i) + "/" + str(iterator['id']) + ">" + "delete" + "</a>"
            temp += " <a href=" + "/edit-answer/" + str(i) + "/" + str(iterator['id']) + ">" + "edit" + "</a>"
            temp += " <a href=" + "/like-answer/" + str(i) + "/" + str(iterator['id']) + ">" + "like" + "</a>"
            temp += " <a href=" + "/dislike-answer/" + str(i) + "/" + str(iterator['id']) + ">" + "dislike" + "</a>"
            if request.cookies['username'] in iterator['likedBy']:
                temp += "   |  liked by you"
            elif request.cookies['username'] in iterator['dislikedBy']:
                temp += "   |  disliked by you"
        temp += '<br>'

    text += temp



    text += "<form action=/answer-submit/" + str(i) + ">" + "<input type=\"text\" name=\"answer\"> <br>" + "<input type=\"submit\" value=\"Submit\">" + "</form>"



    return text


@app.route('/like-problem/<i>')
def like_problem(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for i in question:
        question = i

    liked = question['likedBy']
    disliked = question['dislikedBy']

    if request.cookies['username'] in disliked:
        disliked.remove(request.cookies['username'])

    if request.cookies['username'] not in liked:
        liked.append(request.cookies['username'])

    question = db.problems.update({'id': a}, {'$set': {'likedBy': liked, 'dislikedBy': disliked}})

    return render_template("search-problem.html")

@app.route('/dislike-problem/<i>')
def dislike_problem(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for i in question:
        question = i

    disliked = question['dislikedBy']
    liked = question['likedBy']

    if request.cookies['username'] in liked:
        liked.remove(request.cookies['username'])

    if request.cookies['username'] not in disliked:
        disliked.append(request.cookies['username'])

    question = db.problems.update({'id': a}, {'$set': {'likedBy': liked, 'dislikedBy': disliked}})

    return render_template("search-problem.html")


@app.route('/delete-problem/<i>')
def delete_problem(i):
    a = int(i)

    db.problems.remove({'id': a})

    return render_template("search-problem.html")

@app.route('/edit-problem/<i>')
def edit_problem(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for i in question:
        question = i

    keys = ""
    for i in question['keys']:
        keys += i + " "


    return """<form action="/edit-problem-submit/%d">

                Problem: <br>
                <textarea rows="5" cols="50" name="problem">%s</textarea>
                <br>

                Keys: <br>
                <textarea rows="5" cols="50" name="keys">%s</textarea>

                <br><br>
                <input type="submit" value="Submit">

            </form>""" % (a, question['problem'], keys)


@app.route('/edit-problem-submit/<i>')
def edit_problem_submit(i):
    a = int(i)

    db.problems.update({'id': a}, {'$set': {'problem': request.values['problem'], 'keys': request.values['keys'].split(" ")}})

    return render_template("search-problem.html")

@app.route('/like-answer/<i>/<j>')
def like_answer(i, j):
    a = int(i)
    b = int(j)

    question = db.problems.find({'id': a})

    for i in question:
        question = i

    thisAnswer = question['answers']

    thisAnswerArray = []
    for iterator in thisAnswer:
        if (iterator['id'] == b):
            liked = iterator['likedBy']
            disliked = iterator['dislikedBy']

            if request.cookies['username'] in disliked:
                disliked.remove(request.cookies['username'])

            if request.cookies['username'] not in liked:
                liked.append(request.cookies['username'])
        thisAnswerArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'answers': thisAnswerArray}})

    return render_template("search-problem.html")

@app.route('/dislike-answer/<i>/<j>')
def dislike_answer(i, j):
    a = int(i)
    b = int(j)

    question = db.problems.find({'id': a})

    for i in question:
        question = i

    thisAnswer = question['answers']

    thisAnswerArray = []
    for iterator in thisAnswer:
        if (iterator['id'] == b):
            liked = iterator['likedBy']
            disliked = iterator['dislikedBy']

            if request.cookies['username'] not in disliked:
                disliked.append(request.cookies['username'])

            if request.cookies['username'] in liked:
                liked.remove(request.cookies['username'])
        thisAnswerArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'answers': thisAnswerArray}})

    return render_template("search-problem.html")




@app.route('/edit-answer/<i>/<j>')
def edit_answer(i, j):
    a = int(i)
    b = int(j)
    question = db.problems.find({'id': a})

    for i in question:
        question = i

    thisAnswer = question['answers']

    thisAnswerArray = []
    for iterator in thisAnswer:
        if (iterator['id'] == b):
            thisAnswer = iterator

    return """<form action="/edit-answer-submit/%d/%d">

                    Edit answer: <br>
                    <textarea rows="5" cols="50" name="answer">%s</textarea>
                    <br>

                    <br><br>
                    <input type="submit" value="Submit">

                </form>""" % (a, b, thisAnswer['text'])

@app.route('/edit-answer-submit/<i>/<j>')
def edit_answer_submit(i, j):
    a = int(i)
    b = int(j)
    question = db.problems.find({'id': a})

    for i in question:
        question = i

    thisAnswer = question['answers']

    thisAnswerArray = []
    for iterator in thisAnswer:
        if (iterator['id'] != b):
            thisAnswerArray.append(iterator)
        else:
            iterator['text'] = request.values['answer']
            thisAnswerArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'answers': thisAnswerArray}})
    return "answer edited"


@app.route('/delete-answer/<i>/<j>')
def delete_answer(i, j):
    a = int(i)
    b = int(j)
    question = db.problems.find({'id': a})

    for i in question:
        question = i

    thisAnswer = question['answers']

    thisAnswerArray = []
    for iterator in thisAnswer:
        if (iterator['id'] != b):
            thisAnswerArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'answers': thisAnswerArray}})

    return "answer deleted"

@app.route('/like-comment/<i>/<j>')
def like_comment(i, j):
    a = int(i)
    b = int(j)

    question = db.problems.find({'id': a})

    for i in question:
        question = i

    thisComment = question['comments']

    thisCommentArray = []
    for iterator in thisComment:
        if (iterator['id'] == b):
            liked = iterator['likedBy']
            disliked = iterator['dislikedBy']

            if request.cookies['username'] in disliked:
                disliked.remove(request.cookies['username'])

            if request.cookies['username'] not in liked:
                liked.append(request.cookies['username'])
        thisCommentArray.append(iterator)

    question = db.problems.update({'id': a}, {'$set': {'comments': thisCommentArray}})

    return render_template("search-problem.html")

@app.route('/dislike-comment/<i>/<j>')
def dislike_comment(i, j):
    a = int(i)
    b = int(j)

    question = db.problems.find({'id': a})

    for i in question:
        question = i

    thisComment = question['comments']

    thisCommentArray = []
    for iterator in thisComment:
        if (iterator['id'] == b):
            liked = iterator['likedBy']
            disliked = iterator['dislikedBy']

            if request.cookies['username'] not in disliked:
                disliked.append(request.cookies['username'])

            if request.cookies['username'] in liked:
                liked.remove(request.cookies['username'])
        thisCommentArray.append(iterator)

    question = db.problems.update({'id': a}, {'$set': {'comments': thisCommentArray}})

    return render_template("search-problem.html")


@app.route('/edit-comment/<i>/<j>')
def edit_comment(i, j):
    a = int(i)
    b = int(j)
    question = db.problems.find({'id': a})

    for i in question:
        question = i

    thisComment = question['comments']

    thisCommentArray = []
    for iterator in thisComment:
        if (iterator['id'] == b):
            thisComment = iterator

    return """<form action="/edit-comment-submit/%d/%d">

                    Edit comment: <br>
                    <textarea rows="5" cols="50" name="comment">%s</textarea>
                    <br>

                    <br><br>
                    <input type="submit" value="Submit">

                </form>""" % (a, b, thisComment['text'])

@app.route('/edit-comment-submit/<i>/<j>')
def edit_comment_submit(i, j):
    a = int(i)
    b = int(j)
    question = db.problems.find({'id': a})

    for i in question:
        question = i

    thisComment = question['comments']

    thisCommentArray = []
    for iterator in thisComment:
        if (iterator['id'] != b):
            thisCommentArray.append(iterator)
        else:
            iterator['text'] = request.values['comment']
            thisCommentArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'comments': thisCommentArray}})
    return "comment edited"


@app.route('/delete-comment/<i>/<j>')
def delete_comment(i, j):
    a = int(i)
    b = int(j)
    question = db.problems.find({'id': a})

    for i in question:
        question = i

        thisComment = question['comments']

    thisCommentArray = []
    for iterator in thisComment:
        if (iterator['id'] != b):
            thisCommentArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'comments': thisCommentArray}})

    return "comment deleted"


@app.route('/answer-submit/<i>')
def answer_sumbit(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for i in question:
        question = i


    for j in question['answers']:
        lastAnswer = j

    id = lastAnswer['id'] + 1


    question['answers'].append({'id' : id, 'text' : request.values['answer'], 'comments' : [], 'creator': request.cookies['username'], 'likedBy': [], 'dislikedBy': []})

    db.problems.update({'id': a}, {'$set' : {'answers' : question['answers']}})



    return "answer added"


@app.route('/comment-submit/<i>')
def comment_sumbit(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for i in question:
        question = i


    for j in question['comments']:
        lastComment = j

    id = lastComment['id'] + 1



    question['comments'].append({'id' : id, 'text' : request.values['comment'], 'creator': request.cookies['username'], 'likedBy': [], 'dislikedBy': []})

    db.problems.update({'id': a}, {'$set' : {'comments' : question['comments']}})



    return "comment added"


if __name__ == '__main__':
    # print(db.problems.ensureIndex())
    app.debug = True
    # app.run()
    app.run("0.0.0.0", 5000)


 # 'firstname':request.values['firstname'] , 'lastname': request.values['lastname']
