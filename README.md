# How to use
High level steps are:
1. Go stand in front of a TP
2. Run market_screen_capture_utility.py
   1. You will automatically crouch, open the TP and start clicking around. 
   2. Screenshots will be taken and stored in ./output/market_screenshotsXXX. 
   3. Every so often, you will disengage from the TP, walk back a bit, walk forward a bit and reengage with the TP. This is the anti-anti-afk functionality. 
3. Run those screenshots through the Parser in a big batch
   1. Run the third party tool `resources/Parser.0.1.9/Parser.exe`.
   2. Select all of the combined screenshots.
   3. Select export and save the file as ./output/file.json
4. Convert the JSON output of the Parser to a bunch of lists to easily plug data into the OHG Market Tracker DATA tab. Specifically, use market_gsheet or market_gsheet_prices only.
   1. Run `market_json_to_csv.py` on the file output by the parser
   2. You will see some new files called `market_gsheetXXX.csv` and `market_gsheet_prices_onlyXXX.csv`.
5. Copy and paste the output CSV output (file) of `market_gsheetXXX.csv` into the DATA tab of the OHG Market Tracker spreadsheet
   1. In the future, we will keep a history of prices. That's what the market_gsheet_prices_only list is for. It's a list of prices that will always be in the same order. We can just copy and paste the data from that sheet into the next column of our gsheet once we setup history there.

# Integration with NW profession cost calculator
It seems like you can go to this page:
https://gaming.tools/newworld/price-customization

I followed the github of the creater of the parser I'm using - it had a link to a discord - the discord they're using has discussion of this website. This is why I believe the format of the file is compatible with the website. I've also tried it and it seemed to work 🙂 - the website gives no information about the parser or the format of the json it expects, so I suppose we got lucky here.

Scroll to the bottom, and you will see that you can importa JSON file. The JSON output from the parser seems to be what this is expecting. Unfortunately you'll get some whacky results in that JSON, so do this at your own risk. I will create another utility that will do a sanity check on the JSON and strip out whacky results for better integration with this page.


## Requirements for using these tools
- Python 3.10

- Python libraries found in requirements.txt

- Must install pytesseact for OCR - don't forget to add it to your path
https://digi.bib.uni-mannheim.de/tesseract/?C=M;O=D

- Might be a requirement to have screen resolution set to 1920x1080

- Might be a requirement to have game resolution set to 1920x1080

- Ummm... probably need NW...

Game window must be docked at pixel coordinates 0,0 (probably) because of the python libraries being used. It seems like some of the libraries use absolute pixel values rather than pixel values relative to the active window.
