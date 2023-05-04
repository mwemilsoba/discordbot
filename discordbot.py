# -*- coding:utf-8 -*- 

import discord, random, re, yt_dlp, platform, ctypes, ctypes.util, openai, requests, json, urllib.request
from bs4 import BeautifulSoup

####################################################################
token = ""
####################################################################
openai.api_key = "s"
model_engine = "text-davinci-003"
####################################################################
papago_trans_url = "https://openapi.naver.com/v1/papago/n2mt"
client_id = ""
client_secret = ""
####################################################################
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
####################################################################

# Opus 코덱 로딩
find_opus = ctypes.util.find_library('opus')
try: 
    if platform.system() == 'Darwin': # 만약 뭬밀이 맥을 쓰고 있다면
        discord.opus.load_opus('/opt/homebrew/lib/libopus.dylib')
    elif platform.system() == 'Linux': # 만약 뭬밀이 리눅스를 쓰고 있다면
        discord.opus.load_opus(find_opus)
    else: # 아마 윈도우일거임
        discord.opus.load_opus('libopus.dll')
except:
    print("OPUS Codec needed!!!")
    raise Exception('Opus failed to load')

#주식
headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'}

async def get_stock_price(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    stock_price = soup.select_one('#chart_area > div.rate_info > div > p.no_today > em > span').get_text() + '원'
    return stock_price

async def result_stock_price():
    urls = {
        '삼성전자': 'https://finance.naver.com/item/main.nhn?code=005930',
        '삼성전자우': 'https://finance.naver.com/item/main.naver?code=005935',
        '삼성전기': 'https://finance.naver.com/item/main.nhn?code=009150',
        '삼성SDI': 'https://finance.naver.com/item/main.nhn?code=006400',
        '삼성바이오로직스': 'https://finance.naver.com/item/main.naver?code=207940',
        '삼성중공업': 'https://finance.naver.com/item/main.naver?code=010140',
        '삼성생명': 'https://finance.naver.com/item/main.naver?code=032830',
        '삼성엔지니어링': 'https://finance.naver.com/item/main.naver?code=028050'
    }
    embed = discord.Embed(title="삼성주식 정보랑께!", color=0x0000ff)
    for name, url in urls.items():
        stock_price = await get_stock_price(url)
        embed.add_field(name=name, value=stock_price, inline=True)
    return embed

    
# music bot
async def music_start(message):
    YTurl_pattern = re.compile('(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))')   # 정규 표현식 컴파일
    if len(message.content.split(" ")) <= 1:
        await message.channel.send(embed=discord.Embed(title=":no_entry_sign: url을 제대로 입력해줘!!", color=0x2EFEF7))
        return
    url_test = YTurl_pattern.match(message.content.split(" ")[1])
    if not url_test:
        await message.channel.send(embed=discord.Embed(title=":no_entry_sign: url을 제대로 입력해줘!!", color=0x2EFEF7))
        return
    # 봇이 음성 채널에 연결되어있는지 확인
    voice_client = message.guild.voice_client
    if not voice_client:
        # 음성 채널에 연결되어있지 않은 경우, 음성 채널에 연결
        voice_state = message.author.voice
        if not voice_state:
            await message.channel.send("음성 채널에 먼저 들어가!!")
            return
        else:
            voice_channel = message.author.voice.channel
            voice_client = await voice_channel.connect()
    else:
        # 음성 채널에 이미 연결되어있는 경우, 노래를 재생 중인지 확인
        if voice_client.is_playing():
            await message.channel.send("이미 재생중이야!")
            return
    # 재생 관련 코드
    YDL_OPTIONS = {'format': 'bestaudio/best','noplaylist':'True', 'writesubtitles':'writesubtitles','writethumbnail':'writethumbnail'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -b:a 320k'} # audio bitrate 320kbps setting
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url_test.group(), process=False)
        URL = info['formats'][0]['url']
        preferred_asr = [48000, 44100]
        for video_fm in sorted(info['formats'], key=lambda x: x['quality'] if 'quality' in x else 0, reverse=True):
            if video_fm['asr'] in preferred_asr:
                URL = video_fm['url']
                print(f"음질 선택 성공! -> {video_fm['format_note']}")
                break
        if not URL:
            await message.channel.send(f"{message.author.mention} 제가 잘 알아봤는데요, 소리를 틀수가 없는데요???")
            return
        audio_source = await discord.FFmpegOpusAudio.from_probe(URL, **FFMPEG_OPTIONS)
    # 해당 음성 채널에서 노래 재생
    voice_client.play(audio_source)

async def music_disconnect(message):
    await client.voice_clients[0].disconnect()
    await message.channel.send("힝ㅠㅜㅠㅜ")

async def music_pause(message):
    if not client.voice_clients[0].is_paused():
        client.voice_clients[0].pause()
    else:
        await message.channel.send("already playing!!")

async def music_resume(message):
    if client.voice_clients[0].is_paused():
        client.voice_clients[0].resume()
    else:
        await message.channel.send("already playing!")

async def music_stop(message):
    if client.voice_clients[0].is_playing():
        client.voice_clients[0].stop()
    else:
        await message.channel.send("not playing!")

#파파고번역
async def papago_trans(message):
    source_lang = message.content[4:6]
    target_lang = message.content[7:9]
    original_TXT = message.content[10:]
    encTXT = urllib.parse.quote(message.content[10:])
    papago_data = f'source={source_lang}&target={target_lang}&text=' + encTXT
    request = urllib.request.Request(papago_trans_url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request, data=papago_data.encode('utf-8'))
    rescode = response.getcode()
    if rescode == 200:  
        response_body = response.read()
        decode = json.loads(response_body.decode('utf-8'))
        trans_result = decode['message']['result']['translatedText']
        embed = discord.Embed(title="뭬파고 번역 결과", color=0x70d1f4)
        embed.add_field(name="원문 내용", value=original_TXT, inline=False)
        embed.add_field(name="번역된 내용", value=trans_result, inline=False)
        return embed
    else:
        print('Error Code: ' + str(rescode))

#ChatGPT 실행코드
async def ChatGPT(message):
    gpt_Q = message.content[6:]    # remove $chat part
    reply = openai.Completion.create(model=model_engine, prompt=gpt_Q, max_tokens=4000)
    gpt_text = reply.choices[0].text    # 여기에 .strip() 추가하면 선행 공백을 지울수 있다
    return gpt_text

@client.event
async def on_ready():

    # discord.Status.online에서 online을 dnd로 바꾸면 "다른 용무 중", idle로 바꾸면 "자리 비움"
    await client.change_presence(status=discord.Status.online, activity=discord.Game("뭬밀소바봇 가동중"))
    print(client.user.name) # 봇의 이름을 출력합니다.
    print(client.user.id) # 봇의 Discord 고유 ID를 출력합니다.

    @client.event
    async def on_message(message):
        if message.author == client.user:             # 채팅을 친 사람이 봇일경우
            return

        if message.content.startswith("뭬밀!"):
            message.content = message.content.replace("뭬밀! ","")  # 뭬밀! 문자열에서 제거
            messagesplit = message.content.split("vs")  # vs 기준으로 문자열 리스트화
            rmsg = random.choice(messagesplit)  # 리스트화된 messagesplit에서 랜덤으로 추출
            await message.channel.send(f"{message.author.mention} {rmsg}")

        if message.content == "뭬밀 삼성주식":
            embed = await result_stock_price()
            await message.channel.send(f"{message.author.mention} ""자, 여기!", embed=embed)
        
        if message.content == "뭬밀 내정보":
            data_format = "%Y-%m-%d @ %p %I:%M:%S"
            embed = discord.Embed(title=message.author, color=0x70d1f4)
            embed.set_thumbnail(url=message.author.avatar)
            embed.add_field(name="유저ID", value=message.author.id, inline=False)
            embed.add_field(name="계정 생성일", value=message.author.created_at.strftime(data_format), inline=True)
            embed.add_field(name="서버 입장일", value=message.author.joined_at.strftime(data_format), inline=True)
            await message.channel.send(f"{message.author.mention}", embed=embed)

# 음악봇
        if message.content.startswith("이거틀어줘!"):  #음성채널에 봇 추가 및 음악재생
            await music_start(message)

# 음악봇 나가기
        if message.content == "뭬밀 나가!!":
            await music_disconnect(message)

# 음악봇 일시정지
        if message.content == "뭬밀 일시정지!":
            await music_pause(message)
        
# 음악봇 다시재생
        if message.content == "뭬밀 다시재생!":
            await music_resume(message)
        
# 음악봇 정지
        if message.content == "뭬밀 정지!":
            await music_stop(message)

# ChatGPT
        if message.content.startswith("$chat"):
            gpt_text = await ChatGPT(message)
            await message.channel.send(f"{message.author.mention} {gpt_text}")

# 파파고번역
        if message.content.startswith("!번역"):
            embed = await papago_trans(message)
            await message.channel.send(f"{message.author.mention}", embed=embed)

client.run(token)