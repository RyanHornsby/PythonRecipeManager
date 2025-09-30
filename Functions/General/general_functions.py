import os, sys, time
from . import ASCII_generator as ASCII

## Creates global variables accessed by all files
systemBroken = False
userName = ""
firstLoop = True
firstTimeInMainMenu = True
repeatInstructionsWarning = False
searchResults = ""
searchResultsList = []
currentMenu = "main"
backOneStep = False
backOutFromModify = False
viewFromAdd = False
viewFromSearch = False
editFromView = False
bookTitle = ""
## Creates a list of safe-characters for recipe titles to prevent issues with file-naming (like slashes etc)
safeCharacters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-+*:_'@£$%&() ")

## Overwrites the whole screen. Massive simplification from the "smart" way I was doing it before.
## Originally deleted specific block sizes to leave the ASCII art. What a headache always recalculating how many lines to overwrite.
## God I wish I'd realised this alternate method earlier.
## Optional parameter to disable the flash if wanted
def clear_text(flash=True):
    global bookTitle, firstTimeInMainMenu
    ## Have to import in here to avoid circular logic :-(
    if firstTimeInMainMenu:
        from recipe_manager import myCookbook
        bookTitle = myCookbook.title
        firstTimeInMainMenu = False

    ## Clears the whole screen, including scroll regions
    os.system("cls")
    ## Prints out the stationary ASCII that is always visible
    sys.stdout.write("\r\033[2K\033[14A" + ASCII.steam[0] + "\n" + ASCII.pan["FINAL"] + "\n" + ASCII.fire[0] + f"\n\nWelcome to my personal cookbook - {bookTitle}!\nPlease, feel free to contribute any of your own recipes, or if you think you can improve mine, show me how!\n-----------------------------------------------------------------------------------------------------------\n\033[39m")
    sys.stdout.flush()

    ## Slight delay to make it clear to the user their action was detected
    if flash:
        time.sleep(0.15)

## Output for when they put an invalid input for a list
def failedInput(finalNum):
    clear_text()
    sys.stdout.write(f"\n\033[38;5;203mSorry, I couldn't understand that. Please only enter a number from 1-{finalNum}.\033[0m\n")
    sys.stdout.flush()
