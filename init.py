import sys
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import re
import os

class Controller(object):  
  
    def __init__(self, server):  
        self.__server = server  
 
    @property  
    def server(self):  
        return self.__server  
		
class Router(object):  
  
    def __init__(self, server):  
        self.__routes = []  
        self.__server = server  
  
    def addRoute(self, regexp, controller, action):  
        self.__routes.append({'regexp': regexp, 'controller': controller, 'action': action})  
          
    def route(self, path):  
        for route in self.__routes:  
            if re.search(route['regexp'], path):  
                cls = globals()[route['controller']]  
                func = cls.__dict__[route['action']]  
                obj = cls(self.__server)  
                func(obj, )
                return  
  
        # Not found  
        self.__server.send_response(404)  
        self.__server.end_headers()

class MyRequestHandler(BaseHTTPRequestHandler):  
  
    def __init__(self, request, client_address, server):  
          
        routes = [  
            {'regexp': r'^/$', 'controller': 'HomeController', 'action': 'indexAction'},  
            {'regexp': r'^/content/', 'controller': 'ContentController', 'action': 'showAction'}  
        ] 
          
        self.__router = Router(self)  
        for route in routes:  
            self.__router.addRoute(route['regexp'], route['controller'], route['action'])  
  
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)  
      
    def do_GET(self):  
        self.__router.route(self.path) 
		
class HomeController(Controller):  
  
    def __init__(self, server):  
        Controller.__init__(self, server)  
  
    def indexAction(self):  
        self.server.send_response(200)  
        self.server.send_header('Content-type', 'text/html')  
        self.server.end_headers()  
        self.server.wfile.write(bytes('Hello world','UTF-8'))

class ContentController(Controller):  
      
    CONTENT_BASE_PATH = 'public/'  
  
    def __init__(self, server):  
        Controller.__init__(self, server)  
          
    def showAction(self):  
        filename = ContentController.CONTENT_BASE_PATH + self.server.path[9:]  
        if os.access(filename, os.R_OK) and not os.path.isdir(filename):  
            #TODO: is there any possibility to access files outside the root with ..?  
            file = open(filename, "r")  
            content = file.read()  
            file.close()  
              
            #TODO: set correct content type  
            self.server.send_response(200)  
            self.server.send_header('Content-type', 'text/html')  
            self.server.end_headers()  
            self.server.wfile.write(content)  
        else:  
            self.server.send_response(404)  
            self.server.end_headers()

def main():  
	httpd = HTTPServer(('', 809), MyRequestHandler) 
	try:
		print ("Server started...")	
		httpd.serve_forever()  
	except:
		print("Server shutting down")	
		httpd.socket.close()
  
if __name__ == '__main__':  
    main()
