'''
This is multithreading simple HTTp server which can serve requests for GET, POST, PUT and DELETE.
The routes are specified using decorator pattern. The routes are automatically registered when the program spins up. 
The first parameter of every route is the query string or the body. 
'''
from http.server import BaseHTTPRequestHandler
from urllib import parse
import json
import cgi
import io
'''
These are the mapper being used when the registration takes place. 
The same mapper is being used by the base HTTP handler. Thus this has to be in the global scope
'''
POST_METHOD_MAP={}
GET_METHOD_MAP={}
DELETE_METHOD_MAP={}
PUT_METHOD_MAP={}
'''
The decorator which is used to register the routes and pass the parameter to the target function. 

'''

def route(routeString,methods=["GET"]):
    def routeEncloser(func):
        for methodType in methods:
            if(methodType=="POST"):
                POST_METHOD_MAP[routeString]=func
            elif(methodType=="GET"):
                GET_METHOD_MAP[routeString]=func
            elif(methodType=="DELETE"):
                DELETE_METHOD_MAP[routeString]=func
            elif(methodType=="PUT"):
                PUT_METHOD_MAP[routeString]=func
        def executor(*args,**kwargs):
            return func(*args,**kwargs)
        return executor
    return routeEncloser

'''
A simple HTTP Server which has the basic REST API Methods
'''
class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        body={}
        headers={}
        parsed_path = parse.urlparse(self.path)
        if(parsed_path.path in GET_METHOD_MAP):
            queryString={}
            for x in parsed_path.query.split('&'):
                y=x.split("=")
                if(len(y)>=2):
                    queryString[y[0]]=y[1]
            content=GET_METHOD_MAP[parsed_path.path](queryString,body,headers)
            self.send_response(200)
            self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
            self.end_headers()
            content=json.dumps({'err':True,'message':'Route is Missing'})
            self.wfile.write(content.encode('utf-8'))

    def do_DELETE(self):
        body={}
        headers={}
        parsed_path = parse.urlparse(self.path)
        if(parsed_path.path in DELETE_METHOD_MAP):
            queryString={}
            for x in parsed_path.query.split('&'):
                y=x.split("=")
                if(len(y)>=2):
                    queryString[y[0]]=y[1]
            content=DELETE_METHOD_MAP[parsed_path.path](queryString,body,headers)
            self.send_response(200)
            self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
            self.end_headers()
            content=json.dumps({'err':True,'message':'Route is Missing'})
            self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
        queryString={}
        headers={}
        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': self.headers['Content-Type'],
            }
        )
        # Begin the response
        self.send_response(200)
        self.send_header('Content-Type',
                         'text/plain; charset=utf-8')
        self.end_headers()

        out = io.TextIOWrapper(
            self.wfile,
            encoding='utf-8',
            line_buffering=False,
            write_through=True,
        )
        if(self.path in POST_METHOD_MAP):
            body={}
            for field in form.keys():
                field_item = form[field]
                if field_item.filename:
                    ################ Yet to be implemented
                    # The field contains an uploaded file
                    file_data = field_item.file.read()
                    file_len = len(file_data)
                    del file_data
                    out.write(
                        '\tUploaded {} as {!r} ({} bytes)\n'.format(
                            field, field_item.filename, file_len)
                    )
                else:
                    body[field]=form[field].value
            content=POST_METHOD_MAP[self.path](queryString,body,headers)
            out.write(content)
        else:
            out.write(json.dumps({"err":True,"message":"The Routw is not defiend"}))
        out.detach()

'''
Sample Decorator based route defination. The first parameter of the target function contains the query string.
The decorators takes the following parameter. 
1) Route URL
2) Methods allowed in a list format
'''
@route('/helloworld',methods=["GET"])
def me(query,body,headers):
    print ("QueryString is",body)
    return json.dumps({'err':False,'message':'Hello World'})

'''
Select the port and a IP for local or public facing
'''
if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 5001), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()

'''
#Things to do:
1) Fetch Header as dictionary and pass to the function
2) fetch queryString for post requests and pass to the functions
'''