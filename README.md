취미로 python 언어로 작성한 디스코드봇 입니다.
프로그래밍언어를 배우지 않은 상태로 작성한 코드이기 때문에 코드가 이상할수도 있고 더 최적화가 가능할수도 있습니다.
그렇기 때문에 욕설은 하지 말아주세요 ㅜㅜ 문제점이나 제안 지적은 환영이에요~~


- 현재 제가 알고 있는 소스 코드 문제점 -
1) 파파고 번역 기능. 한국어(ko)<->일본어(ja) 처럼 언어코드가 2글자인경우만 사용 가능합니다.
중국어 간체(zh-chs), 중국어 번체(zh-cht) 같은 경우 안됩니다. <- 나중에 고칠꺼임

2) discord.opus.load_opus()를 통해 opus코덱을 로드합니다.
윈도우의 경우 자동으로 로드되므로 이 함수를 호출할 필요가 없다고 적혀있습니다.
else: # 아마 윈도우일거임
    discord.opus.load_opus('libopus.dll')
이부분이 문제가 생길수도 있을지도? OS가 Windows경우 작동 테스트 안해봄
On Windows, this function should not need to be called as the binaries are automatically loaded.
pip install -r requirements.txt 명령어를 통해 봇 제작시 사용된 패키지를 모두 설치 할수 있습니다.
필요없는 패키지나 누락된 패키지가 있을수도 있으니 참고해주세요