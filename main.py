import os
import random
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, ImageClip
from moviepy.config import change_settings
from PIL import Image, ImageDraw, ImageFont

def parse_text_file(text_file):
    try:
        with open(text_file, 'r') as f:
            content = f.read()
        
        print("File content read:")
        print(content)
        
        blocks = content.split('text : ')[1:]
        texts = [block.strip() for block in blocks]
        
        print("Parsed texts:")
        print(texts)
        
        return texts
    except FileNotFoundError:
        print(f"Error: The file {text_file} does not exist.")
        return []
    except Exception as e:
        print(f"Error parsing text file {text_file}: {e}")
        return []

def split_video_with_text_sound(video_path, text_file, sound_folder, output_folder, split_duration):
    try:
        video = VideoFileClip(video_path)
    except FileNotFoundError:
        print(f"Error: The video file {video_path} does not exist.")
        return
    except Exception as e:
        print(f"Error loading video file {video_path}: {e}")
        return

    video_duration = video.duration
    texts = parse_text_file(text_file)

    if not texts:
        print("No texts to overlay. Exiting.")
        return

    sound_files = [os.path.join(sound_folder, sound) for sound in os.listdir(sound_folder) if sound.endswith(('.mp3', '.wav'))]

    if not sound_files:
        print("No sound files found in the sounds folder.")
        return

    os.makedirs(output_folder, exist_ok=True)

    part = 1
    start_time = 0
    while start_time < video_duration:
        end_time = min(start_time + split_duration, video_duration)
        subclip = video.subclip(start_time, end_time)
        random_text = random.choice(texts)
        random_sound = random.choice(sound_files)

        print(f"Selected text: {random_text}")  # Debug print
        print(f"Selected sound: {random_sound}")  # Debug print
        
        # Create the text image using Pillow
        def getSize(txt, font):
            # Get bounding box of the text to calculate the width and height
            testImg = Image.new('RGBA', (1, 1))
            testDraw = ImageDraw.Draw(testImg)
            bbox = testDraw.textbbox((0, 0), txt, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]  # width, height
        fontname = "Aileron-SemiBold.otf"
        fontsize = 60
        text = random_text

        colorText = "white"
        colorOutline = "black"
        colorBackground = (0, 0, 0, 0)  # Transparent background (RGBA)

        font = ImageFont.truetype(fontname, fontsize)
        width, height = getSize(text, font)
        
        # Create image with transparency and padding for the outline
        img = Image.new('RGBA', (width + 20, height + 20), colorBackground)
        d = ImageDraw.Draw(img)
        
        # Calculate the position to center the text
        text_x = (img.width - width) // 2
        text_y = (img.height - height) // 2
        
        # Stroke size
        stroke_width = 2
        
        # Draw the black stroke (text outline) by drawing the text multiple times around the main text
        for offset in range(-stroke_width, stroke_width+3):
            if offset != 0:
                d.text((text_x + offset, text_y), text, font=font, fill=colorOutline)
                d.text((text_x - offset, text_y), text, font=font, fill=colorOutline)
                d.text((text_x, text_y + offset), text, font=font, fill=colorOutline)
                d.text((text_x, text_y - offset), text, font=font, fill=colorOutline)
        
        # Draw the main white text on top
        d.text((text_x, text_y), text, fill=colorText, font=font)
            
        img.save("image.png")
        
        image = ImageClip("image.png")
        image = image.set_duration(subclip.duration)
        image = image.set_position(("center", "center"))
        final_video = CompositeVideoClip([subclip, image])
        final_clip = final_video.set_audio(AudioFileClip(random_sound).subclip(0, subclip.duration))

        output_path = os.path.join(output_folder, f"part_{part}.mp4")
        try:
            final_clip.write_videofile(output_path, codec='libx264')
            print(f"Saved {output_path}")
        except Exception as e:
            print(f"Error saving video file {output_path}: {e}")

        start_time = end_time
        part += 1

# Usage example
split_duration = input("Enter the duration for each part (in seconds): ")
# split_duration = 1
video_path = input("Enter your video file name: ")
text_file = "text.txt"  # Random text from this file
sound_folder = "sounds"  # Folder containing sound files
output_folder = "output"  # Folder to save output parts

split_video_with_text_sound(video_path, text_file, sound_folder, output_folder,split_duration)

    
    
    
