# SkydropHASS

This is the Skydrop integration for HomeAssistant!



## Currently supported features

* enable/disable controllers
* enable/disable zones
* start/stop watering on individual zones
* API data is rendered as attributes on sensors and switches if additional sensors are needed



## Installation

Install from HACS by adding this repository as a custom repository.



## Configuration

First, you'll need to request API access. From the [Skydrop API Docs](https://api.skydrop.com/docs/):

> ### Quick Steps Overview
> 
> * Create a Skydrop login @ [Skydrop Web Client](https://my.skydrop.com/) then contact api@skydrop.com to initiate a discussion on granting API access.
>
> * After API access has been granted, login to Skydrop's API service @ [Skydrop API](https://api.skydrop.com/)
>
> * Once logged in, create a new application
>
> * Use the new application settings to access the Skydrop API

Once your application is created, you have two options:



### 1. UI Configuration

From the HomeAssistant Configuration panel:

1. Select "Integrations".
1. Click the "+" (add new integration) button.
1. Search for "Skydrop" and select it.
1. Enter your Client Key/ID from your application on the Skydrop API Portal, as well as your Client Secret
1. Submit

After a moment, you should recieve the request to enter your "[grant code](#skydrop-grant-code)" in the notification pane of HomeAssistant.

### 2. YAML Configuration

In your `configuration.yaml` (or other if you have split your configuration into packages):

    skydrop:
        client_key: !secret <your client key/id from Skydrop>
        client_secret: !secret <your client secret from Skydrop>

After starting HomeAssistant, you should recieve the request to enter your "[grant code](#skydrop-grant-code)" in the notification pane of HomeAssistant.

### Skydrop Grant Code

Whether configuring from the UI or from YAML, you must enter your grant code.

This is achieved by following the steps of the [Authorize your Application](https://api.skydrop.com/docs/#authorizefromyourapplication) process of the Skydrop API documentation.

