# pnutty
# Copyright (C) 2024  Morgan McMillian

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pnutpy
import sys
import os
import tomlkit
import cmd2
import threading
import logging
import time
import json
import requests

from pathlib import Path
from colorama import Fore, Style
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosed

PNUT_CLIENT_ID = "qx87SsGu3NZINwAUxEk1bC1TICzupv5e"
PNUT_AUTH_URL = "https://pnut.io/oauth/authenticate"
PNUT_REDIRECT = "urn:ietf:wg:oauth:2.0:oob"
PNUT_SCOPES = "basic,stream,write_post,follow,presence,messages:io.pnut.core.chat,messages:io.pnut.core.pm,files"
PNUT_WS_URL = "wss://stream.pnut.io/v1/user?access_token="
PNUT_API_URL = "https://api.pnut.io/v1"
PNUT_POST_STREAMS_UNIFIED = "/posts/streams/unified"
PNUT_POST_STREAMS_PERSONAL = "/posts/streams/me"
PNUT_POST_STREAMS_GLOBAL = "/posts/streams/global"
PNUT_POSTS_URL = "https://posts.pnut.io/"

REPLY_ONE = 1
REPLY_ALL = 2
REPLY_CC = 3

_shutdown = threading.Event()
_connected = threading.Event()

class PnutStream:

    def __init__(self, config):
        self.config = config
        self.token = config.get('token', '')
        self.show_links = config.get('show_links', False)
        self.show_json = config.get('show_json', False)
        self.timeline = config.get('timeline', 'unified')
        self.pnut_api = pnutpy.API.build_api(access_token=self.token)
        self.websocket = None

    def on_open(self, ws):
        logging.debug("--- starting stream connection with pnut.io ---")

        def run(*args):
            while not _shutdown.is_set():
                ws.send(".")
                time.sleep(5)
            logging.debug("*** terminating stream ***")

        t = threading.Thread(target=run)
        t.start()

    def start(self):
        self.websocket = connect(PNUT_WS_URL + self.token)
        self.on_open(self.websocket)
        for message in self.websocket:
            msg = json.loads(message)
            logging.debug(msg)
            if not _connected.is_set() and 'connection_id' in msg['meta']:
                self.subscribe(msg['meta']['connection_id'])
            else:
                if 'data' in msg:
                    self.parse_data(msg)

    def subscribe(self, connection_id):
        # TODO: Replace with with pnutpy once it's updated
        if self.timeline == 'unified':
            url = PNUT_API_URL + PNUT_POST_STREAMS_UNIFIED
        elif self.timeline == 'personal':
            url = PNUT_API_URL + PNUT_POST_STREAMS_PERSONAL
        else:
            return

        url += "?connection_id=" + connection_id + "&include_post_raw=1"
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            _connected.set()
            self.parse_data(r.json())

    def parse_data(self, data):
        if 'is_deleted' in data['meta']:
            is_deleted = True
        else:
            is_deleted = False
        for item in reversed(data['data']):
            post = pnutpy.models.Post.from_response_data(item)
            if 'content' in post:
                self.print_post(post, is_deleted)

    def print_post(self, post, is_deleted=False):
        text = f"{Fore.YELLOW}{post.id}{Fore.RESET}: "
        if 'repost_of' in post:
            text += f"<{Style.BRIGHT}{Fore.CYAN}{post.user.username}{Style.RESET_ALL}> reposted >> "
            post = post.repost_of
        text += f"<{Style.BRIGHT}{Fore.CYAN}{post.user.username}{Style.RESET_ALL}>"
        if is_deleted:
            text += "\x1b[9m"
            text += f" {post.content.text} "
            text += "\x1b[29m"
        else:
            text += f" {post.content.text} "
        if int(post.thread_id) != post.id:
            text += f"💬"
        text += f"{Fore.LIGHTBLACK_EX}[via {post.source.name}]{Style.RESET_ALL}"
        if self.show_json:
            text += f"{post}\n"
        if "raw" in post and "io.pnut.core.oembed" in post.raw:
            embeds = post.raw["io.pnut.core.oembed"]
            for item in embeds:
                if item["type"] == "photo":
                    text += f"\n🖼️ "
                elif item["type"] == "video":
                    text += f"\n📽️ "
                text += f"{item['embeddable_url']}"
        if self.show_links:
            text += f"\n{Fore.LIGHTBLACK_EX}{PNUT_POSTS_URL}{post.id}{Style.RESET_ALL}"
        print(text)

class NuttyShell(cmd2.Cmd):
    prompt = "pnutty% "

    def __init__(self, config):
        super().__init__()
        self.allow_cli_args = False # defaults to True
        self.config = config
        self.stream = PnutStream(config)
        self.debug = config.get('debug', False)
        self.token = config.get('token')
        self.timeline = config.get('timeline', 'unified')
        self.add_settable(
            cmd2.Settable('timeline', str,
                'Set timeline to [unified, or personal]',
                self, choices=['unified', 'personal'],
                onchange_cb=self._onchange_setting))
        self.feed = config.get('feed', True)
        self.add_settable(
            cmd2.Settable('feed', bool, 'Enable live feed',
                self, onchange_cb=self._onchange_setting))
        self.show_links = config.get('show_links', False)
        self.add_settable(
            cmd2.Settable('show_links', bool, 'Show link to post',
                self, onchange_cb=self._onchange_setting))
        self.show_json = config.get('show_json', False)
        self.add_settable(
            cmd2.Settable('show_json', bool, 'Show raw post json',
                self, onchange_cb=self._onchange_setting))
        self.register_preloop_hook(self.startup)
        self.register_postloop_hook(self.shutdown)

    def do_login(self, statement):
        '''Log in to pnut.io'''
        self.shutdown()
        reply = "Visit the following URL to authorize with pnut.io and paste "
        reply += "the token here.\n\n"
        reply += f"{PNUT_AUTH_URL}?client_id={PNUT_CLIENT_ID}"
        reply += f"&redirect_uri={PNUT_REDIRECT}&scope={PNUT_SCOPES}"
        reply += f"&response_type=token\n"
        self.poutput(reply)
        token = input("TOKEN: ")
        if self.check_auth(token):
            self.token = token
            self.timeline = 'unified'
            self.stream = PnutStream(self.config)
            self.startup()

    def do_logout(self, statement):
        '''Log out of pnut.io'''
        self.shutdown()
        url = PNUT_API_URL + '/token'
        headers = {'Authorization': 'Bearer ' + self.token}
        r = requests.delete(url, headers=headers)
        logging.debug(r.status_code)
        if r.status_code == 200:
            self.token = ""
            self.config['token'] = ""
            self.config['username'] = ""
            save_config(self.config)

    def do_again(self, statement):
        '''Replay the set feed'''
        self.get_timeline(self.timeline)

    def do_global(self, statement):
        '''Show most recent posts from the Global stream'''
        self.get_timeline('global')

    def do_unified(self, statement):
        '''Show most recent posts from your Unified stream'''
        self.get_timeline('unified')

    def do_personal(self, statement):
        '''Show most recent posts from your Personal stream'''
        self.get_timeline('personal')

    def do_replies(self, statement):
        '''Show replies (mentions)'''
        self.get_replies('me')

    show_thread_args = cmd2.Cmd2ArgumentParser()
    show_thread_args.add_argument('post_id', help='ID of the post to show.')
    @cmd2.with_argparser(show_thread_args)
    def do_show_thread(self, args):
        self.get_thread(args.post_id)

    show_post_args = cmd2.Cmd2ArgumentParser()
    show_post_args.add_argument('post_id', help='ID of the post to show.')
    @cmd2.with_argparser(show_post_args)
    def do_show_post(self, args):
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            post, meta = pnut_api.get_post(args.post_id, include_post_raw=1)
            self.stream.print_post(post)

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    post_args = cmd2.Cmd2ArgumentParser()
    post_args.add_argument('text', type=str, nargs='+',
        help='text of message you wish to post.')
    @cmd2.with_argparser(post_args)
    def do_post(self, args):
        """Post to pnut.io"""
        text = ' '.join(args.text)
        self.send_post(text)

    reply_args = cmd2.Cmd2ArgumentParser()
    reply_args.add_argument('post_id', help='ID of the post to reply to.')
    reply_args.add_argument('text', nargs='+', help='text of your reply.')
    @cmd2.with_argparser(reply_args)
    def do_reply(self, args):
        '''Reply to a post'''
        text = ' '.join(args.text)
        self.send_post(text, args.post_id, REPLY_ONE)

    replyg_args = cmd2.Cmd2ArgumentParser()
    replyg_args.add_argument('post_id', help='ID of the post to reply to.')
    replyg_args.add_argument('text', nargs='+', help='text of your reply.')
    @cmd2.with_argparser(replyg_args)
    def do_replyg(self, args):
        '''Reply globally to a post'''
        text = ' '.join(args.text)
        self.send_post(text, args.post_id)

    replycc_args = cmd2.Cmd2ArgumentParser()
    replycc_args.add_argument('post_id', help='ID of the post to reply to.')
    replycc_args.add_argument('text', nargs='+', help='text of your reply.')
    @cmd2.with_argparser(replycc_args)
    def do_replycc(self, args):
        '''Reply to a post and cc others'''
        text = ' '.join(args.text)
        self.send_post(text, args.post_id, REPLY_CC)

    replyall_args = cmd2.Cmd2ArgumentParser()
    replyall_args.add_argument('post_id', help='ID of the post to reply to.')
    replyall_args.add_argument('text', nargs='+', help='text of your reply.')
    @cmd2.with_argparser(replyall_args)
    def do_replyall(self, args):
        '''Reply to all of a post'''
        text = ' '.join(args.text)
        self.send_post(text, args.post_id, REPLY_ALL)

    browse_args = cmd2.Cmd2ArgumentParser()
    browse_args.add_argument('post_id', nargs='+',
        help='ID of the post to open.')
    @cmd2.with_argparser(browse_args)
    def do_browse(self, args):
        '''Open a post in the web browser'''
        for post_id in args.post_id:
            url = PNUT_POSTS_URL + post_id
            self.poutput(url)

    bookmark_args = cmd2.Cmd2ArgumentParser()
    bookmark_args.add_argument('post_id', help='ID of the post to bookmark.')
    @cmd2.with_argparser(bookmark_args)
    def do_bookmark(self, args):
        '''Bookmark a post'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            post, meta = pnut_api.bookmark_post(args.post_id)
            self.poutput(
                f"* bookmarked post {Fore.YELLOW}{post['id']}{Fore.RESET}")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    unbookmark_args = cmd2.Cmd2ArgumentParser()
    unbookmark_args.add_argument('post_id',
        help='ID of the post to unbookmark.')
    @cmd2.with_argparser(unbookmark_args)
    def do_unbookmark(self, args):
        '''Remove a bookmark'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            post, meta = pnut_api.bookmark_post(args.post_id)
            self.poutput(
                f"* removed bookmark post {Fore.YELLOW}{post['id']}{Fore.RESET}")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    repost_args = cmd2.Cmd2ArgumentParser()
    repost_args.add_argument('post_id', help='ID of the post to repost.')
    @cmd2.with_argparser(repost_args)
    def do_repost(self, args):
        '''Repost a post'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            post, meta = pnut_api.repost_post(args.post_id)
            self.poutput(
                f"* reposted {Fore.YELLOW}{post['id']}{Fore.RESET}")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    unrepost_args = cmd2.Cmd2ArgumentParser()
    unrepost_args.add_argument('post_id', help='ID of the post to unrepost.')
    @cmd2.with_argparser(unrepost_args)
    def do_unrepost(self, args):
        '''Repost a post'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            post, meta = pnut_api.unrepost_post(args.post_id)
            self.poutput(
                f"* unreposted {Fore.YELLOW}{post['id']}{Fore.RESET}")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    user_args = cmd2.Cmd2ArgumentParser()
    user_args.add_argument('user', help='username to follow.')
    @cmd2.with_argparser(user_args)
    def do_follow(self, args):
        '''Follow a user'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            int(args.user)

        except ValueError:
            if not args.user.startswith("@"):
                args.user = "@" + args.user

        try:
            user, meta = pnut_api.follow_user(args.user)
            self.poutput(f"* following @{user.username}")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    user_args = cmd2.Cmd2ArgumentParser()
    user_args.add_argument('user', help='username to unfollow.')
    @cmd2.with_argparser(user_args)
    def do_unfollow(self, args):
        '''Unfollow a user'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            int(args.user)

        except ValueError:
            if not args.user.startswith("@"):
                args.user = "@" + args.user

        try:
            user, meta = pnut_api.unfollow_user(args.user)
            self.poutput(f"* no longer following @{user.username}")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    user_args = cmd2.Cmd2ArgumentParser()
    user_args.add_argument('user', help='username to mute.')
    @cmd2.with_argparser(user_args)
    def do_mute(self, args):
        '''Mute a user'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            int(args.user)

        except ValueError:
            if not args.user.startswith("@"):
                args.user = "@" + args.user

        try:
            user, meta = pnut_api.mute_user(args.user)
            self.poutput(f"* @{user.username} has been muted")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    user_args = cmd2.Cmd2ArgumentParser()
    user_args.add_argument('user', help='username to unmute.')
    @cmd2.with_argparser(user_args)
    def do_unmute(self, args):
        '''Unmute a user'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            int(args.user)

        except ValueError:
            if not args.user.startswith("@"):
                args.user = "@" + args.user

        try:
            user, meta = pnut_api.unmute_user(args.user)
            self.poutput(f"* @{user.username} has been unmuted")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    def do_muted(self, args):
        '''List users you have muted'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            pager = True
            before_id = None
            while pager:
                users, meta = pnut_api.users_muted_users("me", before_id=before_id, count=200)

                for user in users:
                    text = f"{Style.BRIGHT}{Fore.CYAN}@{user.username}{Style.RESET_ALL} "
                    text += f"{Fore.LIGHTBLACK_EX}[{user.id}]{Style.RESET_ALL}"
                    self.poutput(text)

                if meta.more:
                    before_id=meta.min_id
                pager = meta.more

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    user_args = cmd2.Cmd2ArgumentParser()
    user_args.add_argument('user', help='username to block.')
    @cmd2.with_argparser(user_args)
    def do_block(self, args):
        '''Block a user'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            int(args.user)

        except ValueError:
            if not args.user.startswith("@"):
                args.user = "@" + args.user

        try:
            user, meta = pnut_api.block_user(args.user)
            self.poutput(f"* @{user.username} has been blocked")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    user_args = cmd2.Cmd2ArgumentParser()
    user_args.add_argument('user', help='username to unblock.')
    @cmd2.with_argparser(user_args)
    def do_unblock(self, args):
        '''Unblock a user'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            int(args.user)

        except ValueError:
            if not args.user.startswith("@"):
                args.user = "@" + args.user

        try:
            user, meta = pnut_api.unblock_user(args.user)
            self.poutput(f"* @{user.username} has been unblocked")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    def do_blocked(self, args):
        '''List users you have blocked'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            pager = True
            before_id = None
            while pager:
                users, meta = pnut_api.users_blocked_users("me", before_id=before_id, count=200)

                for user in users:
                    text = f"{Style.BRIGHT}{Fore.CYAN}@{user.username}{Style.RESET_ALL} "
                    text += f"{Fore.LIGHTBLACK_EX}[{user.id}]{Style.RESET_ALL}"
                    self.poutput(text)

                if meta.more:
                    before_id=meta.min_id
                pager = meta.more

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    def do_following(self, args):
        '''List users you are following'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            pager = True
            before_id = None
            while pager:
                users, meta = pnut_api.users_following("me", before_id=before_id, count=200)

                for user in users:
                    text = f"{Style.BRIGHT}{Fore.CYAN}@{user.username}{Style.RESET_ALL} "
                    text += f"{Fore.LIGHTBLACK_EX}[{user.id}]{Style.RESET_ALL}"
                    self.poutput(text)

                if meta.more:
                    before_id=meta.min_id
                pager = meta.more

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    def do_followers(self, args):
        '''List users who follow you'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            pager = True
            before_id = None
            while pager:
                users, meta = pnut_api.users_followers("me", before_id=before_id, count=200)

                for user in users:
                    text = f"{Style.BRIGHT}{Fore.CYAN}@{user.username}{Style.RESET_ALL} "
                    text += f"{Fore.LIGHTBLACK_EX}[{user.id}]{Style.RESET_ALL}"
                    self.poutput(text)

                if meta.more:
                    before_id=meta.min_id
                pager = meta.more

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    user_args = cmd2.Cmd2ArgumentParser()
    user_args.add_argument('user', help='username of profile to view.')
    @cmd2.with_argparser(user_args)
    def do_user(self, args):
        '''View a user profile'''
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            int(args.user)

        except ValueError:
            if not args.user.startswith("@"):
                args.user = "@" + args.user

        try:
            user, meta = pnut_api.get_user(args.user)
            self.print_user(user)

        except pnutpy.errors.PnutMissing:
            self.poutput(f"{args.user} not found.")

    def print_user(self, user):
        text = f"{Style.BRIGHT}{Fore.CYAN}@{user.username}{Style.RESET_ALL} "
        text += f"{Fore.LIGHTBLACK_EX}[{user.id}]{Style.RESET_ALL}\n"
        if 'name' in user:
            text += f"{Style.BRIGHT}{user.name}{Style.RESET_ALL}\n"
        if 'verified' in user:
            text += f"✅{user.verified.domain}\n"
        if 'content' in user:
            if 'text' in user.content:
                text += f"{user.content.text}\n"
        if 'you_follow' in user and user.you_follow:
            text += f"{Fore.YELLOW}[you_follow]{Style.RESET_ALL}"
        if 'follows_you' in user and user.follows_you:
            text += f"{Fore.YELLOW}[follows_you]{Style.RESET_ALL}"
        if 'you_muted' in user and user.you_muted:
            text += f"{Fore.RED}[you_muted]{Style.RESET_ALL}"
        if 'you_blocked' in user and user.you_blocked:
            text += f"{Fore.RED}[you_blocked]{Style.RESET_ALL}"
        # text += "\n"
        self.poutput(text)

    def startup(self) -> None:
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
        if self.feed and len(self.token) > 0:
            if self.check_auth(self.token):
                self.poutput(f"{Fore.LIGHTBLACK_EX}Opening connection...{Style.RESET_ALL}")
                t = threading.Thread(target=self.stream.start)
                t.start()

    def shutdown(self) -> None:
        self.poutput(f"{Fore.LIGHTBLACK_EX}Closing connection...{Style.RESET_ALL}")
        _shutdown.set()
        if _connected.is_set():
            self.stream.websocket.close()
            time.sleep(6)
        _shutdown.clear()
        _connected.clear()

    def check_auth(self, token):
        pnut_api = pnutpy.API.build_api(access_token=token)

        try:
            pnut_user, meta = pnut_api.get_user("me")
            self.config['username'] = pnut_user.username
            self.config['token'] = token
            save_config(self.config)

            reply = f"You have been successfully authenticated as "
            reply += f"{self.config['username']}."
            self.poutput(reply)
            return True

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

        return False

    def get_timeline(self, stream):
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            if stream == 'unified':
                data, meta = pnut_api.users_post_streams_unified(include_post_raw=1)
            elif stream == 'personal':
                data, meta = pnut_api.users_post_streams_me(include_post_raw=1)
            elif stream == 'global':
                data, meta = pnut_api.posts_streams_global(include_post_raw=1)
            else:
                return

            for post in reversed(data):
                if 'content' in post:
                    self.stream.print_post(post)

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    def get_thread(self, post_id):
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            data, meta = pnut_api.posts_thread(post_id, include_post_raw=1)

            for post in reversed(data):
                if 'content' in post:
                    self.stream.print_post(post)

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    def get_replies(self, username):
        pnut_api = pnutpy.API.build_api(access_token=self.token)

        try:
            data, meta = pnut_api.users_mentioned_posts(username, include_post_raw=1)

            for post in reversed(data):
                if 'content' in post:
                    self.stream.print_post(post)

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    def send_post(self, text, reply_to=None, mention=None):
        pnut_api = pnutpy.API.build_api(access_token=self.token)
        try:

            if mention is not None:
                orig_msg, meta = pnut_api.get_post(reply_to)
                highlight = "@" + orig_msg.user.username

                if mention == REPLY_ONE:
                    text = highlight + " " + text

                elif mention in [REPLY_ALL, REPLY_CC]:

                    cc_list = []
                    if 'content' in orig_msg:
                        if 'mentions' in orig_msg.content.entities:
                            mentions = orig_msg.content.entities.mentions
                        else:
                            mentions = []

                        for m in mentions:
                            if (m.text != self.config['username'] and
                                    m.text != highlight):
                                cc_list.append("@" + m.text)
                    if len(cc_list) > 0:
                        cc = " ".join(cc_list)

                        if mention == REPLY_CC:
                            text = highlight + " " + text + " /" + cc

                        elif mention == REPLY_ALL:
                            text = highlight + " " + cc + " " + text

            post, meta = pnut_api.create_post(
                data={'reply_to': reply_to, 'text': text})
            self.poutput(
                f"* created post {Fore.YELLOW}{post['id']}{Fore.RESET}")

        except pnutpy.errors.PnutAuthAPIException:
            self.perror("Unable to access your account.")

    def _onchange_setting(self, setting, old, new):
        if setting == 'feed' and new is True:
            self.startup()

        elif setting == 'feed' and new is False:
            self.shutdown()

        elif setting == 'timeline':
            self.shutdown()
            self.stream.timeline = new
            self.startup()

        elif setting == 'show_links':
            self.stream.show_links = new

        self.config[setting] = new
        save_config(self.config)

def load_config():
    config_file = get_config_file()
    if config_file.exists():
        with open(config_file, "rb") as cf:
            config = tomlkit.load(cf)
    else:
        config = tomlkit.document()
    return config

def save_config(config):
    config_file = get_config_file()
    with open(config_file, "w") as cf:
        tomlkit.dump(config, cf)

def get_config_file():
    XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME")

    if bool(XDG_CONFIG_HOME):
        config_file = os.path.join(XDG_CONFIG_HOME, "pnutty.toml")
    else:
        config_file = Path.home().joinpath(".pnutty.toml")

    return Path(config_file)

def main():
    parser = cmd2.Cmd2ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_const',
        dest='loglevel', const=logging.DEBUG, default=logging.INFO,
        help="enable debug log output")
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    config = load_config()

    if 'token' not in config:
        config['token'] = ""

    app = NuttyShell(config)
    sys.exit(app.cmdloop())

if __name__ == '__main__':
    main()
