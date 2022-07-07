# import asyncio
# #
# # from clip_client import Client
# #
# #
# # async def to_bert(query):
# #     result = (await bc.aencode(query))[0]
# #     return result
# #
# #
# # bc = Client(server='grpc://0.0.0.0:51000')
# #
# # result = asyncio.run(to_bert('hello world'))
# #
# # print(result)
# #
#
# # -----------------需要笔记-----------------
# #
# from http.server import BaseHTTPRequestHandler, HTTPServer
# import urlparse, json
#
# class GetHandler(BaseHTTPRequestHandler):
#
#     def do_GET(self):
#         parsed_path = urlparse.urlparse(self.path)
#         message = '\n'.join([
#             'CLIENT VALUES:',
#             'client_address=%s (%s)' % (self.client_address,
#                 self.address_string()),
#             'command=%s' % self.command,
#             'path=%s' % self.path,
#             'real path=%s' % parsed_path.path,
#             'query=%s' % parsed_path.query,
#             'request_version=%s' % self.request_version,
#             '',
#             'SERVER VALUES:',
#             'server_version=%s' % self.server_version,
#             'sys_version=%s' % self.sys_version,
#             'protocol_version=%s' % self.protocol_version,
#             '',
#             ])
#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write(message)
#         return
#
#     def do_POST(self):
#         content_len = int(self.headers.getheader('content-length'))
#         post_body = self.rfile.read(content_len)
#         self.send_response(200)
#         self.end_headers()
#
#         data = json.loads(post_body)
#
#         self.wfile.write(data['foo'])
#         return
#
# if __name__ == '__main__':
#     from BaseHTTPServer import HTTPServer
#     server = HTTPServer(('localhost', 8080), GetHandler)
#     print 'Starting server at http://localhost:8080'
#     server.serve_forever()
import json

dict = {
    'a': 1,
    'b': 2
}

s = json.dumps(dict)

print(dict)