from redvid import Downloader

reddit = Downloader()
reddit.url = 'https://www.reddit.com/r/nextfuckinglevel/comments/1ovbrf0/a_drunk_man_got_lost_and_his_bull_found_him_then/'

reddit.check()
if reddit.size <= 5 * (1 << 20):
    reddit.download()
else:
    print('Size > 5 MB')
