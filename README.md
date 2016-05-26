# SCOTUS Scraper
A tool that downloads argument audio, argument transcripts, and slip opinions from supremecourt.gov

Classes
- Scotus
  - Controls the main window 
- ScotusParser: Parses [supremecourt.gov](http://supremecourt.gov) pages and finds links to files
  - Three main functions that find argument audio, slip opinions, and argument transcripts. These return tuples of the format `(url, path)`
- Downloader
- LogListener
  - Keeps track of log files and updates the console with the most recent log messages

Todo:
[ ]: Refactor
[ ]: Re-add basic functionality to Scotus
[ ]: Rewrite Downloader
[ ]: Write LogListener
