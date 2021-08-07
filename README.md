## example:

```
python join_groups.py -a "fb_accounts.csv"  -f "group_ids.csv" -m 1
```

## usage:

```usage: join_groups.py [-h] [-f FILE] [-a ACCOUNTFILE]

Join facebook groups with ids specified in a file

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to text file which contains group ids that we need to join
  -a ACCOUNTFILE, --accountfile ACCOUNTFILE
                        path to csv file which contains facebook accounts
  -m MODE, --mode MODE  choose working mode:mode 0: join, mode 1: check join,mode 2: join then check join
```
