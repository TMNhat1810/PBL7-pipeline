from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from package.service.version import get_version, change_version
from package.utils.pipeline import start_pipeline
from datetime import date
import threading
import time

app = Flask(__name__)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def root():
    return get_version()

@app.route('/model_version', methods=['POST','OPTIONS'])
@cross_origin()
def change_model_version():
    version = request.json['version']
    status = change_version(version)
    
    if status: return jsonify(success=True, message="version changed successully")
    return jsonify(success=False, message="Internal Server Error")



def thread_pipeline():
    while True:
        version = get_version()
        if version == None:
            print('No model version selected, waiting...')
            time.sleep(5)
        
        else: 
            start_pipeline(date.today(), using_version=version)
            time.sleep(5)
            
thread = threading.Thread(target=thread_pipeline)
thread.start()
