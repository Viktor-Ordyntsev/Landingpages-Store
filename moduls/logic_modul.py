import os
import shutil
import zipfile
import socket




def Unzipping(zip_filename: str) -> bool:
    """ Function for unzipping zip files. Gets the name of the file as input
     as a result, a directory with the same name is created. The function returns a boolean value."""
    try:
        # Unzip the zip file
        zf = zipfile.ZipFile(f"./{zip_filename}")
        zf.extractall('')


        # Correction of the name of the directory
        Files = os.listdir('')
        for file in Files:
            if (file != zip_filename):
                if (zip_filename.split(".")[0] in file):
                    os.rename(f"./{file}",f"./{zip_filename.split('.')[0]}")
                    return True
    except:
        return False
def Removing_service_directory(zip_filename: str):
    # Removing the service directory???????
    shutil.rmtree(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../__MACOSX/'))
    os.remove(f'/Users/a1/Downloads/Web/landing_py/landingpages-store/{zip_filename}')
    print("removing")


def Finding_and_changing_index_file(zip_filename: str) -> bool:
    """ Search function and change the index file. It receives the name of the zip file as input.
     As a result, the index file is named 'index'. The function returns a boolean value."""
    try:
        # Get the path to the working directory
        directory = f"./{zip_filename.split('.')[0]}"

        # List of all files   
        Files = os.listdir(directory)

        # Renaming the index file
        for file in Files:
            file_sp = file.split(".")
            if (file_sp[0] == "index"):
                return True
            if ("page" in file_sp[0]):
                os.rename(
                    f"./{zip_filename.split('.')[0]}/{file}", f"./{zip_filename.split('.')[0]}/index.html")
                return True
    except:
        return False


def Domain_check(domain: str) -> bool:
    """A function for checking domain-to-server binding.
     The input is a string - the name of the domain.
     Output boolean value"""
    try:
        # Resolve domain, get ipv4
        ip_v4_lst = socket.gethostbyname_ex(domain)

        # Compare with ip obtained from environment variables
        if (os.environ["IP_ADDRESS"] in ip_v4_lst[2]):
            return True
        else:
            return False
    except:
        return False


def Cyrillic_to_Punycode_conversion(Cyrillic_domain: str) -> str:
    """Cyrillic domain to Punycode conversion function"""
    return Cyrillic_domain.encode('idna').decode()


def Checking_domain_for_Cyrillic(Cyrillic_domain: str) -> bool:
    """The function of checking for the content of Cyrillic in the domain"""
    alphabet = {"а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о",
                "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"}

    return bool(alphabet.intersection(set(Cyrillic_domain.lower())))


def upoload_to_gitlab(poject_name: str, domain_name: str):
    """The function of uploading a local directory to remote git repositories """
    import git

    repo_dir = 'repo/'
    repo = git.Repo.clone_from('git@gitlab.e-queo.xyz:viktor_ordyntsev/landing-storage.git', repo_dir)
    git = repo.git

    new_branch = repo.create_head(domain_name, 'HEAD~2')
    repo.head.reference = new_branch

    shutil.move(f'{poject_name}/', 'repo/')
    os.rename(f'repo/{poject_name}', 'repo/dist')

    get_ls_file = [i for i in os.listdir('repo/') if i[0] != '.']

    repo.index.add(get_ls_file)
    repo.index.commit(domain_name)

    git.push('-u','origin','--all')
    return True


def delet_local_directory(poject_name: str) -> bool:
    """Delete local directory function"""
    try:
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'./{poject_name}')
        shutil.rmtree(path)
        shutil.rmtree(os.path.join(os.path.abspath(os.path.dirname(__file__)), './repo'))
        return True
    except:
        return False
