#!/usr/bin/env python3
import requests
import sqlite3 as db


class BestReddit(object):

    def __init__(self):
        self.conn = None
        self.c = None
        self.old_ids = []

        self.init_db()
        self.saved_ids = self.get_saved()


    def init_db(self):
        self.conn = db.connect('posts.db')
        self.conn.row_factory = db.Row

        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS posts 
                            (
                                title TEXT, 
                                url TEXT, 
                                subr TEXT, 
                                score INTEGER, 
                                id TEXT, 
                                ups INTEGER, 
                                downs INTEGER,
                                comments TEXT
                            )''')


    def get_new_posts(self):

        headers = {
            'User-agent': 'Best_of_Reddit'
        }
        r = requests.get('https://reddit.com/r/all.json', headers=headers)

        posts = r.json()['data']['children']

        postData = []
        for post in posts:
            title = post['data']['title']
            url   = post['data']['url']
            subr  = post['data']['subreddit']
            score = post['data']['score']
            id    = post['data']['id']
            downs = post['data']['downs']
            ups   = post['data']['ups']
            comments = post['data']['permalink']

            if ( (score >= 10000) or (downs > ups) ) and ( id not in self.saved_ids ):
                postData.append((title, url, subr, score, id, ups, downs, comments))

        return postData

    def get_saved(self):
        self.c.execute("SELECT id FROM posts")
        return list(map(lambda x: x['id'], self.c.fetchall()))

    def save(self, postData):
        self.c.executemany("INSERT INTO posts VALUES (?,?,?,?,?,?,?,?)", postData)
        self.conn.commit()

    def finish(self):
        self.conn.close()

    def main(self):
        new_posts = self.get_new_posts()
        self.save(new_posts)
        self.finish()


if __name__ == '__main__':
    app = BestReddit()
    app.main()