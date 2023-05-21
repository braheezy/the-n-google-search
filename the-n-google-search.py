#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from num2words import num2words
from selenium.common.exceptions import NoSuchElementException
from termcolor import colored, cprint

chrome_options = Options()
chrome_options.add_argument("--headless")

# The search start and stop boundaries
START_SEARCH = 1
STOP_SEARCH = 100
# When to truncate links
LINK_LIMIT = 45


def search(n_page):
    # Create new instance of Chrome in headless mode
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to Googl search
    driver.get("https://www.google.com")

    query = f"the {n_page}"

    # Find the search input element and enter the query
    search_input = driver.find_element("name", "q")
    search_input.send_keys(query)
    search_input.submit()

    # The Xpath syntax in the following lines mean the following:
    #   not(ancestor::g-section-with-header)
    #       Any element that is not a child of a g-section-with-header
    #   contains(., '{n_page}'
    #       Any element that contains the text '{n_page}'
    #   not(ancestor::div[contains(@class, 'cUnQKe')])
    #       Any element that is not a child of a div with class cUnQKe
    #   contains(translate(., '{n_page.lower()}', '{n_page.upper()}'), '{n_page.upper()}')
    #       Case insensitive search for  text '{n_page.upper()}'

    # Find the top result link element
    try:
        result = driver.find_element(
            By.XPATH,
            f"//a[not(ancestor::g-section-with-header) and contains(., '{n_page}') and not(ancestor::div[contains(@class, 'cUnQKe')])]"
        )
    except NoSuchElementException:
        # Also try looking for text version of number
        # For example, if n_page is 5, then query is "the five"
        n_page = num2words(n_page)
        result = driver.find_element(
            By.XPATH,
            f"//a[not(ancestor::g-section-with-header) and contains(translate(., '{n_page.lower()}', '{n_page.upper()}'), '{n_page.upper()}') and not(ancestor::div[contains(@class, 'cUnQKe')])]"
        )

    top_result_text = None
    top_result_link = None

    get_text = lambda x: x.text or x.get_attribute(
        "innerText") or x.get_attribute('textContent') or "No title found :("
    if result:
        # print(result.get_attribute("href"))
        # print(len(result.text), result.text, result.text == '')
        # Get useful information from link
        top_result_link = result.get_attribute("href")
        top_result_text = get_text(result).splitlines()[0]

    # close the browser
    driver.quit()

    return (top_result_text, top_result_link)


def main():
    for i in range(START_SEARCH, STOP_SEARCH + 1):
        # Perform search
        result = search(i)

        # Pretty print the results
        query_title = colored(f"The {i}", 'green', attrs=['bold', 'underline'])
        cprint(f"Top result for {query_title}:", 'light_blue')
        if result:
            url = (result[1][0:LINK_LIMIT] +
                   '...') if len(result[1]) > LINK_LIMIT else result[1]
            print(colored("\tTitle: ", 'magenta'), colored(result[0], 'cyan'))
            print(colored("\tURL  : ", 'magenta'), colored(url, 'cyan'))
        else:
            cprint(f'\tNo result found :(', 'light_red')
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\nQuitting...", 'yellow')
