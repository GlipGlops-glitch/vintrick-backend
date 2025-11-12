# python tools/mongo_test.py


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# MongoDB Atlas connection string
uri = "mongodb+srv://casey2higgins:S01sJyanjwVWW0vF@cluster0.sg3jrtl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    # The ping command is cheap and does not require auth
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("MongoDB connection failed:", e)
finally:
    client.close()










# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# import json

# # MongoDB connection details
# uri = "mongodb+srv://casey2higgins:S01sJyanjwVWW0vF@cluster0.sg3jrtl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# client = MongoClient(uri, server_api=ServerApi('1'))

# try:
#     client.admin.command('ping')
#     print("Connected to MongoDB!")
# except Exception as e:
#     print("MongoDB connection failed:", e)
#     exit(1)

# db = client["SMW"]
# collections = {
#     "PlannedLoads": db["PlannedLoads"],
#     "ScaleTransactions": db["ScaleTransactions"]
# }

# # Print all documents from both collections
# for col_name, col in collections.items():
#     print(f"\nDocuments in {col_name} collection:")
#     for doc in col.find():
#         print(json.dumps(doc, indent=2, default=str))

# client.close()