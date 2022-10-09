"""Main module for listening for new tickets and notifying user if under price_threshold"""

import sys
import os
import time
import random

import undetected_chromedriver as uc
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchElementException,
                                        ElementNotInteractableException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from twilio.rest import Client

class TicketListener:
    def __init__(self, event_note, event_url, max_price_threshold, refresh_time_limits):
        self.event_note = event_note
        self.event_url = event_url
        self.max_price_threshold = max_price_threshold
        self.refresh_time_limits = refresh_time_limits

        #Create driver
        self.driver = uc.Chrome(main_version=106)
        self.default_wait = WebDriverWait(self.driver, 30)

        #Twilio (SMS messaging)
        self.twilio_client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])


    def _sleep_for_random_time(self):
        """Create a list of range(lower_limit, upper_limit) and then random choice to sleep"""
        lower_limit = self.refresh_time_limits[0]
        upper_limit = self.refresh_time_limits[1]

        sleep_options = range(lower_limit, upper_limit)
        sleep_time = random.choice(sleep_options)

        print(f"Sleeping for {sleep_time} second(s)...")
        time.sleep(sleep_time)
        print("Sleep exited!")

    def _wait_for_url_load(self):
        """Wait for initial page load upon visiting"""
        try:
            url_is_good = self.default_wait.until(ec.url_to_be(self.event_url))

        except TimeoutException:
            print("Error trying to fetch event url.  Exiting...")
            sys.exit(0)

    def _click_continue_button(self):
        """Click 'continue' button on ticket options page"""
        continue_button_xpath = "//button[contains(text(), 'Continue')]"

        try:
            print("Attempting to click 'continue' button...")
            continue_button = self.default_wait.until(
                    ec.visibility_of_element_located((By.XPATH, continue_button_xpath)))
            self.driver.execute_script("arguments[0].click();", continue_button)
            print("'Continue' button clicked!")

        except TimeoutException:
            print("Unable to locate 'Continue' button element.  Refreshing page...")
            raise TimeoutException

    def _parse_and_check_prices(self, ticket_prices_list):
        refined_prices = []

        for px in ticket_prices_list:
            stripped_px = px.strip()

            if stripped_px == '' or stripped_px is None:
                pass

            else:
                normalized = stripped_px.replace('$', '') #strip '$'
                refined_prices.append(float(normalized))

        filtered_prices = [p for p in refined_prices if p <= self.max_price_threshold]

        #DEBUG
        print(f"Prefiltered prices: {refined_prices}")
        print(f"Filtered prices: {filtered_prices}")

        if len(filtered_prices) > 0:
            print("Tickets matching your criteria!")

            #Send SMS
            print("Sending SMS...")
            self.twilio_client.messages.create(
                body=f"{self.event_note} --> {filtered_prices}",
                from_=os.environ['TWILIO_FROM_NUMBER'],
                to=os.environ['TWILIO_TO_NUMBER']
            )
            print("SMS sent!")

    def _check_prices(self):
        """Locate ticket options and respective prices"""
        table_xpath = "//div[@class='resale-offer-selection']"

        print("Checking for ticket table...")

        try:
            ticket_table = self.default_wait.until(
                    ec.visibility_of_element_located((By.XPATH, table_xpath)))

        except TimeoutException:
            print("Unable to successfully locate the ticket table.  Exiting...")
            sys.exit(0)

        print("Ticket table found!")

        #This will return all tickets --> maybe just return the first one (will be lowest if sorted by lowest)
        print("Checking for ticket options...")
        ticket_options = ticket_table.find_elements(By.XPATH, ".//div[@class='resale-list-item']")
        print("Ticket options found!")

        ticket_prices_list = []

        for ticket in ticket_options:
            ticket_price = ticket.find_element(
                    By.XPATH, ".//div[@class='seat-header-bottom row']/div[3]/div/div/span")

            ticket_price = ticket_price.text

            ticket_prices_list.append(ticket_price)

        self._parse_and_check_prices(ticket_prices_list)

    def _refresh_current_page(self):
        """Lazy refresh"""
        print("Refreshing current page...")
        self.driver.refresh()
        time.sleep(5)
        print("Current page refreshed!")

    def _try_page_load_until_success(self):
        """Wait for successful click of 'continue' button"""
        self._wait_for_url_load()

        timeout = 0

        button_clicked = False

        while not button_clicked:
        
            try:
                self._click_continue_button()
                button_clicked = True

            except TimeoutException:
                time.sleep(5)
                self.driver.refresh()
                timeout += 1

                if timeout > 10:
                    print("Timeout reached in 'try_page_load_until_success'.  Exiting...")
                    sys.exit(0)

    def check_prices_for_all_of_eternity(self):
        #Visit ticket_url
        self.driver.get(self.event_url)

        self._try_page_load_until_success()
        
        #Loop
        should_run = True

        while should_run:
            self._check_prices()
            self._sleep_for_random_time()
            self._refresh_current_page()
            self._click_continue_button()


if __name__ == "__main__":
    EVENT_NOTE = "King Gizz Tickets"
    EVENT_URL = "https://tix.axs.com/rWWALgAAAACxketzAAAAAAAk%2fv%2f%2f%2fwD%2f%2f%2f%2f%2fBlJhZGl1cwD%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fw%3d%3d/shop/search?locale=en-US&aff=usaffsongkick"
    MAX_PRICE_THRESHOLD = 100
    REFRESH_TIME_LIMITS = [30, 120] #Lower / Upper limits in seconds

    listener = TicketListener(EVENT_NOTE, EVENT_URL, MAX_PRICE_THRESHOLD, REFRESH_TIME_LIMITS)

    try:
        listener.check_prices_for_all_of_eternity()

    except Exception as ex:
        listener.driver.quit()
        raise ex
