import grpc
import grpc_pb2
import grpc_pb2_grpc
import json
import tornado.web
import tornado.ioloop
from tornado.web import RequestHandler


def sent_2_grpc(sen):

    client = grpc_pb2_grpc.GRPCStub(conn)
    req = client.Req(grpc_pb2.req(msg=sen))

    req_data = json.loads(req.msg)
    return req_data


class BaseHandler(RequestHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')


class IndexHandler(BaseHandler):

    # 获取get参数
    def get(self):
        ori_infos = self.get_query_argument("infos")

        try:
            result = sent_2_grpc(ori_infos)
        except Exception as err:
            result = "服务器内部错误"
            print(err)

        self.write(result)


if __name__ == '__main__':
    conn = grpc.insecure_channel('localhost:11451') # 与run.py通信
    # run()

    app = tornado.web.Application([(r'/', IndexHandler)])

    app.listen(11452) # 发布http server
    tornado.ioloop.IOLoop.current().start()
