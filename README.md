# BusBookingService
Service for booking tickets for buses and minibuses for forum events written on Django framework


# Database documents
## Driver
* **Phone**: standardized string (+0 (000) 000-00-00)
* **Email:**  standardized string (aaa@bbb.cc) 
* **Password:** hashed string
* **Name:** string
* **uploaded_docs_url:** string
* **docs_verified:** bool
* **Passport series:** string
* **Passport number:** string
***
## User
* **Phone**: standardized string (+0 (000) 000-00-00)
* **Email:**  standardized string (aaa@bbb.cc) 
* **Password:** hashed string
* **Name:** string
* **Passport series:** string
* **Passport number:** string
***
## Bus
* **Brand:** string
* **Color:** string
* **License plate:** string
* **Sitting scheme:** ПРОДУМАТЬ



## Route
* **Name:** string
* **Company:** string (MAY BE BLANK)
* **Driver:** string
* **Bus:** string
* **Stops:** array of stops

## Company
* **Email:** string
* **Password:** string
* **Name:** string


## Ticket