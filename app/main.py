from fastapi import FastAPI, status, Request, Response, Body,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from queue import Queue
from fastapi.routing import APIRouter

from .routers import repository
from .components.database.mongo import Mongo
from .models import Log
from typing import List
from .routers import items
from .routers import repository
from .routers import logs
from .routers import stories
import asyncio
from typing import Dict
from .models import getDummyStory
from .components.pdf.pdf import PdfGenerator
from .models import DataStory, Functions, Readme
import json

from .components.github import GithubRepo

from starlette.requests import Request
app = FastAPI()
router = APIRouter()

app.state.database = Mongo("mongodb+srv://mongo-user:lK30SyUhSrIxND9Q@legacy-refactorer.bqdjbgf.mongodb.net/data?retryWrites=true&w=majority&appName=legacy-refactorer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repository.router)
app.include_router(items.router)
app.include_router(logs.router)
app.include_router(stories.router)


queue = Queue()
status_dict: Dict[str, str] = {}

@app.post("/process")
async def process_url(url: str, background_tasks: BackgroundTasks):
    queue.put(url)
    status_dict[url] = "pending"
    background_tasks.add_task(process_queue)
    return {"message": "URL added to the queue"}

async def process_queue():
    database: Mongo = app.state.database
    while not queue.empty():
        url = queue.get()

        if database.getStory(url):
            status_dict[url] = "done"
            return

        repo_dir = GithubRepo.download_repo(url)

        # TODO: GENERATE BUSINESS ANALYSIS

        status_dict[url] = "done"
        

@app.get("/status/{url}")
async def get_status(request: Request,url: str):
    database: Mongo = request.app.state.database

    # DEMO OVERRIDE
    #url = "my-example-refactor"

    status: str = status_dict.get(url, "not found")
    if status == "done":
        story = await database.getStory(url)
        filename = f"./structured_output_{story.url}_{story.id}.pdf"
        output = f"{request.url.scheme}://{request.headers['host']}/static/{filename}"
        return {"url": url, "status": status, "output": output}
    else: 
        return {"url":url, "status":status, "output": None}


# DEMO GENERATION
@app.get("/test-pdf")
async def asf(request: Request):
    database: Mongo = request.app.state.database

    exampleStory = await database.getStory("my-example-refactor")

    PdfGenerator(request.app,exampleStory).generate_pdf()
    
    return exampleStory