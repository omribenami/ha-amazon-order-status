



**Amazon Order Status Integration for Home Assistant**

This fork keeps the integration documentation together with a Home Assistant Live Activity example for Amazon order tracking.

**Credits**

* Original integration author: `koconnorgit`
* Active maintained fork and 2.0 reference implementation: `ichwars/ha-amazon-order-status`

Reference:
* https://github.com/ichwars/ha-amazon-order-status

The Amazon Order Status integration allows Home Assistant to track your Amazon order emails and provide up-to-date information about delivery status. By connecting directly to your email via IMAP, the integration automatically detects when orders are received, shipped, and delivered, and provides quick links to the order tracking pages.

We obtain this information via email as Amazon does not publish any public API that could be used for order tracking. 

**Features**

* Automatically track Amazon order delivery status.
* Configurable polling interval to check for new order updates.
* Optional automatic marking of processed emails as read.
* Configurable retention for delivered orders.
* Fully customizable options via Home Assistant's UI.

**Installation**

*Custom HACS Repository*

Click here: 

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=koconnorgit&repository=ha-amazon-order-status&category=integration)

OR

   * Open HACS (Home Assistant Community Store) in Home Assistant
   * Click the three dots menu (top right) and select Custom repositories
   * Put koconnorgit/ha-amazon-order-status for Repository, and Integration for Category, then click "Add".
   * Click "Explore and Download Repositories" in the lower right.  Search for "Amazon Order Status" and install
   * Restart Home Assistant




*Manual*

Download the Integration: https://github.com/koconnorgit/ha-amazon-order-status/releases/latest

Place the amazon_order_status folder in your Home Assistant custom_components directory:
* Home Assistant Directory/custom_components/amazon_order_status/

*Make sure it contains:*
```
* translations/en.json
* __init\__.py
* config_flow.py
* coordinator.py
* const.py
* options_flow.py
* manifest.json
* sensor.py
* services.yaml
```

****Restart Home Assistant to detect the new integration.****

**After the install, you must add the Integration:**

* Go to Settings → Devices & Services → Add Integration.

* Search for Amazon Order Status.

* Enter your IMAP server details, username, and password.

Configuration Options

* *All options can be changed through the Integration Options dialog after adding the integration.*

Option - Description

* ```delivered_retention_days```: 	How long Home Assistant should keep a record of delivered items. Default: 30 days.
* ```update_interval```: 	How often Home Assistant should check your Amazon emails for order updates, in minutes. Default: 5 minutes.
* ```mark_as_read```: 	If enabled, emails containing Amazon delivery updates will be automatically marked as read after processing. Default: True.
* ```imap_folder```: Optional - Specify a folder to search for emails rather than the default INBOX.  If left blank, defaults to searching INBOX.  If a folder is specified (Either "Folder Name" or "INBOX/Folder Name" depending on provider) email searches will be limited to that folder. 

Upon initial installation, this integration will scan the previous 14 days worth of emails for Amazon order emails.  Depending on the volume of email in the inbox, this initial scan could take anywhere from a few seconds to a few minutes.  During this time, the integration dialog will display a spinning icon.  You can check the progress of the initial data load by looking at the console of your home assistant instance for debug log messages.  Once the initial data load is complete, the integration will keep track of its last-scanned date/time and perform only rapid scans of the messages recieved since the last check.

**Notes**

***Security Warning - Your IMAP password is stored in the .storage/core_config_entries along with, likely, many other secret values.  This is a cleartext file.  HA, by necessity, must store all secret data in such a way that, if your server is breached at the filesystem level, your secrets could be exposed.  You should be confident in the security of your HA installation (not exposed to the internet, no unencrypted backups of the .storage directory) before using this or any integration that asks for secret values.***

*Note that some email providers (Google, most notably) require the use of a passcode (Google calls it an "App Password") for some third party applications to access your inbox, rather than your gmail/google workspace credentials.  See here for more information on how to create an app password in Google: https://support.google.com/accounts/answer/185833?hl=en*

* Adjust ```update_interval``` depending on how frequently you want to poll your inbox. Setting this too low may result in unnecessary server load.

* Option ```delivered_retention_days``` helps prevent the history from growing too large over time.

Once configured, this integration creates 5 new sensors:

* ```sensor.amazon_orders_delivered``` 
* ```sensor.amazon_orders_out_for_delivery```
* ```sensor.amazon_orders_ordered```
* ```sensor.amazon_orders_shipped```
* ```sensor.amazon_orders_last_updated```

The ```sensor.amazon_orders_last_updated``` sensor contains a datestamp indicating the last email check.

The remaining sensors contain the following attributes :
* ```order_id``` (Amazon Order ID)
* ```subject``` (contains a truncated order name taken from the subject line of the email)
* ```updated``` (send date of the email - indicates the date/time of the most recent order update.  This will be an iso date stamp, which can be reformatted via templates in any way you choose. Some examples are below.)
* ```tracking_url``` (provides the link back to the amazon order tracking page for that order.

...these can be parsed though markdown or other methods to display the Order dates, tracking links, etc. on the dashboard.    Here is an example markdown card to display order information from the ```sensor.amazon_orders_ordered``` sensor:



```
Amazon Orders – Ordered
{% set orders = state_attr('sensor.amazon_orders_ordered', 'orders') or [] %}
{% for data in orders %}
- **Item:** {{ data.subject }}
  - Updated: {{ data.updated | as_timestamp | timestamp_custom('%b %d at %I:%M %p') }}
  - [Track Package]({{ data.tracking_url }})
{% else %}
_No orders in this state._
{% endfor %}
```

### Example: Home Assistant Companion Live Activity for iPhone

If you use the Home Assistant Companion app on iPhone, you can map these Amazon order sensors into a per-order Live Activity. The example below starts one Live Activity card for a single order and reuses the order ID as the notification tag.

```yaml
sequence:
  - action: notify.mobile_app_omri_s_phone
    data:
      title: Amazon Package
      message: "Out for delivery · {{ order.subject }}"
      data:
        tag: "amazon_order_{{ order.order_id | replace('-', '_') }}"
        live_update: true
        progress: 3
        progress_max: 4
        critical_text: "Out for delivery · #{{ order.order_id[-4:] }}"
        notification_icon: mdi:truck-fast-outline
        notification_icon_color: '#FF9800'
        color: '#FF9800'
        progress_bar_color: '#FF9800'
        url: /lovelace/0
```

To clear the Live Activity after delivery:

```yaml
sequence:
  - action: notify.mobile_app_omri_s_phone
    data:
      message: clear_notification
      data:
        tag: "amazon_order_{{ order.order_id | replace('-', '_') }}"
```

Notes:
* Requires the Home Assistant Companion app on the target iPhone.
* `live_update: true` enables Live Activity updates instead of one-off notifications.
* Reusing the same `tag` lets later automations update the same order card as it moves from Ordered → Shipped → Out for delivery → Delivered.

Occasionally Amazon ships packages through 3d party couriers and a "Delivered" email is never sent (or drastically delayed).  To account for this, you can manually delete orders from the database.  You can pass the order id to ```amazon_order_status.purge_order``` through dev tools, although it's easier to create a helper and script, and pass values to the script via a button card.

Create a Helper: 
* Go to Settings > Devices & Services > Helpers
* Click Create Helper
* Select "Text"
* Name: amazon_order_purge_id
* Click Create

Then create a script:
* Go to Settings > Automations & scenes > Scripts
* Click Create script
* Click Create new script
* Click the 3 dots in the upper right > Edit in YAML
* Paste the following:
```
sequence:
  - data_template:
      order_id: "{{ states('input_text.amazon_order_purge_id') }}"
    action: amazon_order_status.purge_order
alias: Purge Amazon Order
description: ""
```
* Click Save.

You can then leverage the helper and script in a dashboard to purge orders by order ID.  Here's a sample set of buttons:
```
  - type: horizontal-stack
    cards:
      - type: entities
        entities:
          - entity: input_text.amazon_order_purge_id
            name: Order ID to purge
            secondary_info: none
      - show_name: true
        show_icon: true
        type: button
        name: Purge order
        icon: mdi:delete
        tap_action:
          action: call-service
          service: script.turn_on
          target:
            entity_id: script.purge_amazon_order
        hold_action:
          action: none
        show_state: false
        icon_height: 20px
```

Here is a complete Mushroom Card template stack, including more attractive widgets and UI for pasting order IDs and purging orders as needed:
```
type: vertical-stack
cards:
  - type: conditional
    conditions:
      - entity: sensor.amazon_orders_ordered
        state_not: "0"
    card:
      type: markdown
      title: 🟡 Ordered
      content: >
        {% for o in state_attr('sensor.amazon_orders_ordered', 'orders') or []
        %} • **{{ o.subject }}**  Updated: {{ o.updated | as_timestamp |
        timestamp_custom('%b %d at %I:%M %p') }} [Open]({{ o.tracking_url }})
        Order ID: {{ o.order_id }} {{ '\n' }}{% else %} _None_ {% endfor %}
  - type: conditional
    conditions:
      - entity: sensor.amazon_orders_shipped
        state_not: "0"
    card:
      type: markdown
      title: 🚚 Shipped
      content: >
        {% for o in state_attr('sensor.amazon_orders_shipped', 'orders') or []
        %} • **{{ o.subject }}**   Updated: {{o.updated | as_timestamp |
        timestamp_custom('%b %d at %I:%M %p') }} [Track]({{ o.tracking_url }})
        Order ID: {{ o.order_id }} {{ '\n' }} {% else %} _None_ {% endfor %}
  - type: conditional
    conditions:
      - entity: sensor.amazon_orders_out_for_delivery
        state_not: "0"
    card:
      type: markdown
      title: 🚚 Out for Delivery
      content: >
        {% for o in state_attr('sensor.amazon_orders_out_for_delivery',
        'orders') or [] %} • **{{ o.subject }}**   Updated: {{o.updated |
        as_timestamp | timestamp_custom('%b %d at %I:%M %p') }} [Track]({{
        o.tracking_url }}) Order ID: {{ o.order_id }} {{ '\n' }} {% else %}
        _None_ {% endfor %}
  - type: conditional
    conditions:
      - entity: sensor.amazon_orders_delivered
        state_not: "0"
    card:
      type: markdown
      title: 📬 Delivered
      content: >
        {% for o in state_attr('sensor.amazon_orders_delivered', 'orders') or []
        %} • **{{ o.subject }}** Updated: {{o.updated | as_timestamp |
        timestamp_custom('%b %d at %I:%M %p') }} [Open]({{ o.tracking_url }})
        Order ID: {{ o.order_id }} {{ '\n' }} {% else %} _None_ {% endfor %}
  - type: horizontal-stack
    cards:
      - type: entities
        entities:
          - entity: input_text.amazon_order_purge_id
            name: Order ID to purge
            secondary_info: none
      - show_name: true
        show_icon: true
        type: button
        name: Purge order
        icon: mdi:delete
        tap_action:
          action: call-service
          service: script.turn_on
          target:
            entity_id: script.purge_amazon_order
        hold_action:
          action: none
        show_state: false
        icon_height: 20px


```
