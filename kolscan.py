from prisma import Prisma
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import logging
import json
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    options = webdriver.ChromeOptions()

    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


# Set up logging configuration at the top of your script
def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Set up logging with timestamp in filename
    log_filename = f'logs/gmgn_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def wait_for_element(driver, selector, by=By.CSS_SELECTOR, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )


def click_time_filter(driver, period, logger):
    logger.info(f"Attempting to click {period} filter button")
    
    # Wait for page load
    time.sleep(3)
    
    # Target buttons using exact class names from the HTML
    button_selectors = {
        'Daily': [
            "//div[contains(@class, 'timeFilterContainer')]//p[contains(@class, 'selected') or text()='Daily']",
            "//p[text()='Daily']",
            "//button[text()='Daily']",
            "//*[contains(text(), 'Daily')]"
        ],
        'Weekly': [
            "//div[contains(@class, 'timeFilterContainer')]//p[text()='Weekly']",
            "//p[text()='Weekly']", 
            "//button[text()='Weekly']",
            "//*[contains(text(), 'Weekly')]"
        ],
        'Monthly': [
            "//div[contains(@class, 'timeFilterContainer')]//p[text()='Monthly']",
            "//p[text()='Monthly']",
            "//button[text()='Monthly']", 
            "//*[contains(text(), 'Monthly')]"
        ]
    }
    
    for selector in button_selectors[period]:
        try:
            logger.info(f"Trying selector: {selector}")
            
            # Wait for element to be present and clickable
            button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            
            # Scroll to element to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(1)
            
            # Try regular click first
            try:
                button.click()
                logger.info(f"Successfully clicked {period} button with regular click")
                time.sleep(3)
                return
            except:
                # If regular click fails, try JavaScript click
                driver.execute_script("arguments[0].click();", button)
                logger.info(f"Successfully clicked {period} button with JavaScript click")
                time.sleep(3)
                return
                
        except Exception as e:
            logger.warning(f"Selector {selector} failed: {str(e)}")
            continue
    
    # If all selectors fail, log the page source for debugging
    logger.error(f"All selectors failed for {period}. Saving page source for debugging...")
    with open(f'debug_page_{period}.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    
    raise Exception(f"Could not find or click {period} button with any selector")

def extract_data(driver, period, logger):
    period_days = {'Daily': 1, 'Weekly': 7, 'Monthly': 30}
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    scripts = soup.find_all('script')
    combined_push_content = ''

    for script in scripts:
        if script.string and 'self.__next_f.push' in script.string:
            cleaned_content = script.string.replace('self.__next_f.push([', '').replace(']);', '')
            if cleaned_content.startswith('1,'):
                cleaned_content = cleaned_content[2:]
            combined_push_content += cleaned_content.replace('])', '')

    combined_push_content = combined_push_content.replace('\\', '').split('"initialData":')[1].split('"initialUserData":')[0]
    combined_push_content = combined_push_content.replace(',"telegram":""', ',"telegram":null').replace('""', '')
    combined_push_content = combined_push_content.rstrip(',')

    # Convert combined_push_content to a Python list and create lookup dictionary
    try:
        combined_data = json.loads('[' + combined_push_content + ']')
        social_lookup = {
            item['wallet_address']: (item.get('telegram'), item.get('twitter'))
            for item in combined_data[0]  # Access the first element since combined_data is a list
        }

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Failed to parse JSON data: {str(e)}")
        social_lookup = {}

    users = soup.find_all('div', class_='leaderboard_leaderboardUser__8OZpJ')
    data = []

    for user in users:
        try:
            account_link = user.find('a')

            wallet_name = account_link.find('h1').text.strip()
            wallet_address = account_link['href'].split('/account/')[1]
            wallet_avatar = account_link.find('img')['src']
            account_name = user.find('p', class_="remove-mobile").text.strip()


            win_div_tags = user.find('div', class_='remove-mobile').find_all('p')
            win = win_div_tags[0].text.strip()
            loss = win_div_tags[1].text.strip()

            pnl_div = user.find('div', class_='leaderboard_totalProfitNum__HzfFO')
            h1_tags = pnl_div.find_all('h1')

            # pnl_sol = h1_tags[0].text.replace('Sol', '').strip()
            pnl_sol = h1_tags[0].text

            # pnl_usd = h1_tags[1].text.replace(',', '').replace('$', '').replace('(', '').replace(')', '').strip()
            pnl_usd = h1_tags[1].text

            telegram, twitter = social_lookup.get(wallet_address, (None, None))

            data.append({
                'period': period_days[period],
                'wallet_name': wallet_name,
                'wallet_address': wallet_address,
                'wallet_avatar':wallet_avatar,
                'account_name': account_name,
                'win': win,
                'loss': loss,
                'pnl_usd': pnl_usd,
                'pnl_sol': pnl_sol,
                'telegram': telegram,
                'twitter': twitter
            })

        except AttributeError as e:
            logger.warning(f"Failed to extract data for a user: {str(e)}")
            continue

    logger.info(f"Successfully extracted data for {len(data)} users")
    return data

async def save_to_database(data):
    db = Prisma()
    await db.connect()

    for record in data:
        try:
            await db.kolleaderboard.upsert(
                where={
                    'wallet_address': record['wallet_address']
                },
                data={
                    'create': {
                        'period': record['period'],
                        'wallet_name': record['wallet_name'],
                        'wallet_address': record['wallet_address'],
                        'pnl_usd': record['pnl_usd'],
                        'pnl_sol': record['pnl_sol'],
                        'telegram': record['telegram'],
                        'twitter': record['twitter']
                    },
                    'update': {
                        'period': record['period'],
                        'wallet_name': record['wallet_name'],
                        'pnl_usd': record['pnl_usd'],
                        'pnl_sol': record['pnl_sol'],
                        'telegram': record['telegram'],
                        'twitter': record['twitter']
                    }
                }
            )
        except Exception as e:
            print(f"Error storing record for {record['wallet_address']}: {str(e)}")

    await db.disconnect()
    print(f"Saved {len(data)} records to database")


async def scrape_kolscan():
    logger = setup_logging()
    logger.info("Initializing scraper")
    
    driver = setup_driver()
    logger.info("Browser driver setup complete")
    
    all_data = []  # Initialize list to store data from all periods
    
    try:
        logger.info("Navigating to KOLscan leaderboard")
        driver.get("https://kolscan.io/leaderboard")
        logger.info("Page loaded, waiting for initial render")
        time.sleep(2)

        for period in ['Daily', 'Weekly', 'Monthly']:
            try:
                logger.info(f"=== Starting {period} period scraping ===")
                click_time_filter(driver, period, logger)
                period_data = extract_data(driver, period, logger)
                all_data.extend(period_data)  # Add period data to all_data
            except Exception as e:
                logger.error(f"Failed to complete {period} scraping: {str(e)}", exc_info=True)

        await save_to_database(all_data)  # Save combined data from all periods
    
    except Exception as e:
        logger.error(f"Critical scraper error: {str(e)}", exc_info=True)
    
    finally:
        driver.quit()
        logger.info("Scraping process completed, browser closed")


if __name__ == "__main__":
    scrape_kolscan()
