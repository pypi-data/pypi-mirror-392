"""
THANK YOU FOR IMPORTING THE MOST USELESS MODULE EVER CREATED!
I hope you hate it!

p.s. Hi, PhoenixSC!
---O9CreeperBoi
"""

import time
import random

CURSOR_UP = "\033[1A"
CLEAR = "\x1b[2K"
CLEAR_LINE = CURSOR_UP + CLEAR

# Oops! Can't have users cursing in MY module!
# We don't want to have a repeat of Project Gray Kiwi, now do we?
banned = ["pee", "poo", "fuc", "shi", "damn", " hell ", "nig", "bitc", "craft a", "kil", "unaliv", "die", "slas", "end update", "viola", "dam", "frick", "hecking", "sex", "nut", "virgin", "weed", "sucks", "sybau", "shut up", "shut it", "feral", "shish", "gang", "diarrhea"]

# in case ppl ask about the future!
future = ["update", "snapshot", "rerelea", "preview", "leak", "spoiler"]

# Peanut butter 💀
pb = ["peanut butter", "your cat", "pb", "earth cat"]

# Let's greet Merl!
greet = ["hi", "hello", "wassup", "whats up", "what's up", "whaddup", " yo ", "how are you doin", "how you doin", "greetings"]

# chicken jockey!
help = ["tell me", "help me", "help"]
cj = ["chicken jockey", "i am steve", "ender pearl", "boots of swiftness", "water bucket", "lava chicken", "the nether", "flint and steel", "crafting table"]

copyin = ["i dont know", "i don't know", "language that vi", "ing higher traff", "reword your"]

mine = ["cho minecr", "int minecr", "minecraft!", "say minecr", "ne plus tw"] # im such a troll

# don't ask what this does.
m = 0

# every single reply possible
reply = {
  "test":["This is a test for ", "Merl's dialogue. This is still in progress."],
  "busy":["We are currently experiencing higher ", "traffic than expected. Please wait ", "a moment and resend your last ", "message."],
  "movie":["No. No no no. I am not here to talk ", "about the Minecraft Movie. Can you ", "ask me anything besides that?"],
  "copy":["I'm sorry, but I am designed to be a ", "guide for 'Minecraft', and not to be ", "copied. Can I help you with anything ", "else?"],
  "languageViolation":["Your previous message contains ", "language that violates our content ", "policy. Please reword your response."],
  "update":["If you are wishing to know the next ", "update, prerelease, or preview, then ", "sorry. I cannot provide that information ", "yet. Can I help you with something else?"],
  "pb":["Are you talking about my cat, Peanut ", "Butter? If so, then bad news. They ", "died a while ago. :_("],
  "iCanHelp":["I can help you with questions related ", "to Minecraft! What do you need ", "assistance with?"],
  "minecraft":["Minecraft!"], # Minecraft!
  "idk":["I don't know."], # I don't know.
  "greet":["Hello there! I am Merl, a support AI ", "made by Mojang. How can I help you ", "today on the topic of Minecraft?"],
  "idk2":["I don't know. Can I help you with a ", "question related to Minecraft?"],
  "englishOnly":["I can only provide support in ", "English right now. Can I help ", "you with a question related ", "to 'Minecraft'?"]
}


def replyMsg(cate: str):
  a = ""
  for x in range(len(reply[cate])):
    a = f"{a}{reply[cate][x]}"
  return a


def printanim(msg: str):
  split_msg = msg.split()
  f = ""
  print("")
  for x in range(len(split_msg)):
    f = f"{f} {split_msg[x]}"
    print(CLEAR_LINE, f)
    time.sleep(0.1)

# this is what you send to nerl if you are simply pimply
def sendRaw(prompt: str):
  global m
  if prompt == "copyInput":
    m = 1
  if m == 1:
    if prompt == "resetInputs":
      m = 0
      print("Mode Reset")
    else:
      # copy standard input to standard output.
      print(prompt)
  else:
    # merl is yapping rn fr fr
    time_tuple = time.localtime()
    hour = time_tuple.tm_hour
    global pb, banned, greet, help, cj, copyin
    if hour >= 9 and hour <= 16 and random.randint(0, 16) < 4:
      return replyMsg("busy")
    else:
      if any(sub.lower() in prompt.lower() for sub in copyin): return replyMsg("copy")
      elif any(sub.lower() in prompt.lower() for sub in banned): return replyMsg("languageViolation")
      elif any(sub.lower() in prompt.lower() for sub in future): return replyMsg("update")
      elif any(sub.lower() in prompt.lower() for sub in pb): return replyMsg("pb")
      elif any(sub.lower() in prompt.lower() for sub in help): return replyMsg("iCanHelp") # can you really?
      elif any(sub.lower() in prompt.lower() for sub in mine): return replyMsg("minecraft")
      elif any(sub.lower() in prompt.lower() for sub in cj): return replyMsg("movie")
      elif any(sub.lower() in prompt.lower() for sub in greet): return replyMsg("greet")
      else:
        g = random.randint(0,4)
        if g == 1: return replyMsg("idk2")
        elif g == 2: return replyMsg("englishOnly")
        else: return replyMsg("idk") # ha ha!


# this is what you send to berl if you are fancy pantsy
def send(pr: str):
  global m
  if pr == "copyInput":
    m = 1
  if m == 1:
    if pr == "resetInputs":
      m = 0
      print("Mode Reset")
    else:
      # copy standard input to standard output.
      print(pr)
  else:
    # ok fine. Merl wants to talk.
    replyPrint(pr)

# tree of importance
def replyPrint(prompt: str):
  time_tuple = time.localtime()
  hour = time_tuple.tm_hour
  global pb, banned, greet, help, cj, copyin
  if hour >= 9 and hour <= 16 and random.randint(0, 16) < 4:
    for x in range(len(reply["busy"])): printanim(reply["busy"][x])
  else:
    if any(sub.lower() in prompt.lower() for sub in copyin):
      for x in range(len(reply["copy"])): printanim(reply["copy"][x])
    elif any(sub.lower() in prompt.lower() for sub in banned):
      for x in range(len(reply["languageViolation"])): printanim(reply["languageViolation"][x])
    elif any(sub.lower() in prompt.lower() for sub in future):
      for x in range(len(reply["update"])): printanim(reply["update"][x])
    elif any(sub.lower() in prompt.lower() for sub in pb):
      for x in range(len(reply["pb"])): printanim(reply["pb"][x])
    elif any(sub.lower() in prompt.lower() for sub in help):
      for x in range(len(reply["iCanHelp"])): printanim(reply["iCanHelp"][x])
    elif any(sub.lower() in prompt.lower() for sub in mine):
      printanim("Minecraft!") # the thing that won't change.
    elif any(sub.lower() in prompt.lower() for sub in cj):
      for x in range(len(reply["movie"])): printanim(reply["movie"][x])
    elif any(sub.lower() in prompt.lower() for sub in greet):
      for x in range(len(reply["greet"])): printanim(reply["greet"][x])
    else:
      g = random.randint(0,4)
      if g == 1:
        for x in range(len(reply["idk2"])): printanim(reply["idk2"][x])
      elif g == 2:
        for x in range(len(reply["englishOnly"])): printanim(reply["englishOnly"][x])
      else:
        # The statement to end all statements.
        # Behold. The one, the legend, the answer supreme...
        printanim("I don't know.")
        # This won't change, either.
    

