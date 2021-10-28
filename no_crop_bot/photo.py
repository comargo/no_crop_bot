from io import BytesIO
from typing import Optional, Any

from PIL import Image, ImageFilter


def process_photo(photo: bytes, resize: bool, blur: int) -> bytes:
    in_image: Image.Image = Image.open(BytesIO(photo))
    max_size = max(*in_image.size)
    out_image: Optional[Image.Image] = None
    if blur:
        out_image = in_image.resize(size=(max_size, max_size),
                                    resample=Image.NEAREST).filter(
            ImageFilter.BoxBlur(blur)
        )
    else:
        out_image = Image.new(in_image.mode, (max_size, max_size), "white")
    out_image.paste(in_image, box=(
        (max_size - in_image.width) // 2, (max_size - in_image.height) // 2))
    if resize and max_size != 1080:
        out_image = out_image.resize((1080, 1080), Image.BICUBIC)
    with BytesIO() as image_io:
        out_image.save(image_io, format=in_image.format)
        return image_io.getvalue()
