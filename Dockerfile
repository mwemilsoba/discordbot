FROM python:3.11-bullseye

ADD requirements.txt .

RUN apt update && apt install -y libopus0 ffmpeg firefox-esr && pip3 install --no-cache-dir -r requirements.txt

ADD . .

CMD [ "python3", "discordbot.py" ]