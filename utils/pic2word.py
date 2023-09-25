import io
import requests

from io import BytesIO
from PIL import Image, ImageOps
from paddleocr import PaddleOCR


def pic2word(ocr, url, cookies):
    response = requests.get(url, cookies=cookies)

    # 对image进行填充否则无法识别
    image = Image.open(BytesIO(response.content))
    padded_image = ImageOps.expand(image, border=50, fill=(255, 255, 255))

    # 将padded_image转换成byte类型
    image_bytes = io.BytesIO()
    padded_image.save(image_bytes, format='PNG')
    image_bytes = image_bytes.getvalue()
    result = ocr.ocr(image_bytes)
    if result:
        return result[0][0][1][0]
    else:
        return None


if __name__ == '__main__':
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    a = {'class': 'dictimgtoword', 'src': 'https://www.frdic.com/tmp/wordimg/NSR595kr5B3jQaozV2p5OuQ9z3M=.png'}
    print(pic2word(a['src'], ocr))
