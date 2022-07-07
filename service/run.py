from processing import Elastic
from concurrent import futures
import json
import grpc
import grpc_pb2
import grpc_pb2_grpc


def data_handler(infos):
    index_name = 'bert_test'
    doc_type_name = 'bert_test'
    es = Elastic(index_name, doc_type_name)

    result = es.query(infos)
    fields = ['spl_words', 'keywords', 'problem_id', 'problem', 'score']

    resp = dict(zip(fields, result))  # 字典结构的response
    with open('../dao/query_resp.json', 'w') as f:
        json.dump(resp, f, indent=4)

    resp_str = json.dumps(resp)

    return resp_str


class RpcServer(grpc_pb2_grpc.GRPCServicer):

    def Req(self, request, context):
        # print(request.msg)
        log_file = open('../dao/bot_log.txt', 'a')

        log_file.write("Q:{}\n".format(request.msg))
        # print(request.msg)
        try:
            reply_answer = data_handler(request.msg)
        except Exception as e:
            reply_answer = "服务器出现了预料外的错误"
            print(e)

        log_file.write("A:" + "".join(reply_answer) + "\n")
        log_file.close()

        return grpc_pb2.rply(msg=reply_answer)


def serve():
    # 启动 rpc 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_pb2_grpc.add_GRPCServicer_to_server(RpcServer(), server)
    server.add_insecure_port('[::]:11451')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
    # data_handler('invest')
