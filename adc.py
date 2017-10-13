# -*- coding: UTF-8 -*-
import requests
import codecs
import re
import HTMLParser
import feedparser
import bs4
from bs4 import BeautifulSoup
import ConfigParser
import os
import sys

session = requests.session()
baseURL = "https://asiandvdclub.org"
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'\
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113'\
        'Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'\
        ',*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'
}

filterA = re.compile(r'(\d{6})')

class adcAnalysis(object):
    def __init__(self):
        '''self.config = config
        
        username = self.config.get('global', 'username')
        password = self.config.get('global', 'password')
        self.takeLogin(username, password)
        
        self.leechers = self.config.get('rules', 'leechers')
        self.age = self.config.get('rules','age')
        self.silver = self.config.get('rules','silver')
        self.BlueRay = self.config.get('rules', 'BlueRay')
        self.logic = self.config.get('rules','logic')
        
        '''
        self.getIndexPage()
        self.getTorrents()
        self.getTorrentsSoup()
        '''
        for torrent in self.torrentSoup:
            if self.getUserSilverRule(torrent) or self.getUserBlueRayRules(torrent):
                if self.setSeederLeecherAgeRule(torrent):
                    torrentId = self.getTorrentId(torrent)
                    self.saveTorrentFile(torrentId)            
            '''
        for torrent in self.torrentSoup:
            #print torrent
            if self.setSeederLeecherAgeRule(torrent):
                print 'leechers:%d' % self.getLeecher(torrent)
                print 'seeders:%d' % self.getSeeder(torrent)
                print self.getTorrentId(torrent)
                print self.getAge(torrent)
        return
    
    
    
    def takeLogin(self,username,password): #登陆，获取cookies
        loginDict = {"username":username, "password":password}
        session.post(baseURL+"/takelogin.php", loginDict, headers = headers)
        return 
    
    def getUserSilverRule(self,torrent):
        '''if self.silver == 'yes' and self.getSilver(torrent):
            return True
        elif self.silver == 'no':
            return True'''
        if self.getSilver(torrent):
            return True
        return False
    
    def saveTorrentFile(self,torrentId):
        getTorrentFile = session.get(baseURL+'/download.php?id='+torrentId,headers = headers)
        fpoint = open(torrentId+'.torrent','wb')
        fpoint.write(getTorrentFile.content)
        fpoint.close()
        return
    
    def getUserBlueRayRules(self,torrent):
        '''if self.BlueRay == 'yes' and self.getBlueRay(torrent):
            return True
        elif self.BlueRay == 'no':
            return True'''
        if self.getBlueRay(torrent):
            return True
        return False
    
    def setSeederLeecherAgeRule(self,torrent):
        if self.getSeeder(torrent) == 1 and self.getLeecher(torrent) >= 5:
            '''if len(self.soupDataTime.span.string) < 4:
                if self.getAge(torrent) <= 30:
                    return True'''
            return True
        return False 
        
    def getTorrentId(self,torrent):
        rawData = torrent.find('td', class_ = 'torrentname')
        #print rawData
        soupData = BeautifulSoup(str(rawData),'html.parser')
        #print soupData
        torrentId = (re.search(filterA, soupData.a["href"]).group())
        return torrentId
    
    def getIndexPage(self):
        #indexPage = session.get(baseURL+"/browse.php?orderBy=added&direction=DESC&page=1",headers=headers)
        f = open('AsianDVDClub.html','r')
        testcontent = f.read()
        f.close()
        #basicSoup = BeautifulSoup(indexPage.text,'html.parser')
        basicSoup = BeautifulSoup(testcontent,'html.parser')
        #self.indexPage = indexPage
        self.basicSoup = basicSoup
        return
    
    def getTorrents(self):
        self.allTorrents = self.basicSoup.find_all('tr', class_ = re.compile('even|odd'), limit = 20)
        return
    
    def getTorrentsSoup(self):
        self.torrentSoup = []
        for torrents in self.allTorrents:
            torrentSoup = BeautifulSoup(str(torrents),'html.parser')
            #print torrentSoup
            self.torrentSoup.append(torrentSoup)
        return
    
    def getSeeder(self,torrent):
        rawData=torrent.find('td', class_ = 'seeders')
        soupData=BeautifulSoup(str(rawData),'html.parser')
        if soupData.find_all('a'):
            seeders = int(soupData.td.string)
            return seeders
        return 0
         
    def getLeecher(self,torrent):  
        rawData = torrent.find('td', class_ = 'leechers') 
        soupData = BeautifulSoup(str(rawData),'html.parser')
        if soupData.find_all('a'):
            leechers = int(soupData.td.string)
            return leechers
        return 0
    
    def getAge(self,torrent):
        rawData = torrent.find('td', class_ = 'time')
        self.soupDataTime = BeautifulSoup(str(rawData),'html.parser')
        age = re.search(re.compile(r'(\d{2})m'), self.soupDataTime.span.string)
        return age.group(0)   
            
    def getSilver(self,torrent):
        if torrent.find_all('td', align = 'right'):
            return True
        return False
    
    def getBlueRay(self,torrent):
        rawData = torrent.find('td', class_ = 'torrentname')
        soupTorrentName = BeautifulSoup(str(rawData),'html.parser')
        if soupTorrentName.find('img', class_ = 'main-bluray tt-bluray'):
            return True
        return False
    
def parserConfig(pathToConfig):
    configPath = os.path.expanduser(pathToConfig)
    config = ConfigParser.SafeConfigParser()
    
    if os.path.isfile(configPath):
        config.read(configPath)
    else:
        configDir = os.path.dirname(configPath)
        if not os.path.isdir(configDir):
            os.makedirs(configDir)
        
        config.add_section('global')
        config.set('global', 'username', '')
        config.set('global', 'password', '')
        
        config.add_section('rules')
        config.set('rules', 'leechers', '')
        config.set('rules', 'age','')
        config.set('rules', 'silver', 'yes')
        config.set('rules', 'BlueRay', 'yes')
        config.set('rules', 'logic', '')
        
    with open(configPath,'w') as fpoint:
        config.write(fpoint)
        
    print('Please edit the configuration file: %s' % pathToConfig)
    sys.exit(2)
    
    return config

newSpider = adcAnalysis()
