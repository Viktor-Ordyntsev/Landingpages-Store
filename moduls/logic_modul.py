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
        zf = zipfile.ZipFile(f"./tmp/{zip_filename}") 
        name_file = zip_filename.split('.')[0]
        zf.extractall(f"./tmp/{name_file}")
        os.remove(f'./tmp/{zip_filename}')

        # This piece of code is needed because of the peculiarities of archiving different operating systems
        Files = os.listdir(f'tmp/{name_file}/')
        if len(Files) == 2:
            Files = os.listdir(f'tmp/{name_file}/{name_file}/')
            for file in Files:
                os.rename(f'tmp/{name_file}/{name_file}/{file}', f'tmp/{name_file}/{file}')
            shutil.rmtree(f'./tmp/{name_file}/{name_file}')
            
        logging.info(f"Successfully unzipped file {name_file}")
        return True
    except:
        logging.error(f"Unzipped file {name_file} failed")
        delet_local_directory()
        return False



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
        logging.warning(f"Unsuccessfully found and renamed index file")
        delet_local_directory()
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
    logging.info("Domain checked for Cyrillic")
    return bool(alphabet.intersection(set(Cyrillic_domain.lower())))


def upoload_to_s3(poject_name: str, domain_name: str) -> bool:
    try:
        # getting data from environment variables
        S3_URL = os.getenv('S3_URL')
        S3_BUCKET = os.getenv('S3_BUCKET')
        S3_PREFIX = os.getenv('S3_PREFIX')
        S3_ACCESSKEY = os.getenv('S3_ACCESSKEY')
        S3_SECRETKEY = os.getenv('S3_SECRETKEY')

        # create S3-client
        s3_client = boto3.client('s3', endpoint_url=S3_URL, aws_access_key_id=S3_ACCESSKEY, aws_secret_access_key=S3_SECRETKEY)
        logging.info("Successful client creation or environment variable import")
    except:
        logging.warning("Unsuccessful client creation or environment variable import")

    try:
        #check if there are already files in S3_BUCKET/S3_PREFIX/DOMAIN_NAME/
        existing_files = []
        for key in s3_client.list_objects(Bucket=S3_BUCKET, Prefix=f'{S3_PREFIX}/{domain_name}/')['Contents']: 
            existing_files.append(key['Key'])

        if len(existing_files) > 1:
            backup_prefix = S3_PREFIX + '/backup/'

        for file in existing_files:
            s3_client.delete_object(Bucket=S3_BUCKET, Key= backup_prefix + "/".join(file.split('/')[1:]))
            s3_client.copy_object(Bucket=S3_BUCKET, CopySource={'Bucket': S3_BUCKET, 'Key': file}, Key=backup_prefix + "/".join(file.split('/')[1:]))
            s3_client.delete_object(Bucket=S3_BUCKET, Key=file)
        logging.info("Successful backup update")
    except KeyError:
        logging.info("No items found for this domain")

    # uploads new file
    for root, dirs, files in os.walk(f'tmp/{poject_name}/'):
        for filename in files:
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, f'tmp/{poject_name}/')
            s3_path = os.path.join(f'{S3_PREFIX}/{domain_name}/', relative_path)
            s3_client.upload_file(local_path, S3_BUCKET, s3_path)
    logging.info("Successful loading of the landing in the storage")

    write_list_folders(list_folders(s3_client, S3_BUCKET, S3_PREFIX))
    s3_client.upload_file('domain_list.txt', S3_BUCKET, f'{S3_PREFIX}/domain_list.txt')
    os.remove('domain_list.txt')
    return True


def list_folders(s3_client, bucket_name: str, s3_prefix: str):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f'{s3_prefix}/', Delimiter='/')
    for content in response.get('CommonPrefixes', []):
        yield content.get('Prefix')


def write_list_folders(folder_list: list):
    f = open('domain_list.txt', 'w')
    for folder in folder_list:
        f.write(str(folder).split("/")[1] + '\n')


def delet_local_directory() -> bool:
    """Delete local directory function"""

    shutil.rmtree(f'./tmp/')
    logging.info("Cleaning up the local directory")
    return True

