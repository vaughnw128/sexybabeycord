"""
    Magick_helper

    Handles some useful stuff for working with ImageMagick

    Made with love and care by Vaughn Woerpel
"""

# builtin
import math

import cv2

# external
from wand.color import Color
from wand.font import Font
from wand.image import Image

# project modules
from bot import constants


async def caption(fname: str, caption_text: str) -> str:
    """Adds a caption to images and gifs with image_magick"""
    try:
        with Image(filename=fname) as temp_img:
            x, y = temp_img.width, temp_img.height
            font_size = round(64 * (x / 720))
            bar_height = int(math.ceil(len(caption_text) / 25) * (x / 8))
            if bar_height < 1:
                bar_height = 1
            font = Font(path="bot/resources/caption_font.otf", size=font_size)

            # Checks gif vs png/jpg
            if fname.endswith("gif"):
                with Image() as dst_image:
                    with Image(filename=fname) as src_image:
                        # Coalesces and then distorts and puts the frame buffers into an output
                        src_image.coalesce()
                        for frame in src_image.sequence:
                            with Image(image=frame) as frameimage:
                                x, y = frame.width, frame.height
                                if x > 1 and y > 1:
                                    with Image(
                                        width=x,
                                        height=y + bar_height,
                                        background=Color("white"),
                                    ) as bg_image:
                                        bg_image.composite(
                                            frameimage, left=0, top=bar_height
                                        )
                                        bg_image.caption(
                                            text=caption_text,
                                            gravity="north",
                                            font=font,
                                        )
                                        dst_image.sequence.append(bg_image)
                    dst_image.optimize_layers()
                    dst_image.optimize_transparency()
                    dst_image.save(filename=fname)
            else:
                with Image(
                    width=x, height=y + bar_height, background=Color("white")
                ) as bg_image:
                    bg_image.composite(temp_img, left=0, top=bar_height)
                    bg_image.caption(text=caption_text, gravity="north", font=font)
                    bg_image.save(filename=fname)

        return fname
    except Exception:
        return None


async def distort(fname: str) -> str:
    """Handles the distortion using ImageMagick"""

    with Image(filename=fname) as src_image:
        # Checks gif vs png/jpg
        if fname.endswith("gif"):
            src_image.coalesce()
            with Image() as dst_image:
                # Coalesces and then distorts and puts the frame buffers into an output
                for frame in src_image.sequence:
                    frameimage = Image(image=frame)
                    x, y = frame.width, frame.height
                    if x > 1 and y > 1:
                        frameimage.liquid_rescale(
                            round(x * constants.Distort.ratio),
                            round(y * constants.Distort.ratio),
                        )
                        frameimage.resize(x, y)
                        dst_image.sequence.append(frameimage)
                dst_image.optimize_layers()
                dst_image.optimize_transparency()
                dst_image.save(filename=fname)
        else:
            # Simple distortion
            x, y = src_image.width, src_image.height
            src_image.liquid_rescale(
                round(x * constants.Distort.ratio), round(y * constants.Distort.ratio)
            )
            src_image.resize(x, y)
            src_image.save(filename=fname)
    return fname


async def get_faces(fname: str) -> list[tuple]:
    """Gets the faces using opencv-python"""

    # Load the cascade
    face_cascade = cv2.CascadeClassifier(
        "bot/resources/haarcascade_frontalface_default.xml"
    )

    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    found_faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    faces = []

    for x, y, w, h in found_faces:
        faces.append((x, y, w, h))

    return faces
