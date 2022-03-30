from configparser import RawConfigParser
from DocumentGenerator import DocumentGenerator
from MailService import Mailer
from os import path
from waitress import serve
import flask
import base64

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def checkParams(params):
    if not ("mode" in params and "template" in params and "fileName" in params):
        return False, "Parameters mode, templace and fileName needed"
    
    if params["mode"] == 'email' and not("mail_template" in params and "mail_to" in params and "mail_subject" in params): 
        return False, "If mode mail, parameters mail_template, mail_subject and mail_to needed"
    
    return True, ''
    

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
    
    valid, error = checkParams(params)
    if not valid:
        wsResponse = flask.jsonify({'error':error})
        return wsResponse, 500
    
    if not params is None and not params["data"] is None:
        data = params["data"]
    else:
        data = {}
    
    mode     = params["mode"]
    template = params["template"]
    output   = params["fileName"]
    out_file = ""
    
    #Create document according to params
    if mode == 'print' or mode == 'email' or mode == 'file' :
        gen = DocumentGenerator(config)
        if output.endswith('.docx') :
            out_file = gen.docxFromTemplate(template, output,  data)
        elif output.endswith('.pdf') :
            out_file = gen.pdfFromTemplate(template, output,  data)
        elif output.endswith('.html') or output.endswith('.htm') :
            out_file = gen.htmlFromTemplate(template, output,  data)
    
    #prepare response with or without data
    wsResponse = flask.jsonify({'result':output})
    if mode == 'file' :
        with open(out_file, 'rb') as f:
            fileData = f.read()
            fileDataB64 = base64.b64encode(fileData)
            wsResponse = flask.jsonify({'result':out_file, 'file':fileDataB64.decode("utf-8")})
    
    #Send email if selected mode is email
    if mode == 'email' :
        mail_content     = ''
        mail_template    = params["mail_template"]
        mail_to          = params["mail_to"]
        mail_subject     = params["mail_subject"]
        if mail_template.endswith('.html') or mail_template.endswith('.htm'):
            mail_output  = path.join(config.get('FileSystem', 'models'), mail_template)
        else:
            mail_output  = gen.htmlFromTemplate(mail_template, output+'.mail.html', data)
        
        with open(mail_output, "r", encoding="utf-8") as html_file:
            mail_content = html_file.read()
        
        mail = Mailer(config)
        mail.sendMail(mail_to, mail_subject, mail_content, out_file)
    
    return wsResponse, 200

if __name__ == "__main__":
    config = RawConfigParser()
    config.read(r'./config.txt')
    
    serve(app, host='0.0.0.0', port=path.join(config.get('Service', 'port')))