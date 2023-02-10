import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from io import BytesIO

def get_num_img(image, fontsize):
    dot_img = np.array(image)

    # 使うフォント，サイズ，描くテキストの設定
    # デフォルトフォントでは文字サイズ取得不可
    # C:\Windows\Fonts\meiryob.ttc
    ttfontname = r"meiryob.ttc"

    # 画像サイズ，背景色，フォントの色を設定
    m = 30
    canvasSize    = (dot_img.shape[1] * m, dot_img.shape[0] * m)
    backgroundRGB = (255, 255, 255)
    textRGB       = (0, 0, 0)

    # 文字を描く画像の作成
    img  = Image.new('RGB', canvasSize, backgroundRGB)
    draw = ImageDraw.Draw(img)

    # 用意した画像に文字列を描く
    font = ImageFont.truetype(ttfontname, fontsize)

    n = 1
    for y in range(dot_img.shape[0]):
      for x in range(dot_img.shape[1]):
        if not np.all(dot_img[y][x]==255):
          textWidth, textHeight = draw.textsize(str(n),font=font)
          textTopLeft = (x * canvasSize[0] // dot_img.shape[1] + canvasSize[0] // (dot_img.shape[1] * 2) - textWidth // 2, y * canvasSize[1] // dot_img.shape[0] + canvasSize[1] // (dot_img.shape[0] * 2) - textHeight // 2)
          draw.text(textTopLeft, str(n), fill=textRGB, font=font)
          # draw.multiline_text(textTopLeft, str(n), font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
          n += 1

    # img.save('num_' + name)

    # 背景透過処理
    img = np.array(img)
    mask = np.all(img > [150, 150, 150], axis=-1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    img[mask,3] = 0

    img = Image.fromarray(img)

    return img

def save_num_img(image, fontsize, name):
    img = get_num_img(image, fontsize)
    img.save(name)

def get_exp_img(image, height, width):

    dot_img = np.array(image)

    x1 = width // dot_img.shape[1]
    y1 = height // dot_img.shape[0]

    img = np.ndarray(shape=(height, width, 3), dtype='uint8')

    for y in range(height):
      for x in range(width):
        img[y][x] = dot_img[y // y1][x // x1][:3]

    img = Image.fromarray(img)
    img.putalpha(alpha=255)

    return img

def save_exp_img(image, height, width, name):
    img = get_exp_img(image, height, width)
    img.save(name)

def get_numd_img(image, num_image):
    layer2 = num_image
    layer1 = get_exp_img(image, layer2.height, layer2.width)

    # layer1と同じ大きさの画像を全面透過で作成
    c = Image.new('RGBA', layer1.size, (255, 255, 255, 0))
    c.paste(layer2, (0,0), layer2)
    img = Image.alpha_composite(layer1, c)

    return img

def save_numd_img(image, num_image, name):
    img = get_numd_img(image, num_image)
    img.save(name)

def main():

    # タイトルの表示
    st.title("Pixel Art Numbering System")

    # アップローダの作成
    uploaded_file = st.file_uploader("Choose a Image...", type="png")

    # 画像がアップロードされた場合...
    if uploaded_file is not None:

        # 画像を画面に表示
        image = Image.open(uploaded_file)
        # st.image(image, caption='Uploaded Image.', use_column_width=True)
        # st.write("")
        # st.write("Classifying...")

        if image.height * image.width > 999:
            st.error('画像ファイルが大きすぎます', icon="🚨")
            st.write("縦×横が999以内のファイルを指定してください")
            st.write("縦ピクセル：" + str(image.height))
            st.write("横ピクセル：" + str(image.width))
        else:
            num_img = get_num_img(image, 10)
            exp_img = get_exp_img(image, num_img.height, num_img.width)
            numd_img = get_numd_img(image, num_img)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.image(exp_img, caption='Expansion Image.', use_column_width=True)
                buf = BytesIO()
                exp_img.save(buf, format="png")
                byte_im = buf.getvalue()
                st.download_button(label="Download image1", data=byte_im, file_name='exp_' + uploaded_file.name, mime="image/png")

            with col2:
                st.image(num_img, caption='Number Image.', use_column_width=True)
                buf = BytesIO()
                num_img.save(buf, format="png")
                byte_im = buf.getvalue()
                st.download_button(label="Download image2", data=byte_im, file_name='num_' + uploaded_file.name, mime="image/png")

            with col3:
                st.image(numd_img, caption='Numbered Image.', use_column_width=True)
                buf = BytesIO()
                numd_img.save(buf, format="png")
                byte_im = buf.getvalue()
                st.download_button(label="Download image3", data=byte_im, file_name='numd_' + uploaded_file.name, mime="image/png")

if __name__ == "__main__":
    main()
