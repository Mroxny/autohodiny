import os
import yaml
import datetime
import calendar
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),'values.yaml')

def load_config():
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)

def send_discord_notification(webhook_url, message=None, embed=None):
    data = {}
    if message:
        data["content"] = message
    if embed:
        data["embeds"] = [embed]
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send Discord notification: {str(e)}")

def is_last_day_of_month():
    today = datetime.date.today()
    _, last_day = calendar.monthrange(today.year, today.month)
    return today.day == last_day

def get_todays_schedule(schedule):
    today = datetime.datetime.now().strftime('%A').lower()
    print(today)
    return schedule.get(today, {})

def main():
    config = load_config()
    
    if is_last_day_of_month():
        embed = {
            "title": "📅 Monthly Timesheet Verification Required",
            "description": "Please verify all entries before the month ends!",
            "color": 16753920, 
            "url": config['login_url'],
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "footer": {
                "text": "Timesheet Automation System"
            }
        }
        send_discord_notification(config['discord_webhook'], embed=embed)

    try:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        driver.get(config['login_url'])
        driver.find_element(By.NAME, 'username').send_keys(config['credentials']['username'])
        driver.find_element(By.NAME, 'password').send_keys(config['credentials']['password'])
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        rows = driver.find_elements(By.CSS_SELECTOR, 'div.row.pt-1.pb-1')
        last_row = rows[-1]

        schedule = get_todays_schedule(config['schedule'])
        if not schedule:
            return
            # raise ValueError(f"No schedule found for today in {CONFIG_FILE}")

        start_input = last_row.find_element(By.CSS_SELECTOR, 'input.form-control.start_time')
        start_input.click()
        for _ in range(5):
            start_input.send_keys(Keys.LEFT)

        vals = schedule['start'].split(":")
        start_input.send_keys(vals[0])
        start_input.send_keys(Keys.RIGHT)
        start_input.send_keys(vals[1])

        end_input = last_row.find_element(By.CSS_SELECTOR, 'input.form-control.end_time')
        end_input.click()
        for _ in range(5):
            end_input.send_keys(Keys.LEFT)

        vals = schedule['end'].split(":")
        end_input.send_keys(vals[0])
        end_input.send_keys(Keys.RIGHT)
        end_input.send_keys(vals[1])

        project_input = last_row.find_element(By.CSS_SELECTOR, 'input.form-control.ddsearch-toggle')
        project_input.click()

        elem = driver.switch_to.active_element

        elem.send_keys(config['project'])
        elem.send_keys(Keys.UP)
        elem.send_keys(Keys.ENTER)

        submit_btn = driver.find_element(By.ID, 'submit')
        WebDriverWait(driver, 180).until(EC.element_to_be_clickable((By.ID, 'submit')))
        submit_btn.click()

    except Exception as e:
        error_msg = f"@here\n## ❌ Timesheet automation failed: \n{str(e)}"
        send_discord_notification(config['discord_webhook'], message=error_msg)
        raise
    finally:
        driver.quit()

if __name__ == '__main__':
    main()