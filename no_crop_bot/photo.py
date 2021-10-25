from io import BytesIO

from PIL import Image


def process_photo(photo: bytes) -> bytes:
    with BytesIO(photo) as in_photo_io, BytesIO() as out_photo_io:
        im: Image.Image
        with Image.open(in_photo_io) as im:
            max_size = max(*im.size)
            out_image = Image.new(im.mode, (max_size, max_size), "white")
            out_image.paste(im,
                            box=(int((max_size - im.width) / 2),
                                 int((max_size - im.height) / 2))
                            )
            out_image.save(out_photo_io, format=im.format)
            return out_photo_io.getvalue()
