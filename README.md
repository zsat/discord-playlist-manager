# discord-playlist-manager

> This discord bot allows you to manage the playlists of a Youtube channel straight from discord.
---
## What can it do?

It functions like any other Discord bot, just type in these functions with a "~" in front to control your music:

- `addsong` : adds a song to a given playlist
- `connectyt` : enables read *and* write operations
- `createplaylist` : makes a new playlist
- `deleteplaylist` : deletes a given playlist
- `dumpplaylist` : copies songs from an external playlist to one of the bot's
- `getlink` : returns the link to specific playlist
- `getsongs` : returns the songs of a playlist
- `getplaylists` : returns all playlists
- `getyt` : returns channel page
- `movesong` : moves a song from one place in a playlist to another
- `removesong` : removes a song from a given playlist

***Argument formats are in music.py***

---

An example of `getplaylists` and `getsongs`

<img src="/readmeimgs/getplaylistsimg.png" width="299" height="363">  <img src="/readmeimgs/getsongsimg.png" width="525" height="373">

---

## How to set it up:
- Create a discord bot using Discord's API [here](https://discord.com/developers/applications) and obtain your "Build-A-Bot" token.
- Create a Google Application [here](https://console.developers.google.com/apis/credentials). [This](https://www.youtube.com/watch?v=-QMg39gK624) short series will help.
- Download all 3 .py files, read all comments, and replace all filepaths and keys as necessary.
- In your command line window, `pip install` the following:
    - `discord`
    - `google-auth-oauthlib`
    - `google-auth-python-client`
- Read through all the comments to make sure everything is good to go, add the bot to your server, then run bot.py.

---

## FAQ:

>What's its purpose?
- There are many Discord bots that will play songs in voice channels, but there wasn't any easy way for my friends and I to organize what we want to play, so I created this bot.


>Why is this on Github and not on Discord's bot list?
- I don't really feel like hosting it on a server, plus it was really only intended for me to use.
- I felt like sharing it so that anyone can suggest any new functions if they want.
