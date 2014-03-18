#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import ConfigParser
import logging
import socket
import subprocess
import sys
import time

from trademybitapi import TradeMyBitAPI
from pycgminer import CgminerAPI


class Algo:
    def __init__(self, name):
        self.command    = '' # the command that is run when we want to mine this coin.
        self.name       = name
        self.cnt        = 0

class TradeMyBitSwitcher(object):
    def __init__(self):
        # Define supported algo
        self.algos = {}
        self.algos['scrypt']  =  Algo('Scrypt')
        self.algos['nscrypt'] =  Algo('N-Scrypt')

        self.__load_config()
        self.api = TradeMyBitAPI(self.api_key, 'https://pool.trademybit.com/api/')
        self.cgminer = CgminerAPI(self.cgminer_host, self.cgminer_port)

        # We track state in a variable
        self.current_algo = None

    def main(self):
        # cnt_all = 0
        # main loop
        print '-' * 72

        while True:
            # print header
            # self.logger.info("<<< Round %d >>>" % (cnt_all+1))
          
            # get data from sources
            self.logger.debug("Fetching data...")
            bestalgo = self.best_algo()
          
            self.logger.debug("=> Best: %s | Currently mining: %s" % (bestalgo, self.current_algo))
         
            if bestalgo != self.current_algo and bestalgo != None:
                # i.e. if we're not already mining the best algo
                self.switch_algo(bestalgo)

            elif self.current_algo == None:
                # No miner running and profitability is similar, run the first algo
                self.logger.warning('No miner running')
                self.switch_algo(self.algos.keys()[0])

            # sleep
            self.logger.debug('Going to sleep for %dmin...' % self.idletime)
            i = 0
            while i < self.idletime*60:
                time.sleep(1)
                i += 1

    def best_algo(self):
        """Retrieves the "bestalgo" from TMB api"""
        try:
            data = self.api.bestalgo()
            # parse json data into variables
            algo1 = data[0]["algo"]
            score1 = float(data[0]["score"])
            algo2 = data[1]["algo"]
            score2 = float(data[1]["score"])

            self.logger.debug("%s : %f | %s: %f" % (algo1, score1, algo2, score2))

            # return result
            if (score2 - score1) / score1 > self.profitability_threshold:
                return algo2
            elif (score1 - score2) / score2 > self.profitability_threshold:
                return algo1
            else:
                return None
        except socket.error: # cgminer not running?
            self.logger.warning('Cannot connect to TMB API...')
            return None

    # # Return scrypt/nscrypt based on the version of the miner running
    # # Temporarly disabled to support sgminer since we can't reliably determine
    # # if sgminer is mining nfactor 10 or 11
    # def current_algo(self):
    #     try:
    #         data = self.cgminer.version()
    #         version = data['STATUS'][0]['Description']
    #         if version.startswith('vertminer'): # vertminer 0.5.4pre1
    #             return 'nscrypt'
    #         elif version.startswith('cgminer'): # cgminer 3.7.2
    #             return 'scrypt'
    #         else:
    #             return None
    #     except:
    #         self.logger.warning('Cannot connect to miner API...')
    #         return None

    def switch_algo(self, algo):
        """Tells the current miner to exit and start the other one"""
        self.logger.info('=> Switching to %s (running %s)' % (algo, self.algos[algo].command))
        self.current_algo = algo
        try:
            self.cgminer.quit()
            time.sleep(self.switchtime) # Wait for it to quit / Or check the process id?
        except socket.error:
            pass # Cgminer not running
        subprocess.Popen(self.algos[algo].command)

    def __prepare_logger(self, logging_config={}):
        """Configure the logger"""

        logfile = logging_config.get('logfile')

        # Set console log level based on the config
        if bool(logging_config.get('verbose')):
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO

        # Prepare logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        ## Console logging
        
        # create console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)

        # create formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s :: %(message)s', "%Y-%m-%d %H:%M:%S")
        stream_handler.setFormatter(formatter)

        # add the handler to the logger
        self.logger.addHandler(stream_handler)

        ## File logging

        if logfile:
            print "Logging to %s" % logfile
            # create file handler
            file_handler = logging.FileHandler(logfile, 'a')
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s :: %(levelname)8s :: %(message)s', "%Y-%m-%d %H:%M:%S")
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

    def __load_config(self):
        # Load the config file
        config = ConfigParser.ConfigParser()
        config.read('./tmb-switcher.conf')

        # Read the logging settings and setup the logger
        logging_config = dict(config.items('Logging'))
        self.__prepare_logger(logging_config)

        # Read the settings or use default values
        try:
            self.api_key = config.get('TradeMyBit', 'apikey')
        except:
            self.logger.critical("Could not read apikey from config file")
            sys.exit()
        try:
            self.idletime = config.getint('Misc','idletime')
        except:
            self.logger.warning("Could not read idletime from config file. Defaulting to 5 min")
            self.idletime = 5
        try:
            self.switchtime = config.getint('Misc', 'switchtime')
        except:
            self.logger.warning("Could not read switchtime from config file. Defaulting to 1s")
            self.switchtime = 1
        try:
            self.profitability_threshold = config.getfloat('Misc','profitability_threshold')
        except:
            self.logger.warning("Could not read profitability_threshold from config file. Defaulting to 10%")
            self.profitability_threshold = 0.1
        try:
            self.cgminer_host = config.get('cgminer', 'host')
        except:
            self.logger.warning("Could not read cgminer host from config file. Defaulting to 127.0.0.1")
            self.cgminer_host = '127.0.0.1'
        try:
            self.cgminer_port = config.getint('cgminer', 'port')
        except:
            self.logger.warning("Could not read cgminer port from config file. Defaulting to 4028")
            self.cgminer_host = 4028

        for key in self.algos:
            try:
                script = config.get('Scripts', key)
                if os.path.isfile(script):
                    self.algos[key].command = script
                else:
                    self.logger.critical('Script for %s not found!' % key)
                    self.cleanup()
            except ConfigParser.NoOptionError :
                self.logger.warning('Script for %s not configured!' % key)
                continue

def main():
    switcher = TradeMyBitSwitcher()
    switcher.main()

if __name__ == '__main__':
    main()
