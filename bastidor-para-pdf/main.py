import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

RAWS_DIR = 'imagens'
OUTPUT_DIR = 'pdfs'
TEMP_JPG_PATH = "temp_image.jpg"
DESIRED_DIAMETER = 0.952380952 * A4[0] 

#
# Calibragem dos parâmetros de detecção de círculos
#
PARAMS= {
    'minDist': 32, # Diminuir para detectar círculos menores, aumentar para detectar círculos maiores
    'param1': 30, # Alterar moderadamente caso a detecção de círculos não esteja funcionando para o seu caso
    'param2': 550, # Quanto maior, menos círculos são detectados (se aproxima do círculo 'principal' da imagem)
}
#
#
#

def try_to_detect_circle(image_path):
    print(f"     Searching for circle in {image_path}...")
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Detect circles using Hough Circle Transform
    circles = cv2.HoughCircles(image, 
                                cv2.HOUGH_GRADIENT,
                                dp=2,
                                minDist=PARAMS['minDist'],
                                param1=PARAMS['param1'], 
                                param2=PARAMS['param2'], 
                                minRadius=0, 
                                maxRadius=0)
    
    if circles is not None:
        x, y, r = circles[0][0]
        return x, y, r
    else:
        return None

def crop_image(image, circle_params):
    x, y, r = circle_params
    cropped_image = image.crop((x - r, y - r, x + r, y + r))
    return cropped_image

def scale_image(image, scale_factor):
    width, height = image.size
    scaled_width = int(width * scale_factor)
    scaled_height = int(height * scale_factor)
    return image.resize((scaled_width, scaled_height))

def circle_crop(image):
    print("     Adding alpha layer to RGB...")
    np_image = np.array(image)
    h,w = image.size
    alpha = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(alpha)
    draw.pieslice([0,0,h,w],0,360,fill=255)
    np_alpha = np.array(alpha)
    np_image = np.dstack((np_image,np_alpha))
    return Image.fromarray(np_image)

def add_bg_and_flip(image):
    bg = Image.new("RGB", image.size, (255,255,255))
    bg.paste(image, image)
    bg = bg.transpose(method=Image.FLIP_TOP_BOTTOM)
    return bg

def proccess_image(circle_params, image_path):        
    with Image.open(image_path) as image:
        x, y, radius = circle_params
        
        print(f"     Circle detected at ({x}, {y}) with radius {radius}.")
        image_square_cropped = crop_image(image, circle_params)
        
        print(f"     Scaling circle to {DESIRED_DIAMETER} pixels...")
        scale_factor = DESIRED_DIAMETER / (2 * radius)
        image_scaled = scale_image(image_square_cropped, scale_factor)
        width, height = image_scaled.size

        print("     Adding alpha layer to RGB...")
        image_circle_cropped = circle_crop(image_scaled)

        print("     Converting PNG to JPG for PDF compatibility...")
        image_with_bg = add_bg_and_flip(image_circle_cropped)
        image_with_bg.save(TEMP_JPG_PATH, "JPEG")
    return width, height

def setup_directories_or_fail():
    # Check if the raws directory exists
    if not os.path.exists(RAWS_DIR):
        os.makedirs(RAWS_DIR, exist_ok=True)
        print(f"No images foundin the {RAWS_DIR} folder. Please add images to the directory and run the script again.")
        exit()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_temp():
    print("Cleaning up temporary files...")
    os.remove(TEMP_JPG_PATH)
    print("Temporary files removed.\n")

def get_num_images_or_fail():
    num_images = len([name for name in os.listdir(RAWS_DIR) if os.path.isfile(os.path.join(RAWS_DIR, name))])
    if num_images == 0:
        print("No images found in the raws directory. Please add images and run the script again.")
        exit()
    print(f"Number of images to convert: {num_images}")
    return num_images

def save_to_pdf(width, height, output_path):
    print(f"     Creating PDF at {output_path}...")
    canv = canvas.Canvas(output_path, pagesize=A4, bottomup=0)
    x_offset = (A4[0] - width) / 2
    y_offset = (A4[1] - height) / 2
    canv.drawImage(TEMP_JPG_PATH, x_offset, y_offset, width=width, height=height)
    print(f"     Saving PDF to {output_path}...")
    canv.save()

def proccess_one_image(image):
    image_path = os.path.join(RAWS_DIR, image)
    output_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(image)[0]}.pdf")
    circle_params = try_to_detect_circle(image_path)
    if not circle_params:
        print(f"     ERROR: No circle detected in {image_path}. Skipping...\n")
        return
    width, height = proccess_image(circle_params, image_path)

    save_to_pdf(width, height, output_path)

def loop_through_images(num_images, done = 0):
    print("Converting images to PDF...\n")
    for image in os.listdir(RAWS_DIR):
        print(f"=> Converting image {done + 1} of {num_images}...")
        proccess_one_image(image)
        done += 1
        print(f"== Image {done} of {num_images} done\n")
    print(">> Conversion complete <<\n")
    print("PDFs saved in the output directory.")

if __name__ == "__main__":
    setup_directories_or_fail()
    num_images = get_num_images_or_fail()
    loop_through_images(num_images)
    clean_temp()