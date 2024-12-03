import json
import torch
import os

# Ask for input file path from CLI
input_file = input("Enter the input JSON file path: ")

# Base output directory
output_base_dir = "/home/user/DHKIM/Materials_DICOM/tensor"

# Check if input file exists
if not os.path.isfile(input_file):
    print(f"Input file not found: {input_file}")
    exit(1)

# Load JSON data
with open(input_file, "r") as f:
    json_data = json.load(f)

# Get a unique list of frames available in the JSON file
frames = sorted(set(item["frame"] for item in json_data))
print(f"Available frames: {frames}")

# Ask user to select a specific frame
selected_frame = int(input("Enter the frame number to process: "))

# Filter JSON data for the selected frame
filtered_data = [item for item in json_data if item["frame"] == selected_frame]

if not filtered_data:
    print(f"No data found for frame {selected_frame}. Exiting.")
    exit(1)

# Convert filtered JSON data to a list of lists
tensor_data = []
for item in filtered_data:
    frame = item["frame"]
    x, y = item["point"]
    tensor_data.append([frame, x, y])

# Convert the list to a PyTorch tensor
tensor = torch.tensor(tensor_data)

# Derive output path based on input file structure
relative_path = os.path.relpath(input_file, "/home/user/DHKIM/Materials_DICOM/json")
output_file_path = os.path.join(output_base_dir, os.path.splitext(relative_path)[0] + f"_frame_{selected_frame}.pt")

# Ensure the output directory exists
output_dir = os.path.dirname(output_file_path)
os.makedirs(output_dir, exist_ok=True)

# Save tensor to the derived path
torch.save(tensor, output_file_path)

print(f"Tensor for frame {selected_frame} saved successfully to {output_file_path}")
