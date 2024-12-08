from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pokemon Trainer Dashboard!"}

@app.get("/trainers/{trainer_id}")
def read_trainer(trainer_id: int):
    trainers = {
        1: {"name": "Ash Ketchum", "team": ["Pikachu", "Charizard"], "region": "Kanto"},
        2: {"name": "Misty", "team": ["Starmie", "Psyduck"], "region": "Cerulean"},
    }
    trainer = trainers.get(trainer_id, {"message": "Trainer not found."})
    return {"trainer_id": trainer_id, "details": trainer}
