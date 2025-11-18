import base64

import magic


def encode_base64_embedded(imageData: bytes) -> str:
    """
    Encode the image data in base64 and return the string to be used in html
    Args:
        imageData: the image data to be encoded
    Returns:
        the base64 encoded image
    """
    themagic = magic.from_buffer(imageData, mime=True)
    if not themagic.startswith('image/'):
        raise ValueError(f"Data is not an image. Magic says: {themagic}")
    return f"data:{themagic};base64,{base64.b64encode(imageData).decode('utf-8')}"