import discord
import asyncio
from YtAccessor import YtAccessor
from discord.ext import commands

#this methods in this class make requests to the YtAccessor depending on the level of authorization required for requests (viewing a pList vs. adding to one)
#and the YtAccessor class interfaces with Youtube's Data API to manage our Youtube channel

class music(commands.Cog):
    
    def __init__(self, bot):
        global ytaccessor
        ytaccessor = YtAccessor() #builds an api class that can only read from yt, not write, so that you dont have to do OAuth every time you want to access YT
        self.bot = bot
        
    
    global ytaccessor
    
    
    #need to call this to make changes to the Youtube channel (adding/deleting songs & playlists), otherwise you can make read-only requests
    
    @commands.command(help='connects the bot to YT; CALL B4 EDITING')
    async def connectyt(self, ctx):
        global ytaccessor
        
        if ytaccessor.built:
            await ctx.send('You\'re already connected to Youtube.')
        else:
            await ctx.send('I\'m pinging the owner to give you access. I\'ll let you know if you get permission.')
            ytaccessor.connect_to_yt()
            await ctx.send(':saxophone::dolphin: You\'re connected to Youtube, have fun. :saxophone::dolphin:')

    
    
    #FORMAT: ~createplaylist playlistname
    @commands.command(help='creates a playlist')
    async def createplaylist(self, ctx, *, name):
        global ytaccessor
        
        if not ytaccessor.built:
            await ctx.send(':no_entry: You need permission to make changes to the channel. Type "~connectyt" to ask for it.')
        else:
            playlist_name, desc = ytaccessor.create_playlist(playlist_name=name, authorName=ctx.author.name, authorId=str(ctx.author.id))
            if desc=='':
                await ctx.send(playlist_name)
            else:
                await ctx.send(':white_check_mark: `"'+playlist_name+'" has been created.`\nYou can now add a song or dump songs from another playlist.')
        
    

    #FORMAT: ~deleteplaylist playlistname
    @commands.command(help='deletes a playlist; requires permission from the owner')
    async def deleteplaylist(self, ctx, *, name):
        global ytaccessor
        
        if not ytaccessor.built:
            await ctx.send(':no_entry: You need permission to make changes to the channel. Type "~connectyt" to ask for it.')
            
        else:
            authorId, plistName = ytaccessor.getDataForPlist(name)
            
            if authorId=='':
                await ctx.send(':x: That playlist either doesn\'t exist or has been deleted.')
                
            #the following commented-out code is optional if you want to control who can delete entire playlists
            #currently, I've made it so that the bot owner (me) and the creator of the playlist (could also be me) can delete it.
            #You have to create a json file that stores that data, the commented out code to read and write is already written in YtAccessor.delete_playlist() 
            #Just uncomment everything within these methods and it should run fine
            
            #elif authorId != str(ctx.author.id) and authorId != 'BOT OWNER'S ID':
                #authorName = self.bot.get_user(int(authorId))
                #await ctx.send(':x: Only the owner and the creator of "'+plistName+'" can delete it. ('+authorName+' is the creator.)')
                
            else:
                #authorName = self.bot.get_user(int(authorId))
                
                response = ytaccessor.delete_playlist(plistName) #, authorId)
                await ctx.send(response)



    #FORMAT: ~addsong playlistname songlink
    #songlink can be from a playlist or just the raw song, doesn't matter
    @commands.command(help='args: <plistName> <songLink>')
    async def addsong(self, ctx, *args):
        global ytaccessor
        
        if not ytaccessor.built:
            await ctx.send(':no_entry: You need permission to make changes to the channel. Type "~connectyt" to ask for it.')
        else:
            args = list(args)
        
            song_link = args[-1]
            args.remove(song_link)
            playlist_name = ' '.join(args)
            response = ytaccessor.addsong(playlist_name, song_link)
            await ctx.send(response)
    


    
    #FORMAT: ~getyt
    @commands.command(help='returns a link to the yt page')
    async def getyt(self, ctx):
        if not ytaccessor.built:
            await ctx.send('Need to be connected to yt to do this, sadly')
        else:
            channelid = ytaccessor.getChannelId()
            #you can also just wipe all of the code above and replace 'channelid' with the dedicated channel's
            #id if you are going to use just one channel
            await ctx.send('https://www.youtube.com/channel/'+channelid+'/playlists?view_as=subscriber')
        


    #FORMAT: ~getplaylists pagenum
    # *pagenum is optional
    @commands.command(help='lists all playlists')
    async def getplaylists(self, ctx, *page, msg=None):
        global ytaccessor
        
        pageheader=''
        names=''
        
        if not page or page == '':
            page='1'
        else: 
            page=list(page)[0]
        
        if page != '' and not page.isnumeric():
            await ctx.send('The only argument you can send is the page number, '+page+' is invalid')
            return None
        
        pageId, names = ytaccessor.get_playlist_names(int(page))
        
        if msg == None:
            embed = discord.Embed(title='`the bot\'s playlists!`', color=0xc62ec1)
            embed.add_field(name='`( Page '+pageId+')`', value=names)
            msg = await ctx.send(embed=embed)
            
            # add reactions only on first iteration
            await msg.add_reaction('⬅️')
            await asyncio.sleep(.5)
            await msg.add_reaction('➡️')
            
        else:
            # editing the preexisting field we had that had the page num and songs in it
            msg.embeds[0].set_field_at(0, name='`(Page '+pageId+')`', value=names)
            await msg.edit(embed=msg.embeds[0])
                
                
        reaction = ''
            
        # now checking for reactions to see if any user wants to go left or right    
        try:
            def check(reaction, user):
                return ((str(reaction.emoji) == '➡️' or str(reaction.emoji) == '⬅️') 
                    and reaction.message == msg and user.id != "YOUR BOT'S ID") #anyone but the bot reacts
                
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=15)
            # cant listen for both an add and remove at the same time, so we'll listen to the add and then remove that user's
            # reaction so that they're only adding reactions
            await reaction.remove(user)
                
        except asyncio.TimeoutError:
            msg.embeds[0].set_footer(text = 'No more reactions can be made here.')
            await msg.edit(embed=msg.embeds[0])       
            return None # exits the method

        pagedata = pageId.split('/')
        page = int(pagedata[0])
        maxpages = int(pagedata[1])
        
        # going to reload the embed to adjust for the new page
        if str(reaction.emoji) == '➡️':
            if page == maxpages:
                await self.getplaylists(ctx, '1', msg=msg)
            else:
                await self.getplaylists(ctx, str(page+1), msg=msg )
        elif str(reaction.emoji) == '⬅️':
            if page == 1:
                await self.getplaylists(ctx, str(maxpages), msg=msg)
            else:
                await self.getplaylists(ctx, str(page-1), msg=msg)
                        

     
    #FORMAT: ~getlink playlistname
    @commands.command(help='gives you the link to a specified playlist')
    async def getlink(self, ctx, *, playlist_name):
        global ytaccessor
        playlist_link, description, thumbnail_url, playlist_name = ytaccessor.get_playlist_link(playlist_name)
        
        if thumbnail_url == '':
            await ctx.send(playlist_link)
        else:
            embed = discord.Embed(color=0x30d073, description = description, title='`Playlist: "'+playlist_name+'"`', url=playlist_link)
            embed.set_thumbnail(url = thumbnail_url)
            await ctx.send(embed=embed)
            
            
            
    
    #FORMAT: ~removesong playlistname songURL
    @commands.command(help='<plName> (<songURL> or <song#>) or <songURLfromPList>')
    async def removesong(self, ctx, *args):
        global ytaccessor
        
        if not ytaccessor.built:
            await ctx.send(':no_entry: You need permission to make changes to the channel. Type "~connectyt" to ask for it.')
        else:
        
            if len(args) > 1:
                args = list(args)
                url = args.pop(-1)
                plName = ' '.join(args)
                
                await ctx.send( ytaccessor.remove_song(plName, url) )
            else:
                await ctx.send( ytaccessor.remove_song(playlist_name='', song_link=args[0]) )
    
    
    
    #FORMAT: ~movesong playlistname oldpos newpos
    @commands.command(help='moves a song in a pl: <plName> <oldpos> <newpos>')
    async def movesong(self, ctx, *args):
        global ytaccessor
        
        if not ytaccessor.built:
            await ctx.send(':no_entry: You need permission to make changes to the channel. Type "~connectyt" to ask for it.')
        else:
            args = list(args)
        
            if len(args)<3:
                await ctx.send('Wrong format, it should be: <plName> <oldpos> <newpos>')
            elif not args[-1].isnumeric() or not args[-2].isnumeric():
                await ctx.send('The two last arguments have to be numbers.')
            else:
                oldpos = int(args.pop(-2)) -1
                newpos = int(args.pop(-1)) -1
                playlist_name = ' '.join(args)
            
                await ctx.send( ytaccessor.move_song(playlist_name, oldpos, newpos) )
            
        
    
    #FORMAT: ~getsongs playlistname pageNum
    # *pageNum is optional  
    @commands.command(help='lists songs of a pl; (<plName>  *<page#>)')
    async def getsongs(self, ctx, *args, msg=None):
        global ytaccessor
        
        args = list(args)
        embedtitle, names, thumnailUrl, pageId = ['',]*4
        
        if args[-1].isnumeric():
            page=args.pop(-1)
        else:
            page=1
        
        plName = ' '.join(args)
        embedtitle, names, thumbnailUrl, pageId = ytaccessor.get_songs(playlist_name=plName, pagenum=int(page))                
            
        if names == '':
            await ctx.send('That\'s not a valid playlist name')
            return None # nothing else to do

        if msg == None:
            embed = discord.Embed(title=embedtitle, color=0x1abc9c)
            embed.set_thumbnail(url=thumbnailUrl)
            embed.add_field(name='`(Page '+pageId+')`', value=names)
            msg = await ctx.send(embed=embed) 
            
            # add reactions only on first iteration
            await msg.add_reaction('⬅️')
            await asyncio.sleep(.5)
            await msg.add_reaction('➡️')
        
        else:
            # editing the preexisting field we had that had the page num and songs in it
            msg.embeds[0].set_field_at(0, name='`(Page '+pageId+')`', value=names)
            await msg.edit(embed=msg.embeds[0])
            
            
        reaction = ''
            
        # now checking for reactions to see if any user wants to go left or right    
        try:
            def check(reaction, user):
                return ((str(reaction.emoji) == '➡️' or str(reaction.emoji) == '⬅️') 
                    and reaction.message == msg and user.id != "YOUR BOT'S DISCORD ID") #anyone but the bot reacts
                
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=15)
            # cant listen for both an add and remove at the same time, so we'll listen to the add and then remove that user's
            # reaction so that they're only adding reactions
            await reaction.remove(user)
                
        except asyncio.TimeoutError:
            msg.embeds[0].set_footer(text = 'No more reactions can be made here.')
            await msg.edit(embed=msg.embeds[0])       
            return None # exits the method

        pagedata = pageId.split('/')
        page = int(pagedata[0])
        maxpages = int(pagedata[1])
        
        # going to reload the embed to adjust for the new page
        if str(reaction.emoji) == '➡️':
            if page == maxpages:
                await self.getsongs(ctx, plName, '1', msg=msg)
            else:
                await self.getsongs(ctx, plName, str(page+1), msg=msg )
        elif str(reaction.emoji) == '⬅️':
            if page == 1:
                await self.getsongs(ctx, plName, str(maxpages), msg=msg)
            else:
                await self.getsongs(ctx, plName, str(page-1), msg=msg)

            
     
    

    #this one can be wonky; YouTube's Data API gives you a daily "quota" for requests of around 10000 points, and adding a song/creating a playlist 
    #costs ~50 points, and over a day these can add up, so if songs arent being inserted into playlists, you've probably reached your quota for the day
    
    #FORMAT: ~dumpplaylist botPlaylistName externalPlaylistLink
    @commands.command(help='copies songs: <ourPlistName> <externalPlistLink>')
    async def dumpplaylist(self, ctx, *args):
        global ytaccessor
        args=list(args)
        
        if not ytaccessor.built:
            await ctx.send(':no_entry: You need permission to make changes to the channel. Type "~connectyt" to ask for it.')
            
        if len(args) < 2:
            await ctx.send('You either didn\'t include a playlist name or an external playlist link :thinking:')
            
        else:
            ext_url = args.pop(-1)
            plistName = ' '.join(args)
            response = ytaccessor.dump_playlist(plistName, ext_url)
            await ctx.send(response)
            
            
    

        

#cogs are those extensions in the bot.py class, and keep our commands categorized if we want to use the bot for other purposes
def setup(bot):
    bot.add_cog(music(bot))
