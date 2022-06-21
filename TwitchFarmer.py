import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import requests
import time
import pickle
import math
from twitchAPI.oauth import refresh_access_token
import random
from datetime import datetime
import os
import psutil
from webdriver_manager.chrome import ChromeDriverManager
import tk as tkinter

to_pass_info = []
clientId = 'hezo4cnv9gyx0i5upt73gq62kzs8ec'
clientSecret = 'wr7d3ol2y5noh9lipzt6x5uvpv2ltf'


class TwitchInteract:
    def __init__(self):
        self.id = 'hezo4cnv9gyx0i5upt73gq62kzs8ec'
        self.secret = 'wr7d3ol2y5noh9lipzt6x5uvpv2ltf'

    def oauth(self):
        oauth_info = {
            'client_id': self.id,
            'redirect_uri': 'https://www.twitch.tv/',
            'response_type': 'code',
            'scope': ['user:read:email', 'channel:manage:redemptions', 'channel:read:redemptions']
        }
        request_session = requests.session()
        response = request_session.get('https://id.twitch.tv/oauth2/authorize', params=oauth_info)
        return response.url

    @staticmethod
    def access_token(oauth_code):
        access_token_info = {
            'client_id': clientId,
            'client_secret': clientSecret,
            'code': oauth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://www.twitch.tv/'
        }
        tokens = requests.post('https://id.twitch.tv/oauth2/token', params=access_token_info).json()
        return tokens['access_token'], tokens['refresh_token']

    def watcher_id(self, username, access_token):
        id_info = {
            'Authorization': 'Bearer ' + access_token,
            'Client-Id': self.id
        }
        id_response = requests.get("https://api.twitch.tv/helix/users?login=%s" % username,
                                   headers=id_info)
        print(id_response.text)
        return int(id_response.text.split('id')[1].split('"')[2])

    def following(self, id_val, access_token, *args):
        following_info = {
            'Authorization': 'Bearer ' + access_token,
            'Client-Id': self.id
        }
        if len(args) == 2:
            following_param = {'after': args[0]}
            api_return = requests.get('https://api.twitch.tv/helix/users/follows?from_id=%s' % id_val,
                                      params=following_param,
                                      headers=following_info)
            api_return_json = api_return.json()['data']
            if args[1] > 0:
                cursor_point = api_return.text.split('cursor')[1].split('"')[2]
            else:
                cursor_point = None
            return api_return_json, cursor_point
        else:
            api_return = requests.get('https://api.twitch.tv/helix/users/follows?from_id=%s' % id_val,
                                      headers=following_info)
            total_channels_followed = int(api_return.text.split(':')[1].split(',')[0])
            total_extra_calls = math.ceil(total_channels_followed / 20) - 1
            cursor_point = api_return.text.split('cursor')[1].split('"')[2]
            api_return_json = api_return.json()['data']
            return total_channels_followed, total_extra_calls, cursor_point, api_return_json

    def is_live(self, streamer_id, access_token):
        live_param = {'user_id': streamer_id}
        live_info = {
            'Authorization': 'Bearer ' + access_token,
            'Client-Id': self.id
        }
        if len(requests.get('https://api.twitch.tv/helix/streams', params=live_param, headers=live_info).json()[
                   'data']) != 0:
            return True
        return False

    def refresh(self, refresh_token):
        return refresh_access_token(refresh_token, self.id, self.secret)


class WebsiteInteract:
    def __init__(self, window_size):
        self.options = self.driver_options(window_size)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.options)
        self.driver.implicitly_wait(10)

    @staticmethod
    def driver_options(window_size):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False})
        chrome_options.add_argument('--profile-directory=Default')
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('window-position=0,0')
        chrome_options.add_argument("window-size=%s, %s" % (window_size.width(), window_size.height()))
        chrome_options.add_argument("--start-maximized")
        return chrome_options

    def fill_verification(self, code, username):
        sepNumbers = [char for char in code]
        potInputs = self.driver.find_elements_by_xpath("//input")
        for i, items in enumerate(potInputs):
            items.send_keys(sepNumbers[i])
        potInputs = self.driver.find_elements_by_xpath("//input")
        for i, items in enumerate(potInputs):
            items.send_keys(sepNumbers[i])
        self.driver.execute_script("window.open('https://www.google.com/')")
        pickle.dump(self.driver.get_cookies(), open(username + "cookies.pkl", "wb"))
        # pickle.dump(info, open("temp_store.pkl", "wb"))
        self.driver.quit()

    def home(self):
        while len(self.driver.window_handles) > 1:
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.get('https://www.twitch.tv/')

    def open_streams(self, streamers, currently_open_streams, opening_count):
        set_open_streams = set([item[1:] for item in currently_open_streams])
        set_streamers = set(streamers)
        to_close = set_open_streams - set_streamers
        to_open = set_streamers - set_open_streams
        opening_count_add = False
        for window_num, streamer in enumerate(to_open):
            if streamer not in currently_open_streams:
                opening_count_add = True
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[window_num + 1])
                self.driver.get('https://www.twitch.tv/' + streamer[2])
                currently_open_streams.append((self.driver.current_url, streamer[0], streamer[1], streamer[2]))
        currently_open_streams = self.close_update_streams(to_close, currently_open_streams)
        if opening_count == 0:
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        else:
            self.driver.switch_to.window(self.driver.window_handles[0])
        if opening_count_add:
            opening_count += 1
        return currently_open_streams, opening_count

    def close_update_streams(self, to_close, currently_open_streams):
        for streamer in to_close:
            location = [item for item, index in enumerate(currently_open_streams) if streamer[2] in item]
            self.driver.switch_to.window(int(location[0]))
            self.driver.close()
            currently_open_streams.pop(int(location[0]))
        return currently_open_streams

    def collect_channel_points(self):
        action_chain = webdriver.ActionChains(self.driver)
        for location in self.driver.find_elements_by_xpath("//*[contains(text(), 'Chat')]"):
            if location.text == 'Chat':
                action_chain.move_to_element_with_offset(location, -185, 0)
                action_chain.click()
                action_chain.perform()

    def print_urls(self):
        urls = []
        for i in range(len(self.driver.window_handles)):
            self.driver.switch_to.window(self.driver.window_handles[i])
            urls.append(self.driver.current_url)
        print(urls)


def process_priority(system, niceness):
    p = psutil.Process(os.getpid())
    if system == 'nt':
        if niceness == 'Below Normal (Recommended)':
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        elif niceness == 'Normal':
            p.nice(psutil.NORMAL_PRIORITY_CLASS)
        elif niceness == 'Above Normal':
            p.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
        elif niceness == 'High':
            p.nice(psutil.HIGH_PRIORITY_CLASS)
    else:
        if niceness == 'Below Normal (Recommended)':
            p.nice(-10)
        elif niceness == 'Normal':
            p.nice(0)
        elif niceness == 'Above Normal':
            p.nice(10)
        elif niceness == 'High':
            p.nice(15)


def watch_twitch(UI_Info):
    """
    try:
        os.remove("temp_store.pkl")
    except FileNotFoundError:
        pass
    """
    global to_pass_info
    to_pass_info = UI_Info

    os_name = UI_Info[0]
    priority = UI_Info[2]
    process_priority(os_name, priority)
    twitch_interact = TwitchInteract()

    authentication_url = twitch_interact.oauth()

    screen_res = UI_Info[1]

    website_interact = WebsiteInteract(screen_res)

    # Opens Tab and URL
    website_interact.driver.get(authentication_url)

    # Login
    username = UI_Info[3]
    usernamePath = website_interact.driver.find_element_by_id('login-username')
    usernamePath.send_keys(username)

    password = UI_Info[4]
    passwordPath = website_interact.driver.find_element_by_id('password-input')
    passwordPath.send_keys(password)

    # Loads Cookies to Prevent Location Checking
    try:
        cookies = pickle.load(open(username + "cookies.pkl", "rb"))
        for cookie in cookies:
            website_interact.driver.add_cookie(cookie)
    except FileNotFoundError:
        print("Location/2FA Verification")

    buttonPath = website_interact.driver.find_elements_by_xpath("//*[contains(text(), 'Log In')]")
    buttonPath[2].click()

    # Check if location verification is needed
    locationVerification = website_interact.driver.find_elements_by_xpath("//*[contains(text(), 'Verify login code')]")
    if len(locationVerification) == 0:
        pass
    else:
        def verification():
            if verifyNumber.get("1.0", "end-1c") != '' and len(verifyNumber.get("1.0", "end-1c")) == 6:
                numSave = verifyNumber.get("1.0", "end-1c")
                root.destroy()
                website_interact.fill_verification(numSave, username)
                watch_twitch(to_pass_info)
                sys.exit()

        root = tkinter.Tk()
        root.title('Verification Code')
        root.geometry("250x80+120+120")

        verify = tkinter.Label(text='What is the 6 Digit Verification Number?')
        verifyNumber = tkinter.Text(root, height=1, width=20)
        verify.pack()
        verifyNumber.pack()

        button = tkinter.Button(root, text='Verify', command=verification)
        button.pack(side=tkinter.BOTTOM)

        root.mainloop()

    # Find OAuth Code

    oauth_code = website_interact.driver.current_url.split('=')[1].split('&')[0]
    print('OAuth', oauth_code)

    # Get Access Token

    access_token, refresh_token = twitch_interact.access_token(oauth_code)
    print('AccessToken', access_token)
    print('RefreshToken', refresh_token)

    id_val = twitch_interact.watcher_id(UI_Info[3], access_token)
    print('ID:', id_val)
    currently_open = []
    opening_count = 0
    while True:
        # Followers And Check
        followed_channels = []
        currently_live = []

        total_channels_followed, total_extra_calls, cursor_point, api_return_json = twitch_interact.following(id_val,
                                                                                                              access_token)
        followed_channels.extend(api_return_json)
        while total_extra_calls > 0:
            total_extra_calls -= 1
            api_return_json, cursor_point = twitch_interact.following(id_val, access_token, cursor_point,
                                                                      total_extra_calls)
            followed_channels.extend(api_return_json)
        print()
        for streamer in followed_channels:
            streamer_id, streamer_name, streamer_login = streamer['to_id'], streamer['to_name'], streamer['to_login']
            if twitch_interact.is_live(streamer_id, access_token):
                currently_live.append((streamer_id, streamer_name, streamer_login))

        now = datetime.now()
        print("Current Time =", now.strftime("%H:%M:%S"))
        print()
        if len(currently_live) == 0:
            website_interact.home()
            currently_open = []
        else:
            currently_open, opening_count = website_interact.open_streams(currently_live, currently_open, opening_count)
        website_interact.print_urls()
        # toWait = random.randint(900, 950)
        toWait = random.randint(900, 1000)
        print(currently_open)
        print("refreshing in %s seconds" % toWait)
        time.sleep(toWait)
        if len(currently_live) > 0:
            if len(website_interact.driver.window_handles) > 0:
                for currTabs in website_interact.driver.window_handles:
                    website_interact.driver.switch_to.window(currTabs)
                    time.sleep(3)
                    website_interact.collect_channel_points()
            try:
                website_interact.driver.execute_script("window.open('');")
                website_interact.driver.switch_to.window(
                    website_interact.driver.window_handles[len(website_interact.driver.window_handles) - 1])
                website_interact.driver.get('https://www.twitch.tv/drops/inventory')
                time.sleep(2)
                location = website_interact.driver.find_elements_by_xpath("//*[contains(text(), 'Claim Now')]")
                if location is not None:
                    for elements in location:
                        elements.click()
                website_interact.driver.close()
                website_interact.driver.switch_to.window(website_interact.driver.window_handles[0])
            except TimeoutException:
                website_interact.driver.close()
                website_interact.driver.switch_to.window(website_interact.driver.window_handles[0])
        access_token, refresh_token = twitch_interact.refresh(refresh_token)


def stop():
    sys.exit()
