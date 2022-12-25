import os
import shutil
import zipfile


def Unzipping(zip_filename):
    extract_dir = 'pages'

    zf = zipfile.ZipFile(f"pages/{zip_filename}")
    zf.extractall(extract_dir)
    #path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pages/__MACOSX')
    #shutil.rmtree(path)
    files = os.listdir("pages/")
    for i in files:
        if (i != zip_filename):
            if (zip_filename.split(".")[0] in i):
                os.rename(f"pages/{i}", f"pages/{zip_filename.split('.')[0]}")

def index_file_search(zip_filename):
    dir_name = zip_filename.split(".")
    dirname = f"pages/{dir_name[0]}"
    files = os.listdir(dirname)
    for i in files:
        fl = i.split(".")
        if(fl[0] == "index"):
            return True
        if("page" in fl[0]):
            os.rename(f"pages/{dir_name[0]}/{i}", f"pages/{dir_name[0]}/index.html")
            return True

Unzipping("laba_8.zip")