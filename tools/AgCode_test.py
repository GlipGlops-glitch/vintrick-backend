import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

mongo_user = os.getenv("MONGO_USER")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_cluster = os.getenv("MONGO_CLUSTER")

# Replace with your actual database and collection names
database_name = "testdb"          # <-- change this to your DB name
collection_name = "testcollection" # <-- change this to your collection name

# Construct connection string
uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_cluster}/?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(uri)
db = client[database_name]
collection = db[collection_name]

# Retrieve up to 10 records
print(f"Retrieving up to 10 records from {database_name}.{collection_name}...")
for doc in collection.find().limit(10):
    print(doc)