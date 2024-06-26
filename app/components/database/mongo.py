from typing import List
from ...models import Log, DataStory
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi import HTTPException, status, Response

class Mongo:

    def __init__(self, URI) -> None:

        client = AsyncIOMotorClient(URI)
        self.database = client.college
        self.logCollection = self.database.get_collection("logs")
        self.storyCollection = self.database.get_collection("stories")



    async def saveStory(self, storyObject: DataStory) -> DataStory:
        result = await self.storyCollection.insert_one(storyObject.model_dump())

        story = await self.getStory(str(storyObject.url))
        print(f"\n\nstory: {story}\n\n")
        return story
     
    async def getStory(self, url: str)-> DataStory:
        story_dict = await self.storyCollection.find_one({"url": url})
        if story_dict:
            return DataStory(**story_dict)
        return None
    

        
    async def getStories(self) -> List[DataStory]:
        logs = []
        async for story in self.storyCollection.find({}):
            logs.append(story)
        return logs

    async def removeStory(self, storyObjectKey: str):
        delete_result = await self.storyCollection.delete_one({"url": storyObjectKey})
        if delete_result.deleted_count == 1:
            return Response( content="deleted",status_code=status.HTTP_204_NO_CONTENT, media_type="application/json")
        raise HTTPException(status_code=404, detail=f"Story {storyObjectKey} not found")
    

 
    

    #####################################################xxx
    
    async def saveLog(self, logObject: Log) -> Log:
        log = await self.logCollection.insert_one(logObject.model_dump())
        return await self.getLog(str(log.inserted_id))
    

    async def getLog(self, logObjectID: str) -> Log:
        if (student := await self.logCollection.find_one({"_id": ObjectId(logObjectID)})) is not None:
            return student
        raise HTTPException(status_code=404, detail=f"Log {id} not found")

    async def getLogs(self) -> List[Log]:
        logs = []
        async for log in self.logCollection.find({}):
            logs.append(log)
        return logs


    async def removeLog(self, logObjectID: str):
        delete_result = await  self.logCollection.delete_one({"_id": ObjectId(logObjectID)})
        if delete_result.deleted_count == 1:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(status_code=404, detail=f"Log {str(id)} not found")    


