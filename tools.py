from os import path,mkdir
import re,json,time

#Cache folder name
cachedir = "ParserCache"

def clearCache():
    """not implemented -- I do not like deleting stuff,
       delete the cache files yourself, yo"""
    pass

def _makeCacheDir():
    """Make cache folder"""
    if not path.exists(cachedir):
        mkdir(cachedir)
    
    if not path.isdir(cachedir):
        print("Cachedir already exists, but as a file?")
        raise
    else:
        return True

def dumpToJSON(dump_object, version):
    """Write dump_object as ajson file in cache folder"""
    _makeCacheDir()
    
    timestamp = str(time.time()).replace('.', '').replace(',', '')
    pth = path.join(cachedir, 'parse_'+timestamp+'.json')
    
    with open(pth, "w") as f:
        json.dump([version, dump_object], f)

def readFromJSON(path_to_jsonfile, version):
    with open(path_to_jsonfile) as f:
        L = json.load(f)
    
    file_version,d = L
    if (file_version != version):
        raise Exception("version of json file: {} does not match version expected by program: {}, re-read logs (and save a new cache instead)".format(file_version, version))
    else:
        return d



def isChampionMatch(p1, p2):
    """Allow stuff like chogath==cho'gat preferably, 
       but not implemented completely"""
    if p1.lower() == p2.lower():
        return True

def validateGame(game):
    """Spectator games and games you were not in are invalid when it comes to the recorded result"""
    #spectated games are out
    #    (they always display as win at the end of the logfile -- no way of knowing who won (maybe?))
    if game.spectated:
        return False
    return True

class Logfile(object):
    def __init__(self, path_to_logfile):
        with open(path_to_logfile) as f:
            contents = f.readlines()
        self.logfilepath = path_to_logfile
        
        self._L = contents
        self._contents = "\n".join(x.strip() for x in contents)
        self.patterns = {}
        self.__addPatterns()
    def __getContents(self):
        return self._contents
    def __getLines(self):
        return self._L
    def __addPatterns(self):
        
       #d = {'linestart' : "^(?:[^|]*\|){4} ",
        #     }
        
        d = {'linestart' : ''}
        self.patterns.update(d)
        
    def getSpectated(self):
        """True if the logfile was the result of spectating"""
        
        #"linestart" + "anything|"x4 + "Spectator server line"
        linestart = self.patterns['linestart']
        
        patt = linestart + "Spectator server version retrieved: "
        return bool(re.search(patt, self.__getContents()))
        
    def getBasicPlayerdata(self):
        """return a list of dictionaries with playerinfo {playername, champion, team, playertype, skin}"""
        L = []
        _names = []
        linestart = self.patterns['linestart']
        
        patt = linestart + "Spawning champion \(({champion})\) with skinID ({skin_ID}) on team ({team_ID}) for clientID ({client_ID}) and summonername \(({summonername})\) \(is ({playertype})\)"
        
        
        """Spawning champion (Lulu) with skinID 1 on team 200 for clientID 0 and summonername (Meriipu) (is HUMAN PLAYER)"""

        patt = patt.format(champion="[\w']+", skin_ID="\-?[0-9]+", team_ID="\-?[0-9]+", client_ID="\-?[0-9]+", summonername="[^)]+", playertype="[A-Z ]+")
        found = re.findall(patt, self.__getContents())
        #print(patt)
        AA=0
        for line in found:
            #print(line)
            champion, skinid, teamid, clientid, summonername, playertype = line
            
            data = {'name' : summonername, 
                    'champion' : champion, 
                    'team' : self.__getTeamFromID(teamid),
                    'playertype' : playertype,
                    'clientid' : clientid,
                    'skin' : self.__getSkinFromID(champion, skinid)}
            
            if not data["name"]+str(teamid) in _names:
                _names.append(data["name"]+str(teamid))
                L.append(data)
            else:
                pass

        try:
            return L
        except:
            #print(self.__getContents())
            raise
    
    def getLogClientID(self):
        """Get the player who produced the log"""
        linestart = self.patterns['linestart']
        
        patt = linestart + 'netUID: ([^ ]+)'
        
        found = re.search(patt, self.__getContents())
        if found:
            #print("Client ID: " + str(found.group(1)))
            return found.group(1)
        else:
            #print("Noclient")
            #print(self.logfilepath)
            return False
    def getPlatformID(self):
        linestart = self.patterns['linestart']
        
        patt = linestart + 'PlatformID: ([^\s]+)'
        
        found = re.search(patt, self.__getContents())
        if found:
            return found.group(1)
        else:
           # print("NoPlatform")
            #print(self.logfilepath)
            return "??1"
        
        
    def getResult(self):
        """Get the team that won"""
        linestart = self.patterns['linestart']
        
        patt = linestart + '{[^}]*"EXITCODE_(WIN|LOSE|ABANDON)"'
        
        result = re.search(patt, self.__getContents())
        
        if result:
            if result.group(1) not in ("WIN", "LOSE", "ABANDON"):
                print(result)
                print(self.logfilepath)
                print("Result not found")
                #print(self.__getContents())
                raise
            else:
                return result.group(1)
        else:
            #print("Crash?: {}".format(self.logfilepath))
            result = re.search("ERROR| Crash Occurred", self.__getContents())
            if result:
                return "CRASH"
            else:
                raise
            
    def __getTeamFromID(self, team_ID):
        """convert the numeric team ID in logfile to a team colour"""
        if team_ID == "100":
           # print("{} - Blue".format(team_ID))
            return "Blue"
        elif team_ID == "200":
            #print("{} - Purple".format(team_ID))
            return "Purple"
        else:
            print("{} - ???".format(team_ID))
    
    def __getSkinFromID(self, champion, skin_ID):
        """convert the numeric skin ID in logfile to a skin name"""
        #AIN'T NOBODY GOT TIME FOR THAT
        return "{}".format(skin_ID)
