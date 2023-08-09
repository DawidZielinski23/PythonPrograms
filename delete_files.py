import sys
import os

if len(sys.argv) == 2:
    extension = str(sys.argv[1])
    location = os.getcwd()
    files_to_delete = []
    countedFiles = 0

    print("Current location: " + str(location))

    if extension.lower() == "nan":
        for filename in os.listdir():
            if not os.path.splitext(filename)[1] and os.path.isfile(filename) == True:
                files_to_delete.append(filename)
                countedFiles += 1
    else:
        for filename in os.listdir():
            if filename.endswith("." + str(extension)):
                files_to_delete.append(filename)
                countedFiles += 1

    if countedFiles == 0:
        print('Did not find files with .' + str(extension) + ' in this location ' + str(location))
    else:
        print("Found " + str(countedFiles) + " in this location " + str(location))
        for file in files_to_delete:
            print(file)
        print("Do you want to delete the files? Type [y] or [n]")
        while True:
            decision = input().lstrip().lower()

            if decision == 'y':
                for file in files_to_delete:
                    os.unlink(file)
                print("Files deleted")
                break

            elif decision == 'n':
                print("Files will not be deleted")
                break

            else:
                continue
else:
    print("Please provide ONE file extension!")