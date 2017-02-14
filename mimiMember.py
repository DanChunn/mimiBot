import discord
from discord.ext import commands
import random
import requests, re
from bs4 import BeautifulSoup
import pickle
import asyncio

class mimiMember():

    
    def __init__(self, discordMember:discord.Member, initialPoints):
        self.points = initialPoints
        self.denounced = 0
        self.title = ""
        self.titles = {}
        self.spouse = int
        self.proposals = []
        
        self.id = discordMember.id

    def incrementDenounced(self, amt:int):
        self.denounced += amt
        if self.denounced > 9999:
            self.denounced = 999

    def decrementDenounced(self, amt:int):
        self.denounced -= amt
        if self.denounced < 0:
            self.denounced = 0
        
    def incrementPoints(self, points:int):
        if(self.points < 999999):
            self.points += points

    def decrementPoints(self, points:int):
        self.points -= points
        if(self.points < 0):
            self.points = 0

