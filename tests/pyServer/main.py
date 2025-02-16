import os
import uvicorn
import ssl
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from uvicorn.protocols.http.httptools_impl import HttpToolsProtocol
old_on_url = HttpToolsProtocol.on_url
def new_on_url(self,url):
    old_on_url(self, url)
    self.scope['transport'] = self.transport
HttpToolsProtocol.on_url = new_on_url

app = FastAPI()

@app.get("/")
async def root(request: Request):
    t= request.scope["transport"].get_extra_info("ssl_object").getpeercert()["subject"]
    common_name = t[4][0][1]
    print(common_name)
    return {"message": "Hello, " + common_name}

# start server using uvicorn from the script itself
if __name__ == "__main__":
    cwd = os.path.dirname(os.path.realpath(__file__))
    cwd = os.path.join(cwd, "../demoCA")

    # ensure all the files exist before starting the server
    with open(os.path.join(cwd, "certs/ca.crt")) as f: pass
    with open(os.path.join(cwd, "certs/server.crt")) as f: pass
    with open(os.path.join(cwd, "private/server.key")) as f: pass

    uvicorn.run(app, 
        port=3000, 
        ssl_ca_certs=os.path.join(cwd, "certs/ca.crt"), 
        ssl_certfile=os.path.join(cwd, "certs/server.crt"), 
        ssl_keyfile=os.path.join(cwd, "private/server.key"), 
        ssl_keyfile_password="test",
        ssl_cert_reqs=ssl.CERT_REQUIRED
    )
