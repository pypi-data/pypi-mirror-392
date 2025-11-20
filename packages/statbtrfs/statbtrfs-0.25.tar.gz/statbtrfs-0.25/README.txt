usage: statbtrfs [-h] [-s] [-i INTERVAL] [-m MAX_SCRUB_COUNT] [--scrub_command_lockout SCRUB_COMMAND_LOCKOUT] [-V]

Check Btrfs filesystem status.

optional arguments:
  -h, --help            show this help message and exit
  -s, --scrub           Issue scrub to all pools
  -i INTERVAL, --interval INTERVAL
                        Interval for status check in seconds
  -m MAX_SCRUB_COUNT, --max_scrub_count MAX_SCRUB_COUNT
                        Maximum number of scrubs to issue at the same time
  --scrub_command_lockout SCRUB_COMMAND_LOCKOUT
                        Lockout for scrub command. Used to block two commands sent quickly.
  -V, --version         show program's version number and exit


Install:
sudo pip install statbtrfs