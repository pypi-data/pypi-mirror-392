# `ddresolve` Distributed Directory name resolver

This tool resolves names to addresses, starting from your local directory and 
following links to other directories.

PROTOTYPE! This is still a work-in-progress. Currently only the local-directory resolving is implemented.

To try it out:

+ Clone this repository
+ Create a file `~/.local/share/petnames/local/server1.txt` containing lines like these:

```
suggested_name=Server One
desthash=aabbccddeeffaabbccddeeffaabbccdd
identity=bacdbacd
```

+ Run `./ddresolve.py server1` which should display : `aabbccddeeffaabbccddeeffaabbccdd`

There is also a modified version of rnx.py which will resolve names instead of destination hashes, so you can run:

```
./rnx.py server1 'cat /proc/cpuinfo'
```

## Usage:
ddresolve.py NAME [PROPERTY]

NAME is a "dot" seperated sequence of names

PROPERTY is the record property you want to retrieve, or 'all' (default: 'desthash')
