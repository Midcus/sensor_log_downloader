# Sensor Log Downloader

A lightweight Home Assistant add-on that allows you to **download the Home Assistant SQLite database** (`home-assistant_v2.db`) directly via the UI.


## How it works

The add-on exposes a simple web interface (Ingress) with a single **Download** button.  
When clicked, the database file is streamed directly from `/config/home-assistant_v2.db` to your browser.
