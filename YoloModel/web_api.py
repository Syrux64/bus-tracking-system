from fastapi import BackgroundTasks, FastAPI
from findBus import find_new_bus


app = FastAPI()

def process_bus_status(video_path):
    find_new_bus(video_path)

@app.get("/")
def read_root(background_tasks: BackgroundTasks):
    video_path = '../showcase_3.mp4' # source
    
    # Video processing in the background
    background_tasks.add_task(process_bus_status, video_path)
    
    return {"status": "Processing video..."}

