import platform
from urllib.parse import urlparse
import chardet
from colorama import Fore, Style, init
import os
import sys
import time
import threading
import subprocess

ascii_art = """


        ┏┓  ┓ ┓•   ┳┳  ┓   ┏┓•┓         
        ┃┃┓┏┣┓┃┓┏  ┃┃┏┓┃┏  ┣ ┓┃╋┏┓┏┓┏┓┏┓
        ┣┛┗┻┗┛┗┗┗  ┗┛┛ ┗┛  ┻ ┗┗┗┗ ┛ ┗ ┛ 
                                


"""

madeBy = """
    
    
    
    
"""
init()
max_number_of_threads = 1
urls_files_paths = []
public_domains_files_paths = []
is_stopped = False
progress = 0
private_urls = 0
public_urls = 0
public_domains = 0
url_per_minute = 0
number_of_finished_threads = 0
loaded_urls = 0
number_of_finished_files = 0
total_urls = 0
working_threads = 0
current_file_counter = 0
filtered_urls_in_current_file = 0
max_filtered_urls_per_file = 200000


def loadingTask():
    try:
        global max_number_of_threads, progress, private_urls, loaded_urls, total_urls, is_stopped, url_per_minute
        global number_of_finished_threads, working_threads, public_urls, public_domains
        loading_counter = 0
        loading_symbols = ["|", "/", "-", "\\"]
        clear_terminal()


        while number_of_finished_threads != max_number_of_threads and not is_stopped:

            progress = (((private_urls + public_urls) / total_urls) * 100) // 1

            print(f"{Fore.GREEN}{ascii_art}")
            print(f"{Fore.GREEN}{madeBy}")
            print(f"{Fore.GREEN}    [{Fore.BLUE}{loading_symbols[loading_counter]}{Fore.GREEN}] Filtering urls")
            print(f"{Fore.GREEN}    Total urls : {Fore.BLUE + str(total_urls)}")
            print(f"{Fore.GREEN}    Total public domains : {Fore.BLUE + str(public_domains)}")
            print(f"{Fore.GREEN}    Progress : {Fore.BLUE + str(progress)} %")
            print(f"{Fore.GREEN}    Loaded urls : {Fore.BLUE + str(loaded_urls)}")
            print(f"{Fore.GREEN}    Url per minute : {Fore.BLUE + str(url_per_minute)}")
            print(f"{Fore.GREEN}    Private urls : {Fore.YELLOW + str(private_urls)}")
            print(f"{Fore.GREEN}    Public urls : {Fore.RED + str(public_urls)}")
            print(f"{Fore.GREEN}    Working threads : {Fore.BLUE + str(working_threads)}")
            print(f"{Fore.GREEN}    Finished threads : {Fore.BLUE + str(number_of_finished_threads)}")

            move_up = "\033[F" * 26
            print(move_up, end='\r')

            loading_counter += 1

            if loading_counter >= len(loading_symbols):
                loading_counter = 0
        else:
            clear_terminal()
            progress = (((private_urls + public_urls) / total_urls) * 100) // 1
            print(f"{Fore.GREEN}{ascii_art}")
            print(f"{Fore.GREEN}{madeBy}")
            print(f"{Fore.GREEN}    Finished filtering urls")
            print(f"{Fore.GREEN}    Total urls : {Fore.BLUE + str(total_urls)}")
            print(f"{Fore.GREEN}    Total public domains : {Fore.BLUE + str(public_domains)}")
            print(f"{Fore.GREEN}    Progress : {Fore.BLUE + str(progress)} %")
            print(f"{Fore.GREEN}    Loaded urls : {Fore.BLUE + str(loaded_urls)}")
            print(f"{Fore.GREEN}    Url per minute : {Fore.BLUE + str(url_per_minute)}")
            print(f"{Fore.GREEN}    Private urls : {Fore.YELLOW + str(private_urls)}")
            print(f"{Fore.GREEN}    Public urls : {Fore.RED + str(public_urls)}")
            print(f"{Fore.GREEN}    Working threads : {Fore.BLUE + str(working_threads)}")
            print(f"{Fore.GREEN}    Finished threads : {Fore.BLUE + str(number_of_finished_threads)}")
            print(f"{Fore.GREEN}    Closing ...")
        is_stopped = True
    except:
        sys.stdout.write(Fore.RED + Style.BRIGHT + "\n>Stopping ...\n")
        sys.stdout.write(Fore.RED + Style.BRIGHT + "Check files paths\n")
        is_stopped = True
        exit()


def detect_encoding(filename):
    try:
        with open(filename, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            file.close()
            print(result['encoding'])
            return result['encoding']
    except Exception as e:
        print(e)
        return None


def urlFiltererThread(urls):
    global public_domains_files_paths, is_stopped, public_urls, private_urls, working_threads, number_of_finished_threads
    global current_file_counter, filtered_urls_in_current_file, max_filtered_urls_per_file, loaded_urls
    try:
        for url in urls:
            is_url_private = True
            loaded_urls += 1
            for public_domain_file_path in public_domains_files_paths:
                with open(public_domain_file_path, 'r') as public_domains_file:

                    public_domains_in_file = public_domains_file.read().split("\n")
                    found_url_index = binary_search(public_domains_in_file, extract_domain(url.strip()))

                    if found_url_index != -1:
                        is_url_private = False
                        break

            if is_url_private:
                with open(f"./result/url_private_{current_file_counter}.txt", 'a') as private_urls_file:
                    private_urls_file.write(url + "\n")
                    private_urls += 1
                    private_urls_file.close()

                filtered_urls_in_current_file += 1

                if filtered_urls_in_current_file > max_filtered_urls_per_file:
                    filtered_urls_in_current_file = 0
                    current_file_counter += 1

            else:
                public_urls += 1

        private_urls += 1
        working_threads -= 1
        number_of_finished_threads += 1

    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"\nError occurred while filtering url file: {e}\n")
        is_stopped = True


def sortPublicDomains(public_domain_file_Path):
    global public_domains, working_threads
    try:
        # sorted_domains = []
        # encoding = detect_encoding(public_domain_file_Path)
        # if encoding is None:
        #     raise ValueError("Encoding detection failed")

        with open(public_domain_file_Path, 'r', errors='ignore') as public_domain_file:
            public_domain_file.seek(0)  # Reset file pointer to the beginning

            sorted_domains = public_domain_file.read().replace("\n", "\n;;").split(";;")

            public_domains += len(sorted_domains)

            sorted_domains.sort()

        with open(public_domain_file_Path, 'w', errors='ignore') as public_domain_file:
            public_domain_file.writelines(sorted_domains)

        working_threads -= 1
    except Exception as e:
        print(f"Error sorting public domains: {e}")


def binary_search(sorted_list, target):
    left, right = 0, len(sorted_list) - 1

    while left <= right:
        mid = (left + right) // 2
        mid_val = sorted_list[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1  # Target not found


def clear_terminal():
    # Determine the command based on the platform
    try:
        if platform.system() == "Windows":
            command = "cls"
        else:
            command = "clear"

        # Use subprocess to call the appropriate command
        subprocess.call(command, shell=True)
        if sys.platform.startswith("win"):
            # For Windows
            _ = sys.stdout.write("\033[H\033[2J")
        else:
            # For Linux and Mac
            _ = sys.stdout.write("\033c")
        sys.stdout.flush()
    except:
        sys.stdout.write(Fore.RED + Style.BRIGHT + "\n>Stopping ...\n")
        sys.stdout.write(Fore.RED + Style.BRIGHT + "Check files paths\n")
        is_aborted = True
        exit()


def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain


def urlPerMCalc():
    global private_urls, is_stopped, number_of_finished_threads, number_of_finished_threads, url_per_minute

    while not is_stopped and number_of_finished_threads != number_of_finished_threads:
        current_urls = private_urls
        time.sleep(60)
        url_per_minute = private_urls - current_urls

def mainThread():
    global is_stopped, working_threads, public_domains_files_paths, max_number_of_threads, total_urls
    global urls_files_paths, loaded_urls
    try:
        print(f"{Fore.GREEN}{ascii_art}")
        print(f"{Fore.GREEN}{madeBy}")

        print(f"{Fore.GREEN}> Enter urls folder path, example : c:\\users\\urls")
        urls_dir = input(f"{Fore.GREEN}> ")

        print(f"{Fore.GREEN}> Enter public domains folder path, example : c:\\users\\public_domains")
        public_domains_dir = input(f"{Fore.GREEN}> ")

        print(f"{Fore.GREEN}> Enter number of threads")
        max_number_of_threads = int(input(f"{Fore.GREEN}> "))

        print(f"{Fore.GREEN}> Please wait , processing files ...")

        for public_domains_path in os.listdir(public_domains_dir):
            if public_domains_path.split(".")[1] == 'txt':
                public_domains_files_paths.append(os.path.join(public_domains_dir, public_domains_path))

                public_domains_file_sorter_thread = threading.Thread(target=sortPublicDomains, args=(
                    public_domains_files_paths[len(public_domains_files_paths) - 1],))

                public_domains_file_sorter_thread.start()

                working_threads += 1

                if working_threads >= max_number_of_threads:
                    public_domains_file_sorter_thread.join()

        for url_file_path in os.listdir(urls_dir):

            if url_file_path.split(".")[1] == 'txt':
                urls_files_paths.append(os.path.join(urls_dir, url_file_path))

                with open(os.path.join(urls_dir, url_file_path), 'r') as url_file:
                    total_urls += len(url_file.read().split("\n"))

                    url_file.close()

        ulr_per_thread = total_urls // max_number_of_threads

        if total_urls < max_number_of_threads:
            ulr_per_thread = total_urls

        while working_threads != 0:
            pass

        ulr_per_thread_counter = 0
        file_url_counter = 0

        loading_thread = threading.Thread(target=loadingTask)
        url_per_minute_thread = threading.Thread(target=urlPerMCalc)

        loading_thread.start()
        url_per_minute_thread.start()

        while ulr_per_thread_counter < total_urls:

            with open(urls_files_paths[file_url_counter], 'r') as url_file:
                urls = url_file.read().split("\n")
                read_urls_lines = 0

                while read_urls_lines < len(urls) and read_urls_lines + ulr_per_thread < len(urls):

                    url_filterer_thread = threading.Thread(target=urlFiltererThread, args=(
                        urls[read_urls_lines:read_urls_lines + ulr_per_thread],))

                    url_filterer_thread.start()
                    working_threads += 1

                    if working_threads > max_number_of_threads:
                        url_filterer_thread.join()

                    read_urls_lines += ulr_per_thread

                    ulr_per_thread_counter += ulr_per_thread
                else:
                    if read_urls_lines < len(urls):

                        url_filterer_thread = threading.Thread(target=urlFiltererThread, args=(urls[read_urls_lines:],))

                        url_filterer_thread.start()

                        working_threads += 1

                        if working_threads > max_number_of_threads:
                            url_filterer_thread.join()

                        read_urls_lines += ulr_per_thread

                        ulr_per_thread_counter += len(urls) - read_urls_lines

        loading_thread.join()
        url_per_minute_thread.join()

    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"\nError occurred, check your input: {e}\n")
        is_stopped = True

mainThread()