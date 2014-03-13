# TradeMyBit Switcher

A script to switch between the scrypt and n-scrypt multipool as profitability dictates.

Currently tested on:
* xubuntu 13.10 with cgminer-kalroth and vertminer
* xubuntu 13.10 with sgminer (nfactor branch)
* SMOS Linux (Strider3000)

## Dependencies

* Python

## Usage

1. Download or clone this repository

2. Have a look at example scripts in the `scripts` folder, and rename/edit them according to your system setup. cgminer API *must* be enabled (`--api-listen --api-allow W:127.0.0.1`)

3. Rename `tmb-switcher.conf.sample` to `tmb-switcher.conf` and edit it to set everything up, including your TradeMyBit API key and the path to your scripts.

4. Finally run: `python trademybit-switcher.py`


```
$ python trademybit-switcher.py 
------------------------------------------------------------------------
2014-03-13 09:27:34 :: Fetching data...
2014-03-13 09:27:35 :: scrypt : 128.310230 | nscrypt: 120.328550
2014-03-13 09:27:35 :: => Best: None | Currently mining: None
2014-03-13 09:27:35 :: No miner running
2014-03-13 09:27:35 :: => Switching to nscrypt (running ./scripts/nscrypt.sgminer.sh)
...
2014-03-13 18:35:56 :: nscrypt : 122.925360 | scrypt: 77.183520
2014-03-13 18:35:56 :: => Best: nscrypt | Currently mining: scrypt
2014-03-13 18:35:56 :: => Switching to nscrypt (running ./scripts/nscrypt.sgminer.sh)
2014-03-13 18:35:57 :: Going to sleep for 5min...
...
```

### SMOS Usage

_Scripts courtesy of Strider3000._

You'll need to have two `cgminer.conf` files under `/etc/bamt/`, `cgminer_scrypt.conf` and `cgminer_nscrypt.conf`.
Then use the sample `xxx.smos.sh.example` scripts in the `scripts` folder.

## Support

Join `#switcher` on `irc.framper.com`

## Todo & ideas
* Improve output/log
  * Stats?
  * Round time and submitted shares?
* Improve switching algorithm. Use SMA?
* CudaMiner support
* Monitoring
  * Gpu status => auto restart
  * Gpu hash speed / temperature => log or email?

## Credits & Tips
In hope, not expectation:

* BTC: `1JTGQbeh74jVFHhGAddYKe3S6oA8azmArk`
* LTC: `LepbPVTB2hovQnedWX75Cea57mezKyBGkW`

And if you'd like to tip other people whose work is used here:
* merc for the awesome TradeMyBit pool (at time of writing. See https://pool.trademybit.com/ for latest):
  * BTC: `1GQmF3QdrftVmhvP8HrgEwyZTztjDuiJLC`
  * LTC: `LKp4mcPeGmfyvP6amY27Q9TzRq3wkp5zJJ`
* CryptoSwitcher (https://github.com/area/CryptoSwitcher) for the general idea 
  * BTC : `1NhathL6LpcgofDnHELSS6Hej6kU9xrVgp`
* tsileo for the cgminer API wrapper (https://github.com/tsileo/pycgminer)
  * BTC `18ZcxHsKnc4a1AhnThQ2tiLVjQehxKaGFX` 
