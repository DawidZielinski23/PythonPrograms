import sys
import os

if len(sys.argv) > 1:
    extension = str(sys.argv[1])
    location = os.getcwd()
    print("Current location: " + str(location) +
      "\nFound files with extension ." + str(extension) + " :")
    countedFiles = 0

    for filename in os.listdir():
        if filename.endswith("." + str(extension)):
            print(filename)
            countedFiles += 1

    if countedFiles == 0:
        print('Did not find files with .' + str(extension) + ' in this location ' + str(location))
    else:
        print("Found " + str(countedFiles) + " in this location " +str(location) +
     "\nDo you want to delete the files? Type [y] or [n]")
        while True:
            decision = input().lstrip().lower()

            if decision == 'y':
                for filename in os.listdir():
                    if filename.endswith("." + str(extension)):
                        os.unlink(filename)
                print("Files deleted")
                break

            elif decision == 'n':
                print("Files will not be deleted")
                break

            else:
                continue
else:
    print("Please provide ONE file extension!")