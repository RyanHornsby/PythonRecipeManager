import json, msvcrt, sys, textwrap, time

## Importing from my other files
import Functions.General.audit_logger as auditLogger
import Functions.General.ASCII_generator as ASCII_generator
import Functions.General.general_functions as GenFuncs
import Functions.Recipe_Manipulation.list_recipes as listRecipes
import Functions.Recipe_Manipulation.search_recipes as searchRecipes
import Functions.Recipe_Manipulation.add_recipe as addRecipe
import Functions.Recipe_Manipulation.edit_recipe as editRecipe
import Functions.Recipe_Manipulation.delete_recipe as deleteRecipe

## Cookbook class constructor. Was originally going to have multiple cookbooks, but scaled back ambition
class Cookbook:
    ## Loads the recipes. If file not there, creates it
    try:
        with open(r"Recipes\savedRecipes.json", "r", encoding="utf-8") as recipesFile:
            recipes = json.load(recipesFile)
    ## If file is corrupt, just overwrite it. Could offer a warning to go check it, this is more elegant for now
    except (FileNotFoundError, json.JSONDecodeError):
        with open(r"Recipes\savedRecipes.json", "w", encoding="utf-8") as recipesFile:
            recipesFile.write("{\n\n}")
        recipes = {}
        ## Logs to the audit file
        auditLogger.logChange(action="createJSON")

    def __init__(self, title, author):
        self.title = title
        self.author = author

## Initialises original cookbook
myCookbook = Cookbook("Ryan's \033[3m\"Pie-fun\"\033[23m Cookbook", "Ryan Hornsby")
if __name__ == "__main__":
    while GenFuncs.currentMenu != "exit":
        ## Loads stuff that sticks around for the first time
        if GenFuncs.firstTimeInMainMenu:
            ASCII_generator.ASCII()
            GenFuncs.clear_text()

            while not GenFuncs.userName:
                sys.stdout.write("\n\033[1m\033[3mTo begin, could I please get your name?\033[0m\n> ")
                sys.stdout.flush()
                GenFuncs.userName = input().strip().title()
                if not GenFuncs.userName:
                    GenFuncs.clear_text()
                    sys.stdout.write(f"\n\033[38;5;203mWhoops, sorry! You don't appear to have entered anything for your name. Would you mind trying again?\033[0m\n")
                    sys.stdout.flush()
            GenFuncs.clear_text()
            sys.stdout.write(f"\nWelcome, {GenFuncs.userName.strip().split(" ")[0]}!\n")
            sys.stdout.flush()

        ## Displays the relevant menu for where you are in the cookbook
        match GenFuncs.currentMenu:
            case "main":
                if GenFuncs.viewFromAdd or GenFuncs.viewFromSearch or GenFuncs.editFromView:
                    userInputMain = "1"
                    if GenFuncs.editFromView:
                        userInputMain = "3"
                        GenFuncs.currentMenu = "editRecipe"
                else:
                    sys.stdout.write(textwrap.dedent("""
                    \033[1m\033[3mWhat would you like to do?\033[0m
                        1. List all recipes we currently have
                        2. Search for recipes via name / ingredients / creator
                        3. Contribute to the recipes via adding / editing / deleting
                        4. Close the book
                        
                    \033[1m\033[3mPlease enter your choice:\033[0m
                    > """))
                    if GenFuncs.firstTimeInMainMenu:
                        GenFuncs.firstTimeInMainMenu = False

                    userInputMain = input().strip()

                match userInputMain:
                    case "1":
                        GenFuncs.currentMenu = "recipes"
                        while GenFuncs.currentMenu == "recipes":
                            GenFuncs.currentMenu = "viewRecipes"
                            ## Handles when there are no recipes
                            if not myCookbook.recipes:
                                GenFuncs.clear_text()
                                sys.stdout.write(textwrap.dedent(f"""
                                Ah. There are no recipes in the book. Couldn't you tell from how light it was to pick up?
                                
                                No? Not a fan of making physical jokes about digital objects?                                  
                                Aw man, I really thought I was cooking with that one.                       
                                          
                                Oh well...
                                
                                \033[1m\033[3mPress enter to return to the main menu ↵.\033[0m
                                > """))
                                sys.stdout.flush()
                                ## Only continues if they press enter, doesn't let them type anything. Clears itself bc was having issues
                                while True:
                                    key = msvcrt.getwch()
                                    if key == "\r":
                                        sys.stdout.write("\r\033[2K")
                                        sys.stdout.flush()
                                        break
                                GenFuncs.clear_text()
                                GenFuncs.currentMenu = "main"
                                continue

                            ## Prints out all recipes currently in the cookbook
                            viewAnother = ""
                            GenFuncs.firstLoop = True
                            if not (GenFuncs.viewFromAdd or GenFuncs.viewFromSearch):
                                dishName = ""
                            else:
                                GenFuncs.firstLoop = False
                            GenFuncs.viewFromAdd = False
                            while not viewAnother:
                                ## If they came from a search, only display the ones in that search result
                                customList = ""
                                searchString = ""
                                if GenFuncs.viewFromSearch:
                                    customList = GenFuncs.searchResults
                                    searchString = " (Resets search results)"
                                ## Now need to ask which dish they want to see
                                if GenFuncs.firstLoop:
                                    GenFuncs.clear_text()
                                    allRecipesList = listRecipes.listRecipes(9, customList=customList)
                                    sys.stdout.write(textwrap.dedent(f"""
                                    \033[1m\033[3mWhich recipe would you like to view?\033[0m               
                                    {allRecipesList}
                                    
                                    \033[1m\033[3mPlease, enter your answer below: (Type \"\\EXIT\" to quit ↵){searchString}\033[0m
                                    > """))
                                while not dishName:
                                    dishName = input().strip()
                                    dishName = listRecipes.sanitizeDishName(dishName, "fromView", customList=customList)
                                    if dishName == "dishNotFound":
                                        dishName = ""
                                        continue

                                ## Handles if they said to exit
                                if dishName == "\\EXIT":
                                    GenFuncs.clear_text()
                                    GenFuncs.currentMenu = "main"
                                    GenFuncs.viewFromSearch = False
                                    GenFuncs.searchResults = ""
                                    GenFuncs.searchResultsList = []
                                    break

                                ## Once they have given the dish they wish to view, display it
                                listRecipes.displayRecipe(dishName)
                                viewAnother = input().strip()

                                match viewAnother:
                                    case "1":
                                        GenFuncs.firstLoop = True
                                        dishName = ""
                                        viewAnother = ""
                                        continue

                                    case "2":
                                        GenFuncs.currentMenu = "main"
                                        GenFuncs.editFromView = True
                                        continue

                                    case "3":
                                        GenFuncs.viewFromSearch = False
                                        GenFuncs.searchResults = ""
                                        GenFuncs.searchResultsList = []
                                        GenFuncs.currentMenu = "main"
                                        GenFuncs.clear_text()
                                        break

                                    case _:
                                        GenFuncs.firstLoop = False
                                        GenFuncs.failedInput(3)
                                        viewAnother = ""
                                        continue

                    case "2":
                        searchBy = ""
                        GenFuncs.clear_text()
                        GenFuncs.currentMenu = "search"
                        GenFuncs.searchResults = ""
                        GenFuncs.searchResultsList = []
                        GenFuncs.firstLoop = True
                        while GenFuncs.currentMenu == "search":
                            if GenFuncs.firstLoop:
                                GenFuncs.firstLoop = False
                                sys.stdout.write(textwrap.dedent("""
                                \033[1m\033[3mWhat would you like to search by?\033[0m
                                    1. Recipe titles
                                    2. Ingredients
                                    3. Recipes by specific creators
                                    4. Return to the main menu ↵ 
    
                                \033[1m\033[3mPlease enter your choice:\033[0m
                                > """))
                                sys.stdout.flush()

                            searchBy = input().strip()
                            match searchBy:
                                case "1":
                                    GenFuncs.firstLoop = True
                                    GenFuncs.clear_text()
                                    recipeSearch = ""
                                    while not recipeSearch:
                                        fillerText = ""
                                        if GenFuncs.firstLoop:
                                            GenFuncs.firstLoop = False
                                            fillerText = "\n" + (" "*40) + "Search for any recipe titles that contain your search query.\n"
                                        sys.stdout.write(textwrap.dedent(f"""{fillerText}
                                        \033[1m\033[3mPlease enter your search query: (Type \"\\EXIT\" to quit)\033[0m
                                        > """))
                                        sys.stdout.flush()

                                        recipeSearch = input().strip()
                                        ## Makes sure they searched for valid recipe titles
                                        recipeSearch = addRecipe.sanitizeDishName(recipeSearch, "fromSearch")
                                        if not recipeSearch:
                                            continue
                                        if recipeSearch == "\\EXIT":
                                            GenFuncs.firstLoop = True
                                            GenFuncs.clear_text()
                                            break

                                        ## Now displays the recipes from their search query
                                        recipeSearch = searchRecipes.displayRecipesFromSubstring(recipeSearch)
                                        if not recipeSearch:
                                            continue
                                        if recipeSearch == "\\EXIT":
                                            GenFuncs.viewFromSearch = False
                                            GenFuncs.searchResults = ""
                                            GenFuncs.searchResultsList = []
                                            GenFuncs.firstLoop = True
                                            recipeSearch = ""
                                            break

                                        dishName = recipeSearch
                                    continue

                                case "2":
                                    GenFuncs.firstLoop = True
                                    GenFuncs.clear_text()
                                    ingredientsSearch = ""
                                    while not ingredientsSearch:
                                        if GenFuncs.firstLoop:
                                            GenFuncs.firstLoop = False
                                            sys.stdout.write(textwrap.dedent("""
                                            \033[1m\033[3mPlease enter all the ingredients you wish to search for, comma-separated: (Type \"\\EXIT\" to quit)\033[0m
                                            > """))
                                            sys.stdout.flush()
                                        if GenFuncs.backOneStep:
                                            GenFuncs.firstLoop = True
                                            GenFuncs.backOneStep = False
                                        ingredientsSearch = input().strip()
                                        ingredientsSearch = addRecipe.sanitizeDishIngredients("", ingredientsSearch,"bySearch")
                                        if not ingredientsSearch or ingredientsSearch == "\\EXIT":
                                            if ingredientsSearch == "\\EXIT":
                                                GenFuncs.firstLoop = True
                                                GenFuncs.clear_text()
                                            else:
                                                GenFuncs.firstLoop = False
                                                GenFuncs.backOneStep = True
                                            continue
                                        ## If valid ingredients to search, do the actual search
                                        ingredientsSearch = searchRecipes.searchIngredients(ingredientsSearch)
                                        if not ingredientsSearch or ingredientsSearch == "\\EXIT":
                                            if ingredientsSearch == "\\EXIT":
                                                GenFuncs.firstLoop = True
                                                ingredientsSearch = ""
                                            break

                                        dishName = ingredientsSearch
                                    continue

                                case "3":
                                    GenFuncs.firstLoop = True
                                    GenFuncs.clear_text()
                                    authorSearch = ""
                                    while not authorSearch:
                                        ## Get a set of all authors, then lets them search for them
                                        allAuthors = searchRecipes.getAuthorNames()
                                        authorSearch = input().strip()
                                        ## Validate they entered a valid author
                                        authorSearch = searchRecipes.sanitizeAuthor(authorSearch, allAuthors)
                                        if not authorSearch or authorSearch == "\\EXIT":
                                            if authorSearch == "\\EXIT":
                                                GenFuncs.clear_text()
                                                GenFuncs.firstLoop = True
                                            continue

                                        ## Once they have successfully chosen an author, display all recipes by that author
                                        authorSearch = searchRecipes.displayAuthorRecipes(authorSearch)
                                        if not authorSearch or authorSearch == "\\EXIT":
                                            if authorSearch == "\\EXIT":
                                                GenFuncs.firstLoop = True
                                                authorSearch = ""
                                            break

                                        dishName = authorSearch
                                    continue


                                case "4":
                                    GenFuncs.clear_text()
                                    GenFuncs.currentMenu = "main"
                                    GenFuncs.viewFromSearch = False
                                    GenFuncs.searchResults = ""
                                    GenFuncs.searchResultsList = []

                                case _:
                                    GenFuncs.firstLoop = True
                                    GenFuncs.failedInput(4)

                    case "3":
                        userInputContribute = ""
                        GenFuncs.clear_text()
                        if GenFuncs.editFromView:
                            GenFuncs.currentMenu = "editRecipe"
                        else:
                            GenFuncs.currentMenu = "contribute"
                        ## while loop ensures that I can "continue" back to previous menu
                        while GenFuncs.currentMenu in ["contribute", "addRecipe", "editRecipe", "deleteRecipe"]:
                            if GenFuncs.currentMenu == "contribute":
                                sys.stdout.write(textwrap.dedent("""
                                \033[1m\033[3mHow would you like to contribute?\033[0m
                                    1. Add new recipe
                                    2. Update existing recipe
                                    3. Rip out a page
                                    4. Return to the main menu ↵ 
                                    
                                \033[1m\033[3mPlease enter your choice:\033[0m
                                > """))
                                sys.stdout.flush()
                                userInputContribute = input().strip()
                            elif GenFuncs.currentMenu == "editRecipe":
                                userInputContribute = "2"

                            match userInputContribute:
                                case "1":
                                    dishName = ""
                                    dishIngredients = ""
                                    dishInstructions = ""
                                    ## If they came back via one step, don't run this
                                    if not GenFuncs.backOneStep:
                                        GenFuncs.clear_text()
                                        GenFuncs.currentMenu = "addRecipe"
                                    else:
                                        GenFuncs.backOneStep = False

                                    while GenFuncs.currentMenu == "addRecipe":
                                        ## Gets recipe's name, sanity checks it
                                        sys.stdout.write("\n\033[1m\033[3mWhich delicious dish are you adding to the records today? (Type \"\\EXIT\" to quit ↵)\033[0m\n> ")
                                        sys.stdout.flush()
                                        while not dishName:
                                            dishName = input().strip()
                                            dishName = addRecipe.sanitizeDishName(dishName, "fromAdd")
                                        ## Handles if they said to exit
                                        if GenFuncs.currentMenu == "contribute":
                                            continue
                                        elif GenFuncs.backOneStep:
                                            if dishName == "\\EXIT":
                                                GenFuncs.clear_text()
                                                GenFuncs.currentMenu = "contribute"
                                                GenFuncs.backOneStep = False
                                            break

                                        ## Gets recipe's ingredients
                                        sys.stdout.write(textwrap.dedent(f"""
                                        Perfect! {dishName} it is!
                                        
                                        \033[1m\033[3mWhich ingredients does this mouth-watering meal require?\033[0m
                                        
                                        \033[1m\033[3mPlease, enter them all, comma separated: (Type \"\\EXIT\" to quit ↵)\033[0m
                                        > """))
                                        sys.stdout.flush()
                                        while not dishIngredients:
                                            dishIngredients = input().strip()
                                            dishIngredients = addRecipe.sanitizeDishIngredients(dishName, dishIngredients, "fromAdd")
                                        ## Handles if they said to exit
                                        if dishIngredients == "\\EXIT":
                                            GenFuncs.clear_text()
                                            GenFuncs.currentMenu = "contribute"
                                            break

                                        ## Gets recipe's instructions
                                        sys.stdout.write(textwrap.dedent(f"""
                                        Finally, a text window will open in a few seconds. Once you're done, don't forget to save it, then close the file!
                                         
                                        \033[1m\033[3mNow, please share with us how to craft this palatable plate...\033[0m
                                        """))
                                        sys.stdout.flush()
                                        time.sleep(3)
                                        while not dishInstructions:
                                            dishInstructions = addRecipe.storeInstructionsAsTxtFile(dishName)
                                        ## Handles if they said to exit
                                        if GenFuncs.currentMenu == "contribute":
                                            continue

                                        ## Stores the recipe
                                        addRecipe.saveRecipe(dishName, dishIngredients, dishInstructions, GenFuncs.userName)

                                        ## Resets back to main menu
                                        GenFuncs.clear_text()
                                        GenFuncs.currentMenu = "main"

                                case "2":
                                    GenFuncs.currentMenu = "editRecipe"

                                    ## If no recipes, don't allow editing
                                    if not myCookbook.recipes:
                                        GenFuncs.clear_text()
                                        sys.stdout.write(textwrap.dedent(f"""
                                        Ah... There appears to be no recipes in the book... So you can't edit any...
                                        How awfully embarrassing.
                                        
                                        Please, feel free to add your own...                                        
                                        For now, let's get you back to the main menu...
                                        
                                        \033[1m\033[3mPress enter to get out of here ↵.\033[0m
                                        > """))
                                        sys.stdout.flush()
                                        ## Only continues if they press enter, doesn't let them type anything
                                        while True:
                                            key = msvcrt.getwch()
                                            if key == "\r":
                                                sys.stdout.write("\r\033[2K")
                                                sys.stdout.flush()
                                                break
                                        GenFuncs.clear_text()
                                        GenFuncs.currentMenu = "main"
                                        continue

                                    ## Determines which recipe they want to edit
                                    GenFuncs.firstLoop = True
                                    if GenFuncs.editFromView:
                                        GenFuncs.firstLoop = False
                                    else:
                                        dishName = ""
                                    while not dishName:
                                        ## If they came from a search, only display the ones in that search result
                                        customList = ""
                                        searchString = ""
                                        if GenFuncs.viewFromSearch:
                                            searchString = "(Resets search results) "
                                            customList = GenFuncs.searchResults
                                        allRecipesList = listRecipes.listRecipes(11, customList=customList)
                                        if GenFuncs.firstLoop:
                                            GenFuncs.clear_text()
                                            sys.stdout.write(textwrap.dedent(f"""
                                            \033[1m\033[3mWhich recipe would you like to edit?\033[0m               
                                            {allRecipesList}
                                            
                                            \033[1m\033[3mPlease, enter your answer below: (Type \"\\EXIT\" to quit ↵) {searchString}\033[0m
                                            > """))
                                            sys.stdout.flush()
                                        dishName = input().strip()
                                        dishName = listRecipes.sanitizeDishName(dishName, "fromEdit", customList=customList)
                                        if dishName == "dishNotFound":
                                            dishName = ""
                                        GenFuncs.firstLoop = False
                                    ## Handles if they said to exit
                                    if dishName == "\\EXIT":
                                        GenFuncs.viewFromSearch = False
                                        GenFuncs.searchResults = ""
                                        GenFuncs.searchResultsList = []
                                        GenFuncs.clear_text()
                                        GenFuncs.currentMenu = "contribute"
                                        dishName = ""
                                        continue
                                    GenFuncs.firstLoop = True
                                    if GenFuncs.backOneStep:
                                        GenFuncs.firstLoop = False
                                        GenFuncs.backOneStep = False

                                    ## Asks which part they wish to edit
                                    editChoice = ""
                                    while not editChoice:
                                        ## Custom text if here by search
                                        searchString = ""
                                        if GenFuncs.viewFromSearch:
                                            searchString = "(Resets search results) "
                                        if GenFuncs.firstLoop:
                                            if not GenFuncs.editFromView:
                                                GenFuncs.clear_text()
                                                GenFuncs.editFromView = False
                                            sys.stdout.write(textwrap.dedent(f"""
                                            Looks like {dishName} is getting a make-over!
        
                                            \033[1m\033[3mWhich part of the recipe would you like to change?\033[0m
                                                1. The recipe's name
                                                2. The recipe's ingredients
                                                3. The recipe's instructions
                                                4. Choose a different recipe
                                                5. Return to the previous menu {searchString}↵
        
                                            \033[1m\033[3mPlease, enter your choice below:\033[0m
                                            > """))
                                        else:
                                            sys.stdout.write(textwrap.dedent(f"""
                                            \033[1m\033[3mWhich part of the recipe would you like to change?\033[0m
                                                1. The recipe's name ({dishName})
                                                2. The recipe's ingredients
                                                3. The recipe's instructions
                                                4. Choose a different recipe
                                                5. Return to the previous menu {searchString}↵

                                            \033[1m\033[3mPlease, enter your choice below:\033[0m
                                            > """))
                                        sys.stdout.flush()

                                        GenFuncs.firstLoop = True
                                        if GenFuncs.backOutFromModify:
                                            editChoice = "2"
                                            GenFuncs.backOutFromModify = False
                                        else:
                                            editChoice = input().strip()
                                        changeConfirmed = ""
                                        match editChoice:
                                            case "1":
                                                changedName = ""
                                                while not changedName:
                                                    if GenFuncs.firstLoop:
                                                        GenFuncs.firstLoop = False
                                                        GenFuncs.clear_text()
                                                        sys.stdout.write(textwrap.dedent(f"""
                                                        \033[1m\033[3mWhat would you like to change {dishName}'s name to?\033[0m
 
                                                        \033[1m\033[3mPlease, enter your answer below: (Type \"\\EXIT\" to quit)\033[0m
                                                        > """))
                                                        sys.stdout.flush()
                                                    changedName = input().strip()
                                                    changedName = editRecipe.sanitizeDishname(dishName, changedName)
                                                    if changedName == "\\EXIT":
                                                        GenFuncs.firstLoop = False
                                                        GenFuncs.clear_text()
                                                        editChoice = ""
                                                        break
                                                    if not changedName:
                                                        continue
                                                    ## If name change confirmed, sets it as the dishName so it shows up properly in the menu
                                                    else:
                                                        dishName = changedName
                                                continue

                                            case "2":
                                                changedIngredients = ""
                                                while not changedIngredients:
                                                    if GenFuncs.firstLoop:
                                                        GenFuncs.firstLoop = False
                                                        GenFuncs.clear_text()
                                                    ## Gets the current ingredients
                                                    currentIngredients = listRecipes.listIngredients(dishName, 13)
                                                    sys.stdout.write(textwrap.dedent(f"""
                                                    \033[1m\033[3mHere are the current ingredients for {dishName}:\033[0m
                                                    {currentIngredients}

                                                    \033[1m\033[3mHow would you like to modify then?\033[0m
                                                        1. Add new ingredients
                                                        2. Remove ingredients
                                                        3. Overwrite all ingredients
                                                        4. Return to previous menu ↵
                                                    
                                                    \033[1m\033[3mPlease, enter your choice below:\033[0m
                                                    > """))
                                                    sys.stdout.flush()
                                                    dishIngredients = ""

                                                    changedIngredients = input().strip()
                                                    ## Performs different actions for ingredient manipulation based on user input
                                                    match changedIngredients:
                                                        case "1":
                                                            GenFuncs.firstLoop = True
                                                            while not dishIngredients:
                                                                dishIngredients = editRecipe.addIngredients(dishName)
                                                                if dishIngredients == "\\EXIT":
                                                                    GenFuncs.changedIngredients = ""
                                                                    GenFuncs.currentMenu = "editRecipe"
                                                                    GenFuncs.editFromView = True
                                                                    GenFuncs.backOneStep = True
                                                                    GenFuncs.backOutFromModify = True
                                                                    break
                                                                if not dishIngredients:
                                                                    continue

                                                        case "2":
                                                            GenFuncs.firstLoop = True
                                                            while not dishIngredients:
                                                                dishIngredients = editRecipe.deleteIngredients(dishName)
                                                                if dishIngredients == "\\EXIT":
                                                                    GenFuncs.changedIngredients = ""
                                                                    GenFuncs.currentMenu = "editRecipe"
                                                                    GenFuncs.editFromView = True
                                                                    GenFuncs.backOneStep = True
                                                                    GenFuncs.backOutFromModify = True
                                                                    break
                                                                if not dishIngredients:
                                                                    continue

                                                        case "3":
                                                            GenFuncs.firstLoop = True
                                                            while not dishIngredients:
                                                                dishIngredients = editRecipe.replaceIngredients(dishName)
                                                                if dishIngredients == "\\EXIT":
                                                                    GenFuncs.changedIngredients = ""
                                                                    GenFuncs.currentMenu = "editRecipe"
                                                                    GenFuncs.editFromView = True
                                                                    GenFuncs.backOneStep = True
                                                                    GenFuncs.backOutFromModify = True
                                                                    break
                                                                if not dishIngredients:
                                                                    continue

                                                        case "4":
                                                            GenFuncs.currentMenu = "editRecipe"
                                                            GenFuncs.clear_text()
                                                            GenFuncs.editFromView = True
                                                            GenFuncs.backOneStep = True
                                                            continue

                                                        case _:
                                                            GenFuncs.failedInput(4)
                                                            changedIngredients = ""
                                                            continue
                                                    continue

                                            case "3":
                                                changedInstructions = ""
                                                while not changedInstructions:
                                                    if GenFuncs.firstLoop:
                                                        GenFuncs.clear_text()
                                                        sys.stdout.write(textwrap.dedent(f"""
                                                        The instructions for {dishName} will open shortly...

                                                        \033[1m\033[3mPlease update them once they do!\033[0m
                                                        """))
                                                        sys.stdout.flush()
                                                        time.sleep(2)

                                                    changedInstructions = editRecipe.updateInstructions(dishName)
                                                    if changedInstructions == "\\EXIT":
                                                        GenFuncs.clear_text()
                                                        GenFuncs.changedIngredients = ""
                                                        GenFuncs.currentMenu = "editRecipe"
                                                        GenFuncs.editFromView = True
                                                        GenFuncs.backOneStep = True
                                                        break
                                                    if not changedInstructions:
                                                        continue

                                                continue

                                            case "4":
                                                GenFuncs.editFromView = False
                                                GenFuncs.firstLoop = True
                                                GenFuncs.editChoice = ""
                                                GenFuncs.currentMenu = "editRecipe"
                                                continue

                                            case "5":
                                                GenFuncs.viewFromSearch = False
                                                GenFuncs.selectedIngredients = []
                                                GenFuncs.editFromView = False
                                                GenFuncs.firstLoop = True
                                                GenFuncs.clear_text()
                                                GenFuncs.currentMenu = "contribute"
                                                break

                                            case _:
                                                GenFuncs.failedInput(5)
                                                GenFuncs.firstLoop = False
                                                editChoice = ""
                                                continue

                                case "3":
                                    dishName = ""
                                    GenFuncs.clear_text()
                                    GenFuncs.currentMenu = "deleteRecipe"
                                    ## If no recipes, don't allow editing
                                    if not myCookbook.recipes:
                                        GenFuncs.clear_text()
                                        sys.stdout.write(textwrap.dedent(f"""
                                        It seems that there are no recipes in the book.
                                        Meaning there are none for you to delete...

                                        Can't tear out the pages of an empty book after all!
                                        Sorry.
                                        
                                        \033[1m\033[3mPress enter to go back to the main menu ↵.\033[0m
                                        > """))
                                        sys.stdout.flush()
                                        ## Only continues if they press enter, doesn't let them type anything
                                        while True:
                                            key = msvcrt.getwch()
                                            if key == "\r":
                                                sys.stdout.write("\r\033[2K")
                                                sys.stdout.flush()
                                                break
                                        GenFuncs.clear_text()
                                        GenFuncs.currentMenu = "main"
                                        continue

                                    ## Determine which recipe they want to delete
                                    allRecipesList = listRecipes.listRecipes(9)
                                    sys.stdout.write(textwrap.dedent(f"""
                                    \033[1m\033[3mWhich recipe would you like to delete?\033[0m            
                                    {allRecipesList}

                                    \033[1m\033[3mPlease, enter your answer below: (Type \"\\EXIT\" to quit ↵)\033[0m 
                                    > """))
                                    sys.stdout.flush()

                                    while not dishName:
                                        dishName = input().strip()
                                        dishName = listRecipes.sanitizeDishName(dishName, "fromDelete")
                                        if dishName == "dishNotFound":
                                            dishName = ""
                                    ## Handles if they said to exit
                                    if dishName == "\\EXIT":
                                        GenFuncs.clear_text()
                                        GenFuncs.currentMenu = "contribute"
                                        continue

                                    ## Deletes the selected recipe
                                    deleteConfirmed = deleteRecipe.deleteRecipe(dishName)
                                    if deleteConfirmed:
                                        GenFuncs.clear_text()
                                        sys.stdout.write(textwrap.dedent(f"""
                                        Well.
                                        It's done.
                                        
                                        We're losing recipes.
                                        {dishName} is gone.

                                        I'm sorry that my culinary abilities weren't up to snuff for you.
                                        Go ahead and press enter to go back to the main menu. ↵
                                        
                                        ...Then maybe press 4 and close the book altogether.
                                        You know, since its contents \033[3mclearly\033[23m aren't of high enough quality for you.
                                        > """))
                                        sys.stdout.flush()
                                        ## Only continues if they press enter, doesn't let them type anything
                                        while True:
                                            key = msvcrt.getwch()
                                            if key == "\r":
                                                sys.stdout.write("\r\033[2K")
                                                sys.stdout.flush()
                                                break
                                        GenFuncs.clear_text()
                                        GenFuncs.currentMenu = "main"
                                        continue
                                    else:
                                        GenFuncs.clear_text()
                                        GenFuncs.currentMenu = "contribute"
                                        continue

                                case "4":
                                    GenFuncs.clear_text()
                                    GenFuncs.currentMenu = "main"

                                case _:
                                    GenFuncs.failedInput(4)

                    case "4":
                        GenFuncs.clear_text(flash=False)
                        GenFuncs.currentMenu = "exit"
                        sys.stdout.write("\nThank you for using my cookbook! Feel free to visit again at any point!\n")
                        sys.stdout.flush()
                        time.sleep(1)

                    case _:
                        GenFuncs.failedInput(4)

            case _:
                GenFuncs.systemBroken = True
                GenFuncs.clear_text()
                sys.stdout.write("\nOh no, you broke the program!\n")
                sys.stdout.flush()
                time.sleep(2)
                sys.stdout.write("Only one thing to do...\n")
                time.sleep(2)
                GenFuncs.currentMenu = "exit"

    ## Hangs for fives seconds, then quits the application
    sys.stdout.write("\033[2K\033[38;5;203m\n")
    for i in reversed(range(1, 6)):
        if GenFuncs.systemBroken:
            sys.stdout.write(f"\rThis device will self-destruct in {i}...")
        else:
            sys.stdout.write(f"\rExiting in {i}...")
        sys.stdout.flush()
        time.sleep(1)
    sys.exit()