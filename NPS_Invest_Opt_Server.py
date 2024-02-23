import uvicorn
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from sse_starlette.sse import ServerSentEvent, EventSourceResponse

from pydantic import BaseModel
from typing import Any, Dict, List, Literal, Optional, Union

class Stream_Response(BaseModel):
    delta: str
    finish_reason: Optional[Literal['stop', 'length']]

def start_server(http_address: str, port: int):
    app = FastAPI()
    app.add_middleware(CORSMiddleware,
                       allow_origins=["*"],
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"])
    @app.post("/cal")
    def cal(arg_dict: dict):
        print(f'arg_dict is {arg_dict}')
        response = {
            'status':'normal',
            'cancel':False,
            'complete':True,
        }
        return response

    print(f'API服务器已启动, url: {http_address}:{port} ...')
    uvicorn.run(app=app, host=http_address, port=port, workers=1)

def main():
    parser = argparse.ArgumentParser(description=f'API Service for NPS_Invest_Opt_Server.')
    parser.add_argument('--host', '-H', help='host to listen', default='0.0.0.0')
    parser.add_argument('--port', '-P', help='port of this service', default=8002)
    args = parser.parse_args()

    start_server(args.host, int(args.port))

if __name__ == '__main__':
    main()