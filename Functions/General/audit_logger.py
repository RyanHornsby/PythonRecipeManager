from datetime import datetime
import os
import Functions.General.general_functions as GenFuncs

## Records when important actions were done
def logChange(**kwargs):
    ## If no audit file exists, create it
    if not os.path.exists("audit.log"):
        with open("audit.log", "w", encoding="utf-8") as auditFile:
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Audit file created\n"
                            f"---------------------------------------------------------------------------\n")

    ## Adds audit actions based on what the user did
    with open("audit.log", "a", encoding="utf-8") as auditFile:
        if kwargs["action"] == "createJSON":
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - savedRecipes.json created\n"
                            f"---------------------------------------------------------------------------\n")
        elif kwargs["action"] == "addRecipe":
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {GenFuncs.userName} added recipe: {kwargs["dishName"]}\n"
                            f"Ingredients:\n"
                            f"{kwargs["dishIngredients"]}\n\n"
                            f"Instructions:\n"
                            f"{kwargs["dishInstructions"]}\n"
                            f"---------------------------------------------------------------------------\n")
        elif kwargs["action"] == "deleteRecipe":
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {GenFuncs.userName} deleted {kwargs["author"]}'s recipe: {kwargs["dishName"]}\n"
                            f"Deleted ingredients:\n"
                            f"{kwargs["dishIngredients"]}\n\n"
                            f"Deleted instructions:\n"
                            f"{kwargs["dishInstructions"]}\n"
                            f"---------------------------------------------------------------------------\n")
        elif kwargs["action"] == "editDishName":
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {GenFuncs.userName} updated the name of {kwargs["oldDishName"]} to {kwargs["newDishName"]}\n"
                            f"---------------------------------------------------------------------------\n")
        elif kwargs["action"] == "editDishIngredientsAdd":
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {GenFuncs.userName} added the following ingredients to {kwargs["dishName"]}:\n"
                            f"{kwargs["dishIngredients"]}\n"
                            f"---------------------------------------------------------------------------\n")
        elif kwargs["action"] == "editDishIngredientsRemove":
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {GenFuncs.userName} deleted the following ingredients from {kwargs["dishName"]}:\n"
                            f"{kwargs["dishIngredients"]}\n"
                            f"---------------------------------------------------------------------------\n")
        elif kwargs["action"] == "editDishIngredientsReplace":
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {GenFuncs.userName} replaced the ingredients for {kwargs["dishName"]}\n"
                            f"Previous ingredients:\n"
                            f"{kwargs["oldDishIngredients"]}\n\n"
                            f"New ingredients:\n"
                            f"{kwargs["newDishIngredients"]}\n"
                            f"---------------------------------------------------------------------------\n")
        elif kwargs["action"] == "editDishInstructions":
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {GenFuncs.userName} changed the instructions for {kwargs["dishName"]}\n"
                            f"Previous instructions:\n"
                            f"{kwargs["oldDishInstructions"]}\n\n"
                            f"New instructions:\n"
                            f"{kwargs["newDishInstructions"]}\n"
                            f"---------------------------------------------------------------------------\n")
        else:
            auditFile.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {GenFuncs.userName} has somehow performed an action that was not logged properly.\n"
                            f"---------------------------------------------------------------------------\n")