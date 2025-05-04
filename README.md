
# Ani Shedule

This script fetches and displays information about anime titles from [animeschedule.net](https://animeschedule.net). It supports searching by anime name or URL, validates and stores URLs, extracts anime details, and allows concurrent fetching using multiple threads. It includes a command-line interface for user interaction.

## Features

- Search for anime titles by name or URL.
- Validate URLs and check for duplicates.
- Extract details like titles, episode numbers, and release dates.
- Fetch information concurrently using multiple threads.
- Command-line interface for easy interaction.

```markdown
## Warning:

This program is still under development

```

## Usage

1. **Add Anime by Search Term:**
   ```sh
   python shedule.py -a
   ```
   Prompts the user to enter an anime name to search and add it to the list.

2. **Add Anime by URL:**
   ```sh
   python shedule.py -a <anime_url>
   ```
   Adds the provided anime URL to the list if valid and not already added.

3. **Display Today's Anime:**
   ```sh
   python shedule.py -t
   ```
   Displays the anime that are coming out on the current day.

4. **Specify Number of Threads:**
   ```sh
   python shedule.py -s <number_of_threads>
   ```
   Specifies the number of threads to use (default is 10).

## Example

Add an anime by search term:
```sh
$ python shedule.py -a
Enter the name of the anime: One Piece
Available Anime Titles (Newest to Oldest):
1. One Piece
2. One Piece: Episode of Sabo
3. One Piece Film: Gold
Enter the number corresponding to your anime selection: 1
Url(https://animeschedule.net/anime/one-piece) is added to the file..
Main Title: One Piece
English Title: One Piece
Episode Number: 1023
Subs Release Date: June 18, 2024
Subs Countdown: 00:10:00
Raw Countdown: 00:20:00
Airing Day: 2024-06-18T00:00:00Z
```

## Required Packages

- `tqdm` (Version: 4.63.0)
- `lxml` (Version: 5.2.2)
- `requests` (Version: 2.32.3)
- `prompt-toolkit` (Version: 3.0.43)

## Installation

## Install view PIP
```sh
pip install ani-shedule
```
 - for PIP install use the command `ani-shedule`

### NOTE:
- To update the program, you should use `ani-schedule -u` as updating the pip version is not applicable.
- As soon as you install, update the program to move to the latest version because the pip version will not upgrade, it has a self-update mechanism.
- If you notice any issue or error, update and check again. If the problem persists, open an issue.

## Manual Install 

1. Install Python (if not already installed).
2. Install the required packages using pip:
   ```sh
   pip install tqdm==4.63.0
   pip install lxml==5.2.2
   pip install requests==2.32.3
   pip install prompt-toolkit==3.0.43
   ```

## Step-by-Step Installation Process

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/yourusername/Ani-shedule.git
   cd Ani-shedule
   ```

2. **Create a Virtual Environment (Optional but recommended):**
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install Required Packages:**
   ```sh
   pip install tqdm==4.63.0
   pip install lxml==5.2.2
   pip install requests==2.32.3
   pip install prompt-toolkit==3.0.43
   ```

4. **Run the Script:**
   ```sh
   python script.py -a
   ```


<p align=left>
Total Views<br/>
  <a href="https://count.getloli.com/"><img src="https://count.getloli.com/@Raiden?name=Ani-shedule&theme=random&padding=7&offset=0&align=top&scale=1&pixelated=1&darkmode=auto"/></a><br/>
</p>

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fhasanfq6%2FAni-shedule&count_bg=%23FFBB00&title_bg=%23B12222&icon=cliqz.svg&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)



## License

This project is licensed under the MIT License.
https://github.com/hasanfq6/Ani-shedule.git
