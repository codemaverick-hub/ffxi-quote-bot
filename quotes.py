import random

NPC_STORY = [
    ("Prishe", "Don't just stand there lookin' all dumbfounded! We've got a world to save!"),
    ("Shantotto", "Oh ho ho! Did you really think you could match wits with the great Shantotto?"),
    ("Kam'lanaut", "The future belongs to those strong enough to seize it."),
    ("Lion", "Don't worry. I'll watch your back - just try not to make it easy for them."),
    ("Nag'molada", "The Emptiness... it calls to all of us, sooner or later."),
    ("Selh'teus", "Time is but a river, and we are merely leaves upon its surface."),
    ("Ulmia", "The song... it still lives within me. As long as I draw breath, hope is not lost."),
    ("Aphmau", "I don't understand everything yet, but I know I have to keep moving forward."),
    ("Luzaf", "A pirate does not ask for forgiveness. He simply takes what is owed."),
    ("Cait Sith", "Mrrrow... The star sings, but do ye have the ears to hear it?"),
    ("Lilisette", "Dance with your heart, and the world will have no choice but to listen."),
    ("Portia", "Some doors, once opened, can never be closed again."),
    ("Arciela", "I have stood at the edge of the abyss... and chosen to turn back."),
    ("Iroha", "Even if no one else remembers, I will always remember you, kupo - I mean, adventurer!"),
    ("Bahamut", "Pitiful creatures of darkness... what do you hope to accomplish?"),
]

BATTLE_CRIES = [
    ("Warrior", "MIGHTY STRIKES!"),
    ("Monk", "HUNDRED FISTS! HAAAAAH!"),
    ("White Mage", "Curaga IV! Hang on everyone!"),
    ("Black Mage", "MANAFONT! FLARE II!"),
    ("Red Mage", "Chainspell - now BURN!"),
    ("Thief", "Flee! ...and maybe I'll come back for you."),
    ("Paladin", "Cover! Get behind me!"),
    ("Dark Knight", "Last Resort - SOULEATER!"),
    ("Beastmaster", "Sic 'em, Courier Carrie!"),
    ("Bard", "Advancing March - let's go, let's GO!"),
    ("Ranger", "Eagle Eye Shot - don't blink."),
    ("Samurai", "Meikyo Shisui - TACHI: KAITEN!"),
    ("Ninja", "Mijin Gakure! ...Sorry about this."),
    ("Dragoon", "Jump! ...Wyvern, you're up!"),
    ("Summoner", "Ifrit! Burning Strike!"),
    ("Blue Mage", "Cannonball - brace yourselves!"),
    ("Corsair", "Bolter's Roll - snake eyes baby!"),
    ("Puppetmaster", "Activate! Stringing Pummel!"),
    ("Dancer", "Saber Dance - let's go!"),
    ("Scholar", "Tabula Rasa - this ends NOW!"),
    ("Geomancer", "Indi-Refresh - hold formation!"),
    ("Rune Fencer", "Lunge - face the runes!"),
]

MOOGLE_QUIPS = [
    ("Moogle", "Kupo! Your delivery has arrived, kupo! Please sign here and here and here, kupo!"),
    ("Moogle", "Kupo kupo! I've been waiting forever, kupo! Do you know what time it is, kupo?"),
    ("Moogle", "Your Mog House is a mess, kupo! I've done my best but I am not a miracle worker, kupo!"),
    ("Moogle", "Kupoooo~! A letter arrived for you! I did NOT read it. (I read it.) Kupo!"),
    ("Moogle", "Kupo! The Mog Locker is almost full! Consider throwing something away, kupo!"),
    ("Moogle", "Kupo! I baked you some kupo nuts but then I ate them. I'm sorry, kupo!"),
    ("Moogle", "Kupo! You've been adventuring so long even the monsters feel sorry for you, kupo!"),
    ("Conquest Tally Moogle", "Kupo! Sandoria is in first this week! ...barely, kupo."),
    ("Moogle", "Rest here, kupo! Your Mog House is always waiting for you, kupo~!"),
    ("Nomad Moogle", "Kupo! Out here in the field, even moogles must be brave, kupo!"),
]

EMOTE_FLAVOR = [
    ("Adventurer", "/cry - You sit down and cry. It doesn't help. The exp loss was real."),
    ("Adventurer", "/comfort - You offer a word of comfort. Nobody feels better."),
    ("Adventurer", "/panic - You panic! The Snoll Tzar is still alive at 0%!"),
    ("Adventurer", "/joy - You leap for joy! You finally got your Haubergeon drop!"),
    ("Adventurer", "/kneel - You kneel before the party leader. They have no idea what they're doing."),
    ("Adventurer", "/fume - You fume with irritation. The bard put on Minuet again."),
    ("Adventurer", "/slap - You slap yourself. You forgot to reraise."),
    ("Adventurer", "/shocked - You are shocked! Someone actually won the claim!"),
    ("Adventurer", "/wave - You wave cheerfully. The NM pops behind you."),
    ("Adventurer", "/poke - You poke your fellow adventurer. They are still AFK in Jeuno."),
    ("Adventurer", "/stagger - You stagger! You were not expecting Absolute Virtue to use Manafont."),
    ("Adventurer", "/cheer - You cheer! The RNG finally blessed you after 47 runs."),
]

ALL_QUOTES = NPC_STORY + BATTLE_CRIES + MOOGLE_QUIPS + EMOTE_FLAVOR


def get_random_quote() -> tuple[str, str]:
    return random.choice(ALL_QUOTES)


def get_quote_by_category(category: str) -> tuple[str, str]:
    categories = {
        "npc": NPC_STORY,
        "battle": BATTLE_CRIES,
        "moogle": MOOGLE_QUIPS,
        "emote": EMOTE_FLAVOR,
    }
    pool = categories.get(category.lower(), ALL_QUOTES)
    return random.choice(pool)


def format_quote(speaker: str, quote: str) -> str:
    return f"**{speaker}**\n*\"{quote}\"*"
