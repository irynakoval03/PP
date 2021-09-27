from flask import Flask
from flask import Response



app=Flask(__name__)

@app.route('/api/v1/hello-world-5')
def hello():
    return Response("Hello word 5", status=200, mimetype='text/plain') 


def create_app():  
    if __name__=="__main__":
        app.run(debug=True,use_reloader = False)
    return app