import torch
import os

tensor_path = input("Enter the tensor file path (.pt): ")
tensor = torch.load(tensor_path)

print(tensor)
