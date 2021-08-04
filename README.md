## example:
```
python join_groups.py -a "fb_accounts.csv" -o "out.json" -f "group_ids.txt"
```
## usage: 
```join_groups.py [-h] [-f FILE] [-o OUTFILE] [-a ACCOUNTFILE]

Join facebook groups with ids specified in a file

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to text file which contains group ids that we need to join
  -o OUTFILE, --outfile OUTFILE
                        path to json file which contains joined group ids
  -a ACCOUNTFILE, --accountfile ACCOUNTFILE
                        path to csv file which contains facebook accounts```