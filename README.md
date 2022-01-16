#How to use
High level steps are:
1. Open the TP and capture screenshots of every relevant page
   1. Run your ass to a TP
   2. Open the TP
   3. Select the tab on the left you want to scrape (Resources, Consumables, etc.). We have to do one category at a time because of the 20 minute AFK timeout. There is currently no AFK protection in the screen capture utility.
   4. Run market_screen_capper.py to gather screenshots
      1. Answer the questions it asks you
   5. look through the output and look at the final screenshots - delete the duplicates  if they exist. There is currently no code to detect when market pages run out. This may be automated some day...
   6. Repeat steps 3 - 5 for each category of interest.
   7. Combine all of the screenshots into one directory.
2. Run those screenshots through the Parser in a big batch
   1. Run the third party tool `resources/Parser.0.1.9/Parser.exe`.
   2. Select all of the combined screenshots.
3. Convert the JSON output of the Parser to CSV to easily plug data into the OHG Market Tracker DATA tab
   1. Run `market_json_to_csv.py` on the file output by the parser
4. Copy and paste the output CSV output (file) of `market_json_to_csv.py` into the DATA tab of the OHG Market Tracker spreadsheet



