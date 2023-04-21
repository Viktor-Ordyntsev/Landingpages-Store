import os
import shutil
import zipfile
import socket
import logging 
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
logging.basicConfig(level=logging.INFO, filename="landing_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

def unzipping(zip_filename: str) -> bool:
    """ Function for unzipping zip files. Gets the name of the file as input
     as a result, a directory with the same name is created. The function returns a boolean value."""
    try:
        # Unzip the zip file
        zf = zipfile.ZipFile(f"./tmp/{zip_filename}") 
        name_file = zip_filename.split('.')[0]
        zf.extractall(f"./tmp/{name_file}")
        os.remove(f'./tmp/{zip_filename}')


        # Correction of the name of the directory
        Files = os.listdir(f'{name_file}')
        for file in Files:
            if (file != zip_filename):
                if (name_file in file):
                    os.rename(f"./{file}",f"./{name_file}")
                    logging.info(f"Successfully unzipped file {name_file}")
                    return True
    except:
        logging.error(f"Unzipped file {name_file} failed")
        return False

# def Removing_service_directory(zip_filename: str):
#     # Removing the service directory???????
#     shutil.rmtree(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../__MACOSX/'))
#     os.remove(f'./{zip_filename}')
#     print("removing")


def finding_and_changing_index_file(name_file: str) -> bool:
    """ Search function and change the index file. It receives the name of the zip file as input.
     As a result, the index file is named 'index'. The function returns a boolean value."""
    try:
        # Get the path to the working directory
        directory = f"./tmp/{name_file}"

        # List of all files   
        Files = os.listdir(directory)

        # Renaming the index file
        for file in Files:
            file_sp = file.split(".")
            if (file_sp[0] == "index"):
                logging.info(f"Successfully found index file")
                return True
            if ("page" in file_sp[0]):
                os.rename(f"./tmp/{name_file}/{file}", f"./tmp/{name_file}/index.html")
                logging.info(f"Successfully found and renamed index file")
                return True
    except:
        logging.info(f"Unsuccessfully found and renamed index file")
        return False


def domain_check(domain: str) -> bool:
    """A function for checking domain-to-server binding.
     The input is a string - the name of the domain.
     Output boolean value"""
    try:
        # Resolve domain, get ipv4
        ip_v4_lst = socket.gethostbyname_ex(domain)

        # Compare with ip obtained from environment variables
        if (os.environ.get("SERVER_IP_ADDRESS") in ip_v4_lst[2]):
            logging.info("domain verification successfully passed")
            return True
        else:
            logging.info("domain verification failed")
            return False
    except:
        logging.info("domain verification failed due to something else")
        return False


def cyrillic_to_punycode_conversion(Cyrillic_domain: str) -> str:
    """Cyrillic domain to Punycode conversion function"""
    logging.info("Domain decoded successfully")
    return Cyrillic_domain.encode('idna').decode()


def checking_domain_for_cyrillic(Cyrillic_domain: str) -> bool:
    """The function of checking for the content of Cyrillic in the domain"""
    alphabet = {"а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о",
                "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"}
    return bool(alphabet.intersection(set(Cyrillic_domain.lower())))


# def upoload_to_gitlab(poject_name: str, domain_name: str):
#     """The function of uploading a local directory to remote git repositories """
#     import git

#     repo_dir = 'repo/'
#     if not os. path. exists('./repo'): 
#         repo = git.Repo.clone_from(os.environ.get("GIT_REPO"), repo_dir)
#         logging.info("Successful cloning of the repository")
#     else:
#         repo = git.Repo('./repo')
#     git = repo.git
#     try:
#         new_branch = repo.create_head(domain_name, 'HEAD~2')
#         repo.head.reference = new_branch
#         shutil.move(f'{poject_name}/', 'repo/')
#         os.rename(f'repo/{poject_name}', 'repo/dist')
#         logging.info("Successful branch creation and data movement")
#     except:
#         logging.warning("Branch already exists")
#         logging.info("Search for an existing branch")
#         git.checkout(domain_name)
#         shutil.rmtree('./repo/dist/')
#         shutil.move(f'{poject_name}/', 'repo/')
#         os.rename(f'repo/{poject_name}', 'repo/dist')

#     get_ls_file = [i for i in os.listdir('repo/') if i[0] != '.']
#     repo.index.add(get_ls_file)
#     repo.index.commit(domain_name)
#     logging.info("Successfully adding changes and commit")
#     try:
#         git.push('--set-upstream', 'origin', domain_name, '-f')
#         logging.info("Successful push")
#     except:
#         logging.info("Unsuccessful push")
#         pass
#     return True
def upoload_to_s3(poject_name: str, domain_name: str):
    # получаем данные из переменных окружения
    S3_URL = os.getenv('S3_URL')
    S3_BUCKET = os.getenv('S3_BUCKET')
    S3_PREFIX = os.getenv('S3_PREFIX')
    S3_ACCESSKEY = os.getenv('S3_ACCESSKEY')
    S3_SECRETKEY = os.getenv('S3_SECRETKEY')

    # создаем клиент s3
    s3_client = boto3.client('s3',
                            endpoint_url=S3_URL,
                            aws_access_key_id=S3_ACCESSKEY,
                            aws_secret_access_key=S3_SECRETKEY)


    # проверяем, есть ли уже файлы в S3_BUCKET/S3_PREFIX/DOMAIN_NAME/
    # если есть, то делаем бекап и удаляем текущую директорию
    existing_files = []
    for key in s3_client.list_objects(Bucket=S3_BUCKET, Prefix=f'{S3_PREFIX}/{domain_name}/')['Contents']: 
        existing_files.append(key['Key'])
        
    if domain_name in existing_files:
        backup_prefix = S3_PREFIX + '/backup/' 
        for file in existing_files:
            s3_client.copy_object(Bucket=S3_BUCKET, CopySource={'Bucket': 'BUCKET_NAME', 'Key': file}, Key=backup_prefix + os.path.basename(file))
            s3_client.delete_object(Bucket=S3_BUCKET, Key=file)
   

    # загружаем новые файлы
    for root, dirs, files in os.walk(f'tmp/{poject_name}/'):
        for filename in files:
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, f'tmp/')
            s3_path = os.path.join(f'{S3_PREFIX}/{domain_name}/', relative_path)
            s3_client.upload_file(local_path, S3_BUCKET, s3_path)
    
    return True


def delet_local_directory(poject_name: str) -> bool:
    """Delete local directory function"""
    # path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'rep')
    shutil.rmtree('./repo/')
    return True

