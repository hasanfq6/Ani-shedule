#!/data/data/com.termux/files/usr/bin/python

import time,sys
import requests, re
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import Fore, Style, init
from argparse import ArgumentParser
import datetime, sys
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.validation import Validator, ValidationError

anime_file = "/data/data/com.termux/files/home/.anime_links"

ge="[32m"
re="[0m"

def die(message):

    red = "[31m"
    reset = "[0m"
    print(f"[{red}warning{reset}] {message}")

def info(message):

    green = "[32m"
    r = "[0m"
    print(f"[{green}INFO{r}] {message}")

class NumberValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text.isdigit():
            raise ValidationError(message="Only numbers are allowed.", cursor_position=len(text))

def val(text):
    while True:
        try:
            user_input = prompt('Enter a number: ', validator=NumberValidator())
            return int(user_input)
        except ValidationError as ve:
            print(f'{ve}')
        except KeyboardInterrupt:
            die("User cancelled the progress")
            sys.exit(1)


# Initialize colorama
init(autoreset=True)

custom_style = Style.from_dict({
    'accepted': 'ansiyellow', # Accepted input color is yellow
    'input': 'ansiblue'
})

# Define the lexer to apply the style to user input
lexer = SimpleLexer('class:input')

def text_(text):
    try:
       user_input = prompt('Enter the name of the anime: ', lexer=lexer, style=custom_style)
       return user_input
    except KeyboardInterrupt:
       die("User canceled the progress")
       sys.exit(1)

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
    
    return {
        "Main Title": main_title,
        "English Title": english_title,
        "Episode Number": episode_number,
        "Subs Release Date": subs_release_date,
        "Subs Countdown": subs_countdown,
        "Raw Countdown": raw_countdown,
        "Airing Day": airing_day
    }

def fetch_anime_info(url):
    response = requests.get(url)
    response.raise_for_status()
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
    response_text = requests.get(url).text
    tree = html.fromstring(response_text)
    anime_data = []
    if "See Other" in response_text:
       pattern = r'href="/shows/(.*?)"'
       match = re.search(pattern, html_link)
       title = match.group(1)
       t_x = title.replace("-"," ")
       anime_data.append({
                "title": t_x,
                "link": f"https://animeschedule.net/anime/{title}"
            })
    else:
     for anime_element in tree.xpath("//div[contains(@class, 'anime-tile')]"):
        title_element = anime_element.xpath(".//h2[@class='anime-tile-title']")
        link_element = anime_element.xpath(".//@route")
        if title_element and link_element:
            anime_data.append({
                "title": title_element[0].text_content().strip(),
                "link": f"https://animeschedule.net/anime/{link_element[0]}"
            })

    return anime_data

def get_list(key):
    url = f"https://animeschedule.net/shows?q={key}"
    anime_data = get_anime_data(url)

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

def main():
    parser = ArgumentParser(description="Fetch anime info from URLs")
    parser.add_argument("-t", "--today", action="store_true", help="Display the anime that is coming on the current day")
    parser.add_argument("-s", "--thread", type=int, default=10, help="Number of threads to use (default=10)")
    parser.add_argument("-a", "--add", nargs="?", const="", help="Add anime to the list by URL or search term")
    args = parser.parse_args()

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
                file.write(url + "")
            print(message)
            for key, value in fetch_anime_info(url).items():
                print(f"{key}: {ge}{value}{re}")
            sys.exit(0)
        else:
            print(message)
            sys.exit(1)
    
    with open(anime_file, "r") as file:
        urls = [line.strip() for line in file.readlines()]

    st = time.time()
    with tqdm(total=len(urls)) as pbar:
        anime_info_list = []
        with ThreadPoolExecutor(max_workers=args.thread) as executor:
            futures = {executor.submit(fetch_anime_info, url): url for url in urls}
            for future in as_completed(futures):
                try:
                    anime_info = future.result()
                    anime_info_list.append(anime_info)
                except Exception as e:
                    print(f"Error fetching data for {futures[future]}: {e}")
                finally:
                    pbar.update(1)
    ed = time.time()
    fn = ed - st

    current_day = datetime.datetime.now().strftime("%A")
    if args.today:
        print(f"Animes Airing on {ge}{current_day}{re}")

    for anime_info in anime_info_list:
        airing_day_str = anime_info["Airing Day"]
        if airing_day_str:
            airing_day = datetime.datetime.fromisoformat(airing_day_str).strftime("%A")
        else:
            airing_day = None
        
        if args.today and airing_day != current_day:
            continue

        for key, value in anime_info.items():
            if key != "Airing Day":
                print(f"{key}: {ge}{value}{re}")
        print("" + "-"*40 + "")

    print(f"total time: {ge}{fn}{re}")

if __name__ == "__main__":
    main()
