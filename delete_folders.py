import os
import shutil

location = os.getcwd()
folders_to_delete = []
counted_folders = 0

print("Current location: " + str(location))

for folder in os.listdir():
    if os.path.isdir(folder):
        folders_to_delete.append(folder)
        counted_folders +=1

if counted_folders > 0:
    print("Found " + str(counted_folders) +" in current directory " + str(location))
    for folder in folders_to_delete:
        print(folder)

    print("Do you want to delete the folders? Type [y] or [n]")

    while(True):
        decision = input().lstrip().lower()
        if decision == 'y':
            for folder in folders_to_delete:
                shutil.rmtree(folder)
            print("Folders deleted")
            break

        elif decision == 'n':
            print("Folders will not be deleted")
            break

        else:
            continue
else:
    print("Did not found any folder")

