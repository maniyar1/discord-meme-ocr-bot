# A Meme OCRing Bot for Discord
## Intro
This bot uses OCR to index images and make them searchable to reference later.
It can be used for any images but I've focused on making sure it works for memes.
To use, simply put your bot token on the last line in bot.py, for example:
```python
...

client.run("OTE0MzEyNjA2OTIyMTk5MTIx.YaLN-A.HAujz3wYde0hu2T3oWmanHDXOU0")
```
(This bot API token does not work)

## Privacy
Only things stored to disk are the results of the OCR query, a link to the message, and a link to the meme.
These links both will return 404s if the message is deleted, and author information is not saved.
Memes are downloaded and used temporarily to run OCR but are never stored to disk.
Each server can only search its own memes.
