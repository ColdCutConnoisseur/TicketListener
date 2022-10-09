# AXS Ticket Listener

Script hosted on GCP that continuously loops and checks event prices for provided event_url.  If ticket prices are below or equal to the max_price_threshold, an SMS is sent to the user.
<br/>

## Requirements
* Undetected Chromedriver -- browser automation
* Twilio -- helper client for sending SMS


## Config
There are two portions of configuration.  The first is setting environment variables for your Twilio account.  Set 'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM_NUMBER', and 'TWILIO_TO_NUMBER'.

The second are internal configuration variables set in __check_ticket_price.py__.

```EVENT_NOTE``` --> Some sort of description for the event to be sent in the SMS. <br/>
```EVENT_URL``` --> The URL for the event. <br/>
```MAX_PRICE_THRESHOLD``` --> If prices are lower than or equal to this price point, an alert will be sent. <br/>
```REFRESH_TIME_LIMITS``` --> Of type list and length 2.  First arg is the lower limit to wait between price checking refreshes and the second arg is the upper limit of this wait range (in seconds). <br/>

## Running
After both configurations are set, run ```python check_ticket_prices.py```.