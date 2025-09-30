import sys, textwrap
import recipe_manager as RM
from ..General import general_functions as GenFuncs

## Returns a stylised list of all recipes that can be used in a stdout output
## Indention level determines how many spaces are needed to work with textwrap.dedent
## Can handle being passed lists or dictionaries to use instead of every recipe in the cookbook
def listRecipes(indentationLevel, customList=None):
    spaces = " " * (indentationLevel * 4)
    recipesToList = RM.myCookbook.recipes
    ## If they've specifed a custom list to post instead of the recipes, show that. Handles if they pass a customList of everything
    if customList and customList != recipesToList:
        recipesToList = customList
        if type(recipesToList) == dict:
            uniqueRecipesString = ""
            if len(GenFuncs.searchResultsList) > 1:
                uniqueRecipesString = "\n" + spaces + "Unique recipes: (" + (", ".join(sorted(GenFuncs.searchResultsList))).rsplit(", ", 1)[0] + " and " + sorted(GenFuncs.searchResultsList)[-1] + ")"
            ## If it's a dictionary, need to do multiple layers
            ingredientsString = ""
            for ingredient in sorted(recipesToList):
                ingredientsHeading = f"\n{spaces}\033[1m\033[3m◈ " + ingredient + "\033[0m\n"
                ingredientsSubstring = f"\n".join(f"{spaces}    • {recipeTitle}" for recipeTitle in sorted(recipesToList[ingredient])) + "\n"
                ingredientsString += ingredientsHeading + ingredientsSubstring
            ingredientsString += uniqueRecipesString
            return ingredientsString

    if RM.myCookbook.recipes:
        ## Grim formatting but needed to work with textwrap.dedent
        recipesString = f"\n{spaces}".join(f"    • {recipeTitle}" for recipeTitle in sorted(recipesToList))
        return recipesString

## Displays the ingredients. Handles lists as well
def listIngredients(dishName, indentationLevel):
    spaces = " " * (indentationLevel * 4)
    if type(dishName) == list:
        listOfIngredients = sorted(dishName)
    else:
        listOfIngredients = sorted(RM.myCookbook.recipes[dishName]["ingredients"])
    ingredientsString = f"\n{spaces}".join(f"    • {ingredient}" for ingredient in listOfIngredients)
    return ingredientsString

## Checks the dish name is acceptable
def sanitizeDishName(dishName, entryMethod, customList=None):
    verb = "view" if entryMethod == "fromView" else "edit" if entryMethod == "fromEdit" else "delete" if entryMethod == "fromDelete" else "CODE BROKEN"
    dishName = dishName.capitalize()
    listToCheck = RM.myCookbook.recipes
    ## Custom text if here by search
    searchString = ""
    if customList:
        listToCheck = customList
    if GenFuncs.viewFromSearch:
        searchString = " (Resets search results)"
        if dishName in GenFuncs.searchResultsList:
            return dishName
    elif dishName in listToCheck:
        return dishName
    if dishName.upper() == "\\EXIT":
        return "\\EXIT"
    if not dishName:
        GenFuncs.clear_text()
        allRecipesList = listRecipes(2, customList=listToCheck)
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mWhoops! You didn't appear to enter anything.\033[0m

        \033[1m\033[3mPlease make sure you choose an exact match for one of these:\033[0m
        {allRecipesList}

        \033[1m\033[3mPlease, enter the recipe you wish to {verb}: (Type \"\\EXIT\" to quit ↵){searchString}\033[0m
        > """))
        return "dishNotFound"
    else:
        GenFuncs.clear_text()
        allRecipesList = listRecipes(2, customList=listToCheck)
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mUh-oh! I don't seem to recognise that recipe. ({dishName})\033[0m
        
        \033[1m\033[3mPlease make sure you choose an exact match for one of these:\033[0m
        {allRecipesList}

        \033[1m\033[3mPlease, enter the recipe you wish to {verb}: (Type \"\\EXIT\" to quit ↵){searchString}\033[0m
        > """))
        return "dishNotFound"

## Displays the selected recipe's creator, name, ingredients and instructions
def displayRecipe(dishName):
    if GenFuncs.firstLoop:
        GenFuncs.clear_text()

    dishName = dishName.capitalize()
    ## Gets the ingredients, puts them in nice formatting
    dishIngredients = listIngredients(dishName, 1)
    #dishIngredients = f"\n    ".join("    • {ingredient}" for ingredient in RM.myCookbook.recipes[dishName]["ingredients"])
    ## Gets the instructions, puts them in nice formatting. Removes any excess newlines at the end
    with (open(fr"Recipes/{dishName}.txt", "r", encoding="utf-8") as recipesFile):
        dishInstructions = "    " + recipesFile.read().rstrip("\n").replace("\n", "\n        ")

    ## Custom text if here by search
    searchString = ""
    if GenFuncs.viewFromSearch:
        searchString = "(Resets search results) "

    sys.stdout.write(textwrap.dedent(f"""
    \033[1m\033[3m{dishName}\033[0m by \033[1m\033[3m{RM.myCookbook.recipes[dishName]["inventor"]}\033[0m

    \033[1mIngredients:\033[0m
    {dishIngredients}

    \033[1mInstructions:\033[0m
    {dishInstructions}

    \033[1m\033[3mWhat would you like to do next?\033[0m
        1. View another recipe
        2. Edit current recipe
        3. Return to main menu {searchString}↵

    \033[1m\033[3mPlease, enter your choice:\033[0m 
    > """))

    return

