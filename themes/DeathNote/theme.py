# Imports here
from themes.required.visual import Visual
from themes.required.sniper import UGCSniper

# Print class definition
def printLogo():
    '''

    :return: int success
    '''

    Visual.betterPrint(
        '''[GRADIENT_#00C800_#005000]
   $$$$$\  $$$$$$\  $$\       $$\                  $$$$$$\            $$\ 
   \__$$ |$$ ___$$\ $$ |      $$ |                $$  __$$\           \__|                              
      $$ |\_/   $$ |$$ | $$$$$$$ | $$$$$$\        $$ /  \__|$$$$$$$\  $$\  $$$$$$\   $$$$$$\   $$$$$$\  
      $$ |  $$$$$ / $$ |$$  __$$ |$$  __$$\       \$$$$$$\  $$  __$$\ $$ |$$  __$$\ $$  __$$\ $$  __$$\ 
$$\   $$ |  \___$$\ $$ |$$ /  $$ |$$ /  $$ |       \____$$\ $$ |  $$ |$$ |$$ /  $$ |$$$$$$$$ |$$ |  \__|
$$ |  $$ |$$\   $$ |$$ |$$ |  $$ |$$ |  $$ |      $$\   $$ |$$ |  $$ |$$ |$$ |  $$ |$$   ____|$$ |      
\$$$$$$  |\$$$$$$  |$$ |\$$$$$$$ |\$$$$$$  |      \$$$$$$  |$$ |  $$ |$$ |$$$$$$$  |\$$$$$$$\ $$ |      
 \______/  \______/ \__| \_______| \______/        \______/ \__|  \__|\__|$$  ____/  \_______|\__|      
                                                                          $$ |                          
                                                                          $$ |                          
                                                                          \__|[END]'''
    )
    return 1

def printText(sniper: UGCSniper, logs):
    '''
    :param: sniper: the sniper with all variables
    :param: logs: The logs made by the sniper will automatically reset after 3 iterations

    :return: bool success
    '''

    Visual.betterPrint(f"""    [COLOR_WHITE][Time: [COLOR_YELLOW][{sniper._time}][COLOR_WHITE]]
        [COLOR_WHITE]--> [Speed: [COLOR_YELLOW]{sniper.speed}[COLOR_WHITE]]
        [COLOR_WHITE]--> [Ratelimits: [COLOR_RED]{sniper.ratelimits}[COLOR_WHITE]]

    [COLOR_WHITE][Price checks made: [COLOR_GREEN]{sniper.checks_made}[COLOR_WHITE]]
    [COLOR_WHITE][Limiteds added: [COLOR_GREEN]{len(sniper.limiteds)}[COLOR_WHITE]]
    [COLOR_GREEN][UGC Items bought][COLOR_WHITE]
        --> [COLOR_WHITE][Bought UGCs: [COLOR_GREEN]{sniper.bought}[COLOR_WHITE]]
        --> [COLOR_WHITE][Bought paid UGCs: [COLOR_GREEN]{sniper.boughtpaid}[COLOR_WHITE]]
    [COLOR_WHITE][Changed Proxies: [COLOR_RED]{sniper.proxies_switched}[COLOR_WHITE]]
        [COLOR_WHITE]--> [Current Proxy: [COLOR_YELLOW]{sniper.proxy}[COLOR_WHITE]]
    [COLOR_WHITE][Status: [COLOR_YELLOW]{sniper.proxy}[COLOR_WHITE]]
    
    Logs:
{logs}
    """)

    return 1

