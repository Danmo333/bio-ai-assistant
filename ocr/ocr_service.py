import easyocr

reader = easyocr.Reader(['ch_sim','en'])

def recognize_text(image_path):

    result = reader.readtext(image_path)

    text = ""

    for item in result:
        text += item[1] + "\n"

    return text