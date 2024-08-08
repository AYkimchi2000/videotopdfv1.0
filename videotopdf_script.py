import time
import os
import cv2
import numpy as np
from PIL import Image
from fpdf import FPDF


#threshold value = the higher the more similar
def extract_append_to_list(video_path):
    video_capture = cv2.VideoCapture(video_path)
    prev_frame = None
    unique_frame_number = 0
    pixel_diff_counter = 0
    color_threshold = 2
    score_list = []
    frame_list = []
    if not video_capture.isOpened():
        print("Error: Could not open video.")
        return [], []
    while True:
        # Capture frame-by-frame
        extract_success, frame = video_capture.read()
        if not extract_success:
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_frame is not None:
            # Compute SSIM between current frame and previous frame
            for row1, row2 in zip(prev_frame, gray_frame):
                for pixel1, pixel2 in zip(row1, row2):
                    if abs(int(pixel1) - int(pixel2)) > color_threshold:
                        pixel_diff_counter += 1
            #This gives how many pixels different there's between gray frame and prev frame
            # print(pixel_diff_counter)
            if pixel_diff_counter <150000: 
                score = 1
            else:
                score = 0
        else:
            score = 1
        frame_list.append(unique_frame_number) 
        score_list.append(score)
        unique_frame_number += 1
        prev_frame = gray_frame
        pixel_diff_list = []
        pixel_diff_list.append(pixel_diff_counter)
        pixel_diff_counter = 0
        
    video_capture.release()
    return score_list, frame_list

def combine_to_tuple_extract_groups(score_list, frame_list):
    combined_tuple = tuple(zip(score_list, frame_list))
    groups = []
    current_group = []
    
    for i, (key, value) in enumerate(combined_tuple):
        if current_group and key != current_group[-1][0]:
            groups.append(current_group)
            current_group = []
        current_group.append((key, value))
        
    if current_group:
        groups.append(current_group)
    
    return groups

def extract_unique_pair_from_group(groups):
    extracted_pairs = []
    
    for group in groups:
        extracted_pairs.append(group[0])  # Extract one key-value pair
        filtered_pairs = [(key, value) for key, value in extracted_pairs if key != 0]

    
    return filtered_pairs

def extract_unique_frames(video_path, output_dir, filtered_pairs):

    # List of specific frame numbers you want to save
    specific_frames_list = [pair[1] for pair in filtered_pairs]
    cap = cv2.VideoCapture(video_path)

    # Check if the video was opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    # Loop through the video frames
    frame_index = 0
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break  # Exit loop if no more frames are available

        if frame_index in specific_frames_list:
            # Save the frame as an image file
            frame_filename = os.path.join(output_dir, f"frame_{frame_index}.jpg")
            cv2.imwrite(frame_filename, frame)
            print(f"Frame {frame_index} saved as {frame_filename}")
        
        frame_index += 1
    # Release the video capture object
    cap.release()
'''
def frame_to_pdf(frame_file, output_pdf):
    image = Image.open(frame_file)
    pdf = FPDF()
    pdf.add_page()
    pdf.image(frame_file, 0, 0, 210, 297)
    pdf.output(output_pdf)

def generate_pdfs(slide_changes, frames_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for i, slide in enumerate(slide_changes):
        frame_file = os.path.join(frames_dir, slide)
        output_pdf = os.path.join(output_dir, f"slide_{i+1}.pdf")
        frame_to_pdf(frame_file, output_pdf)
'''
def main():
    video_path = input('Insert path to video you want to extract: ') 
    output_dir = input('Insert path to directory you want to store the extracted items: ')
    if not os.path.isdir(output_dir):
        print('Invalid directory')
        return
    
    start_time = time.time()

    score_list, frame_list = extract_append_to_list(video_path)
#    print("Scores:", score_list)
#    print("Frames:", frame_list)
    groups = combine_to_tuple_extract_groups(score_list, frame_list)
#    print("Groups:", groups)
    filtered_pairs = extract_unique_pair_from_group(groups)
    print("Extracted Pairs:", filtered_pairs)
    extract_unique_frames(video_path, output_dir, filtered_pairs)

    end_time = time.time()
    elapsed_time = end_time - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Time taken to run the script: {int(hours)} hours, {int(minutes)} minutes, and {seconds:.2f} seconds")



    
    
if __name__ == "__main__":
    main()
