import os
import time
import json
import rgbprint

with open("themes/required/required.json", "r") as f:
    theme_info = json.load(f)

class Visual:
    @staticmethod
    def betterPrint(content, log_time=False, log=False):
        '''

        :param content: str content
        :param: log_time: bool log the time
        :param log: bool log to recent_logs doesnt work here
        :return:
        '''
        now = f"[{time.strftime('%r')}]" if log_time else ""

        if log:
            Visual.betterPrint("[COLOR_RED]WARNING the log variable isnt implemented for themes.Visual")
            exit(1)

        if Visual.__parsegradient(content) == 0:
            print(Visual.textToColour(f"[COLOR_LIGHT_BLUE]{now} {content}"))

    @staticmethod
    def __parsehex(text):
        txt = text.split("[HEX_")
        if len(txt) == 1:
            return txt[0]

        text = txt[0]
        for i in txt[1:]:
            i = i.split("]")
            text += f"{rgbprint.Color(i[0])}{''.join(i[1:])}"

        return text

    @staticmethod
    def __parsegradient(text):  # Meest leesbaar stukje programma in de wereld
        if "[GRADIENT" not in text:
            return 0
        try:
            txt = text.split("[GRADIENT_")
            print(txt[0], end="")
            for i in txt[1:]:
                start, end = i.split("]")[0].split("_")
                toprint, other = i.split("[END]")
                toprint = "".join(toprint.split("]")[1:])
                rgbprint.gradient_print(toprint, start_color=start, end_color=end, end="")
                print(other, end="")
        except IndexError:
            Visual.betterPrint("[COLOR_RED]Syntax error whilst decoding gradients.")
            os.system("pause")
            exit(1)

        return 1

    @staticmethod
    def textToColour(text: str):
        if "[COLOR" in text:
            for key in theme_info["colours"]:
                text = text.replace(key, f"\x1b[38;5;{theme_info['colours'][key]}m")

        try:
            if "[HEX" in text:
                text = Visual.__parsehex(text)
        except IndexError:
            Visual.betterPrint("[COLOR_RED]Syntax error whilst decoding hex.")
            os.system("pause")
            exit(1)

        return text

    @staticmethod
    def textToVar(sniper, text: str):
        if type(sniper) != UGCSniper:
            Visual.betterPrint("[COLOR_RED] WARNING, NO VALID SNIPER PASSED TO textToVar")
            os.system("pause")
            exit(1)

        custom_vars = {
            "[username]": sniper.userinfo["name"],
            "[displayName]": sniper.userinfo["displayName"],
            "[userId]": sniper.userinfo["id"],

            "[proxiesEnabled]": False,
            "[proxyAmount]": len(sniper.proxies_raw),
            "[currentProxy]": sniper.proxy,
            "[changedProxies]": sniper.proxies_switched,
            "[ratelimits]": sniper.ratelimits,

            "[time]": sniper._time,
            "[limitedsAmount]": len(sniper.limiteds),
            "[limiteds]": sniper.limiteds,
            "[speed]": sniper.speed,
            "[status]": sniper.stats,
            "[priceChecks]": sniper.checks_made,
            "[bought]": sniper.bought,
            "[boughtpaid]": sniper.boughtpaid,

            "[x-csrf]": sniper.cookies[0][1],
            "[cooldown]": sniper.cooldown,
            "[errors]": sniper.errors,
            "[version]": VERSION,
            "[mode]": sniper.mode
        }

        for key in custom_vars:
            text = text.replace(key, str(custom_vars[key]))

        return text