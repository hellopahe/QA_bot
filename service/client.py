import grpc
import grpc_pb2
import grpc_pb2_grpc
import json
import tornado.web
import tornado.ioloop
import tornado.gen
import threading
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import time


class IndexHandler(tornado.web.RequestHandler):

    executor = ThreadPoolExecutor(8)  # 开一个线程池，这里设置为8，根据api请求的并发情况设置就可以

    # 这里在get()函数头上加gen.coroutine()装饰器，是为了将get请求在协程模式下运行
    @tornado.gen.coroutine
    def get(self):

        ori_infos = self.get_query_argument("infos")

        try:
            result = yield self.sent_2_grpc(ori_infos)
            # print(result)
        except Exception as err:
            result = "服务器内部错误"
            print(err)

        self.write(str(result))

    # set_2_grpc()函数是阻塞的，这里使用run_on_executor()，利用线程的方式让阻塞函数异步运行
    @run_on_executor()
    def sent_2_grpc(self, sen):

        client = grpc_pb2_grpc.GRPCStub(conn)
        req = client.Req(grpc_pb2.req(msg=sen))

        req_data = json.loads(req.msg)
        # print(req_data)
        return req_data


if __name__ == '__main__':
    conn = grpc.insecure_channel('localhost:11451') # 与run.py通信
    # run()

    threads = threading.Thread() # 这里初始化一个线程管理器
    threads.start()

    app = tornado.web.Application([(r'/', IndexHandler)])

    app.listen(11452)  # 发布http server
    tornado.ioloop.IOLoop.instance().start()
