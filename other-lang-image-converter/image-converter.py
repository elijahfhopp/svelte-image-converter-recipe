import cv2
import numpy
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(req: Request):
    return templates.TemplateResponse(request=req, name="index.html")


@app.post("/convert-to-jpeg", response_class=Response)
async def convert_to_jpeg(req: Request):
    body = await req.body()
    buffer = numpy.frombuffer(body, numpy.uint8)
    png = cv2.imdecode(buffer, cv2.IMREAD_UNCHANGED)
    successful, jpeg = cv2.imencode(".jpeg", png)
    if not successful:
        return Response(status_code=500)
    return Response(content=jpeg.tobytes(), media_type="image/jpeg")
