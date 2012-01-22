# django-cloudflare

## Overview

This package makes it easy for Django sites running behind [CloudFlare](https://www.cloudflare.com/) to report spam comments through the Django Admin Interface.

>> This has only been tested with the standard [Django comments framework](https://docs.djangoproject.com/en/dev/ref/contrib/comments/).

Two modules are included:

* *middleware*: adjusts the request metadata so Django uses the end-user's IP address and not CloudFlare's
* *admin*: adds a _Report spam to CloudFlare_ action to the Django Administration Interface for Comments

## Installation

>> I'm assuming below that you drop this directly into a 'cloudflare' directory in your project. I know this isn't really cool and will (maybe) take a look at packaging this better later.

Adjust your project's `settings.py` as follows:

1. Add the middleware to `MIDDLEWARE_CLASSES`:
    
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        # ...
        'yourproject.cloudflare.middleware.CFMiddleware', # <- This is it!
    )

2. Add `cloudflare` to your `INSTALLED_APPS`:
    
    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.comments',
        # ...
        'yourproject.cloudflare' # <- This is it!>
    )

3. Add your CloudFlare account credentials
    
    # CloudFlare credentials for reporting spam
    CLOUDFLARE_API_KEY = '08c64e15db52f0e9b4fe3418e44c0b4c6dbba9334'
    CLOUDFLARE_EMAIL = 'you@example.com'

>> I'm also assuming you have a logger configured at the project level and am hooking into that.

## Usage

1. Review comments in the Django Admin Interface.
2. Checkmark the ones you want to report to CloudFlare.
3. Select the *Report spam to CloudFlare* action and click *Go*.
4. If successful, a message will flash indicating which comments have been reported (by ID).
5. You can then proceed to delete or remove these using the standard comments actions.