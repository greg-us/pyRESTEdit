from os import path
from configparser import RawConfigParser
from docxtpl import DocxTemplate
from docx2pdf import convert as convertPDF
from pydocx import PyDocX
import pythoncom

class DocumentGenerator:
    
    def __init__(self, config):
        self.config = config
    
    def pdfFromTemplate(self, template, target, data):
        docXFileName = target + '.docx'
        self.docxFromTemplate(template, docXFileName, data)
        pythoncom.CoInitialize()
        
        convertPDF( path.join(self.config.get('FileSystem', 'spooler'), docXFileName), path.join(self.config.get('FileSystem', 'spooler'), target) )
        
        return path.join(self.config.get('FileSystem', 'spooler'), target)
    
    def docxFromTemplate(self, template, target, data):
        doc = DocxTemplate(path.join(self.config.get('FileSystem', 'models'), template))
        doc.render(data)
        doc.save(path.join(self.config.get('FileSystem', 'spooler'), target))
        
        return path.join(self.config.get('FileSystem', 'spooler'), target)

    def htmlFromTemplate(self, template, target, data):
        docXFileName = target + '.docx'
        self.docxFromTemplate(template, docXFileName, data)
        
        html = PyDocX.to_html(path.join(self.config.get('FileSystem', 'spooler'), docXFileName))
        f = open(path.join(self.config.get('FileSystem', 'spooler'), target), 'w', encoding="utf-8")
        f.write(html)
        f.close()
        
        return path.join(self.config.get('FileSystem', 'spooler'), target)
    