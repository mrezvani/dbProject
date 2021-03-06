
from flask import make_response,Flask,redirect, url_for
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

##################################################################

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
            return render_template('login.html', message='Incorrect password')
    return render_template('login.html', message='incorrect username')

##################################################################

@app.route('/new-problem-search')
def new_problem_search():


    text = ""
    text += "<a href=" + "/search-problem>" + "go to search page" + "</a>" + "<br>"



    db.problems.create_index([('keys',pymongo.TEXT)])
    keywordList = db.problems.find({'$text': {'$search': request.values['keys']}}, {'score' : {'$meta' : 'textScore'}}).sort([('score' , {'$meta' : 'textScore'})])


    text += "<br><br><br>Did you mean...? "
    i=0

    for iterator in keywordList:
        i += 1
        text +=  "<a" + " href=/" + "full-problem/" + str(iterator['id']) + ">" + "<p name=" + "\"" + "P" + str(i) + "\"" + ">" + iterator['problem'] + "</p>" + "</a>"

    text += "your question is: <br>"

    text += """<form action="/new-problem-submit"> <textarea readonly rows="5" cols="50" name="problem">%s</textarea>
                        <br>

                        Keys: <br>
                        <textarea readonly rows="5" cols="50" name="keys">%s</textarea> <br> <input type="submit" value="No"> </form>""" % (
        request.values['problem'], request.values['keys'])

    return text

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
    answers = [{'id' : 0 , 'text' : 'no answer', 'creator' : 'admin', 'likedBy':[], 'dislikedBy':[], 'comments':[{'id' : 0 , 'text' : 'no comment for answer', 'creator' : 'admin'}]}]
    comments = [{'id' : 0 , 'text' : 'no comment', 'creator' : 'admin', 'likedBy':[], 'dislikedBy':[]}]
    creator = request.cookies['username']
    likedBy = []
    dislikedBy = []

    db.problems.insert({'problem': problem, 'keys': keys, 'answers': answers, 'comments': comments, 'creator': creator, 'id': id, 'likedBy': likedBy, 'dislikedBy': dislikedBy })

    return "problem added"

##################################################################

@app.route('/search-problem')
def search_problem():
    return render_template('search-problem.html')

@app.route('/search-problem-submit')
def search_problem_submit():

    db.problems.create_index([('keys',pymongo.TEXT)])
    keywordList = db.problems.find({'$text': {'$search': request.values['search']}}, {'score' : {'$meta' : 'textScore'}}).sort([('score' , {'$meta' : 'textScore'})])

    text = ""
    i=0
    text += "<a href=" + "search-problem>" + "go to search page" + "</a>"
    for iterator in keywordList:
        i += 1
        text = text + "<a" + " href=/" + "full-problem/" + str(iterator['id']) + ">" + "<p name=" + "\"" + "P" + str(i) + "\"" + ">" + iterator['problem'] + "</p>" + "</a>"

    return text

##################################################################

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


    temp = ""
    j = 0
    for iterator in thisComments:
        if (j <= 1):
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

    temp = ""
    j = 0
    for iterator in thisAnswer:
        if (j <= 1):
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
        temp2 = ""
        k = 0
        if j != 1:
            for commentIterator in iterator['comments']:
                if (k <= 1):
                    temp2 = ""
                    k += 1
                temp2 += str(commentIterator['text'])
                if (commentIterator['creator'] == request.cookies['username']):
                    temp2 += " <a href=" + "/delete-answer-comment/" + str(i) + "/" + str(iterator['id']) + "/" + str(commentIterator['id']) + ">" + "delete" + "</a>"
                    temp2 += " <a href=" + "/edit-answer-comment/" + str(i) + "/" + str(iterator['id']) + "/" + str(commentIterator['id']) + ">" + "edit" + "</a>"

                temp2 += '<br>'
            temp += temp2
            temp += " <a href=" + "/comment-answer/" + str(i) + "/" + str(iterator['id']) + ">" + "comment for answer" + "</a>"

            temp += "<br><br>"

    text += temp



    text += "<form action=/answer-submit/" + str(i) + ">" + "<input type=\"text\" name=\"answer\"> <br>" + "<input type=\"submit\" value=\"Submit\">" + "</form>"



    return text

###############################################################

@app.route('/all-problem')
def all_problem():
    # question = db.problems.find({'id': 1})
    question = db.problems.find({"id": { "$gt" : 0}} )
    # question = db.problems.find({})

    text = ""
    i = 0
    text += "<a href=" + "search-problem>" + "go to search page" + "</a><br>"
    for iterator in question:
        i += 1
        text = text + "<a" + " href=/" + "full-problem/" + str(iterator['id']) + ">" + "<p name=" + "\"" + "P" + str(
            i) + "\"" + ">" + iterator['problem'] + "</p>" + "</a>"

    return text

    return render_template('new-problem.html')



##################################################################

@app.route('/edit-answer-comment/<i>/<j>/<k>')
def edit_answer_comment(i,j,k):
    a = int(i)
    b = int(j)
    c = int(k)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp
    thisAnswer = question['answers']

    for iterator in thisAnswer:
        if (iterator['id'] == b):
            for iterator2 in iterator['comments']:
                if (iterator2['id'] == c):
                    result = iterator2['text']


    return render_template('edit-answer-comment-submit.html', i=i, j=j, k=k, oldComment=result)

@app.route('/edit-answer-comment-submit/<i>/<j>/<k>')
def edit_answer_comment_submit(i,j,k):
    a = int(i)
    b = int(j)
    c = int(k)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp
    thisAnswer = question['answers']
    thisComment = request.values['comment']

    thisAnswerArray = []
    thisCommentArray = []
    for iterator in thisAnswer:
        if (iterator['id'] == b):
            for iterator2 in iterator['comments']:
                if (iterator2['id'] == c):
                    iterator2['text'] = request.values['comment']
                    thisCommentArray.append(iterator2)

            iterator['comments'] = thisCommentArray
        thisAnswerArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'answers': thisAnswerArray}})

    return redirect(url_for('full_problem', i=i))


@app.route('/delete-answer-comment/<i>/<j>/<k>')
def delete_answer_comment(i,j,k):
    a = int(i)
    b = int(j)
    c = int(k)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp
    thisAnswer = question['answers']

    thisAnswerArray = []
    thisCommentArray = []
    for iterator in thisAnswer:
        if (iterator['id'] == b):
            for iterator2 in iterator['comments']:
                if (iterator2['id'] != c):
                    thisCommentArray.append(iterator2)
            iterator['comments'] = thisCommentArray
        thisAnswerArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'answers': thisAnswerArray}})

    return redirect(url_for('full_problem', i=i))


@app.route('/comment-answer/<i>/<j>')
def comment_answer(i,j):


    return render_template('comment-answer.html', i=i, j=j)

@app.route('/comment-answer-submit/<i>/<j>')
def comment_answer_submit(i,j):
    a = int(i)
    b = int(j)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp
    thisAnswer = question['answers']
    thisComment = request.values['comment']


    thisAnswerArray = []
    thisCommentArray = []
    for iterator in thisAnswer:
        if (iterator['id'] == b):
            for iterator2 in iterator['comments']:
                lastComment = iterator2['id']

            iterator['comments'].append({'id' : lastComment+1, 'text': thisComment, 'creator': request.cookies['username']})
        thisAnswerArray.append(iterator)



    db.problems.update({'id': a}, {'$set': {'answers': thisAnswerArray}})

    return redirect(url_for('full_problem', i=i))

##################################################################

@app.route('/like-problem/<i>')
def like_problem(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp

    liked = question['likedBy']
    disliked = question['dislikedBy']

    if request.cookies['username'] in disliked:
        disliked.remove(request.cookies['username'])

    if request.cookies['username'] not in liked:
        liked.append(request.cookies['username'])

    question = db.problems.update({'id': a}, {'$set': {'likedBy': liked, 'dislikedBy': disliked}})

    return redirect(url_for('full_problem', i=i))

@app.route('/dislike-problem/<i>')
def dislike_problem(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp

    disliked = question['dislikedBy']
    liked = question['likedBy']

    if request.cookies['username'] in liked:
        liked.remove(request.cookies['username'])

    if request.cookies['username'] not in disliked:
        disliked.append(request.cookies['username'])

    question = db.problems.update({'id': a}, {'$set': {'likedBy': liked, 'dislikedBy': disliked}})

    return redirect(url_for('full_problem', i=i))


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

##################################################################

@app.route('/like-answer/<i>/<j>')
def like_answer(i, j):
    a = int(i)
    b = int(j)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp

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

    return redirect(url_for('full_problem', i=i))

@app.route('/dislike-answer/<i>/<j>')
def dislike_answer(i, j):
    a = int(i)
    b = int(j)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp

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

    return redirect(url_for('full_problem', i=i))




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


@app.route('/answer-submit/<i>')
def answer_sumbit(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for temp1 in question:
        question = temp1


    for temp2 in question['answers']:
        lastAnswer = temp2

    id = lastAnswer['id'] + 1


    question['answers'].append({'id' : id, 'text' : request.values['answer'], 'comments' : [], 'creator': request.cookies['username'], 'likedBy': [], 'dislikedBy': [], 'comments':[{'id': 0, 'text': 'no comment for answer', 'creator': 'admin'}]})

    db.problems.update({'id': a}, {'$set' : {'answers' : question['answers']}})



    return redirect(url_for('full_problem', i=i))



@app.route('/delete-answer/<i>/<j>')
def delete_answer(i, j):
    a = int(i)
    b = int(j)
    question = db.problems.find({'id': a})

    for temp in question:
        question = temp

    thisAnswer = question['answers']

    thisAnswerArray = []
    for iterator in thisAnswer:
        if (iterator['id'] != b):
            thisAnswerArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'answers': thisAnswerArray}})

    return redirect(url_for('full_problem', i=i))

##################################################################

@app.route('/like-comment/<i>/<j>')
def like_comment(i, j):
    a = int(i)
    b = int(j)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp

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

    return redirect(url_for('full_problem', i=i))

@app.route('/dislike-comment/<i>/<j>')
def dislike_comment(i, j):
    a = int(i)
    b = int(j)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp

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

    return redirect(url_for('full_problem', i=i))


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

    for temp in question:
        question = temp

        thisComment = question['comments']

    thisCommentArray = []
    for iterator in thisComment:
        if (iterator['id'] != b):
            thisCommentArray.append(iterator)

    db.problems.update({'id': a}, {'$set': {'comments': thisCommentArray}})

    return redirect(url_for('full_problem', i=i))




@app.route('/comment-submit/<i>')
def comment_sumbit(i):
    a = int(i)

    question = db.problems.find({'id': a})

    for temp in question:
        question = temp


    for temp2 in question['comments']:
        lastComment = temp2

    id = lastComment['id'] + 1



    question['comments'].append({'id' : id, 'text' : request.values['comment'], 'creator': request.cookies['username'], 'likedBy': [], 'dislikedBy': []})

    db.problems.update({'id': a}, {'$set' : {'comments' : question['comments']}})

    return redirect(url_for('full_problem', i=i))

##################################################################

if __name__ == '__main__':
    # print(db.problems.ensureIndex())
    app.debug = True
    app.run()
    # app.run("0.0.0.0", 5000)

