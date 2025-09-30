import click, json, msvcrt, sys, textwrap
from ..General import general_functions as GenFuncs
import Functions.General.audit_logger as auditLogger
import recipe_manager as RM

## Checks the dish name is acceptable
def sanitizeDishName(dishName, entryMethod):
    recipeAlreadyExists = True
    dishName = dishName.capitalize()
    if dishName.upper() == "\\EXIT":
        GenFuncs.backOneStep = True
        return "\\EXIT"

    ## Checks if name is fully blank
    if not dishName:
        GenFuncs.clear_text()
        if entryMethod == "fromAdd":
            sys.stdout.write(textwrap.dedent("""
            \033[38;5;203mI'm sorry, but that dish's name appears to be blank!\033[0m
    
            \033[1m\033[3mPlease enter a new name: (Type \"\\EXIT\" to quit)\033[0m
            > """))
        else:
            sys.stdout.write(textwrap.dedent("""
            \033[38;5;203mYikes! You don't appear to have entered anything to search for. Please try again.\033[0m
            """))
        sys.stdout.flush()
        return ""

    ## Checks if the dish name is only safe characters (ones safe for creating Windows files)
    if not all(safe in GenFuncs.safeCharacters for safe in dishName):
        GenFuncs.clear_text()
        warningMessage = "\n        \033[1m\033[3mPlease enter a new name: (Type \"\\EXIT\" to quit)\033[0m\n        > " if entryMethod == "fromAdd" else "\n        This means there couldn't be any dishes containing that search query.\n        Please, try again without any prohibited characters.\n" if entryMethod == "fromSearch" else "        CODE BROKE"
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mI'm sorry, but that dish's name ({dishName}) uses a non-allowed character.\033[0m
        Safe characters are alphanumeric, spaces or any of these: -, +, *, :, _, ', @, £, $, %, &, (, ).
        {warningMessage}"""))
        sys.stdout.flush()
        return ""

    if entryMethod == "fromAdd":
        ## Checks if the recipe already exists
        GenFuncs.clear_text()
        GenFuncs.firstLoop = True
        while recipeAlreadyExists:
            if any(dishName == inBook.capitalize() for inBook in RM.myCookbook.recipes):
                if GenFuncs.firstLoop:
                    sys.stdout.write(textwrap.dedent(f"""
                    \033[38;5;203mLooks like we already have a recipe for {dishName}!\033[0m
                    
                    \033[1m\033[3mWould you prefer to:\033[0m
                        1. View the existing recipe
                        2. Create a new recipe for something else
                        3. Return to the previous menu ↵
                        
                    \033[1m\033[3mPlease enter your choice:\033[0m
                    > """))
                else:
                    sys.stdout.write(textwrap.dedent(f"""
                    \033[1m\033[3mWould you prefer to:\033[0m
                        1. View the existing recipe ({dishName})
                        2. Create a new recipe for something else
                        3. Return to the previous menu ↵
    
                    \033[1m\033[3mPlease enter your choice:\033[0m
                    > """))
                sys.stdout.flush()
                recipeExistsInput = input().strip()
                match recipeExistsInput:
                    case "1":
                        GenFuncs.clear_text()
                        GenFuncs.currentMenu = "main"
                        GenFuncs.firstLoop = True
                        GenFuncs.backOneStep = True
                        GenFuncs.viewFromAdd = True
                        return dishName

                    case "2":
                        GenFuncs.clear_text()
                        GenFuncs.backOneStep = True
                        return dishName

                    case "3":
                        GenFuncs.clear_text()
                        GenFuncs.currentMenu = "contribute"
                        return dishName

                    case _:
                        GenFuncs.firstLoop = False
                        GenFuncs.failedInput(3)
                        continue
            recipeAlreadyExists = False
    return dishName

## Checks the dish ingredients are acceptable
def sanitizeDishIngredients(dishName, dishIngredients, entryMethod):
    dishName = dishName.capitalize()
    ## Different text based on entry method
    midSentence = f"required to make {dishName}" if entryMethod == "byAdd" else "you wish to search for" if entryMethod == "bySearch" else "CODE BROKE"

    ## Splits it into a list of all the different ingredients, cleans up any empty entries
    if dishIngredients.strip().upper() == "\\EXIT":
        return "\\EXIT"
    ingredients = dishIngredients.split(",")
    ## Originally did set not dict, but need to do this to preserve order
    ingredients = list(dict.fromkeys(valid.strip().capitalize() for valid in ingredients if valid.strip()))
    if not ingredients:
        GenFuncs.clear_text()
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mWhoops, you appeared to have entered no ingredients!\033[0m

        \033[1m\033[3mPlease enter all the ingredients {midSentence}, comma-separated: (Type \"\\EXIT\" to quit)\033[0m
        > """))
        sys.stdout.flush()
        return ""

    GenFuncs.clear_text()
    return ingredients

## Creates a text file for storing the instructions and opens it for a typing interface for the user
def storeInstructionsAsTxtFile(dishName):
    GenFuncs.firstLoop = True
    safeToExit = False
    typedInstructions = ""
    dishName = dishName.capitalize()

    ## While loop makes it so I can handle when they enter a bad answer for the error menu
    while not safeToExit:
        if GenFuncs.firstLoop:
            ## Creates empty file for the instructions, prevents "do you want to create file" from showing up when it creates actual file
            typedInstructions = click.edit(f"How to make {dishName}:\n\n").rstrip("\n").strip()
            GenFuncs.clear_text()

        if not typedInstructions or typedInstructions == f"How to make {dishName}:":
            if GenFuncs.firstLoop:
                sys.stdout.write(textwrap.dedent(f"""
                \033[38;5;203mOh dear, either you left the file blank, didn't save your changes or you didn't change it at all.\033[0m
                
                \033[1m\033[3mWhat would you like to do?\033[0m
                    1. Try again!
                    2. Abandon the recipe (return to previous menu ↵)
        
                \033[1m\033[3mPlease enter your choice:\033[0m
                > """))
                sys.stdout.flush()
            else:
                sys.stdout.write(textwrap.dedent(f"""
                \033[1m\033[3mWhat would you like to do?\033[0m
                    1. Try again!
                    2. Abandon the recipe (return to previous menu ↵)

                \033[1m\033[3mPlease enter your choice:\033[0m
                > """))
                sys.stdout.flush()
            failedInstructions = input()

            match failedInstructions:
                case "1":
                    GenFuncs.clear_text()
                    sys.stdout.write(textwrap.dedent(f"""
                    Now re-opening the instructions file for {dishName}.
                    """))
                    sys.stdout.flush()
                    return ""

                case "2":
                    GenFuncs.clear_text()
                    GenFuncs.currentMenu = "contribute"
                    return "backToMenu"

                case _:
                    GenFuncs.firstLoop = False
                    GenFuncs.failedInput(2)
                    continue

        else:
            with open(f"Recipes/{dishName}.txt", "w", encoding="utf-8") as file:
                file.write(typedInstructions)
            sys.stdout.write(textwrap.dedent(f"""
            Wonderful! Thank you for adding the recipe to make {dishName}, {GenFuncs.userName.split(" ")[0]}.
            
            \033[1m\033[3mPress enter to return to the main menu ↵!\033[0m
            > """))
            sys.stdout.flush()
            while True:
                key = msvcrt.getwch()
                if key == "\r":
                    sys.stdout.write("\r\033[2K")
                    sys.stdout.flush()
                    break
            return f"Recipes/{dishName}.txt"

## Adds the new recipe to the list, also adds it to the JSON file to store it permanently
def saveRecipe(dishName, dishIngredients, dishInstructions, author):
    dishName = dishName.capitalize()
    RM.myCookbook.recipes[dishName] = {"ingredients": dishIngredients, "instructions": dishInstructions, "inventor": author}
    with open(r"Recipes/savedRecipes.json", "r+", encoding="utf-8") as recipesFile:
        allRecipes = json.load(recipesFile)
        allRecipes[dishName] = {"ingredients": dishIngredients, "instructions": dishInstructions, "inventor": author}
        ## Moves to the start of file, overwrites what's already there
        recipesFile.seek(0)
        recipesFile.truncate()
        json.dump(allRecipes, recipesFile, indent=2)
    ## Logs to the audit file
    with open(RM.myCookbook.recipes[dishName]["instructions"], "r", encoding="utf-8") as instructionsFile:
        dishInstructions = instructionsFile.read()
    auditLogger.logChange(action="addRecipe", dishName=dishName, dishIngredients=dishIngredients, dishInstructions=dishInstructions)