# How to use
High level steps are:
1. Go stand in front of a TP
2. Run market_screen_capture_utility.py
   1. You will automatically crouch, open the TP and start clicking around. 
   2. Screenshots will be taken and stored in ./output/market_screenshotsXXX. 
   3. Every so often, you will disengage from the TP, walk back a bit, walk forward a bit and reengage with the TP. This is the anti-afk functionality. 
4. Run those screenshots through the Parser in a big batch
   1. Run the third party tool `resources/Parser.0.1.9/Parser.exe`.
   2. Select all of the combined screenshots.
   3. Select export and save the file as ./output/file.json
5. Convert the JSON output of the Parser to CSV to easily plug data into the OHG Market Tracker DATA tab
   1. Run `market_json_to_csv.py` on the file output by the parser
   2. You will see a new file called marketXXX.csv
6. Copy and paste the output CSV output (file) of `market_json_to_csv.py` into the DATA tab of the OHG Market Tracker spreadsheet



## Requirements
Must install pytesseact for OCR - don't forget to add it to your path
https://digi.bib.uni-mannheim.de/tesseract/?C=M;O=D

Might be a requirement to have screen resolution set to 1920x1080
Might be a requirement to have game resolution set to 1920x1080
