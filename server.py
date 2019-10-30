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
import coro
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

import time

class CoroHTTPServer:
    """Encapsulates a CoroHTTPServer. The class itself does not
    handle anything HTTP-specific but is named as such as the
    class passed to its handle_request is expected to be a
    HTTP Request handler.
    """

    def __init__(self, addr, request_handler_class):
        self.ip, self.port = addr
        self.request_handler_class = request_handler_class
        self.sock = None
        self.local_sock = None
        self.requests = []
        self.thread = None
        self.api_on_localhost, self.local_port  = True,5000
        if self.api_on_localhost:
            self.localhost = "127.0.0.1"
            self.local_thread = None

    def start(self):
        try:
            self.sock = self._make_socket(self.ip)
            self._bind_socket(self.sock, self.ip, self.port)
            #if self.api_on_localhost:
            #   self.local_sock = self._make_socket(self.localhost)
            #    self._bind_socket(self.local_sock, self.localhost, self.local_port)
        # except oserrors.EADDRNOTAVAIL:
        #     # sleep and try once more
        #     coro.sleep_relative(2)
        #     self._bind_socket(self.sock, self.ip, self.port)
        #     if self.api_on_localhost:
        #         self._bind_socket(self.local_sock, self.localhost, self.local_port)
        except Exception as e:
            print ("Error Occured",e)
            coro.print_stderr(e)

        self.thread = self._create_server(self.sock, self.ip, self.port)
        while(True):
            coro.event_loop()
        #if self.api_on_localhost:
        #   self.local_thread = self._create_server(self.local_sock,
        #                                            self.localhost, self.local_port)

    def _make_socket(self, ip):
        #sock = coro.make_socket_for_ip(ip)
        #imsock= coro.make_socket(ip,0)
        sock=coro.tcp_sock()
        sock.set_reuse_addr()
        return sock

    def _bind_socket(self, sock, ip, port):
        sock.bind((ip, port))

    def _create_server(self, sock, ip, port):
        print ("Hello World")
        server_thread = coro.spawn(self.serve_forever, sock, ip, port)
        return server_thread

    def serve_forever(self, sock, ip, port):
        """ Always 'on' thread to accept incoming connections and spawn
        threads to serve specific requests.
        """
        print ('API.SERVER.START', self.ip, self.port)
        #qlog.write('API.SERVER.START', self.ip, self.port)
        sock.listen(15)
        try:
            while True:
                s, addr = sock.accept()
                print ('API.SERVER.INCOMING_CONNECTION', '%s:%s' % addr)
                #qlog.write('API.SERVER.INCOMING_CONNECTION', '%s:%s' % addr)
                if len(self.requests) >= 15:
                    s.close()
                    print ('API.SERVER.CONNECTION_REJECTED', '%s:%s' % addr)
                    #qlog.write('API.SERVER.CONNECTION_REJECTED', '%s:%s' % addr)
                    continue
                thread_id = coro.spawn(self.handle_request, s, addr).thread_id()
                self.requests.append(thread_id)
        finally:
            if sock:
                sock.close()
                sock = None
            print ('API.SERVER.STOP', ip, port)
            #qlog.write('API.SERVER.STOP', ip, port)

    def shutdown(self):
        if self.sock:
            self.sock.close()
            self.sock = None
        if self.api_on_localhost and self.local_sock:
            self.local_sock.close()
            self.local_sock = None
        if self.thread:
            self.thread.shutdown()
        if self.local_thread:
            self.local_thread.shutdown()
        for request in self.requests:
            coro.get_thread_by_id(request).shutdown()

        self.requests = []
        self.thread = None

    def handle_request(self, s, addr):
        """Conduit for handling requests.

        :Parameters:
            - `s`    : Accepted socket
            - `addr` : Client address
            - `handler_class` : The class that handles the request. Should
                                be sub-classed from BaseHTTPRequestHandler.
            - `caller` : Pointer to the server

        :Returns:
            - Nothing
        """
        try:
            self.request_handler_class(s, addr, self)
        except coro.Interrupted:
            s.close()
            self.requests.remove(coro.current().thread_id())
            raise
        # except sslip2.Error as serr:
        #     print ('API.SERVER.CONNECTION_FAILED', serr)
        #     #qlog.write('API.SERVER.CONNECTION_FAILED', serr)
        #     # XXX: HTTP-specific error code from generic code
        except Exception as err:
            print ("Error Here",err)
            coro.print_stderr(err)
            #qlog.write('API.SERVER.ERROR', err)
            # XXX: HTTP-specific error code from generic code
        s.close()
        print ('API.SERVER.CONNECTION_CLOSED', '%s:%s' % addr)
        #qlog.write('API.SERVER.CONNECTION_CLOSED', '%s:%s' % addr)
        self.requests.remove(coro.current().thread_id())

if __name__ == '__main__':
    from http.server import HTTPServer
    #server = CoroHTTPServer(('127.0.0.1',5020),GetHandler)
    server = HTTPServer(('localhost', 5001), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()

