import random
from datetime import datetime

# ─────────────────────────────────────────────
#  Source Tag Helpers
#  Every quote tuple is (speaker, quote, source)
#  Use F() for fan-written, G() for confirmed game dialogue
# ─────────────────────────────────────────────

GAME = "📖 Game Dialogue"
FAN  = "✍️ Fan Written"
MEME = "😄 Community"

def G(speaker: str, quote: str) -> tuple:
    """Confirmed in-game dialogue."""
    return (speaker, quote, GAME)

def F(speaker: str, quote: str) -> tuple:
    """Fan-written in character."""
    return (speaker, quote, FAN)

def M(speaker: str, quote: str) -> tuple:
    """Community / meme content."""
    return (speaker, quote, MEME)

# ─────────────────────────────────────────────
#  NPC / Story Quotes
# ─────────────────────────────────────────────

NPC_STORY = [
    # --- Chains of Promathia ---
    F("Prishe", "Don't just stand there lookin' all dumbfounded! We've got a world to save!"),
    F("Prishe", "I don't care if you're a god. You're in my way."),
    F("Prishe", "Yeah, yeah. I know I'm not supposed to hit people that hard. ...Mostly."),
    F("Prishe", "Being immortal isn't living. It's just... not dying. There's a difference."),
    F("Selh'teus", "Time is but a river, and we are merely leaves upon its surface."),
    F("Selh'teus", "To exist outside of time is not freedom. It is exile."),
    F("Selh'teus", "The memories we carry are not burdens — they are proof we lived."),
    F("Nag'molada", "The Emptiness... it calls to all of us, sooner or later."),
    F("Nag'molada", "Progress demands sacrifice. History will understand, even if you do not."),
    F("Ulmia", "The song... it still lives within me. As long as I draw breath, hope is not lost."),
    F("Ulmia", "Music does not conquer darkness. It reminds us what we are fighting to return to."),
    F("Tenzen", "A warrior's path is walked alone. But that does not mean one cannot walk beside another."),
    # --- Rise of the Zilart ---
    F("Kam'lanaut", "The future belongs to those strong enough to seize it."),
    F("Kam'lanaut", "We did not betray anyone. We simply chose a different path to paradise."),
    F("Eald'narche", "You speak of bonds as though they were strength. They are chains, nothing more."),
    F("Eald'narche", "I have lived a thousand years waiting for this moment. You will not stop it in an afternoon."),
    F("Lion", "Don't worry. I'll watch your back — just try not to make it easy for them."),
    F("Lion", "Pirates don't wait for permission. Neither do I."),
    F("Lion", "My father was many things. Right wasn't always one of them."),
    F("Lion", "There's always a way through. You just have to be willing to swim for it."),
    # --- Treasures of Aht Urhgan ---
    F("Aphmau", "I don't understand everything yet, but I know I have to keep moving forward."),
    F("Aphmau", "An empress who cannot protect her own people is no empress at all."),
    F("Luzaf", "A pirate does not ask for forgiveness. He simply takes what is owed."),
    F("Luzaf", "The sea does not judge. That is why I prefer it to courts and councils."),
    F("Shantotto", "Oh ho ho! Did you really think you could match wits with the great Shantotto?"),
    F("Shantotto", "Power and genius rarely share a vessel. Lucky for Vana'diel, I have both."),
    F("Shantotto", "I would explain my genius, but your brain would dissolve before I finished!"),
    F("Shantotto", "Oh ho ho! Do try to keep up, you magnificent disappointment!"),
    F("Lehko Habhoka", "A Corsair never tells you all his cards. That's not dishonesty — that's survival."),
    # --- Wings of the Goddess ---
    F("Lilisette", "Dance with your heart, and the world will have no choice but to listen."),
    F("Lilisette", "The future isn't written yet. That's exactly why we have to fight for it."),
    F("Lilisette", "Every step I take is a step away from the world I don't want to live in."),
    F("Cait Sith", "Mrrrow... The star sings, but do ye have the ears to hear it?"),
    F("Cait Sith", "Fate cannae be read like a map. Ye must walk the path to know it."),
    F("Cait Sith", "The past is a wound. The future is a scar. The present is where ye can still choose."),
    F("Portia", "Some doors, once opened, can never be closed again."),
    F("Lilith", "You cling to a future that was never meant to be. How terribly human of you."),
    F("Lilith", "Hope is the most vicious trap ever devised. And you walked right into it."),
    # --- Seekers of Adoulin ---
    F("Arciela", "I have stood at the edge of the abyss... and chosen to turn back."),
    F("Arciela", "A kingdom that consumes the world to survive deserves neither."),
    F("Ygnas", "Leadership is not about standing in front. It is about making sure no one is left behind."),
    F("Teodor", "Every map ends somewhere. Beyond that line is where the real work begins."),
    F("Teodor", "The jungle doesn't hate you. It simply doesn't care if you survive."),
    # --- Rhapsodies of Vana'diel ---
    F("Iroha", "Even if no one else remembers, I will always remember you — adventurer!"),
    F("Iroha", "The future you fight for exists. I have seen it. Please... don't give up."),
    F("Iroha", "Every impossible thing you've done — someone is alive because of it."),
    F("Bahamut", "Pitiful creatures of darkness... what do you hope to accomplish?"),
    F("Bahamut", "I have endured since before your kingdoms rose. I shall endure after they fall."),
    F("Altana", "I did not create life to see it extinguished. Rise, adventurer. Rise and endure."),
    F("Promathia", "Hope is the cruelest lie. I gave them despair so they would stop suffering it."),
    F("Promathia", "Every prayer to Altana is a wound in me. And yet they never stop praying."),
    # --- Fan Favorites ---
    F("Zeid", "Power without purpose is just destruction with a name."),
    F("Zeid", "The dark does not make monsters. It only reveals what was already there."),
    F("Gilgamesh", "I have sailed every sea and fought every foe worth fighting. You come close."),
    F("Gilgamesh", "Norg has seen empires come and go. We are still here. Make of that what you will."),
    F("Aldo", "Information is the only currency that never devalues. Remember that."),
    F("Volker", "A San d'Orian knight does not retreat. He tactically advances in a rearward direction."),
    F("Verena", "Every ruin was once someone's greatest achievement. Keep that in mind when you build."),
]

BATTLE_CRIES = [
    F("Warrior", "MIGHTY STRIKES!"), F("Warrior", "Berserk! They'll never bring me down!"),
    F("Warrior", "Warcry! COME ON THEN!"), F("Warrior", "Aggressor! My offense is my defense!"),
    F("Monk", "HUNDRED FISTS! HAAAAAH!"), F("Monk", "Chakra... and back in the fight!"),
    F("Monk", "Counterstance! Hit me. I dare you."), F("Monk", "Boost — Boost — Boost — DRAGON KICK!"),
    F("White Mage", "Curaga IV! Hang on everyone!"), F("White Mage", "Benediction! Everyone get up NOW!"),
    F("White Mage", "Divine Seal — Holy!"), F("White Mage", "Reraise is up. Don't make me use it."),
    F("White Mage", "Shellra V! Barfira! We're ready."),
    F("Black Mage", "MANAFONT! FLARE II!"), F("Black Mage", "Freeze II! Stay still and let it take you!"),
    F("Black Mage", "Thundaga IV — goodbye, cluster."), F("Black Mage", "Magic Burst! FIRE IV!"),
    F("Black Mage", "Elemental Seal — Sleep II. Goodnight, everyone."),
    F("Red Mage", "Chainspell — now BURN!"), F("Red Mage", "Refresh is up, heal through it!"),
    F("Red Mage", "Convert! Don't worry, I planned for this."),
    F("Red Mage", "Enfeebling Magic — Slow, Paralyze, Gravity. You're not going anywhere fast."),
    F("Thief", "Flee! ...and maybe I'll come back for you."),
    F("Thief", "Treasure Hunter — the drops belong to me now."),
    F("Thief", "Sneak Attack — Trick Attack — WEAPONSKILL. Beautiful."),
    F("Thief", "Perfect Dodge! Try hitting air."),
    F("Paladin", "Cover! Get behind me!"), F("Paladin", "Invincible! Nobody dies today!"),
    F("Paladin", "Sentinel. Nothing gets through me."), F("Paladin", "Shield Bash — Stun. Sit down."),
    F("Dark Knight", "Last Resort — SOULEATER!"), F("Dark Knight", "Blood Weapon. Let the pain fuel the fight."),
    F("Dark Knight", "Stun! Not while I'm still standing."),
    F("Beastmaster", "Sic 'em, Courier Carrie!"), F("Beastmaster", "Call Beast! Your time has come!"),
    F("Beastmaster", "Reward — good boy. Now go wreck that NM."),
    F("Bard", "Advancing March — let's go, let's GO!"), F("Bard", "Minuet V — Minne V — Ballad II. You're welcome."),
    F("Bard", "Lullaby! Sweet dreams, everyone except us."), F("Bard", "Elegy! Slow and suffer."),
    F("Bard", "Finale! That buff is gone."),
    F("Ranger", "Eagle Eye Shot — don't blink."), F("Ranger", "Barrage! Count those hits!"),
    F("Ranger", "Shadowbind! You're not going anywhere."),
    F("Samurai", "Meikyo Shisui — TACHI: KAITEN!"), F("Samurai", "Meditate... Meditate... Tachi: Gekko!"),
    F("Samurai", "Third Eye. I see you. And you."), F("Samurai", "Sekkanoki! Two weaponskills, one breath."),
    F("Ninja", "Mijin Gakure! ...Sorry about this."), F("Ninja", "Utsusemi: Ni! Shadows up, let's dance."),
    F("Ninja", "Ni-Ton! Kurayami: Ni! You're blind AND slow."),
    F("Dragoon", "Jump! ...Wyvern, you're up!"), F("Dragoon", "High Jump! Penta Thrust incoming!"),
    F("Dragoon", "Ancient Circle — time to fight dragons with a dragon."),
    F("Summoner", "Ifrit! Burning Strike!"), F("Summoner", "Shiva! Diamond Dust — good night!"),
    F("Summoner", "Fenrir! Eclipse Bite — the hunt is on!"), F("Summoner", "Astral Flow... Odin. ZANTETSUKEN."),
    F("Summoner", "Garuda! Predator Claws — strike from the sky!"),
    F("Blue Mage", "Cannonball — brace yourselves!"), F("Blue Mage", "Magic Hammer! TP for me, nothing for you."),
    F("Blue Mage", "Actinic Burst! Now you're blinded AND silenced."),
    F("Corsair", "Bolter's Roll — snake eyes baby!"), F("Corsair", "Chaos Roll! We live and die by the numbers!"),
    F("Corsair", "Leaden Salute! Call it a calculated risk."), F("Corsair", "Quick Draw! No time to dodge."),
    F("Puppetmaster", "Activate! Stringing Pummel!"), F("Puppetmaster", "Overdrive! Maximum pain."),
    F("Dancer", "Saber Dance — let's go!"), F("Dancer", "Reverse Flourish! TP refunded, full house."),
    F("Dancer", "Curing Waltz IV! Nobody asks, everybody gets healed."),
    F("Dancer", "Haste Samba! Keep up!"), F("Dancer", "Violent Flourish! Stunned and sorry."),
    F("Scholar", "Tabula Rasa — this ends NOW!"), F("Scholar", "Sublimation. Patience. Power. Repeat."),
    F("Scholar", "Manifestation — party-wide Sleep II. Night night."),
    F("Scholar", "Enlightenment! Both arts at once. You're welcome."),
    F("Geomancer", "Indi-Refresh — hold formation!"), F("Geomancer", "Geo-Malaise! Feel the earth pulling you down."),
    F("Geomancer", "Bolster! The luopan speaks and the land listens."),
    F("Rune Fencer", "Lunge — face the runes!"), F("Rune Fencer", "Vallation — the runes hold. Come closer."),
    F("Rune Fencer", "Pflug! The element bends to my will."), F("Rune Fencer", "Gambit! The runes choose the battlefield."),
]

MOOGLE_QUIPS = [
    F("Moogle", "Kupo! Your delivery has arrived, kupo! Please sign here... and here... and here, kupo!"),
    F("Moogle", "Kupo kupo! I've been waiting forever, kupo! Do you know what time it is, kupo?"),
    F("Moogle", "Your Mog House is a mess, kupo! I've done my best but I am not a miracle worker, kupo!"),
    F("Moogle", "Kupoooo! A letter arrived for you! I did NOT read it. (I read it.) Kupo!"),
    F("Moogle", "Kupo! The Mog Locker is almost full! Consider throwing something away, kupo!"),
    F("Moogle", "Kupo! I baked you some kupo nuts but then I ate them. I'm sorry, kupo!"),
    F("Moogle", "Kupo! You've been adventuring so long even the monsters feel sorry for you, kupo!"),
    F("Conquest Tally Moogle", "Kupo! Sandoria is in first this week! ...barely, kupo."),
    F("Moogle", "Rest here, kupo! Your Mog House is always waiting for you, kupo!"),
    F("Nomad Moogle", "Kupo! Out here in the field, even moogles must be brave, kupo!"),
    F("Moogle", "Kupo! I tried to reorganize your bazaar. I may have sold something important, kupo."),
    F("Moogle", "Kupo! Your Mog Garden needs attention! The crops are expressing frustration, kupo."),
    F("Rent-a-Room Moogle", "Kupo! Resting is not laziness, kupo! It is strategic recovery! Kupo!"),
    F("Moogle", "Kupo! The Auction House rejected your listing again. Perhaps price it lower, kupo?"),
    F("Moogle", "Kupo! Another adventurer asked me what you do for a living. I had no good answer, kupo."),
    F("Moogle", "Kupo! I polished all your equipment while you were out! The ones I could lift, kupo."),
    F("Moogle", "Kupo! Someone slipped a note under the door saying 'Tell your adventurer to reraise.' Very mysterious, kupo."),
    F("Moogle", "Kupo! I tried cooking your rations. The Mog House still smells a little unusual, kupo."),
    F("Moogle", "Kupo! I was going to clean but then I took a nap. It is very cozy in here, kupo."),
    F("Moogle", "Your fame has grown so much, kupo! Even I get recognized when I mention your name! Mostly confused looks, kupo!"),
    F("Moogle", "Kupo! I accepted a quest on your behalf while you were gone. I am not certain it was a good idea, kupo."),
    F("Moogle", "Kupo! A Goblin came to the door asking for you. I told him you were out. He seemed disappointed, kupo."),
]

EMOTE_FLAVOR = [
    F("Adventurer", "/cry — You sit down and cry. It doesn't help. The exp loss was real."),
    F("Adventurer", "/comfort — You offer a word of comfort. Nobody feels better."),
    F("Adventurer", "/panic — You panic! The Snoll Tzar is still alive at 0%!"),
    F("Adventurer", "/joy — You leap for joy! You finally got your Haubergeon drop!"),
    F("Adventurer", "/kneel — You kneel before the party leader. They have no idea what they're doing."),
    F("Adventurer", "/fume — You fume with irritation. The bard put on Minuet again."),
    F("Adventurer", "/slap — You slap yourself. You forgot to reraise."),
    F("Adventurer", "/shocked — You are shocked! Someone actually won the claim!"),
    F("Adventurer", "/wave — You wave cheerfully. The NM pops behind you."),
    F("Adventurer", "/poke — You poke your fellow adventurer. They are still AFK in Jeuno."),
    F("Adventurer", "/stagger — You stagger! You were not expecting Absolute Virtue to use Manafont."),
    F("Adventurer", "/cheer — You cheer! The RNG finally blessed you after 47 runs."),
    F("Adventurer", "/think — You think. Was Salvage always this hard, or did you get worse?"),
    F("Adventurer", "/sigh — You sigh deeply. The NM died while you were zoning. Again."),
    F("Adventurer", "/blush — You blush. You pulled a mob you shouldn't have. Everyone saw."),
    F("Adventurer", "/sulk — You sulk. The Ninja forgot to put shadows up again."),
    F("Adventurer", "/dance — You dance! The party wipes. Coincidence? Probably not."),
    F("Adventurer", "/bow — You bow respectfully. The Beastmaster just solo'd a god-tier NM."),
    F("Adventurer", "/sweat — You break into a cold sweat. 30 minutes left on the Dynamis clock."),
    F("Adventurer", "/pray — You pray. The ??? spawns. The NM is not what you hoped."),
    F("Adventurer", "/grin — You grin. You got the claim. Let the suffering begin."),
    F("Adventurer", "/no — You shake your head. Someone asked if we should try AV with eight people."),
    F("Adventurer", "/yes — You nod enthusiastically. You have no idea what you just agreed to."),
    F("Adventurer", "/laugh — You laugh. The Goblin dropped absolutely nothing. Again."),
    F("Adventurer", "/angry — You are angry! Someone lotted on gear they can't even equip!"),
    F("Adventurer", "/relieved — You sigh with relief. The White Mage remembered to bring Echo Drops."),
]

AVATAR_QUOTES = [
    F("Ifrit", "Come! Bathe in my flames and be purified... or perish in the attempt!"),
    F("Ifrit", "The fires of Ifrit consume all who stand against us. Are you prepared, summoner?"),
    F("Ifrit", "Burning Strike! Let the conflagration begin!"),
    F("Ifrit", "Crimson Howl! Let the fire in your veins ignite!"),
    F("Ifrit", "Flaming Crush! I will grind you to cinders!"),
    F("Ifrit", "The weak fear fire. The strong learn to wield it."),
    F("Shiva", "Your enemies shall know the cold embrace of oblivion. I will see to it personally."),
    F("Shiva", "Diamond Dust! Let the blizzard swallow them whole."),
    F("Shiva", "The cold does not discriminate. Neither shall I."),
    F("Shiva", "Heavenly Strike! Even the sky freezes at my command."),
    F("Shiva", "Ice is patient. It waits. Then it entombs."),
    F("Ramuh", "Judgment Bolt! Let the heavens themselves bear witness!"),
    F("Ramuh", "Foolish mortals... you would challenge the storm itself?"),
    F("Ramuh", "Chaotic Strike! Lightning does not ask where it may fall."),
    F("Ramuh", "I am older than your kingdoms. I have outlasted greater arrogance than yours."),
    F("Titan", "Geocrush! The very earth rises to answer my call!"),
    F("Titan", "You stand upon my domain. Every stone, every root answers to me."),
    F("Titan", "Solid as the mountain. Unyielding as the stone. That is my covenant with you."),
    F("Titan", "Rock Buster! The earth itself becomes your enemy!"),
    F("Titan", "The earth does not move quickly. But when it does, nothing survives."),
    F("Leviathan", "Tidal Wave! Let the depths reclaim what is theirs!"),
    F("Leviathan", "The sea is patient. It has swallowed greater armies than yours."),
    F("Leviathan", "All rivers return to me in time. As will you."),
    F("Leviathan", "Spinning Dive! The current answers my call!"),
    F("Leviathan", "Drown in the deep. I have been waiting at the bottom for you."),
    F("Garuda", "Predator Claws! The gale answers my call!"),
    F("Garuda", "You cannot outrun the wind. You cannot hide from the sky."),
    F("Garuda", "The storm does not ask permission. Nor do I."),
    F("Garuda", "Aerial Blast! Not even the air is safe from my wrath!"),
    F("Garuda", "The wind remembers everything it has touched. I remember your failures."),
    F("Fenrir", "Eclipse Bite! The moon darkens and the hunt begins!"),
    F("Fenrir", "The lone wolf does not hunger. He endures, and he strikes true."),
    F("Fenrir", "Run if you must. The night is vast... but I am faster."),
    F("Fenrir", "Howling Moon! I call the darkness, and the darkness answers."),
    F("Fenrir", "The hunt does not end at dawn. It only pauses."),
    F("Diabolos", "Ruinous Omen! Your nightmares take shape!"),
    F("Diabolos", "Reality is merely the dream you have not woken from yet."),
    F("Diabolos", "Come, step into the dark. I have been waiting for you here."),
    F("Diabolos", "Nightmare! Sleep, and dream of your failures."),
    F("Diabolos", "Dark Orb! Let the gravity of your despair consume you."),
    F("Carbuncle", "Ruby Light! Let the radiance shield us!"),
    F("Carbuncle", "Do not be afraid. I am here, and the light will hold."),
    F("Carbuncle", "Even in the darkest place, a single gem can illuminate the way."),
    F("Carbuncle", "Soothing Ruby! Rest now. I'll keep watch."),
    F("Carbuncle", "Meteorite! Even small things can shake the world."),
    F("Cait Sith", "Reraise! The battle is not over while breath remains!"),
    F("Cait Sith", "The stars whisper strange things tonight. You'd do well to listen."),
    F("Cait Sith", "Fate is a fickle thing. Even I cannot read it clearly... most of the time."),
    F("Cait Sith", "The stars have seen this moment coming. Whether comfort or warning, I leave to you."),
    F("Alexander", "Holy! Divine judgment descends upon the unworthy!"),
    F("Alexander", "Steel yourself. The fortress does not tremble. Neither shall we."),
    F("Alexander", "Justice is not blind. It sees clearly, and it finds you wanting."),
    F("Alexander", "Perfect Defense! No force in this world shall pass!"),
    F("Alexander", "Radiant Sacrament! The light purifies all impurity."),
    F("Odin", "Zantetsuken! One stroke. One breath. One end."),
    F("Odin", "Sleipnir carries me across eight worlds. There is nowhere you can flee."),
    F("Odin", "All things must end. I am simply the instrument of that inevitability."),
    F("Odin", "Gungnir! The spear of the Allfather does not miss."),
    F("Odin", "I ride not toward death, but past it. What comes after is your concern."),
    F("Bahamut", "Megaflame! The elder dragon speaks, and the world burns!"),
    F("Bahamut", "I have watched civilizations rise and crumble. You are but a moment in the tide."),
    F("Bahamut", "Gigaflare! There is no shelter from my wrath!"),
    F("Bahamut", "You sought to bind the king of dragons? Amusing. And brief."),
    F("Bahamut", "My patience has outlasted empires. Do not mistake it for weakness."),
    F("Phoenix", "Rebirth! From the ash, we rise once more!"),
    F("Phoenix", "Death is not the end for those with the will to return. Rise."),
    F("Phoenix", "Flames that destroy also renew. Do not fear the fire."),
    F("Phoenix", "I have died a thousand times. Each time, I return stronger. Remember that."),
    F("Phoenix", "Flames of Rebirth! What burns away is replaced by something stronger."),
    F("Atomos", "The void consumes all. Distance is meaningless. Resistance is futile."),
    F("Atomos", "Drawn in... drawn in... all things return to the darkness in the end."),
    F("Atomos", "Comet! Even the stars are not safe from my hunger."),
    F("Atomos", "You cannot fight the void. You can only delay the inevitable."),
    F("Atomos", "Slowga... Graviga... the collapse has already begun."),
]

NOTORIOUS_MONSTERS = [
    F("Absolute Virtue", "You thought Jailer of Love was the hard one. Adorable."),
    F("Absolute Virtue", "Manafont. Again. Have you considered a different hobby?"),
    F("Absolute Virtue", "Mijin Gakure? How quaint. I heal for that amount."),
    F("Pandemonium Warden", "18 hours. You had 18 hours and still couldn't finish the job."),
    F("Pandemonium Warden", "Another form. Another chance to reconsider your life choices."),
    F("Nidhogg", "Come for the wyrm, stay for the trauma. The drop rate appreciates your optimism."),
    F("Fafnir", "Another party shattered on my scales. The Haubergeon is not for the weak."),
    F("Fafnir", "You claimed the claim. Congratulations on the first five percent."),
    F("Kirin", "I have seen a thousand alliance wipes. Yours was not particularly memorable."),
    F("Kirin", "The Four Gods answer to me. What exactly do you answer to?"),
    F("Cerberus", "Three heads means three times the disappointment. I admire your persistence."),
    F("Khimaira", "You came with twelve. You left with fewer. I consider that a success."),
    F("Ouryu", "The clouds are my domain. Your airship does not impress me."),
    F("King Behemoth", "You claimed the King. The King finds this... premature."),
    F("King Behemoth", "Thunderbolt. Take your time recovering. I'll wait."),
    F("Genbu", "The north wind answers to me. Your resist rate does not."),
    F("Byakko", "Speed means nothing if your Utsusemi fails at the critical moment."),
    F("Suzaku", "I wonder, does your party always argue about loot before the fight is over?"),
    F("Seiryu", "A worthy effort. Tragically, effort alone does not equal victory."),
    F("Dynamis Lord", "You have cleared every zone. And still you come. I respect the stubbornness."),
    F("Dynamis Lord", "Time is my weapon. Your clock is already running."),
    F("Proto-Ultima", "Adaptive defense engaged. Perhaps adapt your strategy as well."),
    F("Proto-Omega", "Your weaponskills were impressive. Right up until they weren't."),
    F("Tinnin", "The Salaheem's Sentinel was not prepared for this. Neither were you."),
    F("Lilith", "You defeated me once. I simply have more forms than you have patience."),
]

CITY_FLAVOR = [
    F("Jeuno Gate Guard", "All caravans must register before proceeding through Jeuno. Next!"),
    F("Jeuno Merchant", "Ah, the famous adventurer! Come, my prices are only slightly criminal."),
    F("Bastok Blacksmith", "The Republic's steel is the finest in Vana'diel. Anyone who says otherwise hasn't tried it."),
    F("Bastok Miner", "The Palborough Mines don't dig themselves. Mostly because of the Quadavs."),
    F("Windurst Tarutaru", "Taru taru! You look like someone who needs a spell researched, taru!"),
    F("Windurst Scholar", "The Full Moon Fountain's magic is not something we fully understand. That is what makes it exciting, taru!"),
    F("San d'Oria Knight", "The Kingdom's honor is maintained at all borders. State your business, adventurer."),
    F("San d'Oria Noble", "San d'Oria has stood for a thousand years. Assuming the Orcs cooperate, a thousand more."),
    F("Aht Urhgan Merchant", "You have the look of someone who has coin and no idea where to spend it. Welcome."),
    F("Aht Urhgan Guard", "The Empress's peace extends to all within these walls. Try not to test it."),
    F("Selbina Shepherd", "The Crag of Mea isn't far. Don't say I didn't warn you about the Goblins."),
    F("Selbina Fisher", "The bay's good for fishing if the Sahagins aren't in a mood. They're usually in a mood."),
    F("Rabao Trader", "Quicksand Caves, you say? My condolences and my best wishes. Mostly condolences."),
    F("Norg Pirate", "Everyone who walks through that door owes Gilgamesh something. What do you owe?"),
    F("Norg Lookout", "We don't ask where the gil comes from here. That keeps things peaceful."),
    F("Tavnazian NPC", "We don't get many visitors here. Most who come don't come back. ...That wasn't meant to sound ominous."),
    F("Whitegate Guard", "Entry to Aht Urhgan Whitegate requires documentation. Your fame precedes you. Enter."),
    F("Adoulin Pioneer", "Ulbuka is not a place for the unprepared. It is also not a place for the prepared. It is simply dangerous."),
    F("Adoulin Settler", "They say the jungle has a thousand ways to kill you. I've personally counted seventeen so far this week."),
    F("Mhaura Ferryman", "Selbina or Mhaura — that's the route. Nothing in between except sea and regret."),
    F("Kazham Elder", "The Mithra have lived in these jungles since before your nations had names. Show some respect."),
    F("Ru'Lude Gardens Butler", "The Archduke receives visitors by appointment. Your heroism may expedite that process."),
]

PLAYER_SAY = [
    F("Anonymous WHM", "Need WHM? I've been sitting here for 3 hours. Just saying."),
    F("Anonymous WHM", "I WILL cast Raise on you. After I finish my Hi-Potion. ...And a sandwich."),
    F("Anonymous WHM", "Healing is thankless work. Do you say thank you when your liver functions? Exactly."),
    F("Anonymous BRD", "I have Elegy but I need refresh first. ...And Ballad. ...And a tank. Anyone?"),
    F("Anonymous BRD", "I'll put on Minuet as soon as the BLM stops complaining about Minuet. So: never."),
    F("Anonymous BLM", "WHAT DO YOU MEAN THE SKILLCHAIN WINDOW CLOSED. I WAS CASTING."),
    F("Anonymous BLM", "I need to nuke. The tank needs to hold hate. These are two separate problems."),
    F("Anonymous RDM", "I can enfeeble, refresh, heal, and Convert. What I cannot do is carry the whole party. But I will try."),
    F("Anonymous THF", "I'm not lotting on your gear. I'm lotting on MY gear that the RNG put in your class's loot table."),
    F("Anonymous THF", "Flee is a utility skill. Primarily the utility of not dying. You're welcome."),
    F("Anonymous PLD", "I have 3,000 HP and Invincible and you STILL pulled hate. I am in awe."),
    F("Anonymous PLD", "Cover is for protecting allies. I will not explain why I used it on the Goblin."),
    F("Anonymous MNK", "Hundred Fists is a two-hour ability. Using it on every Goblin is fine. I have decided."),
    F("Anonymous DRK", "Souleater trades HP for damage. I'm at 12 HP. This is fine. This is fine."),
    F("Anonymous SMN", "My avatar costs MP. Your complaints about my avatar cost me sanity. We're both losing."),
    F("Anonymous DRG", "My Wyvern is fine. My Wyvern is always fine. Please stop asking about my Wyvern."),
    F("Anonymous COR", "Snake eyes. Again. The dice are broken. The dice are ALWAYS BROKEN."),
    F("Anonymous DNC", "I can heal AND deal damage AND apply status effects. Please stop ignoring me at parties."),
    F("Anonymous NIN", "Utsusemi is not a cooldown. It's a lifestyle. A very stressful lifestyle."),
    F("Anonymous SAM", "I have 3,000% TP. I have been holding it for 20 minutes. Someone please skillchain with me."),
    F("Anonymous GEO", "The luopan is fine where it is. No, I will not move it. Yes, it matters."),
]

ABYSSEA_QUOTES = [
    F("Joachim", "Welcome to Abyssea, adventurer. The Dominion thanks you for your continued sacrifice."),
    F("Joachim", "The Cruor flows freely here. Use it wisely — and spend it before you return. You cannot take it with you."),
    F("Resistance Fighter", "Out here, time moves differently. Stay too long and you may not recognize the world you came from."),
    F("Resistance Fighter", "The visitant limit is not a suggestion. I have seen what happens when it's ignored."),
    F("Visitant NPC", "You smell of the outside world. That means you're either new or lucky. Either way, welcome."),
    F("Abyssea Conflux", "Traverse point locked. This is as far as your judgment allows. For now."),
    F("Primeval Brew Vendor", "One brew. One chance. Do not waste it on a placeholder."),
    F("Dominion Soldier", "We do not speak of how many have come before you. The number is not encouraging."),
    F("Cavernous Maw", "Entrance open. Timer started. Do not dawdle. Abyssea does not reward dawdling."),
    F("Survivor NPC", "I came here for adventure. I stayed because I forgot what day it was. And then the week. And then the year."),
    F("Abyssean NPC", "The atma you carry is the distilled essence of something that was once very hard to kill. Use it accordingly."),
    F("Resistance NPC", "The lights in the sky are not stars. I stopped asking what they are. You should too."),
    F("Emissary of the Veil", "Beyond this point the rules of your world do not apply. They were optional here to begin with."),
    F("Dominion Tactician", "Provenance. Empyreal Paradox. Vunkerl. The names change. The difficulty does not."),
    F("Abyssea Pilgrim", "I found what I was looking for out here. I am still not sure I wanted it."),
]

# ─────────────────────────────────────────────
#  Seasonal Quote Pools
# ─────────────────────────────────────────────

STARLIGHT_QUOTES = [
    F("Starlight Moogle", "Kupo! The Starlight Celebration fills even this moogle's heart with warmth, kupo!"),
    F("Starlight Moogle", "Kupo! Santa Claus Moogle has been VERY busy this year. I am exhausted, kupo."),
    F("Shantotto", "Oh ho ho! Even the great Shantotto takes a moment for Starlight! Oh ho ho!"),
    F("Moogle", "Kupo! I wrapped your presents! I also peeked at them. They are wonderful, kupo."),
    F("Iroha", "Even in a world threatened by darkness, the Starlight Celebration brings light. Hold onto that, adventurer."),
    F("Lion", "Starlight in Vana'diel. Even pirates take the night off. ...Mostly."),
    F("Prishe", "Don't get mushy on me. Just because it's Starlight doesn't mean the world stops needing saving."),
]

HARVEST_QUOTES = [
    F("Spooky Moogle", "Kupo! The Harvest Festival is upon us! I put on a scary face, kupo! ...You cannot tell the difference, kupo."),
    F("Shantotto", "Oh ho ho! Frightening costumes? How adorable. I am the most terrifying thing in Vana'diel already!"),
    F("Diabolos", "You require no costume, adventurer. The darkness suits you naturally."),
    F("Zeid", "Even in celebration, the shadows are long this time of year. Eyes open."),
    F("Cait Sith", "Mrrrow... The veil thins at Harvest. Be careful what ye call across it."),
    F("Moogle", "Kupo! A skeleton came to the door! I gave it candy! ...It was just a Galka in a costume, kupo. Probably."),
    F("Fenrir", "The moon is full and hungry tonight. So am I."),
]

VALENTIONES_QUOTES = [
    F("Valentione Moogle", "Kupo! Love is in the air of Vana'diel, kupo! Have you given chocolates to your adventuring companions, kupo?"),
    F("Shantotto", "Oh ho ho! Valentione's Day! Even love cannot resist the great Shantotto!"),
    F("Ulmia", "A song for someone you love never sounds wrong, no matter how many notes you miss."),
    F("Lilisette", "Dance for someone today. Even if it's embarrassing. Especially if it's embarrassing."),
    F("Carbuncle", "Ruby Light carries warmth as well as protection. Today, focus on the warmth."),
    F("Aphmau", "An empress without someone to protect is just a title. Cherish the people around you."),
    F("Moogle", "Kupo! I made chocolates for you, kupo! I also ate most of them. There is one left, kupo. It is slightly licked."),
]

# ─────────────────────────────────────────────
#  Expansion Lookup
# ─────────────────────────────────────────────

_ZM_SPEAKERS   = {"Kam'lanaut", "Eald'narche", "Lion"}
_COP_SPEAKERS  = {"Prishe", "Selh'teus", "Nag'molada", "Ulmia", "Tenzen"}
_TOAU_SPEAKERS = {"Aphmau", "Luzaf", "Shantotto", "Lehko Habhoka"}
_WOTG_SPEAKERS = {"Lilisette", "Cait Sith", "Portia", "Lilith"}
_SOA_SPEAKERS  = {"Arciela", "Ygnas", "Teodor"}
_ROV_SPEAKERS  = {"Iroha", "Bahamut", "Altana", "Promathia"}

EXPANSION_QUOTES: dict[str, list] = {
    "zilart":  [q for q in NPC_STORY if q[0] in _ZM_SPEAKERS],
    "cop":     [q for q in NPC_STORY if q[0] in _COP_SPEAKERS],
    "toau":    [q for q in NPC_STORY if q[0] in _TOAU_SPEAKERS],
    "wotg":    [q for q in NPC_STORY if q[0] in _WOTG_SPEAKERS],
    "soa":     [q for q in NPC_STORY if q[0] in _SOA_SPEAKERS],
    "rov":     [q for q in NPC_STORY if q[0] in _ROV_SPEAKERS],
    "abyssea": list(ABYSSEA_QUOTES),
}

# ─────────────────────────────────────────────
#  Combined Pools
# ─────────────────────────────────────────────

ALL_QUOTES = (
    NPC_STORY + BATTLE_CRIES + MOOGLE_QUIPS + EMOTE_FLAVOR +
    AVATAR_QUOTES + NOTORIOUS_MONSTERS + CITY_FLAVOR +
    PLAYER_SAY + ABYSSEA_QUOTES
)

WEIGHTED_POOL = (
    NPC_STORY      * 3 +
    BATTLE_CRIES   * 3 +
    MOOGLE_QUIPS   * 2 +
    EMOTE_FLAVOR   * 2 +
    AVATAR_QUOTES  * 2 +
    NOTORIOUS_MONSTERS * 1 +
    CITY_FLAVOR    * 2 +
    PLAYER_SAY     * 2 +
    ABYSSEA_QUOTES * 1
)

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def get_seasonal_pool() -> list | None:
    month = datetime.now().month
    if month == 12: return STARLIGHT_QUOTES
    if month == 10: return HARVEST_QUOTES
    if month == 2:  return VALENTIONES_QUOTES
    return None


def get_quote_by_category(category: str) -> tuple[str, str, str]:
    categories = {
        "npc":     NPC_STORY,
        "battle":  BATTLE_CRIES,
        "moogle":  MOOGLE_QUIPS,
        "emote":   EMOTE_FLAVOR,
        "avatar":  AVATAR_QUOTES,
        "nm":      NOTORIOUS_MONSTERS,
        "city":    CITY_FLAVOR,
        "player":  PLAYER_SAY,
        "abyssea": ABYSSEA_QUOTES,
    }
    pool = categories.get(category.lower(), ALL_QUOTES)
    return random.choice(pool)


def format_quote(speaker: str, quote: str, source: str = FAN) -> str:
    return f"📜 **{speaker}**\n*\"{quote}\"*\n{source}"
