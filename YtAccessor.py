from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import webbrowser
import math
import json
import discord

# this class interfaces with Youtube's Data API v3 to get and set info for a given youtube account

class YtAccessor():
     
    built=''
    youtube=''
    
    
    def __init__(self):
        global built, youtube
        self.built=False
        
        #to find your developerKey, go to https://console.developers.google.com/apis/credentials, by now you shouldve followed the Youtube tutorials
        #in the README and have a project created. Once on this website, your key will be the "key" value under "API Keys"
        youtube = build('youtube', 'v3', developerKey='REPLACE THIS WITH THE ABOVE KEY ^^^^')
    
    
    
    def connect_to_yt(self):
        global built, youtube
        
        #the README will explain that you need a client_secrets.json file in the same file path as this file,
        #instrucitons to obtain: go to https://console.developers.google.com/apis/credentials, 
        #and click the download button on the line under "OAuth 2.0 Client IDs", rename accordingly and then you're done
        
        CLIENT_SECRETS = 'client_secrets.json'
        SCOPES = ['https://www.googleapis.com/auth/youtube']
        
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        auth_url, _ = flow.authorization_url(prompt='consent')
        webbrowser.open(auth_url)
        
        credentials = flow.run_console()
        youtube = build('youtube', 'v3', credentials=credentials)
        self.built=True
    
    
    
    
    def create_playlist(self, playlist_name, authorName, authorId):
        global youtube
        creators, description=['',]*2
        
        playlists = youtube.playlists().list(part='snippet', maxResults=25, mine=True).execute()
        for i in range(playlists['pageInfo']['totalResults']):
            if str.lower(playlists['items'][i]['snippet']['title']) == str.lower(playlist_name):
                return '"'+playlists['items'][i]['snippet']['title']+'" already exists! And yes, playlist names are case insensitive.',''
        
        # uncomment this if you want to store the user id of the person who created the playlist
        """
        with open('/whatever/your/directory/is/plistCreators.txt', 'r') as plistCreators:
            creators = json.load(plistCreators)
            creators.update({playlist_name : authorId})
        
        with open('/whatever/your/directory/is/plistCreators.txt', 'w') as plistCreators:
            json.dump(creators, plistCreators)
        """
        
        try:
            description = 'An assortment of tasteful songs, curated by '+authorName
            youtube.playlists().insert(
                part='snippet,status',
                body={
                    'snippet' : {
                        'title' : playlist_name,
                        'description' : description,
                        'defaultLanguage' : 'en'
                    },
                    'status' : {
                        'privacyStatus' : 'public'
                    }
                }).execute()
            return playlist_name, description
        
        except Exception as e:
            print(str(e))
            return ':x: Hmm... we might\'ve hit our quota for the day :/', ''
    
    
    
    
    #ATTENTION!!! if you choose to restrict who can delete playlists, uncomment the code in the following method and change the filepaths accordingly
    
    def delete_playlist(self, playlist_name): #, authorId):
        global youtube
        creators=''
        
        playlists = youtube.playlists().list(part='snippet', maxResults=25, mine=True).execute()
        playlistId=''
        
        for i in range(playlists['pageInfo']['totalResults']):
            if str.lower(playlists['items'][i]['snippet']['title']) == str.lower(playlist_name):
                playlist_name = playlists['items'][i]['snippet']['title']
                playlistId = playlists['items'][i]['id']
                break
        
        if playlistId=='':
            return ':x: That playlist either doesn\'t exist or has already been deleted.'
        else:
            #with open('/whatever/your/directory/is/plistCreators.txt', 'r') as plistCreators:
            #    creators = json.load(plistCreators)
            #    creators.pop(playlist_name)
        
            #with open('/whatever/your/directory/is/plistCreators.txt', 'w') as plistCreators:
            #    json.dump(creators, plistCreators)
            
            try:
                youtube.playlists().delete(id=playlistId).execute()
                return ':white_check_mark: Playlist "'+playlist_name+'" has been deleted.'
            except Exception as e:
                print(str(e))
                return ':x: Hmm... something probably went wrong on Youtube\'s side. That probably means we\'ve reached our quota for the day or hour or minute.'
    
  
    
    
    
    def addsong(self, playlist_name, song_link):
        global youtube
        playlists = youtube.playlists().list(part="snippet,contentDetails", maxResults=25, mine=True).execute()
        playlist=''
        
        videoId = song_link.split('=')[1].split('&')[0]
        video = youtube.videos().list(part="snippet", id=videoId).execute()
        video_name = video['items'][0]['snippet']['title']
        
        for i in range(playlists['pageInfo']['totalResults']):
            if str.lower(playlists['items'][i]['snippet']['title']) == str.lower(playlist_name):
                playlist=playlists['items'][i]
                break
        
        try:
            if playlist=='':       
                return 'You didn\'t pick a valid name for the playlist :/'
            else:
                request = youtube.playlistItems().insert(
                    part='snippet',
                    body = {
                        'snippet' : {
                            'playlistId' : playlist['id'],
                            'position' : 0,
                            'resourceId' : {
                                'kind' : 'youtube#video',
                                'videoId' : videoId
                            }
                        }
                    }).execute()
                return '`"'+video_name+'"` was added to `"'+playlist['snippet']['title']+'"` !'
        except:
            return 'Hmm, something went wrong, we might\'ve reached our quota for the day.'
            
    
    
    
    def get_playlist_names(self, pageNum):
        global youtube
        names=''
        maxpages=0
        
        playlists = youtube.playlists().list(part="snippet,contentDetails", maxResults=50, channelId=self.getChannelId()).execute()
        totalResults = playlists['pageInfo']['totalResults']
        if totalResults%10 == 0:
            maxpages = int( math.floor(totalResults/10.0) )
        else:
            maxpages = int( math.floor(totalResults/10.0) +1 )
        
        if pageNum > maxpages:
            pageNum = maxpages
        
        pageheader = str(pageNum)+'/'+str(maxpages)
        names += '`name : #ofsongs`'
        
        if pageNum == maxpages:
            for i in range((pageNum-1) *10, totalResults):
                playlist=playlists['items'][i]
                names += '\n'+str(i+1)+'. ['+playlist['snippet']['title'] +']'
                names += '(https://www.youtube.com/playlist?list='+playlist['id']+')'
                names += ' : '+str(playlist['contentDetails']['itemCount'])
        else:
            for i in range((pageNum-1) *10, pageNum*10):
                playlist=playlists['items'][i]
                names += '\n'+str(i+1)+'. ['+ playlist['snippet']['title'] +']'
                names += '(https://www.youtube.com/playlist?list='+playlist['id']+')'
                names += ' : '+str(playlist['contentDetails']['itemCount'])
            
        return pageheader, names 
    
    



    
    def get_playlist_link(self, playlist_name):
        global youtube
        playlist_link='https://www.youtube.com/playlist?list='
        desc, thumbnail_url=['',]
        
        playlists = youtube.playlists().list(part="snippet", maxResults=25, channelId=self.getChannelId()).execute()
        
        for i in range(playlists['pageInfo']['totalResults']):
            if str.lower(playlists['items'][i]['snippet']['title']) == str.lower(playlist_name):
                playlist_link += playlists['items'][i]['id']
                desc = playlists['items'][i]['snippet']['description']
                thumbnail_url = playlists['items'][i]['snippet']['thumbnails']['default']['url']
                playlist_name = playlists['items'][i]['snippet']['title']
                break
        
        if playlist_link == 'https://www.youtube.com/playlist?list=':
            playlist_link = 'The name you sent is invalid.'
        
        return playlist_link, desc, thumbnail_url, playlist_name
        
    
    
     
     
    
    def getChannelId(self):
        global built, youtube
     
        if self.built:
            channel = youtube.channels().list(part='snippet', mine=True).execute()
            return channel['items'][0]['id']
        else:
            return "THE CHANNEL ID THAT YOU WANT TO BE THE DEFAULT FOR THE BOT"
   
     
     
     
     
    def get_songs(self, playlist_name, pagenum):
        global youtube
        names, embedtitle, playlsitId, thumbnailUrl=['',]*4
        maxpage=0
        playlists = youtube.playlists().list(part="snippet", maxResults=25, channelId=self.getChannelId()).execute()
        
        for i in range(playlists['pageInfo']['totalResults']):
            if str.lower(playlists['items'][i]['snippet']['title']) == str.lower(playlist_name):
                playlistId = playlists['items'][i]['id']
                playlist_name = playlists['items'][i]['snippet']['title']
                thumbnailUrl = playlists['items'][i]['snippet']['thumbnails']['default']['url']
                break
        
        if playlistId == '':
            return '', '', '', ''
        
        playlistItems = youtube.playlistItems().list(part='snippet', maxResults=50, playlistId=playlistId).execute()
        totalResults = int( playlistItems['pageInfo']['totalResults'] )
        
        if totalResults%10 == 0:
            maxpages = int( math.floor(totalResults/10.0) )
        else:
            maxpages = int( math.floor(totalResults/10.0) +1 )
            
        if pagenum > maxpages:
            pagenum = maxpages
        
        embedtitle = '`Songs for "'+playlist_name+'"`'
        pageId = str(pagenum)+'/'+str(maxpages)
        
        npnum = int(pagenum/5)
        if pagenum%5 == 0:
            npnum -= 1
        
        if npnum > 0:
            for i in range(npnum):
                nextPageToken = playlistItems['nextPageToken']
                playlistItems = youtube.playlistItems().list(part='snippet', maxResults=50, playlistId=playlistId, pageToken=nextPageToken).execute()
        
        #we're at the end of the list
        if pagenum == maxpages:
            for i in range((10*pagenum) -(50*npnum) -10, totalResults - (50*npnum)):
                if len( str(playlistItems['items'][i]['snippet']['title']) ) > 40:
                    names += '\n'+str(i+1+(50*npnum))+'. ['+str(playlistItems['items'][i]['snippet']['title'])[:40]+'...]'
                    names +='(https://www.youtube.com/watch?v='+playlistItems['items'][i]['snippet']['resourceId']['videoId']+')'
                else:
                    names += '\n'+str(i+1+(50*npnum))+'. ['+str(playlistItems['items'][i]['snippet']['title'])+']'
                    names +='(https://www.youtube.com/watch?v='+playlistItems['items'][i]['snippet']['resourceId']['videoId']+')'
        else:
            
            #we're not @ the end of the playlist and have 10 guaranteed songs
            for i in range( (10*pagenum) -(50*npnum) - 10, (10*pagenum) - (50*npnum)):
                if len( str(playlistItems['items'][i]['snippet']['title']) ) > 40:
                    names += '\n'+str(i+1+(50*npnum))+'. ['+str(playlistItems['items'][i]['snippet']['title'])[:40]+'...]'
                    names +='(https://www.youtube.com/watch?v='+playlistItems['items'][i]['snippet']['resourceId']['videoId']+')'
                else:
                    names += '\n'+str(i+1+(npnum))+'. ['+str(playlistItems['items'][i]['snippet']['title'])+']'
                    names +='(https://www.youtube.com/watch?v='+playlistItems['items'][i]['snippet']['resourceId']['videoId']+')'
        
        return embedtitle, names, thumbnailUrl, pageId     
     
     
    



    def move_song(self, playlist_name, oldpos, newpos):
        global youtube
        playlistId=''
        playlist=''
        
        playlists = youtube.playlists().list(part="snippet", maxResults=25, mine=True).execute()
        
        for i in range(playlists['pageInfo']['totalResults']):
            if str.lower(playlists['items'][i]['snippet']['title']) == str.lower(playlist_name):
                playlist = playlists['items'][i]
                playlistId = playlists['items'][i]['id']
                playlist_name = playlists['items'][i]['snippet']['title']
                break
        
        if playlistId == '':
            return 'That\'s not a valid playlist.'
        else: 
            playlistItems = youtube.playlistItems().list(part='snippet', maxResults=100, playlistId=playlistId).execute()
            totalSongs = playlistItems['pageInfo']['totalResults']
        
            if oldpos+1 > totalSongs or newpos+1 > totalSongs:
                return 'That playlist doesn\'t have that many songs'
            else:
                itemId = playlistItems['items'][oldpos]['id']
                videoId = playlistItems['items'][oldpos]['snippet']['resourceId']['videoId']
                song_name = playlistItems['items'][oldpos]['snippet']['title']
            
                request = youtube.playlistItems().update(
                    part = 'snippet',
                    body = {
                        "id" : itemId,
                        "snippet" : {
                            "playlistId" : playlistId,
                            "position" : newpos,
                            "resourceId" : {
                                "kind" : "youtube#video",
                                "videoId" : videoId
                            }
                        }
                    } ).execute()
            
                if len(song_name) > 35:
                    return '"'+song_name[:35]+'..." has been moved to position '+str(newpos+1)+' in "'+playlist_name+'"'
                else:
                    return '"'+song_name+'" has been moved to position '+str(newpos+1)+' in "'+playlist_name+'"'
    
    
    
    
            
    #the song_link can be either from a search or a playlist (papa bless google for thinking ahead)
    def remove_song(self, playlist_name, song_link):

        global youtube
        playlistId=''
        videoName=''
        playlistItemId=''
        
        playlists = youtube.playlists().list(part="snippet", maxResults=25, mine=True).execute()
        videoId = song_link.split('=')[1].split('&')[0]
        
        if len(videoId) != 11:
            return 'The video id is wrong!'
        
        #user either: 1. only gave a link from a pl; or 2. gave link from pl and a pl name
        elif len(song_link.split('='))>2:
            
            playlistId = song_link.split('=')[2].split('&')[0]
            playlistItems = youtube.playlistItems().list(part='snippet', maxResults=100, playlistId=playlistId).execute() 
            
            # pl name
            for i in range(playlists['pageInfo']['totalResults']):
                if playlists['items'][i]['id'] == playlistId:
                    playlist_name = playlists['items'][i]['snippet']['title']
                    break
            
            # item id & vid name
            for i in range(playlistItems['pageInfo']['totalResults']):
                if playlistItems['items'][i]['snippet']['resourceId']['videoId'] == videoId:
                    playlistItemId = playlistItems['items'][i]['id']
                    videoName = playlistItems['items'][i]['snippet']['title']
                    break
            
            if playlist_name == '':
                return 'You have to include what playlist you want it removed from. Format the args as: <plName> <songURL> or <songURLfromPList>'
            elif videoName == '':
                return 'That video isn\'t in "'+playlist_name+'"'
            else:
                try:
                    youtube.playlistItems().delete(id=playlistItemId).execute()
                    return '"'+videoName+'"'+' has been removed from '+'"'+playlist_name+'"'
                except Exception as e:
                    print(str(e))
                    return 'Hmm... might\'ve hit the quota. Try again?'
            
        #user gave a bare video and a pl name
        else:
            
            # pl name & pl id
            for i in range(playlists['pageInfo']['totalResults']):
                if str.lower(playlists['items'][i]['snippet']['title']) == str.lower(playlist_name):
                    playlist_name = playlists['items'][i]['snippet']['title']
                    playlistId = playlists['items'][i]['id']
                    break
            
            playlistItems = youtube.playlistItems().list(part='snippet', maxResults=100, playlistId=playlistId).execute()
            
            # item id & vid name
            for i in range(playlistItems['pageInfo']['totalResults']):
                if playlistItems['items'][i]['snippet']['resourceId']['videoId'] == videoId:
                    playlistItemId = playlistItems['items'][i]['id']
                    videoName = playlistItems['items'][i]['snippet']['title']
                    break
            
            if playlistId == '':
                return 'That playlist name doesn\'t exist.'
            elif videoName == '':
                return 'That video isn\'t in "'+playlist_name+'"'
            else:
                try:
                    youtube.playlistItems().delete(id=playlistItemId).execute()
                    return '"'+videoName+'"'+' has been removed from '+'"'+playlist_name+'"'
                except Exception as e:
                    print(str(e))
                    return 'Hmm... something went wrong. Try again?'
                
            
                    
    def dump_playlist(self, playlist_name, ext_url):
        global youtube
        extId, intId, ext_name, extplaylists=['',]*4
        iters=0
        
        playlists = youtube.playlists().list(part="snippet", maxResults=25, mine=True).execute()
        for i in range(playlists['pageInfo']['totalResults']):
            if str.lower(playlists['items'][i]['snippet']['title']) == str.lower(playlist_name):
                playlist_name = playlists['items'][i]['snippet']['title']
                intId = playlists['items'][i]['id']
        
        if 'watch?v' in ext_url:
            extId = ext_url.split('=')[2].split('&')[0]
        else:
            extId = ext_url.split('=')[1]
        
        extplistItems = youtube.playlistItems().list(part='snippet', maxResults=50, playlistId=extId).execute()
        extchannelid = extplistItems['items'][0]['snippet']['channelId']
        extplaylists = youtube.playlists().list(part='snippet', maxResults=100, channelId=extchannelid).execute()
        
        for i in range(extplaylists['pageInfo']['totalResults']):
            if extId == extplaylists['items'][i]['id']:
                ext_name = extplaylists['items'][i]['snippet']['title']
        
        if intId == '':
            return 'That playlist in our database either doesn\'t exist or has been deleted.'
        elif ext_name == '':
            return 'The playlist link you sent doesn\'t link to a valid playlist :thinking:'
        else:
            try:
                for i in range(extplistItems['pageInfo']['totalResults']):
                    print(i)
                    videoId = extplistItems['items'][i-(iters*50)]['snippet']['resourceId']['videoId']
                    youtube.playlistItems().insert(
                        part='snippet',
                        body = {
                            'snippet' : {
                                'playlistId' : intId,
                                'position' : i,
                                'resourceId' : {
                                    'kind' : 'youtube#video',
                                    'videoId' : videoId
                                }
                            }
                        }).execute()
                    print(str(i-(iters*50))+' '+str(i)+'. '+extplistItems['items'][i-(iters*50)]['snippet']['title']+' has been copied')
                    if i == 49 and extplistItems.get('nextPageToken') is not None:
                        nextPageToken = extplistItems['nextPageToken']
                        extplistItems = youtube.playlistItems().list(part='snippet', maxResults=50, playlistId=extId, pageToken=nextPageToken).execute()
                        iters+=1
                    
                return 'All of the songs from `"'+ext_name+'"` have been copied to `"'+playlist_name+'"`'
            
            except Exception as e:
                print(str(e))
                return ('Darn, looks like we\'ve reached our quota for the time being, or there\'s a bug in my code. Check to see how many songs ' +
                    '- if any at all - got tranferred over to "'+playlist_name+'", and do the rest yourself if you want.')


          

# end          
