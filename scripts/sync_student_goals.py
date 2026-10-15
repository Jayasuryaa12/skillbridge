from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
career_id = client["skill_db"]["careers"].find_one()["_id"]

count = 0
for s in client["skill_db"]["students"].find({"career_goal": None}):
    client["skill_db"]["students"].update_one({"_id": s["_id"]}, {"$set": {"career_goal": career_id}})
    count += 1

print(f"Updated {count} students with career_id {career_id}")
