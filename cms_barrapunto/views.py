from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import urllib.request
from cms_barrapunto.models import Pages
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
# Create your views here.

content_rss = ""


class myContentHandler(ContentHandler):
    def __init__(self):
            self.inItem = False
            self.inContent = False
            self.theContent = ""

    def startElement(self, name, attrs):
        if name == 'item':
            self.inItem = True
        elif self.inItem:
            if name == 'title':
                self.inContent = True
            elif name == 'link':
                self.inContent = True

    def endElement(self, name):
        global content_rss
        if name == 'item':
            self.inItem = False
        elif self.inItem:
            if name == 'title':
                self.titulo = self.theContent
                self.inContent = False
                self.theContent = ""
            elif name == 'link':
                self.link = self.theContent
                content_rss += ("\t\t\t<li><a href='" + self.link + "'>" +
                                self.titulo + "</a></li>\n")
                self.inContent = False
                self.theContent = ""

    def characters(self, chars):
        if self.inContent:
            self.theContent = self.theContent + chars


def show(request):
    response = "Listado de las paginas que tienes guardadas. "
    lista_paginas = Pages.objects.all()
    for pagina in lista_paginas:
        response += "<br>" + pagina.name
    return HttpResponse(response)


@csrf_exempt
def process(request, resource):
    if request.method == "GET":
        try:
            page = Pages.objects.get(name=resource)
            response = "<html><body><div>La página solicitada es: "
            response += page.name + " -> " + page.page + "</div><div>"
            response += "<br>Titulares de barrapunto.com:<br>"
            response += content_rss + "</div></body></html>"
        except Pages.DoesNotExist:
            response = "La página no existe. Puedes crearla:"
            response += "<form action='/" + resource + "' method=POST>"
            response += "Nombre: <input type='text' name='nombre'>"
            response += "<br>Página: <input type='text' name='page'>"
            response += "<input type='submit' value='Enviar'></form>"
    elif request.method == "POST":
        nombre = request.POST['nombre']
        page = request.POST['page']
        pagina = Pages(name=nombre, page=page)
        pagina.save()
        response = "Has creado la página " + nombre
    elif request.method == "PUT":
        try:
            page = Pages.objects.get(name=resource)
            response = "Ya existe una página con ese nombre"
        except Pages.DoesNotExist:
            page = request.body
            pagina = Pages(name=resource, page=page)
            pagina.save()
            response = "Has creado la página " + resource
    else:
        response = "Error. Method not supported."
    return HttpResponse(response)


def update(request):
    # detecto update
    theParser = make_parser()
    theHandler = myContentHandler()
    theParser.setContentHandler(theHandler)

    xmlFile = urllib.request.urlopen("http://barrapunto.com/index.rss")
    theParser.parse(xmlFile)

    respuesta = ("<html><body><div>Contenido de barrapunto: " + content_rss +
                 "</div></body></html>")
    return HttpResponse(respuesta)
