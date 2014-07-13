from os import listdir
from os import path
from collections import defaultdict

import structures, tools, dataclusters
import graphical



class Logviewer(object):
    def __init__(self):
        self.version = '0.1' 
       
        self.games = dataclusters.Games()
        self.accounts = dataclusters.Accounts()
        
        
    def ReadFromLogs(self, logfiles_folder):
        """Read and construct necessary objects (games, accounts) from logfiles"""
        logs = listdir(logfiles_folder)
        for logfile in logs:
            p = path.join(logfiles_folder, logfile)
            
            game = structures.Game_ReadFromLogfile(p)
            
            self.games.addGame(game)
            self.accounts.UpdateAccountsWithGame(game)

    def ReadFromCache(self, json_file_path):
        """Read and construct necessary objects (games, accounts) from a json dump"""
        dicts = tools.readFromJSON(json_file_path, self.version)
        for d in dicts:
            game = structures.Game_ReadFromDict(d)
            
            self.games.addGame(game)
            self.accounts.UpdateAccountsWithGame(game)
        
    def DumpToCache(self):
        L = [g.getConstructionDict() for g in self.games.games]
        tools.dumpToJSON(L, self.version)
        


def MAIN():
    LV = Logviewer()
    LV.ReadFromCache("ParserCache/parse_14048837284977148.json")
    #LV.ReadFromLogs("../../Desktop/LoLLogs20140705")
    LV.DumpToCache()
    gui = graphical.createGUI(LV)
    
    #input()
    return LV

LV = MAIN()

"""
LV = MAIN()


me = LV.data.accounts['Meriipu']

import collections
d = collections.Counter()
i = 0
for game in me['NA1'].games_played:
    pl = game.getPlayerByName('Meriipu')
    d.update((pl.champion,))
    i += 1
print(me)
[print(x.ljust(12),d[x]) for x in sorted(d,key=lambda q:d[q])[::-1]]
"""