from pymongo import MongoClient
try:
    client = MongoClient("mongodb+srv://suryateja2neti:Suryateja@parksense.coocf1i.mongodb.net/")
    client.server_info()  # This will raise an error if the connection fails
    print("MongoDB connection successful")
    db = client["parksense"]
    print(db.list_collection_names())  # Should include "qr_codes"
except Exception as e:
    print(f"MongoDB connection error: {str(e)}")