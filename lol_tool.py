from riotwatcher import LolWatcher, TftWatcher, ApiError 
import requests
import urllib.request
import plotly.graph_objects as go
import os
import math
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
from plotly.subplots import make_subplots
from zipfile import ZipFile
import base64


class lol_tool():
    """
    class for creating a LoL item + TFT trait tracking tool
    API credit to riotwatcher: https://github.com/pseudonym117/Riot-Watcher
    game data and assets from Data Dragon
    
    """
    
    def __init__(self, my_region='na1', my_name='HarleymCjZh', APIkey='RGAPI-2b5d7eaa-16f8-4cbe-877e-1633666d1e50', champion='Ezreal'):
        self.region = my_region
        self.name = my_name
        self.APIkey = APIkey
        self.champion = champion
        self.lol_watcher = None
        self.tft_watcher = None
        self.matches = []
        self.champion_games = []
        self.item_lists = []
        self.win_list = []
        
        # tft_traits is a dictionary: {trait name: [avg placements of this trait, occurance of this trait]}
        self.tft_traits = dict()
        
        # link is a dictionary: {itemID: (item name, win rate associated with this item, occurance of this item )}
        self.links = dict()   
                
        # use caching to load the data if possible
        filename = 'traits.zip'
        if not os.path.exists(filename):
            #if icons not read before
            self.trait_master_icon = dict()
            url = 'https://static.developer.riotgames.com/docs/tft/set4update.zip'
            urllib.request.urlretrieve(url, os.getcwd()+'/'+filename)
        with ZipFile(os.getcwd()+'/'+filename, 'r') as zipObj:
           zipObj.extractall()
        self.path = os.getcwd()+'/traits'
        
        self.champion_win_rate = None # overall champion win rate
        r = requests.get('http://ddragon.leagueoflegends.com/cdn/11.6.1/data/en_US/item.json')
        self.item_master_list = r.json()
        r = requests.get('http://ddragon.leagueoflegends.com/cdn/11.6.1/data/en_US/champion.json')
        self.champion_master_list = r.json()
        
        self.plot_tft()
        self.plot_lol()
   
    
    def access_lol(self):
        """ test whether the LOL API is working currently
        """
        self.lol_watcher = LolWatcher(self.APIkey)
        try:
            response = self.lol_watcher.summoner.by_name(self.region, self.name)
            return response
        except ApiError as err:
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
                print('future requests wait until the retry-after time passes')
            elif err.response.status_code == 404:
                print('Summoner with that name not found.')
            elif err.response.status_code == 403:
                print('An invalid API key was provided with the API request.')
            else:
                raise
     
        
    def access_tft(self):
        """ test whether the TFT API is working currently
        """
        self.tft_watcher = TftWatcher(self.APIkey)
        try:
            response = self.tft_watcher.summoner.by_name(self.region, self.name)
            return response
        except ApiError as err:
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
                print('future requests wait until the retry-after time passes')
            elif err.response.status_code == 404:
                print('Summoner with that name not found.')
            elif err.response.status_code == 403:
                print('An invalid API key was provided with the API request.')
            else:
                raise
            
            
    def access_match_lol(self):
        """ access match history by LolWatcher
        this function has been tested on LoL Season 11 
        """
        me = self.access_lol()
        all_matches = self.lol_watcher.match.matchlist_by_account(self.region, me['accountId'],season=13)
        total_games_in_season = all_matches['totalGames']
        self.matches = all_matches['matches']
        print('Your LoL history:\nTotal games in this season is',total_games_in_season)
        
        if total_games_in_season > 100:
            count = math.ceil(total_games_in_season/100)
        for i in range(1,count):     
            temp = self.lol_watcher.match.matchlist_by_account(self.region, me['accountId'],\
                            begin_index=100*i+1,season=13)['matches']
            for j in temp:
                self.matches.append(j)
        
        # find id of the input champion name
        try:
            champion_id = self.champion_master_list['data'][self.champion]['key']
#            print('champion_id', champion_id)
        except:
            print("Champion name not found!")
            return 0
        
        # find games of this champion 
        for i in self.matches:
            if(str(i['champion']) == str(champion_id)):
                self.champion_games.append(i['gameId'])
            
        print('You have played ' + self.champion + ' ' + str(len(self.champion_games)) + ' time(s) in the current season!')
        return 1
    
    
    def access_match_tft(self):
        """ access 50 most recent match history by TFTWatcher and summarize traits
        this function has been tested on TFT set4 
        """
        me = self.access_tft()
        my_matches = self.tft_watcher.match.by_puuid('americas',me['puuid'],50)
        traits = dict()
        for match in my_matches:
            match_info = self.tft_watcher.match.by_id('americas',match)
            for p in match_info['info']['participants']:
                if p['puuid'] == me['puuid']:
                    placement = p['placement']
                    current_traits = p['traits']
                    for t in current_traits:
                        name = t['name']
                        style = t['style']
                        
                        #only count when style>=2, ow this trait is not dominating
                        if style >= 2: 
                            if name in traits.keys():
                                traits[name][0] += placement
                                traits[name][1] += 1
                            else:
                                traits[name] = [placement, 1]
                                
                    break
        for k,v in traits.items():
            self.tft_traits[k] = [round(v[0]/v[1], 2), v[1]]
            
        # sort dict by avg placement
        self.tft_traits = {k: v for k, v in sorted(self.tft_traits.items(), key=lambda item: item[1])}
        print('Your TFT history:\nName, Avg. Placement, #Played')
        for k,v in self.tft_traits.items():
            print(str(k)+', '+str(v[0])+', '+str(v[1]))
        print('\n') 
    
        
    def access_item(self):
        """ find items you bought when you played these games and whether you won or not
        """
        if self.access_match_lol() != 1:
            return
        
        for i in self.champion_games:
            match = self.lol_watcher.match.by_id(self.region, i)
            
            #there are 10 players each game and find where you are among these 10 players
            for j in range(10):
                if match['participantIdentities'][j]['player']['summonerName'] == self.name:
                    break           
            player = match['participants'][j]
            self.win_list.append(player['stats']['win'])
            self.item_lists.append([player['stats']['item0'],player['stats']['item1'],player['stats']['item2'],
                                    player['stats']['item3'],player['stats']['item4'],player['stats']['item5']])
    
        # find relationship between items and win rate
        flat_list = set(x for l in self.item_lists for x in l) #find unique item in your item_lists
        flat_list =  [i for i in flat_list if i > 0] #delete empty items (cuz empty item has ID=0)
        unique_names = []
        for i in flat_list:
            try:
                temp = self.item_master_list['data'][str(i)]['name']
            except:
                temp = None
            unique_names.append(temp) #find name of each item
        self.champion_win_rate = self.win_list.count(True)/len(self.champion_games)
        print(self.champion, 'win rate:', self.champion_win_rate)
        
        for idx, item in enumerate(flat_list):
            count_win = 0
            occur = 0
            count = 0
            for i in range(len(self.champion_games)):
                count += len([j for j, x in enumerate(self.item_lists[i]) if x == item])
                if self.item_lists[i].count(item) > 0:
                    occur += 1
                    if self.win_list[i] == True:
                        count_win += 1
            self.links[item] = tuple([unique_names[idx], count_win/occur, count])
            
        return 1
    
    
    def plot_tft(self):
        """plot graphs to visualize the impact of traits
        """
        self.access_match_tft()
        fig = go.Figure()
        
        # Create trace from data
        x_pos = [*range(1, len(self.tft_traits)+1)]
        y_pos = []; n = []; s = [];
        for k,v in self.tft_traits.items():
            n.append(k.split("Set4_")[-1])
            y_pos.append(v[0])
            s.append(math.sqrt(v[1]))
        fig.add_trace(go.Scatter(x=x_pos, y=y_pos, mode="markers", text=n))
        
        # Add images
        for name, image_x, image_y, image_s in zip(n, x_pos, y_pos, s):
            for file in os.listdir(self.path):
                if file.endswith(".png") and name.lower() in file.lower():
                    loc = os.path.join(self.path, file)
                    break
            with open(loc, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            # Add the prefix that plotly will want when using the string as source
            encoded_image = "data:image/png;base64," + encoded_string
            
            fig.add_layout_image(
                dict(
                    source=encoded_image,
                    x=image_x,
                    y=image_y,
                    xref="x",
                    yref="y",
                    sizex=0.2*image_s,
                    sizey=0.2*image_s,
                    xanchor='center',
                    yanchor='middle',
                    layer='above',
                ))
        
        # Configure other layout properties
        fig.update_layout(
            hovermode='x',
            xaxis = dict(
                     range = [0, len(self.tft_traits)+1],
                     showgrid = False, # thin lines in the background
                     zeroline = False, # thick line at x=0
                     visible = False  # numbers below
            ),
            yaxis = dict(
                    range = [0, 8],
                    showgrid = False, # thin lines in the background
                    zeroline = False, # thick line at x=0
            ),
            title_text="Trait Avg. Placement",
            height=1000,
            width=50*len(x_pos),
            template="plotly_white",
        )
        
        plot(fig, filename = 'tft.html')  
            
        
    def plot_lol(self):
        """ plot graphs to visualize the impact of items
        """
        if self.access_item() != 1:
            return
        
        # Create figure
        fig = go.Figure()
        
        # Create trace from data
        x_pos = [*range(1, len(self.links)+1)]
        y_pos = []; n = []; s = [];
        for v in self.links.values():
            n.append(v[0])
            y_pos.append(v[1])
            s.append(math.sqrt(v[2]))
        fig.add_trace(go.Scatter(x=x_pos, y=y_pos, mode="markers", text=n))
        fig.add_hline(y=self.champion_win_rate, opacity=0.5)
#        fig.add_trace(go.Scatter(x=x_pos, y=y_pos, marker=dict(size=s,color=x_pos)))
        
        # Add images
        for image_x, image_y, image_s, image_id in zip(x_pos, y_pos, s, self.links.keys()):
            fig.add_layout_image(
                dict(
                    source="http://ddragon.leagueoflegends.com/cdn/11.6.1/img/item/"+str(image_id)+".png",
                    x=image_x,
                    y=image_y,
                    xref="x",
                    yref="y",
                    sizex=0.5*image_s,
                    sizey=0.5*image_s,
                    xanchor='center',
                    yanchor='middle',
                    layer='above'
                ))
             
        # Configure other layout properties
        fig.update_layout(
            hovermode='x',
            xaxis = dict(
                     range = [0, len(self.links)+1],
                     showgrid = False, # thin lines in the background
                     zeroline = False, # thick line at x=0
                     visible = False  # numbers below
            ),
            yaxis = dict(
                    range = [self.champion_win_rate-0.8, self.champion_win_rate+0.8],
                    showgrid = False, # thin lines in the background
                    zeroline = False, # thick line at x=0
#                    visible = False  # numbers below
            ),
            title_text="Item vs Champion Winrate",
            height=600,
            width=50*len(x_pos),
            template="plotly_white",
        )
        
        # Configure axes
        fig.update_xaxes(title_text="Item")
        fig.update_yaxes(title_text="Win Rate", hoverformat=".3f")
        
        plot(fig, filename = 'lol.html')