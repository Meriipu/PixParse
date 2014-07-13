from itertools import zip_longest
from collections import OrderedDict
from os import path

import tools

class __Game(object):
    def __init__(self):
        raise Exception("Instantiate one of the two subclasses of __Game, not __Game")
    
    def __str__(self):
        return self.identifier

    def __repr__(self):
        Blue = list(self.getPlayersByTeam('Blue'))
        Purple = list(self.getPlayersByTeam('Purple'))
        
        s = '[game {}:\n'.format(self.identifier)
        #based zip_longest
        for b,p in zip_longest(Blue, Purple, fillvalue=''):
            s += "{:50}{}\n".format(str(b),str(p))
        
        s = s[:-1] + ']\n'
        
        return s
    
    def __getitem__(self, key):
        return self.getConstructionDict()[key]
        
    def getReprDict(self):
        #x1 = ('players', x)
        x2 = ('Winnerteam', str(self.getWinningTeam()))
        L = ['identifier', 'platformid', x2, 'spectated']
        
        d = self.getConstructionDict()
        reprdict = OrderedDict()
        
        for field in L:
            if type(field) is str:
                reprdict[field] = d[field]
            
            elif type(field) == tuple:
                k,v = field
                reprdict[k] = v
        
        return reprdict
    
    def getConstructionDict(self):
        d = OrderedDict() 

        d['identifier'] = self.identifier
        d['platformid'] = self.platformid
        d['logclientid'] = self.logclientid
        d['LogPlayerResult'] = self.getLogPlayerResult()
        d['spectated'] = self.spectated
        d['players'] = [x.getConstructionDict() for x in self.players]
        
        return d    
        
    def isCrashed(self):
        return self._LogPlayerResult == 'CRASH'
    
    def isAbandoned(self):
        return self._LogPlayerREsult == 'ABANDON'
    
    def isSingleplayer(self):
        return (len(self.players) == 1)
        
    def getLogPlayer(self):
        """get the player that made the log"""
        for player in self.players:
            if player.clientid == self.logclientid:
                return player
        
        return None
    
    def getLogPlayerResult(self):
        if self.spectated and self._LogPlayerResult in ('WIN', 'LOSE'):
            return 'UNKNOWN'
        else:
            return self._LogPlayerResult
        
    def getWinningTeam(self):
        #Figure out which team won based on who made the logfile
        x = self.getLogPlayer()
        
        #Logowner is unknown/not in the game
        if x is None:
            return 'UNKNOWN'
        
        elif self._LogPlayerResult == 'ABANDON':
            res = None
        
        elif self._LogPlayerResult == 'CRASH':
            res = None
        
        elif self._LogPlayerResult == 'WIN':
            if x.team == "Blue":
                res = 'Blue'
            elif x.team == "Purple":
                res = 'Purple'
        
        elif self._LogPlayerResult == 'LOSE':
            if x.team == "Blue":
                res = 'Purple'                    
            elif x.team == "Purple":
                res = 'Blue'
        else:
            print(self.LogPlayerResult)
            print("?result?")
            raise
        
        return res
    
    def getPlayerByName(self, name):
        for player in self.players:
            if player.name.lower() == name.lower():
                return player
        return False
        
    def getPlayersByChampion(self, champion):
        s = set()
        for player in self.players:
            if tools.isChampionMatch(player.champion, champion):
                s.add(player)
        
        if s:
            return s
        else:
            print("Champion {} not found in {}".format(champion, self))
            print([(p.name, p.champion) for p in self.players])
            raise
    
    def getPlayersByTeam(self, team):
        """team is colour"""
        s = set(player for player in self.players if (player.team == team))
        if s:
            return s
        else:
            print("Team {} has 0 players".format(team))
            #print(self)
            return s
    
    def getTeamByPlayer(player):
        for p in self.players:
            if p == player:
                return p.getTeam()
        
        print("{} not on any team".format(player))
        print(player.name)
        raise
    
    def getTeamByPlayerName(playername):
        for p in self.players:
            if p.name.lower() == playername.lower():
                return p.team
        
        print("playername {} not on any team".format(playername))
        raise
    


class Game_ReadFromLogfile(__Game):
    def __init__(self, path_to_logfile):
        #log object
        log = tools.Logfile(path_to_logfile)
        
        #logfilename
        self.identifier = path.split(path_to_logfile)[-1]
        
        #game was spectated
        self.spectated = log.getSpectated()
        
        #extract info about players in the game from logfile-playerdicts
        self.players = set(_GamePlayer(**pd) for pd in log.getBasicPlayerdata())
        
        #result as stated by logfile
        self._LogPlayerResult = log.getResult()

        #Which player is the client that made the log?
        self.logclientid = log.getLogClientID()
        
        #Which server?
        self.platformid = log.getPlatformID()
class Game_ReadFromDict(__Game):
    def __init__(self, dict):
        self.identifier = dict['identifier']
        self.spectated = dict['spectated']
        self.logclientid = dict['logclientid']
        self.platformid = dict['platformid']
        self._LogPlayerResult = dict['LogPlayerResult']
        self.players = set()
        for pd in dict['players']:
            self.players.add(_GamePlayer(**pd))
        
class _GamePlayer(object):
    def __init__(self, name, champion, team, clientid, playertype, skin):
        self.name = name
        self.champion = champion
        self.team = team
        self.clientid = clientid
        self.playertype = playertype
        self.skin = skin
    
    def __str__(self):
        return "<gp: {} ({})>".format(self.champion, self.name)
    def __repr__(self):
        return self.__class__.__name__ + "({name}, {champion}, {team}, {clientid}, {playertype}, {skin})".format(**self.getConstructionDict())
    def __getitem__(self, key):
        return self.getConstructionDict()[key]
    
    def getReprDict(self):
        L = ['name', 'champion', 'team', 'playertype']
        
        d = self.getConstructionDict()
        reprdict = OrderedDict()
        
        for field in L:
            if type(field) is str:
                reprdict[field] = d[field]
            
            elif type(field) == tuple:
                k,v = field
                reprdict[k] = v
        
        return reprdict
        
    def getConstructionDict(self):
        d = OrderedDict()
        
        d['name'] = self.name,
        d['champion'] = self.champion,
        d['skin'] = self.skin,
        d['clientid'] = self.clientid,
        d['team'] = self.team,
        d['playertype'] = self.playertype,
        
        return d



class Account(object):
    def __init__(self, name, platformid):
        self.name = name
        self.platformid = platformid
        self.games_played = set()
        
        
    def __str__(self):
        return "<Account: {} ({})>".format(self.name, self.platformid)
        
    def __repr__(self):
        return str(self)

    def addGame(self, game):
        if (self.name in  (pn.name for pn in game.players)):
            pass
        else:
            print("{} was not a player in this game {}".format(self, game))
            #raise        
        self.games_played.add(game)
    
    def getReprDict(self):
        x1 = ('Accountname', self.name)
        x2 = ('Server', self.platformid)
        x3 = ('Games played', str(len(self.games_played)))
        L = [x1, x2, x3]
        
        #d = self.getConstructionDict()
        reprdict = OrderedDict()
        
        for field in L:
            #if type(field) is str:
            #    reprdict[field] = d[field]
            
            if type(field) == tuple:
                k,v = field
                reprdict[k] = v
        
        return reprdict