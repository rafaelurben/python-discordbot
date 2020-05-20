import time, youtube_dl, os
from discord import PCMVolumeTransformer, FFmpegPCMAudio
from discord.ext import commands

filespath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "files")

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

color = 0xee00ff

#####

class Report():
    def __init__(self, member, reason:str, reportedbyid:int):
        self.member = member

        self.reason = reason
        self.reportedbyid = reportedbyid
        self.timestamp = time.time()

class Member():
    def __init__(self, server, id:int):
        self.server = server

        self.id = id
        self.reports = []

    def createReport(self, reason:str, reportedbyid:int):
        self.reports.append(Report(member=self, reason=reason, reportedbyid=reportedbyid))

    def getReports(self):
        return [
            {
                "name": str(time.strftime('%d.%m.%Y - %H:%M:%S', time.localtime(report.timestamp))),
                "value": str(report.reason)+" - <@"+str(report.reportedbyid)+">",
                "inline": False
            } for report in self.reports
        ]

class YouTubePlayer(PCMVolumeTransformer):
    _ytdl = youtube_dl.YoutubeDL({
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(filespath,'youtube','%(extractor)s-%(id)s-%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'ffmpeg_location': filespath,
        'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
    })

    _ffmpeg_options = {
        'options': '-vn',
        'executable': os.path.join(filespath,"ffmpeg.exe")
    }

    def __init__(self, filename, *, queue, data, volume=0.5):
        source = FFmpegPCMAudio(filename, **self._ffmpeg_options)

        super().__init__(source, volume)

        data.pop("formats")

        self.queue = queue

        self.data = data

        self.url = data.get('url', '')
        self.link = data.get('webpage_url', self.url)
        self.title = data.get('title', 'Unbekannter Titel')

        self.uploader = data.get('uploader', "")
        self.uploader_url = data.get('uploader_url', "")
        self.thumbnail = data.get('thumbnail', "")
        self.description = data.get('description', "")
        self.duration = int(data.get('duration', 0))

    async def send(self, ctx, status:str="Wird jetzt gespielt..."):
        fields = [("Ansehen/Anhören", "[Hier klicken]("+self.link+")")]
        if self.duration:
            fields.append(("Dauer", str(int(self.duration/60))+"min "+str(int(self.duration%60))+"s"))
        fields.append(("Status", status, False))
        await ctx.sendEmbed(
            title=self.title,
            description=self.description if len(self.description) < 100 else self.description[0:100]+"...",
            color=ctx.cog.color,
            fields=fields,
            thumbnailurl=self.thumbnail if self.thumbnail else None,
            authorname=self.uploader if self.uploader else None,
            authorurl=self.uploader_url if self.uploader_url else None,
        )

    def play(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        elif ctx.voice_client:
            ctx.voice_client.play(self, after=lambda e: self.queue.playNext(ctx))


    @classmethod
    async def from_url(self, url, *, queue, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self._ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else self._ytdl.prepare_filename(data)
        return [self(queue=queue, filename=filename, data=data)]


class MusicQueue():
    def __init__(self, server):
        self.server = server

        self._players = []

    def addPlayer(self, player):
        self._players.append(player)

    def hasPlayer(self):
        return bool(self._players)

    def playNext(self, ctx):
        if self.hasPlayer() and ctx.voice_client and ctx.voice_client.is_connected():
            player = self._players.pop(0)
            player.play(ctx)
            return player
        else:
            return None

    async def sendNowPlaying(self, ctx):
        if ctx.voice_client and ctx.voice_client.source:
            if isinstance(ctx.voice_client.source, YouTubePlayer):
                await ctx.voice_client.source.send(ctx, status="Wird jetzt gespielt!")
        else:
            raise commands.CommandError("Aktuell wird nichts abgespielt.")

    async def createYoutubePlayer(self, search, loop=None, stream=False):
        players = await YouTubePlayer.from_url(search, queue=self, loop=loop, stream=stream)
        if not stream:
            for player in players:
                self.addPlayer(player)
        return players



class Server():
    _all = {}

    def __init__(self,id):
        self.id = id
        self.members = {}
        self.musicqueue = MusicQueue(server=self)
        #self.polls = {}

    def getMember(self, userid:int):
        if not userid in self.members:
            self.members[userid] = Member(server=self, id=userid)
        return self.members[userid]

    def createReport(self, userid:int, reason:str, reportedbyid:int):
        self.getMember(userid).createReport(reason=reason, reportedbyid=reportedbyid)

    def getReports(self, userid:int=None):
        if userid is None:
            reports = []
            for member in list(self.members.values()):
                if len(member.reports) > 0:
                    reports.append({
                        "name": str(len(member.reports))+" Report(s)",
                        "value": "<@"+str(member.id)+">",
                        "inline": False
                    })
            return reports
        else:
            return self.getMember(userid).getReports()


    @classmethod
    def getServer(self, serverid:int):
        if not serverid in self._all:
            self._all[serverid] = Server(serverid)
        return self._all[serverid]
