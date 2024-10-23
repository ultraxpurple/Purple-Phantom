import requests
import argparse
import sys
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed

BANNER = f'''
{Fore.MAGENTA}
ooooooooo.                      oooo                                  .                               
`888   `Y88.                    `888                                .o8                               
 888   .d88'         oo.ooooo.   888 .oo.    .oooo.   ooo. .oo.   .o888oo  .ooooo.  ooo. .oo.  .oo.   
 888ooo88P'           888' `88b  888P"Y88b  `P  )88b  `888P"Y88b    888   d88' `88b `888P"Y88bP"Y88b  
 888         8888888  888   888  888   888   .oP"888   888   888    888   888   888  888   888   888  
 888                  888   888  888   888  d8(  888   888   888    888 . 888   888  888   888   888  
o888o                 888bod8P' o888o o888o `Y888""8o o888o o888o   "888" `Y8bod8P' o888o o888o o888o 
                      888                                                                             

                     o888o                                                                            
                                                                                                      

{Style.RESET_ALL}
                               by ultra purple (@ULTRAxPURPLE)

- URL: {{base_url}}
- Wordlist: {{wordlist_path}}
'''

def get_page_size(url, headers):
    try:
        response = requests.get(url, timeout=5, headers=headers)
        return len(response.text), response.status_code
    except requests.RequestException:
        return None, None

def check_url(base_url, word, headers):
    test_url = f"{base_url}/{word}"
    return test_url, get_page_size(test_url, headers)

def directory_bruteforce(base_url, wordlist_file, headers=None):
    home_page_size, _ = get_page_size(base_url, headers)

    with open(wordlist_file, 'r') as wordlist:
        unique_pages = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_word = {executor.submit(check_url, base_url, word.strip(), headers): word.strip() for word in wordlist}

            for future in as_completed(future_to_word):
                word = future_to_word[future]
                try:
                    test_url, (size, status) = future.result()
                    if size is None or status not in {200, 301}:
                        continue

                    duplicate = None
                    for known_url, known_size in unique_pages.items():
                        if abs(size - known_size) <= 5:
                            duplicate = known_url
                            break

                    if duplicate:
                        print(f"{Fore.RED}URL: {test_url} | Status: {status} | Size: {size} | Duplicated: {duplicate}{Style.RESET_ALL}")
                    else:
                        unique_pages[test_url] = size
                        print(f"{Fore.GREEN}URL: {test_url} | Status: {status} | Size: {size}{Style.RESET_ALL}")

                except Exception as e:
                    print(f"{Fore.YELLOW}Error processing {word}: {e}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="Purple Phantom Directory Brute Forcer")
    parser.add_argument("-u", "--url", required=True, help="Base URL (e.g., http://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist")
    parser.add_argument("-H", "--headers", nargs='*', help="Custom headers (e.g., 'User-Agent: CustomAgent')")

    args = parser.parse_args()

    headers = {}
    if args.headers:
        for header in args.headers:
            key, value = header.split(":", 1)
            headers[key.strip()] = value.strip()

    base_url = args.url
    wordlist_path = args.wordlist

    print(BANNER.format(base_url=base_url, wordlist_path=wordlist_path))
    directory_bruteforce(base_url, wordlist_path, headers)

if __name__ == "__main__":
    main()
