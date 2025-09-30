import msvcrt, sys, textwrap
from collections import defaultdict
import recipe_manager as RM
from ..General import general_functions as GenFuncs
import Functions.Recipe_Manipulation.list_recipes as listRecipes

## Searches for any recipes containing the specified ingredients
def searchIngredients(dishIngredients):
    searchMethod = ""
    GenFuncs.firstLoop = True
    GenFuncs.viewFromSearch = True
    while not searchMethod:
        dishIngredientsString = (", ".join(sorted(dishIngredients))).rsplit(", ", 1)[0] + " and " + sorted(dishIngredients)[-1] if len(dishIngredients) > 1 else dishIngredients[0]
        ## Custom text if here by search
        if GenFuncs.firstLoop:
            GenFuncs.firstLoop = False
            sys.stdout.write(textwrap.dedent(f"""      
            Now searching for recipes containing {dishIngredientsString}...
              
            \033[1m\033[3mWhich type of search would you like to perform?\033[0m
                1. Recipes containing all ingredients
                2. Recipes containing any ingredients
                3. Return to previous menu (Resets search results) ↵
                
            \033[1m\033[3mPlease, enter your choice:\033[0m 
            > """))
        else:
            sys.stdout.write(textwrap.dedent(f"""        
            \033[1m\033[3mWhich type of search would you like to perform?\033[0m
                1. Recipes containing all ingredients ({dishIngredientsString})
                2. Recipes containing any ingredients
                3. Return to previous menu (Resets search results) ↵

            \033[1m\033[3mPlease, enter your choice:\033[0m 
            > """))
        sys.stdout.flush()

        searchMethod = input().strip()
        match searchMethod:
            case "1":
                ## Creates a list of all recipes that contain all ingredients that were search
                recipesWithAllIngredients = []
                for recipe in RM.myCookbook.recipes:
                    if set(dishIngredients).issubset(set(RM.myCookbook.recipes[recipe]["ingredients"])):
                        recipesWithAllIngredients.append(recipe)
                ## Different text if only searched for one ingredient
                multiplesString = " all of"
                if len(dishIngredients) == 1:
                    multiplesString = ""
                ## If it finds no recipes, loop back
                if not recipesWithAllIngredients:
                    GenFuncs.clear_text()
                    sys.stdout.write(textwrap.dedent(f"""
                    \033[38;5;203mUh-oh... No recipes containing{multiplesString}: {dishIngredientsString}\033[0m

                    \033[1m\033[3mPress enter to go back and try a different search ↵.\033[0m 
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
                    searchMethod = ""
                    continue

                GenFuncs.firstLoop = True
                GenFuncs.searchResults = recipesWithAllIngredients
                GenFuncs.searchResultsList = recipesWithAllIngredients
                viewWhichRecipe = ""
                while not viewWhichRecipe:
                    if GenFuncs.firstLoop:
                        GenFuncs.clear_text()
                        GenFuncs.firstLoop = False
                        ## Hijack listRecipes function to post the names of the recipes
                        allRecipesString = listRecipes.listRecipes(6, customList=recipesWithAllIngredients)
                        sys.stdout.write(textwrap.dedent(f"""
                        \033[1m\033[3mRecipes containing: {dishIngredientsString}\033[0m
                        {allRecipesString}
        
                        \033[1m\033[3mWhich would you like to view?
                        Please, enter your choice: (Type \"\\EXIT\" to quit ↵)\033[0m 
                        > """))
                        sys.stdout.flush()

                    ## Yet another list validation check, then swaps them over to "view recipe"
                    viewWhichRecipe = input().strip()
                    viewWhichRecipe = listRecipes.sanitizeDishName(viewWhichRecipe, "fromView", customList=recipesWithAllIngredients)
                    ## Handles if they decide to quit
                    if viewWhichRecipe == "\\EXIT":
                        GenFuncs.clear_text()
                        searchMethod = ""
                        continue
                    if viewWhichRecipe == "dishNotFound":
                        viewWhichRecipe = ""
                        continue

                    ## If they have chosen a dish to view, swap to view
                    GenFuncs.clear_text()
                    GenFuncs.currentMenu = "main"
                    return viewWhichRecipe

            case "2":
                ## Create a dictionary that records each ingredient searched against the recipes it shows up in
                anyIngredientsDictionary = defaultdict(list)
                recipesWithAnyIngredients = []
                for ingredient in dishIngredients:
                    for recipe in RM.myCookbook.recipes:
                        if ingredient in (RM.myCookbook.recipes[recipe]["ingredients"]):
                            anyIngredientsDictionary[ingredient].append(recipe)
                            recipesWithAnyIngredients.append(recipe)
                anyIngredientsDictionary = dict(anyIngredientsDictionary)
                recipesWithAnyIngredients = list(set(recipesWithAnyIngredients))

                ## Different text if only searched for one ingredient
                multiplesString = " any of"
                if len(dishIngredients) == 1:
                    multiplesString = ""
                ## If it finds no recipes, loop back
                if not anyIngredientsDictionary:
                    GenFuncs.clear_text()
                    sys.stdout.write(textwrap.dedent(f"""
                    \033[38;5;203mUh-oh... No recipes containing{multiplesString}: {dishIngredientsString}\033[0m

                    \033[1m\033[3mPress enter to go back and try a different search ↵.\033[0m 
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
                    searchMethod = ""
                    continue

                GenFuncs.firstLoop = True
                GenFuncs.searchResults = anyIngredientsDictionary
                GenFuncs.searchResultsList = recipesWithAnyIngredients
                viewWhichRecipe = ""
                while not viewWhichRecipe:
                    if GenFuncs.firstLoop:
                        GenFuncs.clear_text()
                        GenFuncs.firstLoop = False
                        ## Hijack listRecipes function to post the names of the recipes
                        allRecipesString = listRecipes.listRecipes(6, customList=anyIngredientsDictionary)
                        sys.stdout.write(textwrap.dedent(f"""
                        \033[1m\033[3mRecipes containing{multiplesString}: {dishIngredientsString.replace(" and ", " or ")}\033[0m
                        {allRecipesString}
                        
                        \033[1m\033[3mPlease, enter enter the recipe you wish to view: (Type \"\\EXIT\" to quit ↵)\033[0m 
                        > """))
                        sys.stdout.flush()

                    ## Yet another list validation check, then swaps them over to "view recipe"
                    viewWhichRecipe = input().strip()
                    ## After showing them recipes broken down per ingredient the first time, just
                    viewWhichRecipe = listRecipes.sanitizeDishName(viewWhichRecipe, "fromView", customList=anyIngredientsDictionary)
                    ## Handles if they decide to quit
                    if viewWhichRecipe == "\\EXIT":
                        GenFuncs.clear_text()
                        searchMethod = ""
                        continue
                    if viewWhichRecipe == "dishNotFound":
                        viewWhichRecipe = ""
                        continue

                    ## If they have chosen a dish to view, swap to view
                    GenFuncs.clear_text()
                    GenFuncs.currentMenu = "main"
                    return viewWhichRecipe

            case "3":
                GenFuncs.clear_text()
                GenFuncs.firstLoop = True
                GenFuncs.viewFromSearch = False
                GenFuncs.searchResults = ""
                GenFuncs.searchResultsList = []
                return ""

            case _:
                searchMethod = ""
                GenFuncs.failedInput(3)

## Makes sure the author's name they enter is valid
def sanitizeAuthor(author, allAuthors):
    author = author.title()

    if author.upper() == "\\EXIT":
        return "\\EXIT"
    if not author:
        GenFuncs.clear_text()
        sys.stdout.write(textwrap.dedent("""
        \033[38;5;203mI'm sorry, but every chef deserves their recognition.\033[0m
        You can't enter a blank name.
        """))
        sys.stdout.flush()
        return ""
    ## Checks they entered a real author
    if author not in allAuthors:
        GenFuncs.clear_text()
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mI was unable to find an author by the name of \"{author}\" in this book. Please only choose from the list below.\033[0m
        """))
        sys.stdout.flush()
        return ""
    return author

## Displays all the recipes by a specific author
def displayAuthorRecipes(author):
    author = author.title()
    GenFuncs.viewFromSearch = True

    allRecipesByAuthor = []
    ## Gets a list of all recipes by the author
    for recipe in RM.myCookbook.recipes:
        if author == RM.myCookbook.recipes[recipe]["inventor"]:
            allRecipesByAuthor.append(recipe)
    GenFuncs.searchResults = allRecipesByAuthor
    GenFuncs.searchResultsList = allRecipesByAuthor

    recipesString = listRecipes.listRecipes(1, customList=allRecipesByAuthor)
    GenFuncs.clear_text()
    sys.stdout.write(textwrap.dedent(f"""
    \033[1m\033[3mHere's a list of every recipe by {author}:\033[0m
    {recipesString}
    
    \033[1m\033[3mPlease enter the recipe you wish to view: (Type \"\\EXIT\" to quit ↵) (Resets search results)\033[0m
    > """))
    sys.stdout.flush()

    dishName = ""
    while not dishName:
        dishName = input().strip()
        ## Make sure they chose a valid one
        dishName = listRecipes.sanitizeDishName(dishName, "fromView", customList=allRecipesByAuthor)

        ## Handles if they decide to quit
        if dishName == "\\EXIT":
            GenFuncs.clear_text()
            return dishName
        if dishName == "dishNotFound":
            dishName = ""
            continue

    ## If they have chosen a dish to view, swap to view
    GenFuncs.viewFromSearch = True
    GenFuncs.clear_text()
    GenFuncs.currentMenu = "main"
    return dishName

## Displays all recipes containing a specific search query
def displayRecipesFromSubstring(searchQuery):
    searchQuery = searchQuery.lower()

    if searchQuery.upper() == "\\EXIT":
        return "\\EXIT"

    allRecipesWithSubstring = []
    for recipe in RM.myCookbook.recipes:
        if searchQuery in recipe.lower():
            allRecipesWithSubstring.append(recipe)
    GenFuncs.searchResults = allRecipesWithSubstring
    GenFuncs.searchResultsList = allRecipesWithSubstring

    if not allRecipesWithSubstring:
        GenFuncs.clear_text()
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mI was unable to find any recipes containing the phrase \"{searchQuery}\". Please try a different search.\033[0m
        """))
        sys.stdout.flush()
        return ""

    recipesString = listRecipes.listRecipes(1, customList=allRecipesWithSubstring)
    GenFuncs.clear_text()
    sys.stdout.write(textwrap.dedent(f"""
    \033[1m\033[3mHere's a list of every recipe containing the phrase \"{searchQuery}\":\033[0m
    {recipesString}

    \033[1m\033[3mPlease enter the recipe you wish to view: (Type \"\\EXIT\" to quit ↵) (Resets search results)\033[0m
    > """))
    sys.stdout.flush()

    dishName = ""
    GenFuncs.viewFromSearch = True
    while not dishName:
        dishName = input().strip()
        ## Make sure they chose a valid one
        dishName = listRecipes.sanitizeDishName(dishName, "fromView", customList=allRecipesWithSubstring)

        ## Handles if they decide to quit
        if dishName == "\\EXIT":
            GenFuncs.clear_text()
            return dishName
        if dishName == "dishNotFound":
            dishName = ""
            continue

    ## If they have chosen a dish to view, swap to view
    GenFuncs.clear_text()
    GenFuncs.currentMenu = "main"
    return dishName