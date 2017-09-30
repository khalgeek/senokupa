# Senokupa - An Idle time process runner
This script monitors the screensaver and starts a configurable process when the screensaver starts and kills it when the screensaver stops.

The word **senokupa** is Esperanto for idle or unoccupied.  It originated as a means to mine crytocurrencies during machine idle time and evolved to be more generic.

## Configuration
Configuration is stored in `~/.config/senokuparc` and contains:

```
[Main]
command = ethminer <args>
```

## Running
Run the command with `python senokupa.py` in another virtual console.