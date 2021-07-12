from requests import post
from termcolor import colored
from config import chatId, WHslack, telegramToken

class Notifications:

    def telegrame(self, message):
        """  Send message to Telegram """
        try:
            telegramUrl = "https://api.telegram.org/bot{0}/sendMessage".format(telegramToken)
            req = post(url=telegramUrl, params={'text': message, 'chat_id': chatId, 'parse_mode': 'Markdown'},
                       headers={'Content-Type': 'application/json'})
            if req.status_code != 200:
                print(colored("[!] error wile sending Message \n[!] status code : {0}".format(req.status_code), "red"))
            if req.status_code == 429:
                print(colored("[!] Api Rate limit : ", "red"))

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)
        except Exception as e:
            print(colored("[!] error while sending slack message \n [!] {}".format(e), "red"))

    def slack(self, message):
        """ send message to slack """
        try:
            req = post(url=WHslack, json={'text': ':new: {0}'.format(message)},
                       headers={'Content-Type': 'application/json'})
            if req.status_code != 200:
                print(colored("[!] error wile sending Message \n[!] status code : {0}".format(req.status_code), "red"))
            if req.status_code == 429:
                print(colored("[!] Api Rate limit : ", "red"))

        except KeyboardInterrupt:
            print(colored("[!] Ctrl+c detected", "yellow"))
            exit(0)
        except Exception as e:
            print(colored("[!] error while sending slack message \n [!] {}".format(e), "red"))
