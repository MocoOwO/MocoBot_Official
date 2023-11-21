import MocoBot
from MocoBot.System.API import getToken

if __name__ == "__main__":
    MocoBot.init()
    print("finished")
    print(getToken())
