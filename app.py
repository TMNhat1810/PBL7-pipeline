from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from package.service.version import get_version, change_version, get_all_version
from package.service.play_ground import summarizer_available, summarizer_wrapper, load_summarizer
from package.utils.import_db.db import get_version_data, import_version_data, export_feedback_data
# from package.utils.pipeline import start_pipeline
# from datetime import date
# import threading
# import time

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
    return jsonify(success=True, data=get_version())

@app.route('/model_version', methods=['POST','OPTIONS'])
@cross_origin()
def change_model_version():
    version = request.json['version']
    status = change_version(version)
    load_summarizer()
    if status: return jsonify(success=True, message="version changed successully")
    return jsonify(success=False, message="Internal Server Error")

@app.route('/version/all')
@cross_origin()
def get_all_model_version():
    data = get_all_version()
    return jsonify(success=True, data=data)

@app.route('/playground', methods=['POST', 'OPTIONS'])
@cross_origin()
def playground():
    if summarizer_available() == False: return jsonify(success=False, message="Playground is not available")
    
    try:
        text = request.json['text']
        summary = summarizer_wrapper(text)
        return jsonify(success=True, data=summary)
        
    except: return jsonify(success=False, message="Internal Server Error")
    
@app.route('/reload')
@cross_origin()
def reload():
    new_version = get_version_data()
    import_version_data(new_version)
    
    return jsonify(success=True)

@app.route('/export')
@cross_origin()
def export_csv():
    try:
        export_feedback_data()
        return jsonify(success=True)
    except: return jsonify(success=False, message="Internal Server Error")
    
load_summarizer()


# def thread_pipeline():
#     while True:
#         version = get_version()
#         if version == None:
#             print('No model version selected, waiting...')
#             time.sleep(5)
        
#         else: 
#             start_pipeline(date.today(), using_version=version)
#             time.sleep(5)
            
# thread = threading.Thread(target=thread_pipeline)
# thread.start()
