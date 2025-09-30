import click, json, msvcrt, os, sys, textwrap, time
from ..General import general_functions as GenFuncs
import Functions.General.audit_logger as auditLogger
import Functions.Recipe_Manipulation.list_recipes as listRecipes
import recipe_manager as RM

## A lot of these functions are similar to addRecipe, but different enough I think it's better to have as their own functions
def confirmChange(dishName, entryMethod, newDishName="", newIngredients="", existingIngredients=""):
    changeType = "CODE BROKEN"
    newDishString = ". "
    ingredients = newIngredients
    if existingIngredients:
        pass
    else:
        existingIngredients = ""
    GenFuncs.clear_text()

    ## Sets what the text will be based on where the function was called from
    if entryMethod == "fromName":
        changeType = "change the recipe name for"
        newDishString = f" to {newDishName}.\n\n        "
    elif entryMethod in ["fromIngredientsAdd", "fromIngredientsDelete"]:
        newDishString = ":"
        ingredients = "\n        " + listRecipes.listIngredients(ingredients, 2) + "\n\n        "
        if entryMethod == "fromIngredientsAdd":
            changeType = "add these ingredients to"
            ## If some ingredients already exist, display those as well
            if existingIngredients:
                existingIngredientsString = listRecipes.listIngredients(existingIngredients, 2)
                existingIngredients = f"\033[38;5;203mIt appears some of the ingredients you entered were already in the recipe. I'm choosing to ignore these ones:\n        {existingIngredientsString}\033[0m" + "\n\n        "
        elif entryMethod == "fromIngredientsDelete":
            changeType = "remove these ingredients from"
            ## If some ingredients they said weren't in the current ingredients, display those as well
            if existingIngredients:
                existingIngredientsString = listRecipes.listIngredients(existingIngredients, 2)
                existingIngredients = f"\033[38;5;203mIt appears some of the ingredients you entered aren't currently ingredients. I'm choosing to ignore these ones:\n        {existingIngredientsString}\033[0m" + "\n\n        "
    elif entryMethod == "fromIngredientsOverwrite":
        changeType = "overwrite the ingredients for"
        newDishString = "with these ingredients:"
        ingredients = "\n        " + listRecipes.listIngredients(ingredients, 2) + "\n\n        "
    elif entryMethod == "fromInstructions":
        changeType = "update the instructions for"
        newDishString = ".\n\n        "

    ## Prints out the actual text, makes them confirm their decision
    confirmChoice = ""
    while not confirmChoice:
        sys.stdout.write(textwrap.dedent(f"""
        {existingIngredients}\033[1m\033[3mYou are about to permanently {changeType} {dishName}{newDishString}\033[0m{ingredients}\033[1m\033[3mAre you sure you want to go ahead?\033[0m
            1. Yes, make the change
            2. No, take me back ↵

        \033[1m\033[3mPlease, enter your choice below:\033[0m
        > """))
        sys.stdout.flush()

        confirmChoice = input().strip()
        match confirmChoice:
            case "1":
                return "Confirm"

            case "2":
                return "\\EXIT"

            case _:
                confirmChoice = ""
                GenFuncs.failedInput(2)

## Makes sure the dishName they want to swap to is fine
def sanitizeDishname(currentDishName, dishName):
    dishName = dishName.capitalize()

    if dishName.upper() == "\\EXIT":
        return "\\EXIT"

    ## Checks if name is fully blank
    if not dishName:
        GenFuncs.clear_text()
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mI'm sorry, but that dish's name appears to be blank!\033[0m

        \033[1m\033[3mPlease enter a new name for {currentDishName}: (Type \"\\EXIT\" to quit)\033[0m
        > """))
        sys.stdout.flush()
        return ""

    ## If they haven't changed the name at all
    if currentDishName == dishName:
        GenFuncs.clear_text()
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mUhh? You know that's the exact same name, right? {dishName}?\033[0m
        
        \033[1m\033[3mWhat would you actually like to change it to? (Type \"\\EXIT\" to quit)\033[0m
        > """))
        sys.stdout.flush()
        return ""

    ## Makes sure the recipe doesn't already exist
    if any(dishName == inBook.capitalize() for inBook in RM.myCookbook.recipes):
        GenFuncs.clear_text()
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mWhoa, slow down! {dishName} already exists as a another recipe!
        So you can't rename {currentDishName} to it, sorry.\033[0m

        \033[1m\033[3mPlease enter a new name for {currentDishName}: (Type \"\\EXIT\" to quit)\033[0m
        > """))
        sys.stdout.flush()
        return ""

    ## Checks if the dish name is only safe characters (ones safe for creating Windows files)
    if not all(safe in GenFuncs.safeCharacters for safe in dishName):
        GenFuncs.clear_text()
        sys.stdout.write(textwrap.dedent(f"""
        \033[38;5;203mI'm sorry, but that dish's name ({dishName}) uses a non-allowed character.\033[0m
        Safe characters are alphanumeric, spaces or any of these: -, +, *, :, _, ', @, £, $, %, &, (, ).

        \033[1m\033[3mPlease enter a new name for {currentDishName}: (Type \"\\EXIT\" to quit)\033[0m
        > """))
        sys.stdout.flush()
        return ""

    ## Now we confirm that the user definitely wants to make the changes
    confirmChoice = confirmChange(currentDishName, "fromName", dishName)
    if confirmChoice == "\\EXIT":
        return "\\EXIT"
    ## Updates the recipes dictionary, the savedRecipes.json and the instructions.txt file
    if confirmChoice:
        ## Removes from recipes list
        RM.myCookbook.recipes[dishName] = RM.myCookbook.recipes.pop(currentDishName)
        ## Updates JSON
        with open(r"Recipes/savedRecipes.json", "r+", encoding="utf-8") as recipesFile:
            allRecipes = json.load(recipesFile)
            allRecipes[dishName] = allRecipes.pop(currentDishName)
            ## Moves to the start of file, overwrites what's already there
            recipesFile.seek(0)
            recipesFile.truncate()
            json.dump(allRecipes, recipesFile, indent=2)
        ## Renames the text file
        os.rename(f"Recipes/{currentDishName}.txt", f"Recipes/{dishName}.txt")
        ## Logs to the audit file
        auditLogger.logChange(action="editDishName", oldDishName=currentDishName, newDishName=dishName)

        ## Only continues if they press enter, doesn't let them type anything
        GenFuncs.clear_text()
        sys.stdout.write(textwrap.dedent(f"""
        Successfully renamed {currentDishName} to {dishName}.

        \033[1m\033[3mPress enter to return to the previous menu ↵\033[0m
        > """))
        sys.stdout.flush()
        while True:
            key = msvcrt.getwch()
            if key == "\r":
                sys.stdout.write("\r\033[2K")
                sys.stdout.flush()
                break
        GenFuncs.editFromView = True
        GenFuncs.clear_text()
        GenFuncs.backOneStep = True
        return dishName

    else:
        return ""

## Sanitizes dish ingredients
def sanitizeDishIngredients(dishName, entryMethod):
    verb = "add" if entryMethod == "fromAdd" else "remove" if entryMethod == "fromDelete" else "replace the existing ones with" if entryMethod == "fromOverwrite" else "CODE BROKE"
    adjective = "new " if entryMethod == "fromAdd" else "current " if entryMethod == "fromDelete" else "" if entryMethod == "fromOverwrite" else "CODE BROKE"

    ## Gets and displays the current ingredients
    currentIngredients = listRecipes.listIngredients(dishName, 1)
    sys.stdout.write(textwrap.dedent(f"""
    \033[1m\033[3m{dishName}'s ingredients:\033[0m
    {currentIngredients}

    \033[1m\033[3mPlease, enter all {adjective}ingredients you wish to {verb}, comma separated: (Type \"\\EXIT\" to quit ↵)\033[0m
    > """))
    sys.stdout.flush()

    ## Checks the ingredients they've inputted
    ingredients = input().strip()
    if ingredients.upper() == "\\EXIT":
        return "\\EXIT"
    ingredients = ingredients.split(",")
    ## Originally did set not dict, but need to do this to preserve order
    ingredients = list(dict.fromkeys(valid.strip().capitalize() for valid in ingredients if valid.strip()))
    if not ingredients:
        GenFuncs.clear_text()
        sys.stdout.write(f"\n\033[38;5;203mSorry, you don't appear to have entered any ingredients to {verb}...\033[0m\n")
        sys.stdout.flush()
        return ""

    return ingredients

## Adds new ingredients to the dish
def addIngredients(dishName):
    if GenFuncs.firstLoop:
        GenFuncs.clear_text()
        GenFuncs.firstLoop = False
    currentIngredients = RM.myCookbook.recipes[dishName]["ingredients"]

    ingredientsToAdd = ""
    while not ingredientsToAdd:
        ingredientsToAdd = sanitizeDishIngredients(dishName, "fromAdd")
        if ingredientsToAdd == "\\EXIT":
            return "\\EXIT"
        if not ingredientsToAdd:
            continue

        confirmChoice = ""
        ## If the input is fine, now compare it to the list of already existing ingredients
        while not confirmChoice:
            alreadyInIngredients = []
            newIngredients = []
            for ingredient in ingredientsToAdd:
                if ingredient in currentIngredients:
                    alreadyInIngredients.append(ingredient)
                else:
                    newIngredients.append(ingredient)

            ## If they haven't added any new ingredients, loop back
            if not newIngredients:
                alreadyInIngredientsString = listRecipes.listIngredients(alreadyInIngredients, 4)
                GenFuncs.clear_text()
                sys.stdout.write(textwrap.dedent(f"""
                \033[38;5;203mIt appears none of the ingredients you entered were new. Try again. 
                {alreadyInIngredientsString}\033[0m
                """))
                return ""

            ## Now we confirm that the user definitely wants to make the changes
            confirmChoice = confirmChange(dishName, "fromIngredientsAdd", newIngredients=newIngredients, existingIngredients=alreadyInIngredients)
            if confirmChoice == "\\EXIT":
                return "\\EXIT"
            ## Updates the recipes dictionary, and savedRecipes.json
            if confirmChoice:
                ## Updates the recipes dictionary
                RM.myCookbook.recipes[dishName]["ingredients"].extend(newIngredients)
                ## Updates the JSON file
                with open(r"Recipes/savedRecipes.json", "r+", encoding="utf-8") as recipesFile:
                    allRecipes = json.load(recipesFile)
                    allRecipes[dishName]["ingredients"].extend(newIngredients)
                    ## Moves to the start of file, overwrites what's already there
                    recipesFile.seek(0)
                    recipesFile.truncate()
                    json.dump(allRecipes, recipesFile, indent=2)
                ## Logs to the audit file
                auditLogger.logChange(action="editDishIngredientsAdd", dishName=dishName, dishIngredients=newIngredients)

                ## Only continues if they press enter, doesn't let them type anything
                newIngredientsString = listRecipes.listIngredients(newIngredients, 4)
                GenFuncs.clear_text()
                sys.stdout.write(textwrap.dedent(f"""
                \033[1m\033[3mSuccessfully added the following ingredients to {dishName}:\033[0m
                {newIngredientsString}

                \033[1m\033[3mPress enter to return to the previous menu ↵\033[0m
                > """))
                sys.stdout.flush()
                while True:
                    key = msvcrt.getwch()
                    if key == "\r":
                        sys.stdout.write("\r\033[2K")
                        sys.stdout.flush()
                        break
                GenFuncs.editFromView = True
                GenFuncs.clear_text()
                GenFuncs.backOneStep = True
                return newIngredients

            else:
                return ""

## Adds new ingredients to the dish
def deleteIngredients(dishName):
    if GenFuncs.firstLoop:
        GenFuncs.clear_text()
        GenFuncs.firstLoop = False
    currentIngredients = RM.myCookbook.recipes[dishName]["ingredients"]

    ingredientsToDelete = ""
    while not ingredientsToDelete:
        ingredientsToDelete = sanitizeDishIngredients(dishName, "fromDelete")
        if ingredientsToDelete == "\\EXIT":
            return "\\EXIT"
        if not ingredientsToDelete:
            continue

        confirmChoice = ""
        ## If the input is fine, now compare it to the list of already existing ingredients
        while not confirmChoice:
            inIngredients = []
            notInIngredients = []
            for ingredient in ingredientsToDelete:
                if ingredient in currentIngredients:
                    inIngredients.append(ingredient)
                else:
                    notInIngredients.append(ingredient)

            ## If they only added ingredients that aren't in the current set of ingredients, loop back
            if not inIngredients:
                inIngredientsString = listRecipes.listIngredients(notInIngredients, 4)
                GenFuncs.clear_text()
                sys.stdout.write(textwrap.dedent(f"""
                \033[38;5;203mIt appears none of the ingredients you entered are actually in the current ingredients list. Try again. 
                {inIngredientsString}\033[0m
                """))
                return ""

            ## If they are trying to remove all ingredients, prevent it
            if len(inIngredients) == len(RM.myCookbook.recipes[dishName]["ingredients"]):
                extra = ""
                if notInIngredients:
                    extra = " and some that weren't even in the list"
                GenFuncs.clear_text()
                sys.stdout.write(textwrap.dedent(f"""
                \033[38;5;203mThat's... That's every remaining ingredient{extra}.\033[0m
                
                I'm obviously not going to let you reduce it down to a recipe with no ingredients. 
                Let's try again, but be more serious about it this time, yeah?
                """))
                return ""

            ## Now we confirm that the user definitely wants to make the changes
            confirmChoice = confirmChange(dishName, "fromIngredientsDelete", newIngredients=inIngredients, existingIngredients=notInIngredients)
            if confirmChoice == "\\EXIT":
                return "\\EXIT"
            ## Updates the recipes dictionary, and savedRecipes.json
            if confirmChoice:
                ## Updates the recipes dictionary
                RM.myCookbook.recipes[dishName]["ingredients"] = [ingredient for ingredient in RM.myCookbook.recipes[dishName]["ingredients"] if ingredient not in ingredientsToDelete]
                ## Updates the JSON file
                with open(r"Recipes/savedRecipes.json", "r+", encoding="utf-8") as recipesFile:
                    allRecipes = json.load(recipesFile)
                    allRecipes[dishName]["ingredients"] = [ingredient for ingredient in allRecipes[dishName]["ingredients"] if ingredient not in ingredientsToDelete]
                    ## Moves to the start of file, overwrites what's already there
                    recipesFile.seek(0)
                    recipesFile.truncate()
                    json.dump(allRecipes, recipesFile, indent=2)
                ## Logs to the audit file
                auditLogger.logChange(action="editDishIngredientsRemove", dishName=dishName, dishIngredients=ingredientsToDelete)

                ## Only continues if they press enter, doesn't let them type anything
                removedIngredientsString = listRecipes.listIngredients(inIngredients, 4)
                GenFuncs.clear_text()
                sys.stdout.write(textwrap.dedent(f"""
                \033[1m\033[3mSuccessfully removed the following ingredients from {dishName}:\033[0m
                {removedIngredientsString}

                \033[1m\033[3mPress enter to return to the previous menu ↵\033[0m
                > """))
                sys.stdout.flush()
                while True:
                    key = msvcrt.getwch()
                    if key == "\r":
                        sys.stdout.write("\r\033[2K")
                        sys.stdout.flush()
                        break
                GenFuncs.editFromView = True
                GenFuncs.clear_text()
                GenFuncs.backOneStep = True
                return ingredientsToDelete

            else:
                return ""

## Replaces existing ingredients
def replaceIngredients(dishName):
    if GenFuncs.firstLoop:
        GenFuncs.clear_text()
        GenFuncs.firstLoop = False

    newIngredients = ""
    while not newIngredients:
        newIngredients = sanitizeDishIngredients(dishName, "fromOverwrite")
        if newIngredients == "\\EXIT":
            return "\\EXIT"
        if not newIngredients:
            continue

        confirmChoice = ""
        ## If the input is fine, now compare it to the list of already existing ingredients
        while not confirmChoice:
            ## If the ingredients are the exact same as is always there, point that out. Using set to ignore order
            if set(newIngredients) == set(RM.myCookbook.recipes[dishName]["ingredients"]):
                GenFuncs.clear_text()
                sys.stdout.write(textwrap.dedent(f"""
                \033[38;5;203mThose ingredients are exactly the same as the ones currently in the cookbook.\033[0m 
                
                If you meant to overwrite the current ingredients, please try putting different ingredients.
                Otherwise try using one of the other features of the book!
                """))
                sys.stdout.flush()
                return ""

            ## Now we confirm that the user definitely wants to make the changes
            confirmChoice = confirmChange(dishName, "fromIngredientsOverwrite", newIngredients=newIngredients)
            if confirmChoice == "\\EXIT":
                return "\\EXIT"
            ## Updates the recipes dictionary, and savedRecipes.json
            if confirmChoice:
                ## Logs to the audit file
                auditLogger.logChange(action="editDishIngredientsReplace", dishName=dishName, oldDishIngredients=RM.myCookbook.recipes[dishName]["ingredients"], newDishIngredients=newIngredients)
                ## Updates the recipes dictionary
                RM.myCookbook.recipes[dishName]["ingredients"] = newIngredients
                ## Updates the JSON file
                with open(r"Recipes/savedRecipes.json", "r+", encoding="utf-8") as recipesFile:
                    allRecipes = json.load(recipesFile)
                    allRecipes[dishName]["ingredients"] = newIngredients
                    ## Moves to the start of file, overwrites what's already there
                    recipesFile.seek(0)
                    recipesFile.truncate()
                    json.dump(allRecipes, recipesFile, indent=2)

                ## Only continues if they press enter, doesn't let them type anything
                newIngredientsString = listRecipes.listIngredients(newIngredients, 4)
                GenFuncs.clear_text()
                sys.stdout.write(textwrap.dedent(f"""
                \033[1m\033[3mSuccessfully overwritten the ingredients for {dishName} with these:\033[0m
                {newIngredientsString}

                \033[1m\033[3mPress enter to return to the previous menu ↵\033[0m
                > """))
                sys.stdout.flush()
                while True:
                    key = msvcrt.getwch()
                    if key == "\r":
                        sys.stdout.write("\r\033[2K")
                        sys.stdout.flush()
                        break
                GenFuncs.editFromView = True
                GenFuncs.clear_text()
                GenFuncs.backOneStep = True
                return newIngredients

            else:
                return ""

## Updates the instructions.txt file
def updateInstructions(dishName):
    safeToExit = False

    ## Creates a copy of the current instructions
    with open(f"Recipes/{dishName}.txt", "r", encoding="utf-8") as instructionsFile:
        currentInstructions = instructionsFile.read().rstrip("\n").strip()
    ## Opens the text file for them to edit
    typedInstructions = click.edit(currentInstructions)
    if typedInstructions:
        typedInstructions = typedInstructions.rstrip("\n").strip()
    ## Forces the user to make a change
    while not safeToExit:
        if not typedInstructions or not typedInstructions.strip() or typedInstructions == currentInstructions:
            if GenFuncs.firstLoop or GenFuncs.repeatInstructionsWarning:
                GenFuncs.firstLoop = False
                GenFuncs.repeatInstructionsWarning = False
                GenFuncs.clear_text()
                sys.stdout.write(textwrap.dedent(f"""
                \033[38;5;203mOh dear, either you left the file blank, didn't save your changes or you didn't change it at all.\033[0m
    
                \033[1m\033[3mWhat would you like to do?\033[0m
                    1. Try again!
                    2. Cancel changing the instructions (return to previous menu ↵)
    
                \033[1m\033[3mPlease enter your choice:\033[0m
                > """))
                sys.stdout.flush()
            else:
                sys.stdout.write(textwrap.dedent(f"""
                \033[1m\033[3mWhat would you like to do?\033[0m
                    1. Try again!
                    2. Cancel changing the instructions (return to previous menu ↵)
    
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
                    GenFuncs.repeatInstructionsWarning = True
                    time.sleep(2)
                    return ""

                case "2":
                    return "\\EXIT"

                case _:
                    GenFuncs.failedInput(2)
                    continue
        safeToExit = True

    confirmChoice = ""
    ## If they have put new instructions fine, confirm they want to save the changes
    while not confirmChoice:
        ## Now we confirm that the user definitely wants to make the changes
        confirmChoice = confirmChange(dishName, "fromInstructions")
        if confirmChoice == "\\EXIT":
            return "\\EXIT"
        ## Updates the .txt file
        if confirmChoice:
            ## Updates the .txt file
            with open(f"Recipes/{dishName}.txt", "r+", encoding="utf-8") as instructionsFile:
                instructionsFile.write(typedInstructions)
            ## Logs to the audit file
            auditLogger.logChange(action="editDishInstructions", dishName=dishName, oldDishInstructions=currentInstructions, newDishInstructions=typedInstructions)

            ## Only continues if they press enter, doesn't let them type anything
            GenFuncs.clear_text()
            sys.stdout.write(textwrap.dedent(f"""
            \033[1m\033[3mSuccessfully updated the instructions for {dishName}!\033[0m

            \033[1m\033[3mPress enter to return to the previous menu ↵\033[0m
            > """))
            sys.stdout.flush()
            while True:
                key = msvcrt.getwch()
                if key == "\r":
                    sys.stdout.write("\r\033[2K")
                    sys.stdout.flush()
                    break
            GenFuncs.editFromView = True
            GenFuncs.clear_text()
            GenFuncs.backOneStep = True
            return typedInstructions

        else:
            return ""