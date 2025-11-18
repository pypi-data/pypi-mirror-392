# pnutty

A TTY client application for pnut.io

## Installation using pip

```
$ pip install --user pnutty
```

## Installation from source

```
$ git clone https://codeberg.org/thrrgilag/pnutty
$ cd pnutty
$ pip install .
```

## Basic Usage

When you first launch pnutty, you'll need to login your account on pnut.io with the `login` command.

```
pnutty% login
Visit the following URL to authorize with pnut.io and paste the token here.

https://pnut.io/oauth/authenticate?client_id=qx87SsGu3NZINwAUxEk1bC1TICzupv5e&redirect_uri=urn:ietf:wg:oauth:2.0:oob&scope=basic,stream,write_post,follow,presence,messages,files&response_type=token

TOKEN:
```

After successfully authenticating your timeline will load automatically and new posts will show as they stream in. To get a list of available commands use `help`.

```
pnutty% help -v

Documented commands (use 'help -v' for verbose/'help <topic>' for details):
======================================================================================================
again                 Replay the set feed
alias                 Manage aliases
block                 Block a user
blocked               List users you have blocked
bookmark              Bookmark a post
browse                Open a post in the web browser
edit                  Run a text editor and optionally open a file with it
follow                Follow a user
followers             List users who follow you
following             List users you are following
global                Show most recent posts from the Global stream
help                  List available commands or provide detailed help for a specific command
history               View, run, edit, save, or clear previously entered commands
login                 Log in to pnut.io
logout                Log out of pnut.io
macro                 Manage macros
mute                  Mute a user
muted                 List users you have muted
personal              Show most recent posts from your Personal stream
post                  Post to pnut.io
quit                  Exit this application
replies               Show replies (mentions)
reply                 Reply to a post
replyall              Reply to all of a post
replycc               Reply to a post and cc others
replyg                Reply globally to a post
repost                Repost a post
run_pyscript          Run a Python script file inside the console
run_script            Run commands in script file that is encoded as either ASCII or UTF-8 text
set                   Set a settable parameter or show current settings of parameters.
shell                 Execute a command as if at the OS prompt
shortcuts             List available shortcuts
show_post
show_thread
unblock               Unblock a user
unbookmark            Remove a bookmark
unfollow              Unfollow a user
unified               Show most recent posts from your Unified stream
unmute                Unmute a user
unrepost              Repost a post
user                  View a user profile
```

Client settings can be viewed and altered with the `set` command.

```
pnutty% set
Name                    Value                           Description
====================================================================================================================
allow_style             Terminal                        Allow ANSI text style sequences in output (valid values:
                                                        Always, Never, Terminal)
always_show_hint        False                           Display tab completion hint even when completion suggestions
                                                        print
debug                   False                           Show full traceback on exception
echo                    False                           Echo command issued into output
editor                  /usr/bin/nano                   Program used by 'edit'
feed                    True                            Enable live feed
feedback_to_output      False                           Include nonessentials in '|', '>' results
max_completion_items    50                              Maximum number of CompletionItems to display during tab
                                                        completion
quiet                   False                           Don't print nonessential feedback
scripts_add_to_history  True                            Scripts and pyscripts add commands to history
show_json               False                           Show raw post json
show_links              False                           Show link to post
timeline                personal                        Set timeline to [unified, or personal]
timing                  False                           Report execution times
```
