import random

# ─────────────────────────────────────────────
#  FFXI Quote Database — Expanded Edition
# ─────────────────────────────────────────────

NPC_STORY = [
    # --- Chains of Promathia ---
    ("Prishe", "Don't just stand there lookin' all dumbfounded! We've got a world to save!"),
    ("Prishe", "I don't care if you're a god. You're in my way."),
    ("Prishe", "Yeah, yeah. I know I'm not supposed to hit people that hard. ...Mostly."),
    ("Selh'teus", "Time is but a river, and we are merely leaves upon its surface."),
    ("Selh'teus", "To exist outside of time is not freedom. It is exile."),
    ("Nag'molada", "The Emptiness... it calls to all of us, sooner or later."),
    ("Nag'molada", "Progress demands sacrifice. History will understand, even if you do not."),
    ("Ulmia", "The song... it still lives within me. As long as I draw breath, hope is not lost."),
    ("Ulmia", "Music does not conquer darkness. It reminds us what we are fighting to return to."),
    ("Tenzen", "A warrior's path is walked alone. But that does not mean one cannot walk beside another."),
    # --- Rise of the Zilart ---
    ("Kam'lanaut", "The future belongs to those strong enough to seize it."),
    ("Kam'lanaut", "We did not betray anyone. We simply chose a different path to paradise."),
    ("Eald'narche", "You speak of bonds as though they were strength. They are chains, nothing more."),
    ("Lion", "Don't worry. I'll watch your back — just try not to make it easy for them."),
    ("Lion", "Pirates don't wait for permission. Neither do I."),
    ("Lion", "My father was many things. Right wasn't always one of them."),
    # --- Treasures of Aht Urhgan ---
    ("Aphmau", "I don't understand everything yet, but I know I have to keep moving forward."),
    ("Aphmau", "An empress who cannot protect her own people is no empress at all."),
    ("Luzaf", "A pirate does not ask for forgiveness. He simply takes what is owed."),
    ("Luzaf", "Betrayal and loyalty are two sides of the same coin. It depends which way it lands."),
    ("Razfahd", "Power is wasted on the compassionate. I will not make that mistake."),
    ("Shantotto", "Oh ho ho! Did you really think you could match wits with the great Shantotto?"),
    ("Shantotto", "Your pathetic resistance only makes this more entertaining, ho ho ho!"),
    ("Shantotto", "Power and genius rarely share a vessel. Lucky for Vana'diel, I have both."),
    # --- Wings of the Goddess ---
    ("Lilisette", "Dance with your heart, and the world will have no choice but to listen."),
    ("Lilisette", "The future isn't written yet. That's exactly why we have to fight for it."),
    ("Cait Sith", "Mrrrow... The star sings, but do ye have the ears to hear it?"),
    ("Cait Sith", "Fate cannae be read like a map, kupo. Ye must walk the path to know it."),
    ("Portia", "Some doors, once opened, can never be closed again."),
    ("Lilith", "You cling to a future that was never meant to be. How terribly human of you."),
    # --- Seekers of Adoulin ---
    ("Arciela", "I have stood at the edge of the abyss... and chosen to turn back."),
    ("Arciela", "The colonization of Ulbuka is not just about land. It is about what we become."),
    ("Ygnas", "Leadership is not about standing in front. It is about making sure no one is left behind."),
    ("Teodor", "Every map ends somewhere. Beyond that line is where the real work begins."),
    # --- Rhapsodies of Vana'diel ---
    ("Iroha", "Even if no one else remembers, I will always remember you — adventurer!"),
    ("Iroha", "The future you fight for exists. I have seen it. Please... don't give up."),
    ("Bahamut", "Pitiful creatures of darkness... what do you hope to accomplish?"),
    ("Bahamut", "I have endured since before your kingdoms rose. I shall endure after they fall."),
    (" Altana", "I did not create life to see it extinguished. Rise, adventurer. Rise and endure."),
    ("Promathia", "Hope is the cruelest lie. I gave them despair so they would stop suffering it."),
    # --- General NPCs ---
    ("Zeid", "Power without purpose is just destruction with a name."),
    ("Zeid", "The dark does not make monsters. It only reveals what was already there."),
    ("Gilgamesh", "I have sailed every sea and fought every foe worth fighting. You come close."),
    ("Semih Lafihna", "The Mithra do not fear death. We simply prefer to avoid it... most of the time."),
    ("Gabranth", "An empire built on fear is built on sand. But sand can bury armies."),
    ("Volker", "A San d'Orian knight does not retreat. He tactically advances in a rearward direction."),
]

BATTLE_CRIES = [
    ("Warrior", "MIGHTY STRIKES!"),
    ("Warrior", "Berserk! They'll never bring me down!"),
    ("Warrior", "Warcry! COME ON THEN!"),
    ("Monk", "HUNDRED FISTS! HAAAAAH!"),
    ("Monk", "Chakra... and back in the fight!"),
    ("Monk", "Counterstance! Hit me. I dare you."),
    ("White Mage", "Curaga IV! Hang on everyone!"),
    ("White Mage", "Benediction! Everyone get up NOW!"),
    ("White Mage", "Divine Seal — Holy!"),
    ("White Mage", "Reraise is up. Don't make me use it."),
    ("Black Mage", "MANAFONT! FLARE II!"),
    ("Black Mage", "Freeze II! Stay still and let the blizzard take you!"),
    ("Black Mage", "Thundaga IV — goodbye, cluster."),
    ("Black Mage", "Magic Burst! FIRE IV!"),
    ("Red Mage", "Chainspell — now BURN!"),
    ("Red Mage", "Refresh is up, heal through it!"),
    ("Red Mage", "Convert! Don't worry, I planned for this."),
    ("Thief", "Flee! ...and maybe I'll come back for you."),
    ("Thief", "Treasure Hunter — the drops belong to me now."),
    ("Thief", "Sneak Attack — Trick Attack — WEAPONSKILL. Beautiful."),
    ("Thief", "Perfect Dodge! Try hitting air."),
    ("Paladin", "Cover! Get behind me!"),
    ("Paladin", "Invincible! Nobody dies today!"),
    ("Paladin", "Sentinel. Nothing gets through me."),
    ("Dark Knight", "Last Resort — SOULEATER!"),
    ("Dark Knight", "Absorb-TP... yes. Drain... yes. This is going well."),
    ("Dark Knight", "Blood Weapon. Let the pain fuel the fight."),
    ("Beastmaster", "Sic 'em, Courier Carrie!"),
    ("Beastmaster", "Call Beast! Your time has come, Funguar!"),
    ("Beastmaster", "Reward — good boy. Now go wreck that NM."),
    ("Bard", "Advancing March — let's go, let's GO!"),
    ("Bard", "Minuet V — Minne V — Ballad II. You're welcome."),
    ("Bard", "Lullaby! Sweet dreams, everyone except us."),
    ("Bard", "Elegy! Slow and suffer."),
    ("Ranger", "Eagle Eye Shot — don't blink."),
    ("Ranger", "Barrage! Count those hits!"),
    ("Ranger", "Shadowbind! You're not going anywhere."),
    ("Samurai", "Meikyo Shisui — TACHI: KAITEN!"),
    ("Samurai", "Meditate... Meditate... Tachi: Gekko!"),
    ("Samurai", "Third Eye. I see you. And you."),
    ("Ninja", "Mijin Gakure! ...Sorry about this."),
    ("Ninja", "Utsusemi: Ni! Shadows up, let's dance."),
    ("Ninja", "Ni-Ton! Kurayami: Ni! You're blind AND slow."),
    ("Dragoon", "Jump! ...Wyvern, you're up!"),
    ("Dragoon", "High Jump! Penta Thrust incoming!"),
    ("Dragoon", "Ancient Circle — time to fight dragons with a dragon."),
    ("Summoner", "Ifrit! Burning Strike!"),
    ("Summoner", "Shiva! Diamond Dust — good night!"),
    ("Summoner", "Fenrir! Eclipse Bite — the hunt is on!"),
    ("Summoner", "Astral Flow... Odin. ZANTETSUKEN."),
    ("Blue Mage", "Cannonball — brace yourselves!"),
    ("Blue Mage", "Disseverment! Learned that one the hard way."),
    ("Blue Mage", "Goblin Rush! ...Yes, I copied a Goblin. No, I'm not proud."),
    ("Blue Mage", "Magic Hammer! TP for me, nothing for you."),
    ("Corsair", "Bolter's Roll — snake eyes baby!"),
    ("Corsair", "Chaos Roll! We live and die by the numbers!"),
    ("Corsair", "Leaden Salute! Call it a calculated risk."),
    ("Corsair", "Quick Draw! No time to dodge."),
    ("Puppetmaster", "Activate! Stringing Pummel!"),
    ("Puppetmaster", "Overdrive! Full automation, maximum pain."),
    ("Puppetmaster", "Tactical Switch — you're doing great, buddy."),
    ("Dancer", "Saber Dance — let's go!"),
    ("Dancer", "Reverse Flourish! TP refunded, full house."),
    ("Dancer", "Curing Waltz IV! Nobody asks, everybody gets healed."),
    ("Dancer", "Haste Samba! Keep up!"),
    ("Scholar", "Tabula Rasa — this ends NOW!"),
    ("Scholar", "Sublimation. Patience. Power. Repeat."),
    ("Scholar", "Manifestation — party-wide Sleep II. Night night."),
    ("Scholar", "Stratagems refreshed. Let the lecture resume."),
    ("Geomancer", "Indi-Refresh — hold formation!"),
    ("Geomancer", "Geo-Malaise! Feel the earth pulling you down."),
    ("Geomancer", "Bolster! The luopan speaks and the land listens."),
    ("Rune Fencer", "Lunge — face the runes!"),
    ("Rune Fencer", "Vallation — the runes hold. Come closer."),
    ("Rune Fencer", "Pflug! The element bends to my will."),
]

MOOGLE_QUIPS = [
    ("Moogle", "Kupo! Your delivery has arrived, kupo! Please sign here... and here... and here, kupo!"),
    ("Moogle", "Kupo kupo! I've been waiting forever, kupo! Do you know what time it is, kupo?"),
    ("Moogle", "Your Mog House is a mess, kupo! I've done my best but I am not a miracle worker, kupo!"),
    ("Moogle", "Kupoooo! A letter arrived for you! I did NOT read it. (I read it.) Kupo!"),
    ("Moogle", "Kupo! The Mog Locker is almost full! Consider throwing something away, kupo!"),
    ("Moogle", "Kupo! I baked you some kupo nuts but then I ate them. I'm sorry, kupo!"),
    ("Moogle", "Kupo! You've been adventuring so long even the monsters feel sorry for you, kupo!"),
    ("Conquest Tally Moogle", "Kupo! Sandoria is in first this week! ...barely, kupo."),
    ("Moogle", "Rest here, kupo! Your Mog House is always waiting for you, kupo!"),
    ("Nomad Moogle", "Kupo! Out here in the field, even moogles must be brave, kupo!"),
    ("Moogle", "Kupo! I tried to reorganize your bazaar while you were gone. Kupo, I may have sold something important."),
    ("Moogle", "A delivery arrived while you were out, kupo! I signed for it. I also opened it. Kupo, it smelled nice."),
    ("Moogle", "Kupo! I heard adventurers talking about a fearsome NM today. They did not look confident, kupo."),
    ("Moogle", "Kupo! Your Mog Garden needs attention! The crops are... expressing frustration, kupo."),
    ("Rent-a-Room Moogle", "Kupo! Resting is not laziness, kupo! It is strategic recovery! Kupo!"),
    ("Moogle", "Kupo! You have new moogle mail! I did not read it this time. Kupo. Mostly."),
    ("Moogle", "Kupo! The Auction House rejected your listing again. Perhaps price it lower, kupo?"),
    ("Moogle", "Kupo! Another adventurer asked me what you do for a living. Kupo... I did not have a good answer."),
]

EMOTE_FLAVOR = [
    ("Adventurer", "/cry — You sit down and cry. It doesn't help. The exp loss was real."),
    ("Adventurer", "/comfort — You offer a word of comfort. Nobody feels better."),
    ("Adventurer", "/panic — You panic! The Snoll Tzar is still alive at 0%!"),
    ("Adventurer", "/joy — You leap for joy! You finally got your Haubergeon drop!"),
    ("Adventurer", "/kneel — You kneel before the party leader. They have no idea what they're doing."),
    ("Adventurer", "/fume — You fume with irritation. The bard put on Minuet again."),
    ("Adventurer", "/slap — You slap yourself. You forgot to reraise."),
    ("Adventurer", "/shocked — You are shocked! Someone actually won the claim!"),
    ("Adventurer", "/wave — You wave cheerfully. The NM pops behind you."),
    ("Adventurer", "/poke — You poke your fellow adventurer. They are still AFK in Jeuno."),
    ("Adventurer", "/stagger — You stagger! You were not expecting Absolute Virtue to use Manafont."),
    ("Adventurer", "/cheer — You cheer! The RNG finally blessed you after 47 runs."),
    ("Adventurer", "/think — You think. Was Salvage always this hard, or did you get worse?"),
    ("Adventurer", "/sigh — You sigh deeply. The NM died while you were zoning. Again."),
    ("Adventurer", "/blush — You blush. You pulled a mob you shouldn't have. Everyone saw."),
    ("Adventurer", "/sulk — You sulk. The Ninja forgot to put shadows up again."),
    ("Adventurer", "/dance — You dance! The party wipes. Coincidence? Probably not."),
    ("Adventurer", "/bow — You bow respectfully. The Beastmaster just solo'd a god-tier NM."),
    ("Adventurer", "/sweat — You break into a cold sweat. There are 30 minutes left on the Dynamis clock."),
    ("Adventurer", "/pray — You pray. The ??? spawns. The NM is not what you hoped."),
    ("Adventurer", "/grin — You grin. You got the claim. Let the suffering begin."),
]

AVATAR_QUOTES = [
    # --- Ifrit ---
    ("Ifrit", "Come! Bathe in my flames and be purified... or perish in the attempt!"),
    ("Ifrit", "The fires of Ifrit consume all who stand against us. Are you prepared, summoner?"),
    ("Ifrit", "Burning Strike! Let the conflagration begin!"),
    ("Ifrit", "Crimson Howl! Let the fire in your veins ignite!"),
    ("Ifrit", "Flaming Crush! I will grind you to cinders!"),
    # --- Shiva ---
    ("Shiva", "Your enemies shall know the cold embrace of oblivion. I will see to it personally."),
    ("Shiva", "Diamond Dust! Let the blizzard swallow them whole."),
    ("Shiva", "The cold does not discriminate. Neither shall I."),
    ("Shiva", "Heavenly Strike! Even the sky freezes at my command."),
    ("Shiva", "Rush! Do not mistake stillness for weakness."),
    # --- Ramuh ---
    ("Ramuh", "Judgment Bolt! Let the heavens themselves bear witness!"),
    ("Ramuh", "Foolish mortals... you would challenge the storm itself?"),
    ("Ramuh", "The thunder speaks where words cannot. Heed its counsel well."),
    ("Ramuh", "Chaotic Strike! Lightning does not ask where it may fall."),
    ("Ramuh", "I am older than your kingdoms. I have outlasted greater arrogance than yours."),
    # --- Titan ---
    ("Titan", "Geocrush! The very earth rises to answer my call!"),
    ("Titan", "You stand upon my domain. Every stone, every root answers to me."),
    ("Titan", "Solid as the mountain. Unyielding as the stone. That is my covenant with you."),
    ("Titan", "Rock Buster! The earth itself becomes your enemy!"),
    ("Titan", "Megalith Throw! Let the mountains themselves come to you!"),
    # --- Leviathan ---
    ("Leviathan", "Tidal Wave! Let the depths reclaim what is theirs!"),
    ("Leviathan", "The sea is patient. It has swallowed greater armies than yours."),
    ("Leviathan", "All rivers return to me in time. As will you."),
    ("Leviathan", "Spinning Dive! The current answers my call!"),
    ("Leviathan", "Water Cannon! The ocean does not yield. Neither do I."),
    # --- Garuda ---
    ("Garuda", "Predator Claws! The gale answers my call!"),
    ("Garuda", "You cannot outrun the wind. You cannot hide from the sky."),
    ("Garuda", "The storm does not ask permission. Nor do I."),
    ("Garuda", "Aerial Blast! Not even the air is safe from my wrath!"),
    ("Garuda", "Whispering Wind! The breeze that heals... or the gale that destroys."),
    # --- Fenrir ---
    ("Fenrir", "Eclipse Bite! The moon darkens and the hunt begins!"),
    ("Fenrir", "The lone wolf does not hunger. He endures, and he strikes true."),
    ("Fenrir", "Run if you must. The night is vast... but I am faster."),
    ("Fenrir", "Lunar Cry! Even the moon turns its face from your weakness!"),
    ("Fenrir", "Howling Moon! I call the darkness, and the darkness answers."),
    # --- Diabolos ---
    ("Diabolos", "Ruinous Omen! Your nightmares take shape!"),
    ("Diabolos", "Reality is merely the dream you have not woken from yet."),
    ("Diabolos", "Come, step into the dark. I have been waiting for you here."),
    ("Diabolos", "Nightmare! Sleep, and dream of your failures."),
    ("Diabolos", "Camisado! The mind is the battlefield I prefer."),
    # --- Carbuncle ---
    ("Carbuncle", "Ruby Light! Let the radiance shield us!"),
    ("Carbuncle", "Do not be afraid. I am here, and the light will hold."),
    ("Carbuncle", "Even in the darkest place, a single gem can illuminate the way."),
    ("Carbuncle", "Soothing Ruby! Rest now. I'll keep watch."),
    ("Carbuncle", "Meteorite! Even small things can shake the world."),
    # --- Cait Sith ---
    ("Cait Sith", "Reraise! The battle is not over while breath remains!"),
    ("Cait Sith", "Mrrrow! The stars whisper strange things tonight. You'd do well to listen."),
    ("Cait Sith", "Fate is a fickle thing. Even I cannot read it clearly... most of the time."),
    ("Cait Sith", "Altair! The star guides us true."),
    ("Cait Sith", "Beware the Ides, kupo. Or was it Ides? I forget. Be careful either way."),
    # --- Alexander ---
    ("Alexander", "Holy! Divine judgment descends upon the unworthy!"),
    ("Alexander", "Steel yourself. The fortress does not tremble. Neither shall we."),
    ("Alexander", "Justice is not blind. It sees clearly, and it finds you wanting."),
    ("Alexander", "Perfect Defense! No force in this world shall pass!"),
    ("Alexander", "Radiant Sacrament! The light purifies all impurity."),
    # --- Odin ---
    ("Odin", "Zantetsuken! One stroke. One breath. One end."),
    ("Odin", "Sleipnir carries me across eight worlds. There is nowhere you can flee."),
    ("Odin", "All things must end. I am simply the instrument of that inevitability."),
    ("Odin", "Gungnir! The spear of the Allfather does not miss."),
    ("Odin", "Dark Wave! Even the gods must answer to entropy."),
    # --- Bahamut ---
    ("Bahamut", "Megaflame! The elder dragon speaks, and the world burns!"),
    ("Bahamut", "I have watched civilizations rise and crumble. You are but a moment in the tide."),
    ("Bahamut", "Gigaflare! There is no shelter from my wrath!"),
    ("Bahamut", "You sought to bind the king of dragons? Amusing. And brief."),
    # --- Phoenix ---
    ("Phoenix", "Rebirth! From the ash, we rise once more!"),
    ("Phoenix", "Death is not the end for those with the will to return. Rise."),
    ("Phoenix", "Flames that destroy also renew. Do not fear the fire."),
    ("Phoenix", "Revelation! The cycle continues as it always has!"),
    ("Phoenix", "I have died a thousand times. Each time, I return stronger. Remember that."),
    # --- Atomos ---
    ("Atomos", "The void consumes all. Distance is meaningless. Resistance is futile."),
    ("Atomos", "Drawn in... drawn in... all things return to the darkness in the end."),
    ("Atomos", "Comet! Even the stars are not safe from my hunger."),
    ("Atomos", "You cannot fight the void. You can only delay the inevitable."),
]

NOTORIOUS_MONSTERS = [
    ("Absolute Virtue", "You thought Jailer of Love was the hard one. Adorable."),
    ("Pandemonium Warden", "18 hours. You had 18 hours and still couldn't finish the job."),
    ("Nidhogg", "Come for the wyrm, stay for the trauma. The drop rate appreciates your optimism."),
    ("Fafnir", "Another day, another party shattered on my scales. The Haubergeon is not for the weak."),
    ("Kirin", "I have seen a thousand alliance wipes. Yours was not particularly memorable."),
    ("Cerberus", "Three heads means three times the disappointment. I admire your persistence."),
    ("Khimaira", "You came with twelve. You left with fewer. I consider that a success."),
    ("Ouryu", "The clouds are my domain. Your airship does not impress me."),
    ("King Behemoth", "You claimed the King. The King finds this... premature."),
    ("Behemoth", "Thunderbolt. Again. You'll learn... or you won't."),
    ("Genbu", "The north wind answers to me. Your resist rate does not."),
    ("Byakko", "Speed means nothing if your Utsusemi fails at the critical moment."),
    ("Suzaku", "I wonder, does your party always argue about loot before the fight is over?"),
    ("Seiryu", "A worthy effort. Tragically, effort alone does not equal victory."),
]

CITY_FLAVOR = [
    ("Jeuno Gate Guard", "All caravans must register before proceeding through Jeuno airspace. Next!"),
    ("Bastok Blacksmith", "The Republic's steel is the finest in Vana'diel. Anyone who says otherwise hasn't tried it."),
    ("Windurst Tarutaru", "Taru taru! You look like someone who needs a spell researched, taru!"),
    ("San d'Oria Knight", "The Kingdom's honor is maintained at all borders. State your business, adventurer."),
    ("Aht Urhgan Merchant", "You have the look of someone who has coin to spend and no idea where to spend it. Welcome."),
    ("Selbina Shepherd", "The Crag of Mea isn't far. Don't say I didn't warn you about the Goblins."),
    ("Rabao Trader", "Quicksand Caves, you say? My condolences and my best wishes. Mostly condolences."),
    ("Norg Pirate", "Everyone who walks through that door owes Gilgamesh something. What do you owe?"),
    ("Tavnazian NPC", "We don't get many visitors here. Most who come don't come back. ...That wasn't meant to sound ominous."),
    ("Whitegate Guard", "Entry to Aht Urhgan Whitegate requires documentation. Your fame precedes you. Enter."),
    ("Adoulin Pioneer", "Ulbuka is not a place for the unprepared. It is also not a place for the prepared. It is simply dangerous."),
]

ALL_QUOTES = (
    NPC_STORY + BATTLE_CRIES + MOOGLE_QUIPS +
    EMOTE_FLAVOR + AVATAR_QUOTES + NOTORIOUS_MONSTERS + CITY_FLAVOR
)


def get_random_quote() -> tuple[str, str]:
    """Return a random (speaker, quote) tuple from the full pool."""
    return random.choice(ALL_QUOTES)


def get_quote_by_category(category: str) -> tuple[str, str]:
    categories = {
        "npc": NPC_STORY,
        "battle": BATTLE_CRIES,
        "moogle": MOOGLE_QUIPS,
        "emote": EMOTE_FLAVOR,
        "avatar": AVATAR_QUOTES,
        "nm": NOTORIOUS_MONSTERS,
        "city": CITY_FLAVOR,
    }
    pool = categories.get(category.lower(), ALL_QUOTES)
    return random.choice(pool)


def format_quote(speaker: str, quote: str) -> str:
    return f"📜 **{speaker}**\n*\"{quote}\"*"
