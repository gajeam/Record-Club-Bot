import time
from slackclient import SlackClient

import constants

# variables
BOT_NAME = 'recordboy'
BOT_ID = 'U284Z1E06'

# constants
AT_BOT = "<@" + BOT_ID + ">"
NOMINATE = "\\NOMINATE"
#TODO Remove this command
SCAN = "\\SCAN"

slack_client = SlackClient(constants.SLACK_TOKEN)


class Nomination:
    artist = ''
    album = ''

    def __init__(self, album, artist):
        """
        :type album: string
        :type artist: string
        """
        self.artist = artist
        self.album = album

    def __repr__(self):
        return "<Nomination artist:%s album:%s" % (self.artist, self.album)


def main():
    # Big shout out to this tutorial for help:
    # https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
    WEBSOCKET_DELAY = 1  # Delay for reading from firehose

    if slack_client.rtm_connect():
        print(BOT_NAME + " started running!")
        while True:
            command, channel, = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
                time.sleep(WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

# POLLING

def scan_for_poll(channel):

    # TODO: Make search start two weeks ago
    chat_history = slack_client.api_call('channels.history', channel=channel, count=500)
    if chat_history.get('ok'):
        nominations = []
        for message in chat_history.get('messages'):
            if message.get('type') == 'message':
                nomination = parse_nomination(message.get('text').upper())
                if nomination != None:
                    nominations.append(nomination)
        print(nominations)
    else:
        print("An error occurred fetching the chat history")

# NOMINATION

def handle_nominate(nomination, channel):
    if nomination == None:
        message = "Sorry, your nomination could not be parsed. Try using the format ALBUM : ARTIST"
    else:
        message = "Successfully nominated \"" + nomination.album + "\" by " + nomination.artist
    slack_client.api_call('chat.meMessage', channel=channel, text=message)


def parse_nomination(text):
    split_text = text.split(NOMINATE)
    if len(split_text) != 2:
        return None
    nomination_arr = split_text[1].split(" : ")
    if len(nomination_arr) != 2:
        return None
    return Nomination(nomination_arr[0], nomination_arr[1])


def handle_command(text_input, channel):
    command = None
    for input in text_input.split(' '):
        if input[0] == '\\':
            command = input
            break
    if command == None:
        return

    if command == NOMINATE:
        nomination = parse_nomination(text_input)
        handle_nominate(nomination, channel)
    elif command == SCAN:
        scan_for_poll(channel)

def parse_slack_output(slack_rtm_output):

    # Another shout out to the same tutorial:
    # https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().upper(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    main()
