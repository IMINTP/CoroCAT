import os
import torch
import cv2
import numpy as np

from base64 import b64encode
from cotracker.utils.visualizer import Visualizer, read_video_from_path
from IPython.display import HTML

# Read the video from the specified path
#######path복붙
video = read_video_from_path('/home/user/DHKIM/Materials_DICOM/mp4/30004407/20200710/XA/007.mp4')

# Handle grayscale video
if video.ndim == 3:  # Grayscale video: (T, H, W)
    video = video[:, :, :, None]  # Add a channel dimension to make it (T, H, W, C)
elif video.ndim != 4:
    raise ValueError(f"Unexpected video dimensions: {video.shape}")

video_tensor = torch.from_numpy(video).permute(0, 3, 1, 2).float()  # Convert to (T, C, H, W)

print("Original video shape:", video.shape)
print("Converted video tensor shape:", video_tensor.shape)

def show_video(video_path):
    """Display the video in the notebook."""
    try:
        with open(video_path, "r+b") as video_file:
            video_data = video_file.read()
        video_url = f"data:video/mp4;base64,{b64encode(video_data).decode()}"
        return HTML(f"""<video width="640" height="480" autoplay loop controls>
                        <source src="{video_url}" type="video/mp4"></video>""")
    except Exception as e:
        print(f"Error loading video for display: {e}")
        return None

# Load the CoTracker model
from cotracker.predictor import CoTrackerPredictor

checkpoint_path = '/home/user/DHKIM/Materials_DICOM/co-tracker/checkpoints/scaled_offline.pth'
if not os.path.exists(checkpoint_path):
    raise FileNotFoundError(f"Checkpoint not found at {checkpoint_path}")

model = CoTrackerPredictor(checkpoint=checkpoint_path)

# Move model to GPU if available
if torch.cuda.is_available():
    model = model.cuda()

# Path to the .pt file containing queries
#######path복붙
file_path = '/home/user/DHKIM/Materials_DICOM/tensor/30004407/20200710/XA/007_frame_31.pt'
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Query file not found at {file_path}")

queries = torch.load(file_path)

# Ensure queries are on the correct device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
video_tensor = video_tensor.to(device)
queries = queries.to(device)
model = model.to(device)

# Add batch dimension to video tensor if needed (B, T, C, H, W)
if video_tensor.ndim == 4:
    video_tensor = video_tensor.unsqueeze(0)

# Debugging output
print("Video tensor device:", video_tensor.device)
print("Queries device:", queries.device)
print("Model device:", next(model.parameters()).device)
print("Video tensor shape:", video_tensor.shape)
print("Queries shape:", queries.shape)

# Perform prediction
try:
    pred_tracks, pred_visibility = model(video_tensor, queries=queries[None])
except Exception as e:
    print(f"Error during prediction: {e}")
    raise

# Initialize visualizer
vis = Visualizer(
    save_dir='./videos',
    linewidth=2,
    mode='cool',
    tracks_leave_trace=0
)

# Backward tracking and visualization
#######filename 수정
try:
    pred_tracks, pred_visibility = model(video_tensor, queries=queries[None], backward_tracking=True)
    vis.visualize(
        video=video_tensor,
        tracks=pred_tracks,
        visibility=pred_visibility,
        filename='30004407_2020_0710_XA_007'
    )
    print("Visualization saved successfully.")
except Exception as e:
    print(f"Error during visualization: {e}")

# Display the video
#######filename 수정

output_video_path = "./videos/30004407_2020_0710_XA_007.mp4"
if os.path.exists(output_video_path):
    print(f"Visualization output saved successfully at {output_video_path}.")
    print("Open the file using a video player to confirm the result.")
else:
    print(f"Visualization output not found at {output_video_path}.")
