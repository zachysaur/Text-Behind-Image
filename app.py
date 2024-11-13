import gradio as gr
from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy as np
import os
import io
from rembg import remove
import uuid

def add_text_with_stroke(draw, text, x, y, font, text_color, stroke_width):
    """Helper function to draw text with stroke"""
    for adj_x in range(-stroke_width, stroke_width + 1):
        for adj_y in range(-stroke_width, stroke_width + 1):
            draw.text((x + adj_x, y + adj_y), text, font=font, fill=text_color)

def remove_background(image):
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()
    output = remove(img_bytes)
    return Image.open(io.BytesIO(output))

def superimpose(image_with_text, overlay_image):
    overlay_image = overlay_image.convert("RGBA")
    image_with_text.paste(overlay_image, (0, 0), overlay_image)
    return image_with_text

def add_text_to_image(
    input_image,
    text,
    font_size,
    color,
    opacity,
    x_position,
    y_position,
    thickness
):
    if input_image is None:
        return None
    
    image = Image.fromarray(input_image)
    overlay_image = remove_background(image)

    txt_overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_overlay)
    
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", int(font_size))
    except:
        try:
            font = ImageFont.truetype("arial.ttf", int(font_size))
        except:
            font = ImageFont.load_default()
    
    # Convert the color string to RGB by stripping alpha if necessary
    if color.startswith("rgba"):
        rgb_values = color[5:-1].split(",")[:3]
        rgb_color = tuple(int(float(c)) for c in rgb_values)
    else:
        rgb_color = ImageColor.getrgb(color)

    text_color = (*rgb_color, int(opacity))
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    actual_x = int((image.width - text_width) * (x_position / 100))
    actual_y = int((image.height - text_height) * (y_position / 100))

    add_text_with_stroke(draw, text, actual_x, actual_y, font, text_color, int(thickness))

    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    output_image = Image.alpha_composite(image, txt_overlay)
    output_image = output_image.convert('RGB')

    output_image = superimpose(output_image, overlay_image)
    
    return np.array(output_image)

def create_interface():
    with gr.Blocks() as app:
        gr.Markdown("# Add Text Behind Image")
        gr.Markdown("Upload an image and customize text properties to add text overlay.")
        
        with gr.Row():
            with gr.Column():
                input_image = gr.Image(label="Upload Image", type="numpy")
                text_input = gr.Textbox(label="Enter Text", placeholder="Type your text here...")
                font_size = gr.Slider(minimum=10, maximum=800, value=400, step=10, label="Font Size")
                thickness = gr.Slider(minimum=0, maximum=20, value=0, step=1, label="Text Thickness")
                color_picker = gr.ColorPicker(value="#FFFFFF", label="Text Color")
                opacity_slider = gr.Slider(minimum=0, maximum=255, value=255, step=1, label="Opacity")
                x_position = gr.Slider(minimum=0, maximum=100, value=50, step=1, label="X Position (%)")
                y_position = gr.Slider(minimum=0, maximum=100, value=50, step=1, label="Y Position (%)")
                
            with gr.Column():
                output_image = gr.Image(label="Output Image")
        
        process_btn = gr.Button("Add Text to Image")
        
        process_btn.click(
            fn=add_text_to_image,
            inputs=[
                input_image,
                text_input,
                font_size,
                color_picker,
                opacity_slider,
                x_position,
                y_position,
                thickness
            ],
            outputs=output_image
        )
        
        gr.Examples(
            examples=[
                [
                    "pink_convertible.webp",
                    "EPIC",
                    420,
                    "#800080",
                    150,
                    50,
                    21,
                    9
                ],
                [
                    "pear.jpg",
                    "PEAR",
                    350,
                    "#000000",
                    100,
                    50,
                    2,
                    5
                ],
                [
                    "sample_text_image.jpeg",
                    "LIFE",
                    400,
                    "#000000",
                    150,
                    50,
                    2,
                    8
                ],
            ],
            inputs=[
                input_image,
                text_input,
                font_size,
                color_picker,
                opacity_slider,
                x_position,
                y_position,
                thickness
            ],
            outputs=output_image,
            fn=add_text_to_image,
            cache_examples=True,
        )

    return app

if __name__ == "__main__":
    try:
        import subprocess
        subprocess.run(['apt-get', 'update'])
        subprocess.run(['apt-get', 'install', '-y', 'fonts-dejavu'])
        print("Font installed successfully")
    except:
        print("Could not install font automatically. Please install DejaVu font manually.")
    
    app = create_interface()
    app.launch(share=True)
