#!/usr/bin/python
import httplib, urllib
import os.path
import sys
import htmllib
import formatter
import math

from optparse import OptionParser

CACHE_DIR = './cache'
def make_fn(club,r):
    return '%s/%s_%s.html' % (CACHE_DIR, club, r)

def get_round(club,round):
    headers = {"Accept": "text/plain"}

    conn = httplib.HTTPConnection("www.frbe-kbsb.be")
    conn.request("GET", "/sites/manager/ICN/Result.php")
    response = conn.getresponse()
    print club,round, response.status, response.reason
    cookie = response.getheader('set-cookie')
    data = response.read()

    form = {'user': '0',
            'val_clb': club,
            'val_rnd': round,
            'search':'Search'
            }

    headers = {'Host':'www.frbe-kbsb.be',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'User-Agent':'Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0',
               'Accept-Language': 'en-us,en;q=0.5',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
               'Cookie': cookie,
               'Content-Type':'application/x-www-form-urlencoded'
               }

    params = urllib.urlencode(form)
    conn.request('POST', '/sites/manager/ICN/Result.php', params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def write_data(data,club,r):
    fn = make_fn(club,r)
    f = open(fn,'w')
    f.write(data)
    f.close()

def read_data(club, round):
    fn = make_fn(club, round)
    f = open(fn,'r')
    data = f.read()
    f.close()
    return data



def to_dict(attrl):
    d = {}
    for(n,v) in attrl:
        d[n] = v
    return d

class Player():
    def __init__(self, name, elo = None):
        self.name = name
        self.elo = elo

    def __repr__(self):
        return "Player('%s',%s)" % (self.name, self.elo)

    __str__ = __repr__



def parse_elo(elo_s):
    if elo_s == '':
        elo = 0
    else:
        elo = int(elo_s)
    return elo


def tpr(avg_elo, score, ng):

    eps = 0.005
    if score < eps:
        score = eps
    f = float(score)/ float(ng)
    a = (1.0 - f) / f
    if a == 0.0:
        a = eps
    d = - 400.0 * math.log(a, 10)
    return avg_elo + d

class MyParser(htmllib.HTMLParser):
    def __init__(self,f, club):
        htmllib.HTMLParser.__init__(self,f)
        self._club = club
        self._clubs = 0
        self._teams = 1
        self._table = 0
        self._clubs = 0
        self._tr = 0
        self._td = 0
        self._r = {}
        self._take = False
        self._pb = 0
        self._team = 1
        self._board = 1
        self._where = {}
        self._clubname = ""

    def start_table(self,x):
        self._table = self._table + 1
        self._tr = 0

    def start_tr(self,x):
        self._tr = self._tr + 1
        self._td = 0

    def end_tr(self):
        pass

    def start_td(self,attrl):
        self._td = self._td + 1

    def start_option(self,attrl):
        d = to_dict(attrl)
        b = self._tr -3
        if d.has_key('selected'):
            score = d['value']
            if score == '\xbd-\xbd':
                score = '0.5'
            self._r[b] = {'score':score}

    def end_td(self):
        self._take = False

    def do_input(self,attrl):
        d = to_dict(attrl)
        b = self._tr - 3
        if self._table == 3 :
            if b > self._pb + 1:
                self._team = self._team + 1
                self._board = 1
            self._pb = b
            if self._td == 5:
                p = Player(d['value'])
                self._r[b][0] = p

            if self._td == 6:
                p = self._r[b][0]
                elo = parse_elo(d['value'])
                p.elo = elo
                #print p,'-',
            if self._td == 7:
                p =  Player(d['value'])
                self._r[b][1] = p

                self._r[b]['board'] = self._board
                self._r[b]['team'] = self._team
                self._board = self._board + 1
                #print self._team
            if self._td == 8:
                p = self._r[b][1]
                elo = parse_elo(d['value'])
                p.elo = elo
                #print p,
                #print

    def handle_data(self,data):
        if self._table == 3 and self._tr >= 2 and self._td == 1:
            line = data.strip()
            key = str(self._club)
            if line.find('(') > 0 and line.find(')'):
                if line.find(key) > 0:
                    self._where[self._teams] = self._clubs
                    if self._clubname == "":
                        self._clubname = line[0:line.find('(')-3]
                        #print self._clubname
                self._clubs = 1 - self._clubs
                if self._clubs == 0:
                    self._teams = self._teams + 1


def take(bords, where, players, round):
    for k in bords.keys():
        g = bords[k]
        team = g['team']
        side = where[team]
        p = g[side]

        score = g['score']
        value = {
            '1-0':1,
            '0-1':0,
            '0.5':0.5,
        }
        result = 0
        if value.has_key(score):
            result = value[score]
            if side == 1:
                result = 1 - result

            elo_opp = g[1-side].elo

            pn = p.name
            if pn <> '':
                if not players.has_key(pn):
                    players[pn] = (p,[])
                sofar = players[pn]
                pos = round, g['team'], g['board'],result, elo_opp
                sofar[1].append(pos)
        else: # probably forfait
            pass



def get(club,r):
    fn = make_fn(club,r)
    if not os.path.exists(fn):
        data = get_round(club,r)
        write_data(data,club,r)


def played_for(players, team):
    result = []
    for pn in players.keys():
        poss = players[pn]
        ok = False
        for pos in poss[1]:
            (r, t, b, pr, elo_opp) = pos
            if t == team:
                ok = True
        if ok:
            result.append(pn)
    return result

def boards(players, team, teamnr, prevr):
    result = {}
    for pn in team:
        result[pn]={}
        for round in range(1, prevr+1):
            result[pn][round]=0
        poss = players[pn]
        for pos in poss[1]:
            (r, t, b, pr, elo_opp) = pos
            if t == teamnr:
                result[pn][r]=b
    return result

def predict(start, club, prevr, teamnr):
    players = {}

    def board_order(boards, players):
        w = []
        for x in boards.keys():
            bx = boards[x]
            counts = {}
            for r in bx.keys():
                b = bx[r]
                if b:
                    c = counts.get(b, 0) + 1
                    counts[b] = c
            w.append((x, counts))

        def cmp (v0, v1):
            x0,c0 = v0
            x1,c1 = v1
            r0 = min(c0.keys()) - min(c1.keys())
            if r0 == 0:
                p0 = players[x0][0]
                p1 = players[x1][0]
                r0 = p1.elo - p0.elo
            return r0

        w.sort(cmp)
        r = map(lambda(x,c) : x, w)
        return r

    for round in range(start, prevr + 1):
        data = read_data(club,round)
        parser = MyParser(formatter.NullFormatter(), club)
        parser.feed(data)
        r = parser._r
        where = parser._where
        teams = parser._teams
        clubname = parser._clubname
        take(r, where, players, round)

    for team_it in range(1, teams):
        if teamnr == 0 or team_it == teamnr:
            team = played_for(players, team_it)
            boards_ = boards(players, team, team_it, prevr+1)
            boards_ordered = board_order(boards_, players)
            print "%s %i:" % (clubname, team_it)
            template = "\t{:s}\t{:30s}\t\t({:4s}) ({:5s})  {:4s} {:4s}"
            print template.format("code", "NAME", "elo", " s / g", "avg", "tpr")
            result = []
            for pn in boards_ordered:
                poss = players[pn]
                bs = []
                for round in range(1, prevr+1):
                    played = False
                    for p in poss[1]:
                        r, t, b, pr, elo_opp = p
                        if r == round and team_it == t:
                            bs.append(b)
                            played = True
                    if not played:
                        bs.append(9)
                result.append((bs,pn))

            for (c,pn) in result:
                code = ''
                for b in c:
                    if b == 9:
                        code = code + '-'
                    else:
                        code = code + str(b)
                r = 0
                poss = players[pn]
                elo = poss[0].elo

                for x in poss[1]:
                    gr = x[3]
                    r += gr

                elo_opps = 0.0
                for x in poss[1]:
                    elo_opp = x[4]
                    if elo_opp == 0:
                        elo_opp = poss[0].elo
                    elo_opps += elo_opp

                ng = len(poss[1])

                avg_elo_opps = float(elo_opps) / float (ng)
                ptpr = tpr(avg_elo_opps, r, ng)
                t = (code, pn, elo, r, ng, avg_elo_opps, ptpr)
                template = "\t{:s}\t{:30s}  ({:4d}) ({:.1f}/{:2d}) {:4.0f} {:4.0f}"
                print template.format(*t)

def main():

    parser = OptionParser()
    parser.add_option("-c","--club",
                      dest = "club", type = "int",
                      default = 230,
                      help = "number of the club")
    parser.add_option("-r","--ronde",
                      dest = "prevr", type = "int",
                      default = 11,
                      help = "next round")
    parser.add_option("-t","--teamnr",
                      dest = "teamnr", type="int",
                      default = 0,
                      help = "limit output to just one team")
    parser.add_option("-s", "--startr",
                      dest = "start", type = "int",
                      default = 1
    )
    options, args = parser.parse_args()

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    club = options.club
    prevr = options.prevr
    teamnr = options.teamnr
    start = options.start
    for r in range(start, prevr+1):
        get(club,r)
    predict(start, club,prevr,teamnr)


if __name__ == '__main__':
    main()
