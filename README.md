# secret-network
A cli tool to download images from the pixiv.

## Why secret-network?
Its name is came from the game `Last Origin`. At beginning, the purpose of this project was downloading illustrates from pixiv that related to `Last Origin`. Now it supports tag customization.

## How do I use?
If you launch it first time, it will create a `settings.json` file. You should edit it with correct format/information. After that, it will start to download images.

### username
Your pixiv account's username or email address to be used to authorization.

### password
Your pixiv account's password to be used to authorization.

### tags
Tags to be used to search and download images.

### max-page-image-count
Maximum allowed images for each artworks. This filter is useful to prevent it from downloading irrelevant images. Some artwork includes huge amount of images at once, and it can make it hard to filter images. This filter will do its job on that situations. Setting it to less than 1 will disable it.

## What is refresh token?
Pivix uses access token and refresh token for authorization. By using refresh token, we don't need to re-authenticate everytime. secret-network saves them for later use.

## Why I'm getting authorization notification emails from pixiv?
If you use it first time, pixiv will send an email to you to notify about authorizations. Next time it won't - it will use the saved refresh token. If you still getting emails, please check the `refresh_token.txt` file is created.
