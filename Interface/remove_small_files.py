import sys
import os

if __name__ == '__main__':
    folder_path = sys.argv[1]

    files_list = os.listdir(folder_path)
    for file in files_list:
        if os.path.getsize(folder_path+'/'+file) <= 10:
            os.remove(folder_path+'/'+file)
