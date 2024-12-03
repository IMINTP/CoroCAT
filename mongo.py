import json
import os
import sys
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)  # Convert ObjectId to string
        return super().default(o)

def main():
    # Prompt user for input if not provided in CLI arguments
    if len(sys.argv) < 2:
        print("Usage: python script.py <filename_prefix>")
        filename_prefix = input("filename_prefix를 입력하시오: ").strip()
        if not filename_prefix:
            print("Error: filename_prefix를 입력해야 합니다.")
            sys.exit(1)
    else:
        filename_prefix = sys.argv[1]

    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://172.30.1.46:27017", serverSelectionTimeoutMS=5000)
        db = client["snubhcvc"]
        collection = db["frames"]

        # Query for documents with specific filename prefix
        query = {"filename": {"$regex": f"^{filename_prefix}"}}
        documents = list(collection.find(query))

        if not documents:
            print(f"No documents found for filename prefix '{filename_prefix}'")
            return

        # Process each document and save to individual JSON files
        for doc in documents:
            filename = doc.get("filename", "")
            data = doc.get("data", [])

            # Extract subdirectory structure and base filename
            subdir = os.path.dirname(filename)  # Extract "30002456/20181024/XA"
            base_filename = os.path.basename(filename).replace(".dcm", ".json")  # "004.json"

            # Create directories if they do not exist
            if not os.path.exists(subdir):
                os.makedirs(subdir)

            # Prepare output data
            output = []
            for item in data:
                index = item.get("index", 0) + 1  # Adjust frame (index + 1)
                cag_tracking = item.get("cag_tracking", {})
                if cag_tracking:
                    points = cag_tracking.get("point", [])
                    for point in points:
                        key = int(point.get("key", 0)) + 1  # Adjust key (key + 1)
                        output.append({
                            "filename": filename,
                            "frame": index,
                            "key": key,
                            "point": point.get("pt", []),  # Include point coordinates
                            "visible": point.get("visible", False)  # Include visibility status
                        })

            # Save to a JSON file in the same structure as the filename
            output_file = os.path.join(subdir, base_filename)
            with open(output_file, "w") as f:
                json.dump(output, f, indent=2, cls=JSONEncoder)

            print(f"Data saved to {output_file}.")

    except ServerSelectionTimeoutError as e:
        print(f"Error: Could not connect to MongoDB server. Details: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
