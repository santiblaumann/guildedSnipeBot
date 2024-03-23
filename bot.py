import guilded, pickle, os
import const

token = const.API_TOKEN  # purposefully obfuscated
snipeBot = guilded.Client()
allowed_channels = const.ALLOWED_CHANNELS
if not os.path.exists('scores.pickle'):
    with open('scores.pickle', 'wb') as file:
        pickle.dump({}, file)
# when a message is sent into snipes, check if the bot should act on it. 

@snipeBot.event
async def on_ready():
    print("Bot is ready.")
    mes = await snipeBot.fetch_channel(allowed_channels[1])  # note initialization in test channel
    await mes.send(f"Live for score testing.")
    # mes2 = await snipeBot.fetch_channel(allowed_channels[0])
    # await mes2.send(f"Live with very rudamentary features.")


@snipeBot.event
async def on_message(message):
    # check the following: robot isn't replying to itself, this message is in snipes, has an attachment, and an @ to tag someone
    if (message.author.id == snipeBot.user.id 
        or message.channel_id not in allowed_channels  
        or len(message.attachments) == 0 
        or len(message.mentions) == 0
        ):
        return
    print("A snipe has occured...")
    result = await snipe_message(message)
    # await message.channel.send("Score keeping has not been implemented yet. Stay tuned...")
    verdict = await update_score(message)
    await message.channel.send(f"{result}\n{verdict}")
    return


async def snipe_message(message):
    # snipee should be a list. 
    sniper, snipee = await getNicknames(message)
    return (f"{sniper} sniped {snipee}!")


async def update_score(message):
    """Update the snipe scores following the snipe. 
    This should update the score, and be accounted for in a person's head to head tallies. """
    # the way this will be indexed: { sniper : sniper_stats, sniper : sniper_stats}
    # statistics: {total:int, deaths:int, playerID1:int, playerID2:int}

    # if sniper has never recorded a snipe, add them to the dictionary. 
    # every user ID is unique. this should be fine. 

    # grab the pickle file, unpickle it, make changes as needed to update score
    with open('scores.pickle', 'rb') as file:
        scores = pickle.load(file)

    sniper_id = message.author.id
    snipee_ids = [victim.id for victim in message.mentions]

    sniper_stats = scores.get(sniper_id, {})
    sniper_stats['kills'] = sniper_stats.get('kills', 0) + len(snipee_ids)  # add as many kills as people were sniped

    # going to try to rewrite logic for snipe victims with a for loop. 
    for snipee_id in snipee_ids:
        sniper_stats[snipee_id] = sniper_stats.get(snipee_id, 0) + 1  # add a kill to head to head

        snipee_stats = scores.get(snipee_id, {})  # get death count
        snipee_stats['deaths'] = snipee_stats.get('deaths', 0) + 1

    # snipees_stats = [scores.get(snipee_id, {}) for snipee_id in snipee_ids]  # get death counts of each person sniped, and
    # [stats.update({'deaths': stats.get('deaths', 0) + 1}) for stats in snipees_stats]  # update all death counts

    # scores[sniper_id] = sniper_stats
    # scores[snipee_id] = snipee_stats
    sniper_total = scores[sniper_id].get('kills', 1)
    sniper_snipee = scores[sniper_id].get(snipee_id, 0)
    snipee_death = scores[snipee_id].get('deaths', 1)

    with open('scores.pickle', 'wb') as file:
        pickle.dump(scores, file)
    
    sniper_nick, snipee_nick = await getNicknames(message)

    # now, return the string to be outputted in the message. 
    kill = " snipe" if (sniper_total <= 1) else " snipes"
    time = " time." if (snipee_death <= 1) else " times."

    return (sniper_nick + " has " + str(sniper_total) + kill + ", with " + str(sniper_snipee) + " being against " + snipee_nick + ".\n" + 
            snipee_nick + " has been sniped " + str(snipee_death) + time)
    
async def getNicknames(message):
    """This might break compatibility later if we decide to add sniping in two messages.
    Expects a valid snipe message. """
    # snipee should be a list. 
    serv = message.server
    sniper = await serv.fetch_member(message.author.id)
    snipee = [await serv.fetch_member(mention.id) for mention in message.mentions]
    sniper = get_first_name(sniper)
    snipee = [get_first_name(id) for id in snipee]
    return (sniper, snipee)

def get_first_name(nam):
    try:
        res, *_ = nam.nick.strip().split(' ')
    except AttributeError:
        res, *_ = nam.name.strip().split(' ')
    return res

snipeBot.run(token)
