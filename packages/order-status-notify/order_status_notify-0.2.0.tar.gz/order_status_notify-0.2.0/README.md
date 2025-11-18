# order_status_notify

A lightweight Django library for automatically sending **email notifications** to users whenever their order status changes 
---

## Features

- Simple integration with any Django project  
- Works with Django’s built-in `User` model  
- Sends rich HTML + plain-text emails  
- Handles exceptions gracefully  
- Fully compatible with **Django 3.2.x**

---

## Installation

You can install this library directly from PyPI (after upload):

##bash
pip install order_status_notify

## Usage

from order_status_notify import notify_status_change
notify_status_change(user, order)