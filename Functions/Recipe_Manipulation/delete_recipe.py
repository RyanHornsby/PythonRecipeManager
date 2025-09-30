import json, os, sys, textwrap
import recipe_manager as RM
import Functions.General.audit_logger as auditLogger
from ..General import general_functions as GenFuncs

## Confirms they want to delete the recipe, then removes it from the recipes dict, savedRecipes.json and deletes the .txt instructions file
def deleteRecipe(dishName):
    confirmDeleteInput = ""
    dishName = dishName.capitalize()
    GenFuncs.clear_text()

    while not confirmDeleteInput:
        sys.stdout.write(textwrap.dedent(f"""
        About to delete {dishName}. 
        
        \033[1m\033[3mAre you certain you want to go through with this?\033[0m
            1. Yes. Burn it down.
            2. No, take me back ↵
            
        \033[1m\033[3mPlease enter your choice:\033[0m
        > """))
        sys.stdout.flush()

        confirmDeleteInput = input().strip()
        match confirmDeleteInput:
            case "1":
                ## Logs to the audit file
                with open(RM.myCookbook.recipes[dishName]["instructions"], "r", encoding="utf-8") as instructionsFile:
                    dishInstructions = instructionsFile.read()
                auditLogger.logChange(action="deleteRecipe", dishName=dishName, dishIngredients=RM.myCookbook.recipes[dishName]["ingredients"], dishInstructions=dishInstructions, author=RM.myCookbook.recipes[dishName]["inventor"])
                ## Removes from the recipes list
                del(RM.myCookbook.recipes[dishName])
                ## Clears out from the json file
                with open(r"Recipes/savedRecipes.json", "r+", encoding="utf-8") as recipesFile:
                    allRecipes = json.load(recipesFile)
                    del(allRecipes[dishName])
                    ## Moves to the start of file, overwrites what's already there
                    recipesFile.seek(0)
                    recipesFile.truncate()
                    json.dump(allRecipes, recipesFile, indent=2)
                ## Deletes the instructions.txt file
                os.remove(f"Recipes/{dishName}.txt")


                return "The deed is done."

            case "2":
                return ""

            case _:
                GenFuncs.failedInput(2)
                confirmDeleteInput = ""
                continue