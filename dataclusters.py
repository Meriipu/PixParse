from collections import OrderedDict
import structures
class __clusters(object):
    def __init__(self):
        raise
    
    def getFieldWidths(self):
        """Returns a dictionary {field:field_width}
        gives the maximum width of each field among elements in cluster
        Bases itself on default specifiers, filters filtering away potential long element strings are ignored
        """
        d = {}
        
        for field in self.getFields():
            lengths = (len(str(x.getReprDict()[field])) for x in self.iter(self.getSpecifiers()))
            d[field] = max(lengths)
            
        return d

class Accounts(__clusters):
    def __init__(self):
        self.accounts = {}
    
    def addAccountIfNeeded(self, name, platformid):
        """{accountname: {platformid1: account, 
                          platformid2: account}, 
           }"""
        
        if name not in self.accounts:
            self.accounts[name] = {}
        
        if platformid not in self.accounts[name]:
            self.accounts[name][platformid] = structures.Account(name, platformid)
    
    def UpdateAccountsWithGame(self, game):
        for player in game.players:
            self.addAccountIfNeeded(player.name, game.platformid)
            
            self.accounts[player.name][game.platformid].addGame(game)
    
    def getAccountsFromName(self, accountname):
        """returns dictionary of {platformid:account}"""
        if accountname in self.accounts:
            return self.accounts[accountname]
        else:
            raise KeyError("Accountname {} not found in accounts".format(accountname))
            
    def iter(self, specifiers):
        """Iterate through elements given specifier"""
        d = specifiers
        for accountname in self.accounts:
            for platform in self.accounts[accountname]:
                if (d['platformid']) and platform not in d['platformid']:
                    continue
                yield self.accounts[accountname][platform]
    
    def getFields(self):
        if self.accounts:
            accname = list(self.accounts)[0]
            platform = list(self.accounts[accname])[0]
            acc = self.accounts[accname][platform]

            return [x for x in acc.getReprDict()]
        else:
            return ['NotLoaded']

    def getSpecifiers(self):
        d = OrderedDict([('platformid', []),
                         ])
        return d
    
class Games(__clusters):
    def __init__(self):
        self.games = set()
    def addGame(self, game):
        self.games.add(game)
        
    def iter(self, specifiers):
        d = specifiers
        for game in self.games:
            if not d['include_spectated']:
                if game.spectated:
                    continue
            if not d['include_crashed']:
                if game.isCrashed():
                    continue
            if not d['include_abandon']:
                if game.isAbandoned():
                    continue
            
            yield game
    
    def getFields(self):
        if self.games:
            return [x for x in (list(self.games)[0]).getReprDict()]
        else:
            return ['NotLoaded']
            
    def getSpecifiers(self):
        """Default specifiers"""
        d = OrderedDict([('include_spectated', False), 
                         ('include_crashed', True), 
                         ('include_abandon', True)])
        return d