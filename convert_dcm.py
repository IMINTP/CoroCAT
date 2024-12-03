import os
import numpy as np
import pydicom
import cv2
import ffmpeg

def dcm_to_mp4(dcm_file_path, output_mp4_path, fps=15):
    """
    Converts a DICOM video file (.dcm) to MP4 format.

    :param dcm_file_path: Path to the input DICOM file.
    :param output_mp4_path: Path for the output MP4 file.
    :param fps: Frames per second for the output video.
    """
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_mp4_path)
    os.makedirs(output_dir, exist_ok=True)

    # Load the DICOM file
    ds = pydicom.dcmread(dcm_file_path)
    pixel_data = ds.pixel_array  # Extract pixel data
    num_frames, original_height, original_width = pixel_data.shape

    # Normalize pixel values to uint8 if needed
    if pixel_data.dtype == np.uint16:
        pixel_data = ((pixel_data - pixel_data.min()) / (pixel_data.max() - pixel_data.min()) * 255).astype(np.uint8)

    # Convert to numpy array in uint8 format for video encoding
    video_data = np.array(pixel_data, dtype=np.uint8)

    # Use ffmpeg to encode frames directly to MP4 with lossless compression
    process = (
        ffmpeg
        .input('pipe:', format='rawvideo', pix_fmt='gray', s=f"{original_width}x{original_height}", framerate=fps)
        .output(output_mp4_path, vcodec='libx264', pix_fmt='yuv420p', crf=0, preset='ultrafast')
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    # Write each frame to the ffmpeg process
    for i, frame in enumerate(video_data):
        print(f"Writing frame {i + 1}/{len(video_data)}...")
        process.stdin.write(frame.tobytes())

    # Close the process properly
    process.stdin.close()
    process.wait()
    print(f"Converted {dcm_file_path} to {output_mp4_path}.")

def process_directory(input_dir, output_dir, fps=15):
    """
    Processes all .dcm files in the input directory and converts them to MP4,
    maintaining the directory structure.

    :param input_dir: Path to the input directory containing .dcm files.
    :param output_dir: Path to the base output directory for MP4 files.
    :param fps: Frames per second for the output video.
    """
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".dcm"):
                # Input file path
                input_file_path = os.path.join(root, file)

                # Relative path for the output structure
                relative_path = os.path.relpath(root, input_dir)
                output_file_dir = os.path.join(output_dir, relative_path)
                output_file_path = os.path.join(output_file_dir, os.path.splitext(file)[0] + ".mp4")

                # Convert DICOM to MP4
                print(f"Processing: {input_file_path} -> {output_file_path}")
                dcm_to_mp4(input_file_path, output_file_path, fps)

if __name__ == "__main__":
    # Define input and output directories
    input_base_dir = "/home/user/DHKIM/Materials_DICOM/dcm"  # Replace with your input directory
    output_base_dir = "/home/user/DHKIM/Materials_DICOM/mp4"  # Replace with your output directory

    # Set FPS
    fps = 15

    # Process all .dcm files in the input directory
    process_directory(input_base_dir, output_base_dir, fps=fps)
