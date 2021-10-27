from io import BytesIO

from PIL import Image


def process_photo(photo: bytes, resize: bool) -> bytes:
    im = Image.open(BytesIO(photo))
    max_size = max(*im.size)
    out_image = Image.new(im.mode, (max_size, max_size), "white")
    out_image.paste(im, box=((max_size - im.width) // 2, (max_size - im.height) // 2))
    if resize and max_size != 1080:
        out_image = out_image.resize((1080, 1080), Image.LANCZOS)
    with BytesIO() as image_io:
        out_image.save(image_io, format=im.format)
        return image_io.getvalue()
