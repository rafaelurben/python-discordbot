import time

class Report():
    def __init__(self, reason:str, reportedbyid:int):
        self.reason = reason
        self.reportedbyid = reportedbyid
        self.timestamp = time.time()

class Member():
    def __init__(self, id):
        self.id = id
        self.reports = []

    def createReport(self, reason:str, reportedbyid:int):
        self.reports.append(Report(reason=reason, reportedbyid=reportedbyid))

    def getReports(self):
        return [
            {
                "name": str(time.strftime('%d.%m.%Y - %H:%M:%S', time.localtime(report.timestamp))),
                "value": str(report.reason)+" - <@"+str(report.reportedbyid)+">",
                "inline": False
            } for report in self.reports
        ]


class Server():
    all = {}

    def __init__(self,id):
        self.id = id
        self.members = {}
        #self.queue = []
        #self.polls = {}

    def getMember(self, userid:int):
        if not userid in self.members:
            self.members[userid] = Member(userid)
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
        if not serverid in self.all:
            self.all[serverid] = Server(serverid)
        return self.all[serverid]



def createReport(serverid:int, userid:int, reason:str, reportedbyid:int):
    return Server.getServer(serverid).createReport(userid,reason,reportedbyid)

def getReports(serverid:int, userid:int=None):
    return Server.getServer(serverid).getReports(userid)
