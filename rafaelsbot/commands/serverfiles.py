import time

Servers = {}

class Report():
    def __init__(self,userid,reason,reportedbyid):
        self.userid = userid
        self.reason = reason
        self.reportedbyid = reportedbyid
        self.timestamp = time.time()

class Server():
    def __init__(self,id):
        self.id = id
        self.reports = {}
        self.queue = []
        self.umfragen = {}

    def createReport(self,userid,reason,reportedbyid):
        if userid in self.reports:
            self.reports[userid].append(Report(userid,reason,reportedbyid))
        else:
            self.reports[userid] = [Report(userid,reason,reportedbyid)]


def createReport(serverid:int,userid:int,reason:str,reportedbyid:int):
    if not serverid in Servers:
        Servers[serverid] = Server(serverid)
    Servers[serverid].createReport(userid,reason,reportedbyid)

def getReports(serverid:int,memberid:int=None):
    if not serverid in Servers:
        return []
    else:
        if memberid == None:
            reports = []
            for user in Servers[serverid].reports:
                reports.append((user,len(Servers[serverid].reports[user])))
            return reports
        else:
            if not memberid in Servers[serverid].reports:
                return []
            else:
                reports = []
                for i in Servers[serverid].reports[memberid]:
                    reports.append(i.__dict__)
                return reports
