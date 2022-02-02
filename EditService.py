from configparser import RawConfigParser
from DocumentGenerator import DocumentGenerator
import flask
import base64
from waitress import serve

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Simple edition service</h1><p>Create pdf and docx from docx templates with jinja2 tags.</p>"

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Not found.</p>", 404

@app.route('/edit/', methods=['POST'])
def editDocument():
    #Get parameters
    params = flask.request.json
    
    if not params is None and not params["data"] is None:
        data = params["data"]
    else:
        data = {}
    
    mode     = params["mode"]
    template = params["template"]
    output   = params["fileName"]
    
    #Create document according to params
    if mode == 'print' or mode == 'email' or mode == 'file' :
        gen = DocumentGenerator(config)
        if output.endswith('.docx') :
            output = gen.docxFromTemplate(template, output,  data)
        elif output.endswith('.pdf') :
            output = gen.pdfFromTemplate(template, output,  data)
        elif output.endswith('.html') or output.endswith('.htm') :
            output = gen.htmlFromTemplate(template, output,  data)
        else :
            output = ''

    #prepare response with or without data
    wsResponse = flask.jsonify({'result':output})
    if mode == 'file' :
        with open(output, 'rb') as f:
            fileData = f.read()
            fileDataB64 = base64.b64encode(fileData)
            wsResponse = flask.jsonify({'result':output, 'file':fileDataB64.decode("utf-8")})
    
    return wsResponse, 200

if __name__ == "__main__":
    config = RawConfigParser()
    config.read(r'./config.txt')
    
    serve(app, host='0.0.0.0', port=5000)