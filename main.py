from flask import Flask
from flask import request
import pymongo
from pymongo import MongoClient
import json
from bson import json_util


app = Flask(__name__)

# seed_type, seed_count
cluster = MongoClient("mongodb+srv://aananya:tyagu2712@cluster0-ozbm1.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["seeds"]
collection = db["seeds"]

@app.route("/seeds",methods=["GET"])
def get_seeds():
    all_seeds = list(collection.find({}))
    return  json.dumps(all_seeds, default=json_util.default)

@app.route("/addseed",methods=["POST"])
def add_seed():
    request_payload = request.json #if key doesn't exist, returns None
    seed = request_payload['seed']
    existing_seed = collection.find({"_id":seed['name']})

    if existing_seed:
        for ex_seed in existing_seed:
            old_count = int(ex_seed["seed_count"])
            addition = int(seed['count'])
            updated_seeds = addition+old_count
        collection.find_one_and_update({"_id" : seed['name'] },{"$set": {"seed_count": updated_seeds } } , upsert=True)
    else:
        collection.insert_one({"_id":seed['name'],"seed_count":seed["count"]})
    return (f"Thankyou for adding {addition} seeds, the total count of the {seed['name']} seeds is now {updated_seeds}")


@app.route("/buyseed", methods=["POST"])
def buy_seed():
    request_payload = request.json
    seed = request_payload['seed']
    existing_seed = collection.find({"_id":seed['name']})
    if existing_seed.count():
        for ex_seed in existing_seed:
            old_count = int(ex_seed["seed_count"])
            requirement = int(seed['count'])
            if requirement>old_count:
                return (f"only {old_count} seeds left, try buying lesser number of seeds")
            else:
                remaining_seeds = old_count-requirement
                collection.find_one_and_update({"_id" : seed['name'] },{"$set": {"seed_count": remaining_seeds } } , upsert=True)
                return (f"Thankyou for buying {requirement} seeds, the total count of the {seed['name']} seeds is now {remaining_seeds}")
    else:
        return (f"{seed['name']} seed not in the inventory. please try again.")



if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")

# to run :
# export FLASK_APP=main.py
# python -m flask run
# http://0.0.0.0:5000/addseed
