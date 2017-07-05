import flask from Flask

@app.route('/')
def index
	return "hello_world"


if __name__ == '__main__'
	app.debug = True
	app.run()