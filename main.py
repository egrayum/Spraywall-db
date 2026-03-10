from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

DATA_FILE = 'climbs.json'

def read_entries():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def write_all_entries(entries):
    with open(DATA_FILE, 'w') as f:
        json.dump(entries, f, indent=4)

def write_entry(name, holds, feet, date, difficulty):
    entries = read_entries()
    
    # Convert holds string to array of tags
    holds_array = [h.strip().lower() for h in holds.split(',')]
    
    new_entry = {
        "name": name,
        "holds": holds_array,  # Now an array
        "feet": feet,
        "date": date,
        "difficulty": difficulty
    }
    entries.append(new_entry)
    write_all_entries(entries)

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.get("/api/climbs")
async def get_climbs():
    return read_entries()

@app.post("/api/climbs")
async def add_climb(climb: dict):
    write_entry(
        climb['name'],
        climb['holds'],
        climb['feet'],
        climb['date'],
        climb['difficulty']
    )
    return {"status": "success"}

@app.put("/api/climbs/{index}")
async def update_climb(index: int, climb: dict):
    entries = read_entries()
    if 0 <= index < len(entries):
        entries[index] = {
            "name": climb['name'],
            "holds": climb['holds'],
            "feet": climb['feet'],
            "date": climb['date'],
            "difficulty": climb['difficulty']
        }
        write_all_entries(entries)
        return {"status": "success"}
    return {"status": "error", "message": "Index out of range"}

@app.delete("/api/climbs/{index}")
async def delete_climb(index: int):
    entries = read_entries()
    if 0 <= index < len(entries):
        deleted = entries.pop(index)
        write_all_entries(entries)
        return {"status": "success", "deleted": deleted}
    return {"status": "error", "message": "Index out of range"}