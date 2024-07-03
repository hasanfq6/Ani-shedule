#!/data/data/com.termux/files/usr/bin/python
import time,sys
import requests, re
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from argparse import ArgumentParser
import datetime, sys
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.validation import Validator, ValidationError
from pathlib import Path
from tabulate import tabulate

version = "1.0.6"
home_dir = Path.home()
anime_file = home_dir / '.anime_links'

if not anime_file.exists():
    anime_file.touch()

ge="\033[32m"
res="\033[0m"

def die(message):
    red = "\033[31m"
    reset = "\033[0m"
    print(f"[{red}warning{reset}] {message}")

def info(message):
    green = "\033[32m"
    r = "\033[0m"
    print(f"[{green}INFO{r}] {message}")

class NumberValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text.isdigit():
            raise ValidationError(message="Only numbers are allowed.", cursor_position=len(text))

def is_valid_link(line):
    return re.match(r'^(http://|https://)', line)

with anime_file.open('r') as file:
    lines = file.readlines()
    invalid_lines = [line for line in lines if not is_valid_link(line.strip())]

if invalid_lines:
    die("In the file there is an invalid link, please remove it")
    sys.exit(1)
else:
    pass

def val(text):
    while True:
        try:
            user_input = prompt(text, validator=NumberValidator())
            return int(user_input)
        except ValidationError as ve:
            print(f'{ve}')
        except KeyboardInterrupt:
            die("User cancelled the progress")
            sys.exit(1)


custom_style = Style.from_dict({
    'accepted': 'ansiyellow',
    'input': 'ansiblue'
})

lexer = SimpleLexer('class:input')

def text_(text):
    try:
       user_input = prompt(text, lexer=lexer, style=custom_style)
       return user_input
    except KeyboardInterrupt:
       die("User canceled the progress")
       sys.exit(1)

def get_latest_version():
    url = f"https://raw.githubusercontent.com/Kamanati/Ani-shedule/main/shedule.py"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        die(f"Failed to fetch the latest version from GitHub: {response.status_code}")
        return None

def get_current_version():
    with open(__file__, 'r') as file:
        return file.read()

def self_update():
    latest_version = get_latest_version()
    current_version = get_current_version()

    if latest_version and latest_version != current_version:
        backup_path = __file__ + ".bak"
        with open(backup_path, 'w') as backup_file:
            backup_file.write(current_version)
        
        with open(__file__, 'w') as script_file:
            script_file.write(latest_version)
        
        info(f"Script has been updated to the latest version. Please restart the script.")
        sys.exit(0)
    else:
        info("Script is already up-to-date :)")

def extract_anime_info(page_content):
    tree = html.fromstring(page_content)
    
    def safe_extract(xpath_expr):
        result = tree.xpath(xpath_expr)
        return result[0] if result else None
    
    main_title = safe_extract('//div[@id="anime-header-main-title"]/text()')
    english_title = safe_extract('//div[@id="anime-header-english-title"]/text()')
    episode_number = safe_extract('//div[@class="release-time-wrapper"]//h3[contains(text(), "Subs:")]/span[@class="release-time-episode-number"]/text()')
    subs_release_date = safe_extract('//div[@class="release-time-wrapper"]//h3[contains(text(), "Subs:")]/following-sibling::time[@id="release-time-subs"]/text()')
    subs_countdown = safe_extract('//div[@class="countdown-container"]//div[contains(@class, "countdown-text-subs")]/following-sibling::time[@class="countdown-time"]/text()')
    raw_countdown = safe_extract('//div[@class="countdown-container"]//div[contains(@class, "countdown-text-raw")]/following-sibling::time[@class="countdown-time"]/text()')
    airing_day = safe_extract('//div[@class="release-time-wrapper"]//h3[contains(text(), "Subs:")]/following-sibling::time[@id="release-time-subs"]/@datetime')
    try:
      status = tree.xpath('//h3[text()="Status"]/following-sibling::div/text()')[0]
    except IndexError:
      status = None
    try:
      total_ep = tree.xpath('//h3[text()="Episodes"]/following-sibling::div/text()')[0]
    except IndexError:
      total_ep = None
    
    return {
        "Main Title": main_title,
        "English Title": english_title,
        "Episode Number": episode_number,
        "Subs Release Date": subs_release_date,
        "Subs Countdown": subs_countdown,
        "Total episode": total_ep,
        "Airing Day": airing_day,
        "Status": status
    }

def fetch_anime_info(url):
    try:
       response = requests.get(url)
       response.raise_for_status()
    except Exception as e:
       pass
    return extract_anime_info(response.content)

def check_url(url, anime_file):
    import re
    pattern = re.compile(r'^https://animeschedule\.net/anime/[\w-]+$')
    if not pattern.match(url):
        print(url)
        return False, "URL format is incorrect."

    try:
        with open(anime_file, 'r') as file:
            for line in file:
                if url.strip() == line.strip():
                    return False, "URL is already in the file."
    except FileNotFoundError:
        return True, f"Url({url}) is added to the file.."

    return True, f"Url({url}) is added to the file.."

def get_anime_data(url):
    response = requests.get(url,allow_redirects=True)
    response_text = response.text
    tree = html.fromstring(response_text)
    anime_data = []

    if len(response.history) > 0:
         return False, response.url

    else:
     for anime_element in tree.xpath("//div[contains(@class, 'anime-tile')]"):
        title_element = anime_element.xpath(".//h2[@class='anime-tile-title']")
        link_element = anime_element.xpath(".//@route")
        if title_element and link_element:
            anime_data.append({
                "title": title_element[0].text_content().strip(),
                "link": f"https://animeschedule.net/anime/{link_element[0]}"
            })

    return True,anime_data

def get_list(key):
    url = f"https://animeschedule.net/shows?q={key}"
    status, anime_data = get_anime_data(url)

    if not status:
         return True, anime_data

    if (not anime_data):
        return False, "No anime titles found on the webpage."
      
    print("Available Anime Titles (Newest to Oldest):")

    for i, anime in enumerate(anime_data):
        print(f"{i+1}. {anime['title']}")

    user_choice = val("Enter the number corresponding to your anime selection: ") - 1
    if 0 <= user_choice < len(anime_data):
        selected_anime = anime_data[user_choice]
        return True, selected_anime['link']
    else:
        return False, "Invalid selection. Please choose a number from the list."

def get_color(success_count, total_anime):
    red = max(0, 255 - int(255 * (success_count / total_anime)))
    green = min(255, int(255 * (success_count / total_anime)))
    return f'\033[38;2;{red};{green};0m'

def process_anime_info_1(link):
    link = link.strip()
    status = fetch_anime_info(link)
    if status:
        title_1 = status.get("Main Title")
        title_2 = status.get("English Title")
        if status.get("Status") == "Finished":
            return (f"{title_1} / {title_2}", link, "Finished")
        elif status.get("Status") == "Ongoing":
            return (None, link, "Ongoing")
    return (None, link, "Unknown")

def process_anime_links(file_path):
    with open(file_path, 'r') as file:
        links = file.readlines()

    finished_anime = []
    ongoing_anime = []
    fetch_count = 0
    total_anime = len(links)


    with ThreadPoolExecutor(max_workers=10) as executor:
     futures = {executor.submit(process_anime_info_1, link): link for link in links}
     for future in as_completed(futures):
        try:
            title, link, status = future.result()
            fetch_count += 1
            color = get_color(fetch_count, total_anime)
            print(f"Number of anime fetched: {color}{fetch_count}\033[0m", end="\r")

            if status == "Finished":
                finished_anime.append((title, link))
            else:
                ongoing_anime.append(link)
        except Exception as e:
            print(f"Error fetching data for {futures[future]}: {e}")

    print()

    if finished_anime:
        print("The following anime are finished:")
        for i, (title, link) in enumerate(finished_anime, start=1):
            print(f"{i}. {title}")

        user_input = text_("Do you want to delete all finished anime? (yes to delete all, no to specify exceptions, 0 to delete none): ")

        if user_input.lower() == "yes":
            exceptions = []
        elif user_input == "0":
            exceptions = list(range(1, len(finished_anime) + 1))
        elif user_input == "no":
            exceptions = text_("Enter the numbers of the anime you want to keep, separated by commas: ")
            exceptions = list(map(int, exceptions.split(',')))
        else:
            die("Invalid Option selected")
            sys.exit(1)

        links_to_keep = ongoing_anime + [link for i, (title, link) in enumerate(finished_anime, start=1) if i in exceptions]
        deleted_count = len(links) - len(links_to_keep)

        with open(file_path, 'w') as file:
            for link in links_to_keep:
                file.write(link + '\n')

        info(f"Number of anime links deleted: {deleted_count}")
    else:
        info("No finished anime found.")

def display_anime_info(anime):
    for key, value in anime.items():
        print(f"{key}: {ge}{value}{res}")
    sys.exit(0)

def specific(thread):
   with open(anime_file, "r") as file:
        urls = [line.strip() for line in file.readlines()]
   success_count = 0
   total_anime = len(urls)
   with ThreadPoolExecutor(max_workers=thread) as executor:
      anime_info_list = []
      futures = {executor.submit(fetch_anime_info, url): url for url in urls}
      for future in as_completed(futures):
        try:
            anime_info = future.result()
            anime_info_list.append(anime_info)
            success_count += 1
        except Exception as e:
            print(f"Error fetching data for {futures[future]}: {e}")

        color = get_color(success_count, total_anime)

        print(f"Number of anime fetched: {color}{success_count}\033[0m", end="\r")

   for idx, anime in enumerate(anime_info_list):
        print(f"{ge}{idx + 1}{res}. {anime['Main Title']} / {anime['English Title']}")

    
   selection = val("Enter the index of the anime you want to view: ") - 1
   if 0 <= selection < len(anime_info_list):
            selected_anime = anime_info_list[selection]
            display_anime_info(selected_anime)
   else:
            die("Invalid index.")


def main():
    parser = ArgumentParser(description="Fetch anime info from URLs")
    parser.add_argument("-t", "--today", action="store_true", help="Display the anime that is coming on the current day")
    parser.add_argument("-s", "--thread", type=int, default=10, help="Number of threads to use (default=10)")
    parser.add_argument("-a", "--add", nargs="?", const="", help="Add anime to the list by URL or search term")
    parser.add_argument("-b", "--airing",action="store_true" , help="List the Upcoming Anime ")
    parser.add_argument("-d", "--delete",action="store_true" , help="Delete the anime that is finished airing")
    parser.add_argument("-u", "--update",action="store_true" , help="Update the script to latest version")
    parser.add_argument("-S", "--specific",action="store_true" , help="Select specific anime to see the details")

    args = parser.parse_args()

    if args.update:
       self_update()
       sys.exit(0)

    if args.delete:
       process_anime_links(anime_file)
       sys.exit(0)

    if args.specific:
       specific(args.thread)
       sys.exit(0)

    if args.airing:
        info(f"It is under progress, it will available soon, if not try {ge}ani-shedule --update | -u{res}")
        sys.exit(0)

    if args.add is not None:
        if args.add == "":
            search = text_("Enter Anime you want to search: ")
            result, message = get_list(search)
            if result:
                url = message
            else:
                print(message)
                sys.exit(1)
        else:
            url = args.add

        result, message = check_url(url, anime_file)
        if result:
            with open(anime_file, 'a') as file:
                file.write(url + "\n")
            print(message)
            for key, value in fetch_anime_info(url).items():
                print(f"{key}: {ge}{value}{res}")
            sys.exit(0)
        else:
            info(message)
            sys.exit(1)
    
    with open(anime_file, "r") as file:
        urls = [line.strip() for line in file.readlines()]

    with anime_file.open('r') as file:
       line = file.readlines()

    if not lines:
       die("Please add Anime: use ani-shedule -a | ani-shedule --add")
       sys.exit(1)

    st = time.time()
    success_count = 0
    total_anime = len(urls)

    with ThreadPoolExecutor(max_workers=args.thread) as executor:
      anime_info_list = []
      futures = {executor.submit(fetch_anime_info, url): url for url in urls}
      for future in as_completed(futures):
        try:
            anime_info = future.result()
            anime_info_list.append(anime_info)
            success_count += 1
        except Exception as e:
            print(f"Error fetching data for {futures[future]}: {e}")

        color = get_color(success_count, total_anime)
        
        print(f"Number of anime fetched: {color}{success_count}\033[0m", end="\r")
    print()

    ed = time.time()
    fn = ed - st
    flag = False
    current_day = datetime.datetime.now().strftime("%A")
    if args.today:
        print(f"Animes Airing on {ge}{current_day}{res}")

    for anime_info in anime_info_list:
        airing_day_str = anime_info["Airing Day"]
        if airing_day_str:
            airing_day = datetime.datetime.fromisoformat(airing_day_str).strftime("%A")
        else:
            airing_day = None
        
        if args.today and airing_day != current_day:
            continue

        flag = True

        for key, value in anime_info.items():
            if key != "Airing Day":
                print(f"{key}: {ge}{value}{res}")
        print("" + "-"*40 + "")

    if not flag:
       die("It seems like no anime airing today.")
       info("if you sure the anime aires today then it may be the last episode")
       info("Or it May be some error please check network connection Or")
       info("Try reduce the thread by -b or --thread to 2-4, (default 10)")
       sys.exit(1)

    print(f"total time: {ge}{fn}{res}")

if __name__ == "__main__":
    main()
