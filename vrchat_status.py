from bs4 import BeautifulSoup

import cairosvg, discord, io
from PIL import Image, ImageDraw, ImageFont

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.options import Options

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://status.vrchat.com/'

async def vrchat_status(message: discord.Message):
  print("Start load VRChat Status!")

  try:
    options = Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options)
    driver.get(url)

    # selenium 으로 차트가 로딩 될 때까지 기다린다
    element: WebElement = WebDriverWait(driver, 30).until(
      EC.presence_of_element_located((By.ID, 'vrccharts'))
    )

    # 로딩이 되었다면 차트를 찾아 가져온다
    html = BeautifulSoup(element.get_attribute('innerHTML'), 'html.parser')

    # 차트 정보를 for 문으로 돌려 전부 이미지로 변환한다
    vrchat_images = []
    for tag in html.find_all("div", "vrcchart"):
      title = tag.find("h3").text
      filename = title + ".png"
      
      # 받아온 차트 SVG 를 PNG 로 변환한다
      image_original = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=str(tag.find("svg")))))
      
      # PNG 이미지에 타이틀을 넣기 위해 불러와서 이미지 위에 빈칸을 만든다
      image_modified = Image.new(image_original.mode, (image_original.width, image_original.height + 26))
      image_modified.paste(image_original, (0, 26))

      # 타이틀을 이미지에 넣는다
      drawer = ImageDraw.Draw(image_modified)
      # 폰트를 가져온다
      font = ImageFont.truetype("neodgm.ttf", 16)
      # 글자를 미리 그려서 글자가 몇픽셀인지 가져옴
      _, _, text_width, _ = drawer.textbbox((0, 0), title, font=font)
      # 원래 이미지 너비 - 글자 길이 빼서 중앙정렬 한 타이틀을 이미지에 씀
      drawer.text(((image_modified.width - text_width) / 2, 8), f'{title}', (255, 255, 255), font=font)

      # 변환한 이미지를 메모리에 저장한다
      bytes_io = io.BytesIO()
      image_modified.save(bytes_io, format='PNG')
      bytes_io.seek(0)
      # 메모리에 저장 해 둔 이미지를 디스코드 파일로 인식 시킨다
      vrchat_images.append(discord.File(bytes_io, filename))

    # embed = discord.Embed(title="뭬밀냥이 제공하는 VRChat 상태에요!")
    await message.channel.send("뭬밀냥이 제공하는 VRChat 상태에요!", files=vrchat_images)
    print("VRChat Status was Loaded Successfully!")
  except Exception:
    # embed = discord.Embed(title="VRChat 상태를 가져오지 못 했어요...")
    await message.channel.send("VRChat 상태를 가져오지 못 했어요...")
    print("Failed load VRChat Status!")
  finally:
    driver.quit()

# html = response.text
# soup = BeautifulSoup(html, 'html.parser')
# print(soup)