from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
col = client["opportunity_db"]["opportunities"]

count = 0
for doc in col.find():
    dl = doc.get("deadline")
    if dl and "2026-" in dl:
        new_dl = dl.replace("2026-", "2027-")
        col.update_one({"_id": doc["_id"]}, {"$set": {"deadline": new_dl}})
        count += 1

print(f"Successfully updated deadlines for {count} opportunities to 2027!")
