import getopt
import sys
from termcolor import cprint
from pyfiglet import figlet_format
from bs4 import BeautifulSoup
import urllib.request
import os
from rich.progress import track
import requests


def display_help():
    """ """
    help = """INRSRAP - INRS - Scrap download the documentation of a specified chemical component from
    the INRS website. It takes two mandatory arguments :

        - input : could be a single input (e.g : 87) or a file containing one input per line
        - output : path to the output folder, create it of not already exists

    Usage :
        
        - python inrscrap.py -i 87 -o /my/output/folder
        - python insrcrap.py -i /my/ids/file -o /my/output/folder

    """

    print(help)


def scrap(target_id: int, output_folder: str) -> bool:
    """Download pdf for target_id, save it in output folder

    Args:
        - target_id (int) : INRS id of the chemical component to hunt
        - output_folder (str) : path to the folder where pdf files are downloaded
    Returns:
        - file_found (bool) : true if at least one pdf files have been found and downloaded, else if not

    """

    # parameters
    target_url = f"https://www.inrs.fr/publications/bdd/fichetox/fiche.html?refINRS=FICHETOX_{target_id}"
    file_found = False

    # get source code
    page_source = requests.get(target_url).text

    # catch the link to the pdf
    soup = BeautifulSoup(page_source, features="lxml")
    root_url = "https://www.inrs.fr"
    url_list = []
    for a in soup.find_all("a", {"class": "boutonImportant orange"}, href=True):
        u = f"{root_url}/{a['href']}"
        if u not in url_list:
            url_list.append(u)

            # catch name
            n = u.split("/")[-1]

            # control that file is a pdf
            if n.split(".")[-1] == "pdf":

                # download
                response = urllib.request.urlopen(u)
                file = open(f"{output_folder}/{n}", "wb")
                file.write(response.read())
                file.close()
                file_found = True

    # return file found status
    return file_found


def run(target, output_folder):
    """Main function of the script, determine if a target is an int or a file,
    if its a file try to load targets from it and download a pdf for each of the targets"""

    # parameters
    target_list = []

    # check if output folder exist
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    # init log file
    log_data = open(f"{output_folder}/inscrap.log", "w")

    # check if target is a file or a int, load id from file if target is a file
    if not os.path.isfile(target):
        try:
            target_list = [int(target)]
            log_data.write(f"[+] Identify input as a single target : {target}\n")
        except:
            print(f"[!] Can't parse {target} as a valid input")
            return 1
    else:
        input_data = open(target, "r")
        log_data.write(f"[+] Identify input as a file : {target}\n")
        for line in input_data:
            id = line.rstrip()
            try:
                target_list.append(int(id))
                log_data.write(f"[+] Load target {id} from file : {target}\n")
            except:
                pass
        input_data.close()

    # check that there is target to parse
    if len(target_list) == 0:
        print(f"[!] No valid target found in {target}")
        return 1

    # run scrap on targets
    missing_doc = []
    for t in track(target_list):

        # Hunt & donwload pdf
        success = scrap(t, output_folder)

        # Update log
        if success:
            log_data.write(f"[+] Files found for compound {t}\n")
        else:
            log_data.write(f"[!] No files found for compound {t}\n")
            missing_doc.append(t)

    # close log file
    log_data.close()

    # display warning if necessary
    for d in missing_doc:
        print(f"[WARNING] No document found for target {d}")


if __name__ == "__main__":

    # parameters
    target = ""
    output_folder = ""

    # catch arguments
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input=", "output="])
    except getopt.GetoptError:
        display_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            display_help()
            sys.exit()
        elif opt in ("-i", "--input"):
            target = arg
        elif opt in ("-o", "--output"):
            output_folder = arg

    # display cool banner
    title = "> INSCRAP <"
    text = "=" * (len(title) - 2) + "\n" + title + "\n" + "=" * (len(title) - 2) + "\n"
    cprint(figlet_format(text, font="standard"), "green")

    # check that all arguments are present
    if target == "":
        print("[!] No input specified")
        print("[!] Use -h or --help options to get more informations")
        sys.exit()
    if output_folder == "":
        print("[!] No output folder specified")
        print("[!] Use -h or --help options to get more informations")
        sys.exit()

    # run selection
    run(target, output_folder)
