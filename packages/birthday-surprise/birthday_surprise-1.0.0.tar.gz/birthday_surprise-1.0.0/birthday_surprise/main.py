import time
import random
import os
from pyfiglet import Figlet
from colorama import Fore, Style, init

init(autoreset=True)

user_input = input("Type your first-name to unlock your surprise: ").strip().lower()
if user_input not in {"buddy", "arunendra"}:
    print("\n Sorry, your surprise isn't available this time :(")
    exit()

friend_name = user_input[0].upper() + user_input[1:].lower()
colors = [Fore.RED, Fore.CYAN, Fore.GREEN, Fore.MAGENTA, Fore.YELLOW, Fore.BLUE]
f = Figlet(font='slant')
banner = f.renderText(f"Happy Birthday, {friend_name}!")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def falling_confetti(rows=20, cols=60, duration=5):
    symbols = ['*', '✦', '+', '❉', '♡', '❂', '•']
    confetti = []
    end_time = time.time() + duration
    for _ in range(100):
        confetti.append({
            'x': random.randint(0, cols - 1),
            'y': random.randint(-rows, 0),
            'symbol': random.choice(symbols),
            'color': random.choice(colors)
        })
    while time.time() < end_time:
        clear()
        screen = [[" " for _ in range(cols)] for _ in range(rows)]
        for c in confetti:
            if 0 <= c['y'] < rows:
                screen[c['y']][c['x']] = c['color'] + c['symbol']
            c['y'] += 1
            if c['y'] >= rows:
                c['y'] = random.randint(-5, 0)
                c['x'] = random.randint(0, cols - 1)
                c['symbol'] = random.choice(symbols)
                c['color'] = random.choice(colors)
        for row in screen:
            print("".join(row))
        time.sleep(0.1)

def reveal_banner(banner_text):
    for line in banner_text.split("\n"):
        print(random.choice(colors) + line)
        time.sleep(0.1)

def fun_quiz():
    clear()
    print(Fore.YELLOW + "\n🎮 Before we begin... let's warm up with a quick fun quiz! 🎮\n")
    time.sleep(1)
    input("Q1: Do you like cake? (press ENTER)\n")
    print(Fore.GREEN + "Correct answer! Everyone loves cake 😎\n")
    time.sleep(1)
    input("Q2: Are you excited for your surprise? (press ENTER)\n")
    print(Fore.MAGENTA + "I KNEW IT! 🎉\n")
    time.sleep(1)

def smile_drawing_animation():
    frames = [
        """

        
        
        
        
        
        """,
        """
           _______
        """,
        """
           _______
          /       \\
        """,
        """
           _______
          /       \\
         |  0   0  |
        """,
        """
           _______
          /       \\
         |  0   0  |
         |         |
        """,
        """
           _______
          /       \\
         |  0   0  |
         |         |
         |   \\_/   |
        """,
        """
           _______
          /       \\
         |  0   0  |
         |         |
         |   \\_/   |
          \\_______/
        """,
        """
        
           KEEP SMILING :)
        
        """,
    ]
    for frame in frames:
        clear()
        print(Fore.YELLOW + frame)
        time.sleep(0.5)

def youtube_surprise():
    import webbrowser, time, requests, re
    print(Fore.CYAN + "\n🎧 Your Musical Surprise 🎧")
    song = input("Type the name of your favorite song: ").strip()
    if not song:
        print("No song entered.")
        return

    print("\nFetching your song...")
    time.sleep(1)

    query = song.replace(" ", "+")
    url = f"https://www.youtube.com/results?search_query={query}"

    r = requests.get(url).text
    match = re.search(r"watch\?v=([a-zA-Z0-9_-]{11})", r)

    if not match:
        print("Could not find a playable video.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return

    video_id = match.group(1)
    final_url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"

    print("\n▶ Playing now on YouTube...")
    webbrowser.open(final_url)

def gift_box():
    print(Fore.CYAN + "\n🎁 Choose Your Birthday Gift Box 🎁")
    print(Fore.CYAN + "1) 🎞️  Short Film")
    print(Fore.CYAN + "2) ✉️  Birthday Card")
    print(Fore.CYAN + "3) 🎵 Birthday Song")
    print(Fore.CYAN + "4) 😊 A Smiley")
    print(Fore.CYAN + "5) 🎧 Your Favorite Song\n")
    choice = input("Pick a box (1/2/3/4/5): ")
    print("\nOpening your box...\n")
    time.sleep(2)
    if choice == "1":
        import webbrowser
        webbrowser.open("https://youtu.be/PF1_Z3APOh0?si=cl4zcsSCa-Hf5jke")
    elif choice == "2":
        image_path = os.path.join(os.path.dirname(__file__), "assets", "card.png")
        try:
            os.startfile(image_path)
        except:
            import webbrowser
            webbrowser.open(image_path)
    elif choice == "3":
        song_path = os.path.join(os.path.dirname(__file__), "assets", "birthday-song.wav")
        try:
            import winsound
            winsound.PlaySound(song_path, winsound.SND_FILENAME)
        except:
            print(Fore.RED + "Couldn't play sound on this system.")
    elif choice == "4":
        smile_drawing_animation()
    elif choice == "5":
        youtube_surprise()
    else:
        print(Fore.YELLOW + "😂 Oops! Empty box... choose wisely next time!")

def main():
    clear()
    input(Fore.YELLOW + "Press ENTER to begin your birthday adventure... 🎁")
    fun_quiz()
    for i in range(3, 0, -1):
        clear()
        print(Fore.MAGENTA + f"Your surprise arrives in {i}...")
        time.sleep(1)
    falling_confetti()
    clear()
    reveal_banner(banner)
    time.sleep(0.5)
    wishes = [
        "Wishing you endless happiness and success 🎂",
        "May your year ahead be full of joy 💫",
        "Keep smiling! 😊",
    ]
    for msg in wishes:
        print(random.choice(colors) + msg)
        time.sleep(1.2)
    gift_box()
    print(Style.BRIGHT + Fore.YELLOW + "\a")
    print(Style.BRIGHT + Fore.CYAN + f"\n🎉 Have an amazing day, {friend_name}! 🎉\n")
    time.sleep(1)

if __name__ == "__main__":
    main()

def run():
    main()