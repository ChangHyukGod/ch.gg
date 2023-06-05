from unittest import result
from django.shortcuts import render
import requests
from django.utils import timezone
from django.shortcuts import  get_object_or_404
from .models import Post
from .forms import PostForm
from django.http import HttpResponse

# Create your views here.

def post_new(request):
    form = PostForm()
    return render(request, 'score/post_edit.html', {'form': form})

def post_list(request):
    #posts = 쿼리셋의 이름 (매개변수)
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    #request = 사용자가 요청하는 모든 것
    return render(request, 'score/post_list.html', {'posts':posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'score/post_detail.html', {'post': post})

#LOL 전적 검색
def score_view(request): #urls에 만들었던 함수
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request,'score/score_view.html',{'posts':posts})



#검색결과 함수
def search_result(request):
    if request.method == "GET":
        summoner_name = request.GET.get('search_text') #score_view html에서 넘겨 받은 text
 
        summoner_exist = False
        sum_result = {}
        solo_tier = {}
        team_tier = {}
        store_list1 = []
        store_list2 = []
        game_info = []

        api_key = 'RGAPI-7e838370-49f6-4ea3-9d8e-ae92de307087' #부여받은 api
 
 
        summoner_url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + str(summoner_name)    #소환사 정보 검색 - 넘겨받은 텍스트를 이용하여
        params = {'api_key': api_key}
        res = requests.get(summoner_url, params=params)
        # summoners_result = json.loads(((res.text).encode('utf-8')))
        if res.status_code == requests.codes.ok: #결과값이 정상적으로 반환되었을때만 실행하도록 설정(response200)
            summoner_exist = True
            summoners_result = res.json() #response 값을 json 형태로 변환시키는 함수
            if summoners_result: #만약 summorners_result가 값이 존재한다면
                sum_result['name'] = summoners_result['name'] # 소환사 닉네임
                sum_result['level'] = summoners_result['summonerLevel'] #소환사 레벨
                sum_result['profileIconId'] = summoners_result['profileIconId'] #소환사 프로필코드(프로필도 api를 통해서 받아야함)
                sum_result['puuid'] = summoners_result['puuid'] #puuid 코드

                icon_image = f"http://ddragon.leagueoflegends.com/cdn/13.10.1/img/profileicon/"+ str(summoners_result['profileIconId'])+".png"

                tier_url = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/" + summoners_result['id']    #소환사 티어(랭크게임) 검색
                tier_info = requests.get(tier_url, params=params)
                tier_info = tier_info.json()

                for t in tier_info:
                    if t["queueType"] == "RANKED_FLEX_SR":
                        team_tier['rank_type'] = '자유랭크 5:5'
                        team_tier['tier'] = t['tier']
                        team_tier['rank'] = t['rank']
                        team_tier['points'] = t['leaguePoints']
                        team_tier['wins'] = t['wins']
                        team_tier['losses'] = t['losses']
                    elif t["queueType"] == "RANKED_SOLO_5x5":
                        solo_tier['rank_type'] = '솔로랭크 5:5'
                        solo_tier['tier'] = t['tier']
                        solo_tier['rank'] = t['rank']
                        solo_tier['points'] = t['leaguePoints']
                        solo_tier['wins'] = t['wins']
                        solo_tier['losses'] = t['losses']


                gameinfo_url = "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/" + summoners_result[
                    'puuid'] + "/ids?start=0&count=20"
                gameinfo_info = requests.get(gameinfo_url, params=params)
                gameinfo_info = gameinfo_info.json()
                for i in gameinfo_info:
                    game_url = "https://asia.api.riotgames.com/lol/match/v5/matches/" + i
                    game_data = requests.get(game_url, params=params).json()
                    sublist = []

                    for j in range(len(game_data['info']['participants'])):



                        participant = game_data['info']['participants'][j]
                        player_info = {
                            'summonerName': participant['summonerName'],
                            'championName': participant['championName'],
                            'kills': participant['kills'],
                            'deaths': participant['deaths'],
                            'assists': participant['assists'],
                            'teamid': participant['teamId'],
                            'win': participant['win'],
                            'item0': participant['item0'],
                            'item1': participant['item1'],
                            'item2': participant['item2'],
                            'item3': participant['item3'],
                            'item4': participant['item4'],
                            'item5': participant['item5'],
                            'item6': participant['item6'],
                            'summoner1Id': participant['summoner1Id'],
                            'summoner2Id': participant['summoner2Id'],
                            'queueId': game_data['info']['queueId'],
                        }
                        sublist.append(player_info)
                        if len(sublist) == 10:  # sublist에 10개의 딕셔너리가 모이면 game_info에 추가
                            game_info.append(sublist)
                            sublist = []  # sublist 초기화
                    if sublist:  # 남은 딕셔너리가 있다면 game_info에 추가
                        game_info.append(sublist)
                item_image = "http://ddragon.leagueoflegends.com/cdn/13.10.1/img/item/"
                champ_image = "http://ddragon.leagueoflegends.com/cdn/13.10.1/img/champion/"
                print(game_info)
            return render(request, 'score/search_result.html', {
                'summoner_exist': summoner_exist,
                'summoners_result': sum_result,
                'solo_tier': solo_tier,
                'team_tier': team_tier,
                'icon_image': icon_image,
                'game_info': game_info,
                'item_image': item_image,
                'champ_image': champ_image,

            })



    