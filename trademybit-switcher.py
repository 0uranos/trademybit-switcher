#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Retrieves the "bestalgo" JSON from the TMB website and returns a value
# indicating which type of mining software is currently more profitable.
#
# Possible return values:
#   "scrypt" - indicates that scrypt mining is more profitable
#   "nscrypt" - indicates that nscrypt mining is more profitable
#   "none" - indicates that there is no more than a 10% difference between
#            scrypt and nscrypt mining profitability
#

###############
import ConfigParser
import logging
import json
import subprocess
import sys
import time
import urllib2
import urlparse

from trademybitapi import TradeMyBitAPI
from pycgminer import CgminerAPI


class Algo:
    def __init__(self, name):
      self.command = '' # the command that is run when we want to mine this coin.
      self.name    = name
      self.cnt     = 0

class TradeMyBitSwitcher(object):
  def __init__(self):
    self.__prepare_logger()

    # Define supported algo
    self.algos = {}
    self.algos['scrypt']  =  Algo('Scrypt')
    self.algos['nscrypt'] =  Algo('N-Scrypt')

    self.__load_config()
    self.api = TradeMyBitAPI(self.api_key, 'https://pool.trademybit.com/api/')
    self.cgminer = CgminerAPI(self.cgminer_host, self.cgminer_port)

  def log(self, message):
    print "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message)

  def main(self):
    cnt_all = 0
    # main loop
    print '-' * 72

    while True:
      # print header
      # self.logger.info("<<< Round %d >>>" % (cnt_all+1))
      
      # get data from sources
      self.logger.debug("Fetching data...")
      bestalgo = self.best_algo()
      currentalgo = self.current_algo()
      
      self.logger.debug("=> Best: %s | Currently mining: %s" % (bestalgo, currentalgo))
     
      if bestalgo != currentalgo and bestalgo != None:
        # i.e. if we're not already mining the best algo
        self.switch_algo(bestalgo)

      # sleep
      self.logger.debug('Going to sleep for %dmin...' % self.idletime)
      i=0
      while i<self.idletime*60:
        time.sleep(1)
        i+=1

  # Retrieves the "bestalgo" from TMB api
  def best_algo(self):
    data = self.api.bestalgo()
    # parse json data into variables
    algo1 = data[0]["algo"];
    score1 = float(data[0]["score"]);
    algo2 = data[1]["algo"];
    score2 = float(data[1]["score"]);
     
    # return result
    if (score2 - score1) / score1 > self.profitability_threshold:
      return algo2
    elif (score1 - score2) / score2 > self.profitability_threshold:
      return algo1
    else:
      return None


  # Return scrypt/nscrypt based on the version of the miner running
  def current_algo(self):
    data = self.cgminer.version()
    version = data['STATUS'][0]['Description']
    if version.startswith('vertminer'): # vertminer 0.5.4pre1
      return 'nscrypt'
    elif version.startswith('cgminer'): # cgminer 3.7.2
      return 'scrypt'
    else:
      return None

  # Tells the current miner to exit and start the other one
  def switch_algo(self, algo):
    self.logger.info('=> Switching to %s (running %s)' % (algo, self.algos[algo].command))
    self.cgminer.quit()
    time.sleep(1) # Wait for it to quit / Or check the process id?
    subprocess.Popen(self.algos[algo].command)

  def __prepare_logger(self):
    # Prepare logger
    self.logger = logging.getLogger()
    self.logger.setLevel(logging.DEBUG)
    
    # create console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    # create formatter and add it to the handler
    #formatter = logging.Formatter('%(asctime)s :: %(levelname)8s :: %(message)s', "%Y-%m-%d %H:%M:%S")
    formatter = logging.Formatter('%(asctime)s :: %(message)s', "%Y-%m-%d %H:%M:%S")
    stream_handler.setFormatter(formatter)
    
    # add the handler to the logger
    self.logger.addHandler(stream_handler)

  def __load_config(self):
    # Load the config file
    config = ConfigParser.ConfigParser()
    config.read('./tmb-switcher.conf')

    # Read the settings or use default values
    try:
      self.api_key = config.get('TradeMyBit', 'apikey')
    except:
      self.logger.critical("Could not read apikey from config file")
      sys.exit()
    try:
      self.idletime = int(config.get('Misc','idletime'))
    except:
      self.logger.warning("Could not read idletime from config file. Defaulting to 5 min")
      self.idletime = 5
    try:
      self.profitability_threshold = float(config.get('Misc','profitability_threshold'))
    except:
      self.logger.warning("Could not read profitability_threshold from config file. Defaulting to 10%")
      self.profitability_threshold = 0.1
    try:
      self.cgminer_host = config.get('cgminer', 'host')
    except:
      self.logger.warning("Could not read cgminer host from config file. Defaulting to 127.0.0.1")
      self.cgminer_host = '127.0.0.1'
    try:
      self.cgminer_port = int(config.get('cgminer', 'port'))
    except:
      self.logger.warning("Could not read cgminer port from config file. Defaulting to 4028")
      self.cgminer_host = 4028

    for key in self.algos:
        try:
            self.algos[key].command = config.get('Scripts',key)
        except:
            continue

switcher = TradeMyBitSwitcher()
switcher.main()
