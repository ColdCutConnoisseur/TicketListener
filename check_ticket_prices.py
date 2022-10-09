"""Main module for listening for new tickets and notifying user if under price_threshold"""

import sys
import time
import random

import undetected_chromedriver as uc
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchElementException,
                                        ElementNotInteractableException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class TicketListener:
    def __init__(self, event_note, event_url, refresh_time_limits):
        self.event_note = event_note
        self.event_url = event_url
        self.refresh_time_limits = refresh_time_limits

        #Create driver
        self.driver = uc.Chrome()
        self.default_wait = WebDriverWait(self.driver, 30)

        #Twilio (SMS messaging)


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
            print("Error trying to fetch eventn url.  Exiting...")
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
            print("Unable to located 'Continue' button element.  Exiting...")
            sys.exit(0)

    def _check_prices(self):
        """Locate ticket options and respective prices"""
        table_xpath = "//div[@class='resale-offer-selection']"

        print("Checking for ticket table...")

        try:
            ticket_table = self.default_wait.untill(
                    ec.visibility_of_element_located((By.XPATH, table_xpath)))

        except TimeoutException:
            print("Unable to successfully locate the ticket table.  Exiting...")
            sys.exit(0)

        print("Ticket table found!")

        #This will return all tickets --> maybe just return the first one (will be lowest if sorted by lowest)
        print("Checking for ticket options...")
        ticket_options = ticket_table.find_elements(By.XPATH, ".//div[@class='resale-list-item']")
        print("Ticket options found!")

        for ticket in ticket_options:
            ticket_price = ticket.find_element(
                    By.XPATH, ".//div[@class='seat-header-bottom row']/div[3]/div/div/span").text()

            print(ticket_price)

    def _refresh_current_page(self):
        """Lazy refresh"""
        print("Refreshing current page...")
        self.driver.refresh()
        time.sleep(5)
        print("Current page refreshed!")

    def check_prices_for_all_of_eternity(self):
        #Visit ticket_url
        self.driver.get(self.event_url)

        self._wait_for_url_load()
        
        self._click_continue_button()
        
        #Loop
        should_run = True

        while should_run:
            self._check_prices()
            self._sleep_for_random_time()
            self._refresh_current_page()


if __name__ == "__main__":
    EVENT_NOTE = "King Gizz Tickets"
    EVENT_URL = "https://tix.axs.com/rWWALgAAAACxketzAAAAAAAk%2fv%2f%2f%2fwD%2f%2f%2f%2f%2fBlJhZGl1cwD%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fw%3d%3d/shop/search?locale=en-US&aff=usaffsongkick"
    REFRESH_TIME_LIMITS = [30, 120] #Lower / Upper limits in seconds

    listener = TicketListener(EVENT_NOTE, EVENT_URL, REFRESH_TIME_LIMITS)

    listener.check_prices_for_all_of_eternity()