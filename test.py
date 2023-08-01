from wand.image import Image
from wand.color import Color
from wand.font import Font
from wand.drawing import Drawing
import math

with Image(filename="james.jpg") as temp_img:
    x, y = temp_img.width, temp_img.height
    
    caption_text = "the quick brown"

    font_size = round(64 * (x/720))
    bar_height = math.ceil(len(caption_text)/25)
    if bar_height < 1: bar_height = 1 

    font = Font(path="bot/resources/caption_font.otf", size=font_size)

    with Image(width = x, height = y, background=Color("white")) as bg_image:
        bg_image.caption(text=caption_text, gravity="north", font=font)
        with Drawing() as context:
            metrics = context.get_font_metrics(bg_image, caption_text, False)
            print(metrics.text_height)
        bg_image.save(filename="temp_out.png")

    # with Image(width = x, height = y + 60*bar_height, background=Color("white")) as bg_image:
    #     bg_image.composite(temp_img, left = 0, top = 60*bar_height)
    #     bg_image.caption(text=caption_text, gravity="north", font=font)
    #     bg_image.save(filename="temp_out.png")


    