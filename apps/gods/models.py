"""Gods models."""

from typing import Any

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Pantheon(models.TextChoices):
    """Available pantheons for gods."""

    GREEK = "greek", "Greek"
    AZTEC = "aztec", "Aztec"
    CHINESE = "chinese", "Chinese"
    EGYPTIAN = "egyptian", "Egyptian"
    NORDIC = "nordic", "Nordic"


class Role(models.TextChoices):
    """Available roles for gods."""

    ASSASSIN = "assassin", "Assassin"
    TANK = "tank", "Tank"
    SUPPORT = "support", "Support"
    MAGE = "mage", "Mage"
    ARCHER = "archer", "Archer"


CLASS_ADVANTAGES: dict[str, str] = {
    "assassin": "mage",
    "tank": "assassin",
    "mage": "tank",
    "archer": "support",
    "support": "archer",
}

CLASS_ADVANTAGE_BONUS = 0.15

GOD_SKILLS: dict[str, dict[str, dict[str, Any]]] = {
    # Greek Gods
    "Zeus": {
        "basic1": {
            "name": _("Thunderbolt"),
            "desc": _("Hurls lightning dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Storm Call"),
            "desc": _("Summons storm dealing {dmg} AoE damage"),
            "multiplier": 0.7,
        },
        "ultimate": {
            "name": _("Wrath of Olympus"),
            "desc": _("Divine lightning storm dealing {dmg} damage to all enemies"),
            "multiplier": 3.5,
        },
    },
    "Poseidon": {
        "basic1": {
            "name": _("Tidal Wave"),
            "desc": _("Crashing wave dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Ocean's Grasp"),
            "desc": _("Water tentacles dealing {dmg} damage + slow"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("Leviathan's Fury"),
            "desc": _("Summons sea monster dealing {dmg} damage to all"),
            "multiplier": 3.2,
        },
    },
    "Hades": {
        "basic1": {
            "name": _("Soul Drain"),
            "desc": _("Steals life dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Shadow Step"),
            "desc": _("Phase through shadows dealing {dmg} damage"),
            "multiplier": 1.1,
        },
        "ultimate": {
            "name": _("Gate of the Underworld"),
            "desc": _("Opens hell portal dealing {dmg} damage, ignores armor"),
            "multiplier": 3.0,
        },
    },
    "Ares": {
        "basic1": {
            "name": _("War Cry"),
            "desc": _("Battle shout dealing {dmg} damage + fear"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Bloodlust Strike"),
            "desc": _("Frenzied attack dealing {dmg} damage"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("God of War"),
            "desc": _("Enters battle frenzy dealing {dmg} damage to all enemies"),
            "multiplier": 2.8,
        },
    },
    "Athena": {
        "basic1": {
            "name": _("Wisdom's Shield"),
            "desc": _("Protective barrier absorbing {dmg} damage"),
            "multiplier": 0.5,
        },
        "basic2": {
            "name": _("Strategic Strike"),
            "desc": _("Calculated attack dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "ultimate": {
            "name": _("Aegis of Athena"),
            "desc": _("Invulnerable shield for team, reflects {dmg} damage"),
            "multiplier": 2.5,
        },
    },
    "Apollo": {
        "basic1": {
            "name": _("Sun Arrow"),
            "desc": _("Solar projectile dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Healing Light"),
            "desc": _("Restores {dmg} HP to ally"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Solar Flare"),
            "desc": _("Blinding sun burst dealing {dmg} damage to all"),
            "multiplier": 3.0,
        },
    },
    "Artemis": {
        "basic1": {
            "name": _("Moonshot"),
            "desc": _("Lunar arrow dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Beast Call"),
            "desc": _("Summons wolf dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "ultimate": {
            "name": _("Huntress's Mark"),
            "desc": _("Marks all enemies, arrows deal {dmg} damage each"),
            "multiplier": 2.8,
        },
    },
    "Hermes": {
        "basic1": {
            "name": _("Swift Strike"),
            "desc": _("Lightning-fast attack dealing {dmg} damage"),
            "multiplier": 0.75,
        },
        "basic2": {
            "name": _("Trickster's Dash"),
            "desc": _("Dodges and strikes for {dmg} damage"),
            "multiplier": 0.9,
        },
        "ultimate": {
            "name": _("Messenger's Wrath"),
            "desc": _("Strikes all enemies in {dmg} speed burst"),
            "multiplier": 2.5,
        },
    },
    "Hephaestus": {
        "basic1": {
            "name": _("Forge Hammer"),
            "desc": _("Molten strike dealing {dmg} damage + burn"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Iron Wall"),
            "desc": _("Raises shield blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Volcanic Eruption"),
            "desc": _("Erupts ground dealing {dmg} damage to all enemies"),
            "multiplier": 3.0,
        },
    },
    "Demeter": {
        "basic1": {
            "name": _("Nature's Grasp"),
            "desc": _("Vines deal {dmg} damage + root"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Harvest Blessing"),
            "desc": _("Heals ally for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Earth's Embrace"),
            "desc": _("Regenerates team, deals {dmg} damage to enemies"),
            "multiplier": 2.2,
        },
    },
    # Aztec Gods
    "Huitzilopochtli": {
        "basic1": {
            "name": _("Sun Spear"),
            "desc": _("Solar lance dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Hummingbird Strike"),
            "desc": _("Swift attack dealing {dmg} damage"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("War of the Sun"),
            "desc": _("Summons solar fire dealing {dmg} damage to all"),
            "multiplier": 3.0,
        },
    },
    "Quetzalcoatl": {
        "basic1": {
            "name": _("Feather Wind"),
            "desc": _("Wind blade dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Serpent Coil"),
            "desc": _("Heals ally for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Plumed Serpent"),
            "desc": _("Transforms into dragon, deals {dmg} damage to all"),
            "multiplier": 3.5,
        },
    },
    "Tezcatlipoca": {
        "basic1": {
            "name": _("Shadow Claw"),
            "desc": _("Dark strike dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Smoke Mirror"),
            "desc": _("Creates illusion, blocks {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Night Jaguar"),
            "desc": _("Becomes invisible, deals {dmg} damage to all"),
            "multiplier": 3.2,
        },
    },
    "Tlaloc": {
        "basic1": {
            "name": _("Rain Drop"),
            "desc": _("Water bolt dealing {dmg} damage"),
            "multiplier": 0.75,
        },
        "basic2": {
            "name": _("Storm Cloud"),
            "desc": _("Heals team for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Great Flood"),
            "desc": _("Drowns battlefield dealing {dmg} damage to all"),
            "multiplier": 2.8,
        },
    },
    "Xipe Totec": {
        "basic1": {
            "name": _("Flayed Strike"),
            "desc": _("Skinning blow dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Rebirth Skin"),
            "desc": _("Sheds skin, heals {dmg} HP"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Lord of Flayed"),
            "desc": _("Wears enemy skin, deals {dmg} damage to all"),
            "multiplier": 3.0,
        },
    },
    "Coatlicue": {
        "basic1": {
            "name": _("Serpent Skirt"),
            "desc": _("Snake bite dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Earth Mother"),
            "desc": _("Raises defense, blocks {dmg} damage"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Mother of Gods"),
            "desc": _("Consumes all, deals {dmg} damage to enemies"),
            "multiplier": 2.5,
        },
    },
    "Mictlantecuhtli": {
        "basic1": {
            "name": _("Bone Spear"),
            "desc": _("Skeletal lance dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Death Gaze"),
            "desc": _("Terrifying stare dealing {dmg} damage"),
            "multiplier": 1.1,
        },
        "ultimate": {
            "name": _("Underworld Gate"),
            "desc": _("Opens portal to Mictlan, deals {dmg} damage to all"),
            "multiplier": 3.0,
        },
    },
    "Xochiquetzal": {
        "basic1": {
            "name": _("Flower Petal"),
            "desc": _("Petal storm dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Beauty's Charm"),
            "desc": _("Charms enemy, heals {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Garden of Eden"),
            "desc": _("Summons paradise garden, deals {dmg} damage to all"),
            "multiplier": 2.8,
        },
    },
    "Xiuhtecuhtli": {
        "basic1": {
            "name": _("Obsidian Blade"),
            "desc": _("Volcanic glass dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Fire Walker"),
            "desc": _("Lava step dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "ultimate": {
            "name": _("Volcanic Eruption"),
            "desc": _("Destroys mountain dealing {dmg} damage to all"),
            "multiplier": 3.2,
        },
    },
    "Coyolxauhqui": {
        "basic1": {
            "name": _("Moon Disk"),
            "desc": _("Lunar throw dealing {dmg} damage"),
            "multiplier": 0.75,
        },
        "basic2": {
            "name": _("Silver Light"),
            "desc": _("Moonbeam healing {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Dismembered Moon"),
            "desc": _("Shatters moon, deals {dmg} damage to all"),
            "multiplier": 2.5,
        },
    },
    "Ehecatl": {
        "basic1": {
            "name": _("Wind Gust"),
            "desc": _("Hurricane blast dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Breath of Life"),
            "desc": _("Heals ally for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Great Hurricane"),
            "desc": _("Summons storm dealing {dmg} damage to all"),
            "multiplier": 3.0,
        },
    },
    "Tonatiuh": {
        "basic1": {
            "name": _("Sun Ray"),
            "desc": _("Solar beam dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Fifth Sun"),
            "desc": _("Raises attack by {dmg}"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Solar Eclipse"),
            "desc": _("Darkens sun, deals {dmg} damage to all"),
            "multiplier": 2.8,
        },
    },
    "Taurus": {
        "basic1": {
            "name": _("Earth Stomp"),
            "desc": _("Ground shake dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Bulwark"),
            "desc": _("Raises defense, blocks {dmg} damage"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Immovable Object"),
            "desc": _("Becomes unkillable for 2 turns, reflects {dmg} damage"),
            "multiplier": 3.0,
        },
    },
    "Gemini": {
        "basic1": {
            "name": _("Twin Strike"),
            "desc": _("Dual attack dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Mirror Image"),
            "desc": _("Creates clone dealing {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Duality Cascade"),
            "desc": _("Infinite clones deal {dmg} damage to all"),
            "multiplier": 3.2,
        },
    },
    "Cancer": {
        "basic1": {
            "name": _("Shell Guard"),
            "desc": _("Hides in shell, blocks {dmg} damage"),
            "multiplier": 0.5,
        },
        "basic2": {
            "name": _("Tidal Claw"),
            "desc": _("Water-infused claw dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "ultimate": {
            "name": _("Ocean's Fortress"),
            "desc": _("Creates water fortress, heals team {dmg} HP"),
            "multiplier": 2.0,
        },
    },
    "Leo": {
        "basic1": {
            "name": _("Lion's Roar"),
            "desc": _("Intimidating roar dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Royal Pounce"),
            "desc": _("Leaping strike dealing {dmg} damage"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("King of Beasts"),
            "desc": _("Summons lion spirits dealing {dmg} damage to all"),
            "multiplier": 3.0,
        },
    },
    "Virgo": {
        "basic1": {
            "name": _("Purifying Light"),
            "desc": _("Cleansing beam dealing {dmg} damage"),
            "multiplier": 0.75,
        },
        "basic2": {
            "name": _("Healing Touch"),
            "desc": _("Restores {dmg} HP to ally"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Virgin's Grace"),
            "desc": _("Full team heal + {dmg} damage to enemies"),
            "multiplier": 2.5,
        },
    },
    "Libra": {
        "basic1": {
            "name": _("Balance Strike"),
            "desc": _("Equalizing blow dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Scales of Justice"),
            "desc": _("Redistributes damage, blocks {dmg}"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Cosmic Equilibrium"),
            "desc": _("Balances all HP, deals {dmg} to enemies"),
            "multiplier": 2.8,
        },
    },
    "Scorpio": {
        "basic1": {
            "name": _("Venom Sting"),
            "desc": _("Poisonous strike dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Shadow Ambush"),
            "desc": _("Stealth attack dealing {dmg} damage"),
            "multiplier": 1.1,
        },
        "ultimate": {
            "name": _("Death's Embrace"),
            "desc": _("Lethal poison dealing {dmg} damage over time"),
            "multiplier": 3.0,
        },
    },
    "Sagittarius": {
        "basic1": {
            "name": _("Star Arrow"),
            "desc": _("Cosmic arrow dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Centaur Charge"),
            "desc": _("Galloping strike dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "ultimate": {
            "name": _("Meteor Shower"),
            "desc": _("Rains fire arrows dealing {dmg} damage to all"),
            "multiplier": 3.2,
        },
    },
    "Capricorn": {
        "basic1": {
            "name": _("Mountain Strike"),
            "desc": _("Earth-shaking blow dealing {dmg} damage"),
            "multiplier": 0.75,
        },
        "basic2": {
            "name": _("Sea Goat's Wall"),
            "desc": _("Water-earth shield blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Peak of Ambition"),
            "desc": _("Ascends mountain, deals {dmg} damage to all"),
            "multiplier": 2.8,
        },
    },
    "Aquarius": {
        "basic1": {
            "name": _("Water Bearer's Flow"),
            "desc": _("Cosmic water dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Starlight Rain"),
            "desc": _("Healing rain restoring {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Cosmic Flood"),
            "desc": _("Drowns battlefield dealing {dmg} damage to all"),
            "multiplier": 3.0,
        },
    },
    "Pisces": {
        "basic1": {
            "name": _("Fish Companion"),
            "desc": _("Summons fish dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Dream Wave"),
            "desc": _("Illusion wave dealing {dmg} damage + confuse"),
            "multiplier": 0.8,
        },
        "ultimate": {
            "name": _("Ocean's Dream"),
            "desc": _("Puts enemies to sleep, deals {dmg} damage"),
            "multiplier": 2.5,
        },
    },
    # Chinese Gods
    "Jade Emperor": {
        "basic1": {
            "name": _("Celestial Decree"),
            "desc": _("Divine order dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Heaven's Blessing"),
            "desc": _("Grants shield absorbing {dmg} damage"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Mandate of Heaven"),
            "desc": _("Commands cosmos dealing {dmg} damage to all"),
            "multiplier": 3.5,
        },
    },
    "Sun Wukong": {
        "basic1": {
            "name": _("Staff Strike"),
            "desc": _("Golden staff blow dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Cloud Somersault"),
            "desc": _("Aerial strike dealing {dmg} damage"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("72 Transformations"),
            "desc": _("Shape-shifts into army dealing {dmg} damage"),
            "multiplier": 3.0,
        },
    },
    "Nezha": {
        "basic1": {
            "name": _("Fire Wheel Spin"),
            "desc": _("Flaming wheels dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Lotus Armor"),
            "desc": _("Blooms shield blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Three Heads Six Arms"),
            "desc": _("Unleashes full form dealing {dmg} damage"),
            "multiplier": 3.2,
        },
    },
    "Erlang Shen": {
        "basic1": {
            "name": _("Third Eye Beam"),
            "desc": _("Truth-seeing beam dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Heavenly Spear"),
            "desc": _("Divine thrust dealing {dmg} damage"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("Demon Queller"),
            "desc": _("Reveals all weaknesses, deals {dmg} damage"),
            "multiplier": 2.8,
        },
    },
    "Chang'e": {
        "basic1": {
            "name": _("Moonlight Beam"),
            "desc": _("Lunar ray dealing {dmg} damage"),
            "multiplier": 0.75,
        },
        "basic2": {
            "name": _("Jade Rabbit's Grace"),
            "desc": _("Heals ally for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Eternal Moon Palace"),
            "desc": _("Freezes time, deals {dmg} damage to all"),
            "multiplier": 2.5,
        },
    },
    "Dragon King": {
        "basic1": {
            "name": _("Dragon's Breath"),
            "desc": _("Water dragon breath dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Tidal Shield"),
            "desc": _("Ocean barrier blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Leviathan Ascension"),
            "desc": _("Transforms into dragon dealing {dmg} damage"),
            "multiplier": 3.0,
        },
    },
    "Guan Yu": {
        "basic1": {
            "name": _("Green Dragon Blade"),
            "desc": _("Sweeping strike dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Loyal Oath"),
            "desc": _("Protects ally, blocks {dmg} damage"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("God of War's Fury"),
            "desc": _("Unleashes legendary might dealing {dmg} damage"),
            "multiplier": 2.8,
        },
    },
    "Nuwa": {
        "basic1": {
            "name": _("Five Colored Stone"),
            "desc": _("Elemental projectile dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Creation Mending"),
            "desc": _("Repairs ally for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("World Forge"),
            "desc": _("Reshapes reality dealing {dmg} damage to all"),
            "multiplier": 3.5,
        },
    },
    "Zhong Kui": {
        "basic1": {
            "name": _("Demon Hunter's Strike"),
            "desc": _("Purifying blow dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Ghost Wall"),
            "desc": _("Spirit barrier blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("King of Demons"),
            "desc": _("Commands ghost army dealing {dmg} damage"),
            "multiplier": 2.8,
        },
    },
    "Caishen": {
        "basic1": {
            "name": _("Golden Ingot Throw"),
            "desc": _("Wealth projectile dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Prosperity Blessing"),
            "desc": _("Grants {dmg} gold shield to ally"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Treasure Flood"),
            "desc": _("Rains gold dealing {dmg} damage to all enemies"),
            "multiplier": 2.2,
        },
    },
    # Egyptian Gods
    "Ra": {
        "basic1": {
            "name": _("Sun Disk"),
            "desc": _("Solar beam dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Falcon's Gaze"),
            "desc": _("Burning stare dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "ultimate": {
            "name": _("Solar Eclipse"),
            "desc": _("Blots out sun dealing {dmg} damage to all"),
            "multiplier": 3.5,
        },
    },
    "Osiris": {
        "basic1": {
            "name": _("Afterlife Touch"),
            "desc": _("Soul drain dealing {dmg} damage"),
            "multiplier": 0.75,
        },
        "basic2": {
            "name": _("Resurrection Blessing"),
            "desc": _("Heals ally for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Lord of the Dead"),
            "desc": _("Raises undead army dealing {dmg} damage"),
            "multiplier": 3.0,
        },
    },
    "Anubis": {
        "basic1": {
            "name": _("Jackal's Bite"),
            "desc": _("Savage bite dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Soul Weigh"),
            "desc": _("Judges enemy dealing {dmg} damage"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("Gate of Judgment"),
            "desc": _("Opens underworld dealing {dmg} damage to all"),
            "multiplier": 2.8,
        },
    },
    "Horus": {
        "basic1": {
            "name": _("Falcon Strike"),
            "desc": _("Aerial dive dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Sky Shield"),
            "desc": _("Wing barrier blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Eye of Horus"),
            "desc": _("All-seeing blast dealing {dmg} damage to all"),
            "multiplier": 3.0,
        },
    },
    "Isis": {
        "basic1": {
            "name": _("Magic Wings"),
            "desc": _("Feather strike dealing {dmg} damage"),
            "multiplier": 0.75,
        },
        "basic2": {
            "name": _("Healing Spell"),
            "desc": _("Restores {dmg} HP to ally"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Throne of Magic"),
            "desc": _("Unleashes ancient magic dealing {dmg} damage"),
            "multiplier": 2.5,
        },
    },
    "Set": {
        "basic1": {
            "name": _("Sandstorm"),
            "desc": _("Desert wind dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Chaos Spear"),
            "desc": _("Unstable energy dealing {dmg} damage"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("Desert of Destruction"),
            "desc": _("Consumes land dealing {dmg} damage to all"),
            "multiplier": 2.8,
        },
    },
    "Thoth": {
        "basic1": {
            "name": _("Hieroglyph Blast"),
            "desc": _("Ancient script dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Wisdom's Ward"),
            "desc": _("Knowledge shield blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Book of Thoth"),
            "desc": _("Rewrites reality dealing {dmg} damage to all"),
            "multiplier": 3.2,
        },
    },
    "Sekhmet": {
        "basic1": {
            "name": _("Lioness Claw"),
            "desc": _("Fierce swipe dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Blood Frenzy"),
            "desc": _("Berserker strike dealing {dmg} damage"),
            "multiplier": 1.1,
        },
        "ultimate": {
            "name": _("Goddess of Slaughter"),
            "desc": _("Unleashes war fury dealing {dmg} damage"),
            "multiplier": 3.0,
        },
    },
    "Bastet": {
        "basic1": {
            "name": _("Cat's Grace"),
            "desc": _("Swift strike dealing {dmg} damage"),
            "multiplier": 0.75,
        },
        "basic2": {
            "name": _("Protective Purr"),
            "desc": _("Heals ally for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Nine Lives"),
            "desc": _("Revives fallen ally, deals {dmg} damage"),
            "multiplier": 2.2,
        },
    },
    "Ptah": {
        "basic1": {
            "name": _("Creation Strike"),
            "desc": _("Forged blow dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Divine Craft"),
            "desc": _("Builds shield blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("World Shaper"),
            "desc": _("Reshapes battlefield dealing {dmg} damage"),
            "multiplier": 2.8,
        },
    },
    # Nordic Gods
    "Odin": {
        "basic1": {
            "name": _("Gungnir's Throw"),
            "desc": _("Spear of destiny dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Raven's Sight"),
            "desc": _("All-seeing strike dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "ultimate": {
            "name": _("Allfather's Wrath"),
            "desc": _("Commands Valhalla dealing {dmg} damage to all"),
            "multiplier": 3.5,
        },
    },
    "Thor": {
        "basic1": {
            "name": _("Mjolnir Strike"),
            "desc": _("Hammer blow dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Thunder Block"),
            "desc": _("Lightning shield blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Ragnarok's Thunder"),
            "desc": _("World-shaking storm dealing {dmg} damage"),
            "multiplier": 3.0,
        },
    },
    "Loki": {
        "basic1": {
            "name": _("Trickster's Blade"),
            "desc": _("Deceptive strike dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "basic2": {
            "name": _("Shape Shift"),
            "desc": _("Transforms and strikes for {dmg} damage"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("Chaos Incarnate"),
            "desc": _("Unleashes pure chaos dealing {dmg} damage"),
            "multiplier": 2.8,
        },
    },
    "Freya": {
        "basic1": {
            "name": _("Falcon Dive"),
            "desc": _("Aerial strike dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Love's Embrace"),
            "desc": _("Heals ally for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Valkyrie's Call"),
            "desc": _("Summons warriors dealing {dmg} damage"),
            "multiplier": 2.5,
        },
    },
    "Tyr": {
        "basic1": {
            "name": _("Justice Strike"),
            "desc": _("Righteous blow dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Honor's Shield"),
            "desc": _("Defends ally blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("God of Justice"),
            "desc": _("Judges all enemies dealing {dmg} damage"),
            "multiplier": 2.8,
        },
    },
    "Heimdall": {
        "basic1": {
            "name": _("Bifrost Beam"),
            "desc": _("Rainbow energy dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Watchman's Ward"),
            "desc": _("Vigilant shield blocking {dmg} damage"),
            "multiplier": 0.6,
        },
        "ultimate": {
            "name": _("Gjallarhorn's Call"),
            "desc": _("Awakens gods dealing {dmg} damage to all"),
            "multiplier": 3.0,
        },
    },
    "Frigg": {
        "basic1": {
            "name": _("Fate's Thread"),
            "desc": _("Destiny weave dealing {dmg} damage"),
            "multiplier": 0.7,
        },
        "basic2": {
            "name": _("Mother's Blessing"),
            "desc": _("Heals ally for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("Weaver of Fate"),
            "desc": _("Rewrites destiny dealing {dmg} damage"),
            "multiplier": 2.2,
        },
    },
    "Baldr": {
        "basic1": {
            "name": _("Light's Touch"),
            "desc": _("Radiant beam dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Pure Heart"),
            "desc": _("Heals self for {dmg} HP"),
            "multiplier": 0.5,
        },
        "ultimate": {
            "name": _("God of Light"),
            "desc": _("Blinding radiance dealing {dmg} damage to all"),
            "multiplier": 2.8,
        },
    },
    "Skadi": {
        "basic1": {
            "name": _("Winter's Arrow"),
            "desc": _("Frozen projectile dealing {dmg} damage"),
            "multiplier": 0.85,
        },
        "basic2": {
            "name": _("Snow Hunt"),
            "desc": _("Tracking strike dealing {dmg} damage"),
            "multiplier": 0.9,
        },
        "ultimate": {
            "name": _("Eternal Winter"),
            "desc": _("Freezes battlefield dealing {dmg} damage"),
            "multiplier": 3.0,
        },
    },
    "Vidar": {
        "basic1": {
            "name": _("Silent Strike"),
            "desc": _("Quiet blow dealing {dmg} damage"),
            "multiplier": 0.8,
        },
        "basic2": {
            "name": _("Vengeance Step"),
            "desc": _("Counter-attack dealing {dmg} damage"),
            "multiplier": 1.0,
        },
        "ultimate": {
            "name": _("Avenger's Fury"),
            "desc": _("Silent vengeance dealing {dmg} damage to all"),
            "multiplier": 2.5,
        },
    },
}

DEFAULT_SKILLS: dict[str, dict[str, Any]] = {
    "basic1": {
        "name": _("Basic Attack"),
        "desc": _("Standard strike dealing {dmg} damage"),
        "multiplier": 0.8,
    },
    "basic2": {
        "name": _("Power Strike"),
        "desc": _("Strong attack dealing {dmg} damage"),
        "multiplier": 1.0,
    },
    "ultimate": {
        "name": _("Divine Power"),
        "desc": _("Ultimate ability dealing {dmg} damage"),
        "multiplier": 2.5,
    },
}


class Rarity(models.TextChoices):
    """Rarity tiers for gods."""

    COMMON = "common", "Common"
    RARE = "rare", "Rare"
    EPIC = "epic", "Epic"
    LEGENDARY = "legendary", "Legendary"
    MYTHIC = "mythic", "Mythic"


RARITY_PULL_WEIGHTS = {
    Rarity.COMMON: 550,
    Rarity.RARE: 280,
    Rarity.EPIC: 140,
    Rarity.LEGENDARY: 29,
    Rarity.MYTHIC: 1,
}


class GodSynergyTag(models.Model):
    """Mythology-based synergy tag assigned to a God."""

    god = models.ForeignKey(
        "God", on_delete=models.CASCADE, related_name="synergy_tags"
    )
    tag = models.CharField(max_length=50, db_index=True)

    class Meta:
        unique_together = ["god", "tag"]

    def __str__(self) -> str:
        return f"{self.god.name}: {self.tag}"


SYNERGY_BONUSES: dict[int, dict[str, float]] = {
    2: {"stat_bonus_pct": 0.05},
    3: {"stat_bonus_pct": 0.10},
    4: {"stat_bonus_pct": 0.15},
    5: {"stat_bonus_pct": 0.25},
}

SYNERGY_SPECIAL_EFFECTS: dict[int, str] = {
    3: "heal_5pct",
    4: "armor_pen_10pct",
    5: "ultra_buff",
}

ULTRA_BUFF_POWER_SURGE = 0.10
ULTRA_BUFF_FIRST_STRIKE = 0.30
ULTRA_BUFF_COLOSSUS = 0.15


class God(models.Model):
    """Represents a god character in the game."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    pantheon = models.CharField(max_length=20, choices=Pantheon.choices)
    role = models.CharField(max_length=20, choices=Role.choices)
    rarity = models.CharField(max_length=20, choices=Rarity.choices)
    base_attack = models.PositiveIntegerField(default=100)
    base_defense = models.PositiveIntegerField(default=100)
    base_hp = models.PositiveIntegerField(default=1000)
    base_speed = models.PositiveIntegerField(default=100)
    image = models.ImageField(upload_to="gods/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    GOD_PROMPTS = {
        "Zeus": "Zeus king of Greek gods holding lightning bolt, white beard, golden crown, ancient Greek temple background, dramatic storm clouds, hyperrealistic digital art",
        "Poseidon": "Poseidon god of the sea holding golden trident, flowing blue robes, ocean waves crashing, underwater palace, realistic fantasy portrait",
        "Hades": "Hades god of the underworld, dark obsidian crown, shadowy cloak, skull motifs, fiery underworld background, menacing expression, dark fantasy art",
        "Ares": "Ares god of war in crimson battle armor, blood-stained sword, battlefield background, intense warrior expression, realistic Greek mythology",
        "Athena": "Athena goddess of wisdom in golden armor, owl companion, Greek helmet, shield with Medusa, Parthenon background, noble expression",
        "Apollo": "Apollo god of the sun and music, golden lyre, radiant light aura, laurel crown, Mount Olympus background, youthful divine beauty",
        "Artemis": "Artemis goddess of the hunt with silver bow, moonlit forest background, deer companion, silver dress, crescent moon crown",
        "Hermes": "Hermes messenger god with winged sandals, caduceus staff, traveler cloak, Mount Olympus path, youthful mischievous expression",
        "Hephaestus": "Hephaestus god of the forge at his anvil, hammer in hand, volcanic fire background, muscular blacksmith, soot-covered face",
        "Demeter": "Demeter goddess of harvest with wheat crown, golden fields background, flowing green robes, nurturing expression, autumn atmosphere",
        "Huitzilopochtli": "Huitzilopochtli Aztec god of war and sun, hummingbird headdress, turquoise shield, obsidian spear, Tenochtitlan temple background, fierce warrior expression, Mesoamerican art style",
        "Quetzalcoatl": "Quetzalcoatl feathered serpent god, emerald and quetzal feathers, wind god mask, Mesoamerican temple background, divine serpent form, ancient Mexican art",
        "Tezcatlipoca": "Tezcatlipoca Aztec god of night and sorcery, obsidian mirror, jaguar skin, smoking foot, dark mystical background, menacing powerful presence, Aztec mythology",
        "Tlaloc": "Tlaloc Aztec rain god, goggle eyes, fanged mouth, water serpent, storm clouds, rain effects, Mesoamerican temple, divine water deity",
        "Xipe Totec": "Xipe Totec Aztec god of rebirth, flayed skin garment, golden body, corn and seeds, spring renewal theme, Mesoamerican ritual background",
        "Coatlicue": "Coatlicue Aztec earth mother goddess, serpent skirt, skull necklace, clawed hands, powerful maternal presence, Mesoamerican stone sculpture style",
        "Mictlantecuhtli": "Mictlantecuhtli Aztec god of the underworld, skeletal body, blood bowl headdress, bone accessories, dark underworld background, terrifying death deity",
        "Xochiquetzal": "Xochiquetzal Aztec goddess of beauty and flowers, floral headdress, butterfly wings, colorful feathers, paradise garden background, beautiful divine presence",
        "Xiuhtecuhtli": "Xiuhtecuhtli Aztec god of fire and volcanoes, fire mask, turquoise mosaic, volcanic background, flame effects, powerful fire deity, Mesoamerican art",
        "Coyolxauhqui": "Coyolxauhqui Aztec moon goddess, bell-adorned face, dismembered form, lunar disk, night sky background, tragic divine beauty, Aztec stone carving style",
        "Ehecatl": "Ehecatl Aztec wind god, duck-billed mask, wind effects, feathered costume, sweeping storm background, invisible force personified, Mesoamerican mythology",
        "Tonatiuh": "Tonatiuh Aztec sun god, sun disk face, eagle claw hands, solar rays, temple sacrifice background, powerful celestial presence, Aztec calendar stone style",
        "Jade Emperor": "Jade Emperor celestial ruler on dragon throne, golden imperial robes, Chinese celestial palace background, divine authority",
        "Sun Wukong": "Sun Wukong Monkey King with golden staff, cloud somersault, Chinese armor, mischievous powerful expression, Journey to the West",
        "Nezha": "Nezha young deity with fire wheels, lotus armor, Chinese mythological warrior, fierce determined expression, flame effects",
        "Erlang Shen": "Erlang Shen three-eyed god with divine spear, Chinese celestial armor, third eye glowing, powerful warrior stance",
        "Chang'e": "Chang'e moon goddess with jade rabbit, silk flowing robes, lunar palace background, ethereal beautiful expression",
        "Dragon King": "Dragon King of the sea with dragon scales, trident, underwater dragon palace, majestic powerful presence, Chinese mythology",
        "Guan Yu": "Guan Yu god of war with green robe, guandao blade, red face, Chinese warrior armor, loyal righteous expression",
        "Nuwa": "Nuwa goddess of creation with serpent tail, five colored stones, Chinese cosmic background, divine maternal presence",
        "Zhong Kui": "Zhong Kui demon queller with fierce face, demon-slaying sword, Chinese underworld background, powerful intimidating presence",
        "Caishen": "Caishen Chinese god of wealth, photorealistic portrait, elderly wise face with long white beard, wearing elaborate red and gold imperial robes with dragon embroidery, holding golden ingots, traditional Chinese palace interior with red lanterns, cinematic lighting, 8k ultra detailed, DSLR photography style",
        "Ra": "Ra Egyptian sun god with falcon head, sun disk crown, golden robes, Egyptian temple background, divine solar power",
        "Osiris": "Osiris Egyptian god of afterlife, green skin, crook and flail, Egyptian underworld, regal mummy wrappings, wise expression",
        "Anubis": "Anubis Egyptian jackal-headed god, black fur, scales of justice, Egyptian tomb background, guardian of the dead",
        "Horus": "Horus Egyptian falcon-headed god, double crown, wings spread, sky temple background, divine protector expression",
        "Isis": "Isis Egyptian goddess of magic with wings, throne crown, healing aura, Egyptian temple, powerful maternal presence",
        "Set": "Set Egyptian god of chaos with red eyes, desert storm background, spear weapon, fierce destructive expression",
        "Thoth": "Thoth Egyptian ibis-headed god of wisdom, photorealistic portrait, human body with realistic ibis bird head, dark feathers, holding ancient scroll and reed pen, ancient Egyptian library with hieroglyph walls, warm torch lighting, 8k ultra detailed, cinematic photography style",
        "Sekhmet": "Sekhmet Egyptian lioness goddess, sun disk crown, war fury expression, Egyptian battlefield, fierce powerful presence",
        "Bastet": "Bastet Egyptian cat goddess, graceful pose, gold jewelry, Egyptian temple, elegant protective expression",
        "Ptah": "Ptah Egyptian creator god, mummy form, skull cap, divine beard, Egyptian creation temple, solemn expression",
        "Odin": "Odin Norse allfather with one eye, ravens Huginn and Muninn, Gungnir spear, Valhalla background, wise powerful expression",
        "Thor": "Thor Norse god of thunder with Mjolnir hammer, red beard, lightning effects, Norse fjord background, mighty warrior",
        "Loki": "Loki Norse trickster god with green horns, mischievous smile, shape-shifting aura, Norse underworld, cunning expression",
        "Freya": "Freya Norse goddess of love with falcon cloak, gold jewelry, flower crown, Norse meadow, beautiful powerful presence",
        "Tyr": "Tyr Norse god of justice with one hand, sword and shield, Norse hall background, honorable warrior expression",
        "Heimdall": "Heimdall Norse watchman with Gjallarhorn, rainbow bridge Bifrost, golden teeth, vigilant guardian expression",
        "Frigg": "Frigg Norse goddess of marriage with spinning wheel, crown, Norse hall background, wise maternal expression",
        "Baldr": "Baldr Norse god of light with golden hair, mistletoe, radiant aura, Norse paradise, pure beautiful expression",
        "Skadi": "Skadi Norse goddess of winter with bow, mountain snow background, hunting gear, fierce independent expression",
        "Vidar": "Vidar Norse god of vengeance with thick shoe, silent warrior, Norse battlefield, strong determined presence",
        # Mythic gods
        "Chronos": "Chronos primordial god of time, cosmic clockwork, swirling galaxies, ancient Greek cosmic background, timeless powerful presence",
        "Gaia": "Gaia mother earth goddess, flowing nature robes, mountains and forests growing from her form, primordial creation background",
        "Amun-Ra": "Amun-Ra hidden king of Egyptian gods, dual crown sun and feathers, golden divine light, Egyptian cosmic temple background",
        "Apophis": "Apophis serpent of chaos, massive snake form, red eyes, desert storm background, destructive ancient Egyptian mythology",
        "Yggdrasil": "Yggdrasil the World Tree, cosmic tree connecting nine realms, glowing roots and branches, Norse cosmic background, ancient powerful presence",
        "Ragnarok": "Ragnarok destroyer of worlds, apocalyptic warrior, fire and ice effects, Norse battlefield end times, fierce devastating expression",
        "Pangu": "Pangu creator who separated heaven and earth, giant cosmic figure, axe in hand, Chinese cosmic background, primordial powerful presence",
        "Fuxi": "Fuxi creator of humanity, serpent tail, eight trigrams floating, Chinese cosmic background, divine wise expression",
        "Ophiuchus": "Ophiuchus the serpent bearer, zodiac healer with snake staff, star constellation background, mystical powerful presence",
        "Cetus": "Cetus the sea monster, massive cosmic whale form, ocean storm background, zodiac constellation, terrifying powerful presence",
    }

    class Meta:
        ordering = ["rarity", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_pantheon_display()})"

    @property
    def icon(self) -> str:
        """Get emoji icon for this god."""
        return "👤"

    @property
    def image_prompt(self) -> str:
        """Generate AI image prompt for this god."""
        god_specific = {
            "Zeus": "Zeus Greek god king of gods lightning bolt white beard crown",
            "Poseidon": "Poseidon Greek god of sea trident ocean waves blue robes",
            "Hades": "Hades Greek god underworld dark cloak skull crown shadows",
            "Ares": "Ares Greek god war red armor sword battle helmet muscular",
            "Athena": "Athena Greek goddess wisdom owl helmet shield Greek armor",
            "Apollo": "Apollo Greek god sun golden bow laurel crown radiant light",
            "Artemis": "Artemis Greek goddess hunt moon bow silver dress forest",
            "Hermes": "Hermes Greek god speed winged sandals messenger staff traveler",
            "Hephaestus": "Hephaestus Greek god forge blacksmith hammer anvil fire",
            "Demeter": "Demeter Greek goddess harvest wheat crown green robes nature",
            "Huitzilopochtli": "Huitzilopochtli Aztec god war sun hummingbird headdress turquoise shield obsidian spear",
            "Quetzalcoatl": "Quetzalcoatl Aztec feathered serpent god emerald feathers wind mask divine",
            "Tezcatlipoca": "Tezcatlipoca Aztec god night sorcery obsidian mirror jaguar skin smoking foot",
            "Tlaloc": "Tlaloc Aztec rain god goggle eyes fangs water serpent storm clouds",
            "Xipe Totec": "Xipe Totec Aztec god rebirth flayed skin golden body corn seeds",
            "Coatlicue": "Coatlicue Aztec earth mother serpent skirt skull necklace clawed hands",
            "Mictlantecuhtli": "Mictlantecuhtli Aztec god underworld skeletal blood bowl headdress bone accessories",
            "Xochiquetzal": "Xochiquetzal Aztec goddess beauty flowers floral headdress butterfly wings",
            "Xiuhtecuhtli": "Xiuhtecuhtli Aztec god fire volcanoes fire mask turquoise mosaic flames",
            "Coyolxauhqui": "Coyolxauhqui Aztec moon goddess bells face lunar disk night sky",
            "Ehecatl": "Ehecatl Aztec wind god duck-billed mask wind effects feathered costume",
            "Tonatiuh": "Tonatiuh Aztec sun god sun disk eagle claws solar rays temple",
            "Jade Emperor": "Jade Emperor Chinese celestial dragon throne golden robes",
            "Sun Wukong": "Sun Wukong Monkey King golden staff cloud armor mischievous",
            "Nezha": "Nezha Chinese deity fire wheels lotus armor young warrior",
            "Erlang Shen": "Erlang Shen Chinese god three eyes spear divine armor",
            "Chang'e": "Chang'e Chinese moon goddess rabbit silk robes celestial",
            "Dragon King": "Dragon King Chinese sea dragon scales trident ocean throne",
            "Guan Yu": "Guan Yu Chinese god war green robe guandao blade red face",
            "Nuwa": "Nuwa Chinese goddess creation serpent tail five colored stones",
            "Zhong Kui": "Zhong Kui Chinese demon queller fierce face sword armor",
            "Caishen": "Caishen Chinese god wealth gold ingots red robes prosperity",
            "Ra": "Ra Egyptian sun god falcon head sun disk golden robes",
            "Osiris": "Osiris Egyptian god afterlife green skin crook flail mummy",
            "Anubis": "Anubis Egyptian jackal god underworld scales black fur",
            "Horus": "Horus Egyptian falcon god sky crown wings divine light",
            "Isis": "Isis Egyptian goddess magic wings throne crown healing",
            "Set": "Set Egyptian god chaos desert storm red eyes spear",
            "Thoth": "Thoth Egyptian god wisdom ibis head scroll writing magic",
            "Sekhmet": "Sekhmet Egyptian lioness goddess war sun disk fierce",
            "Bastet": "Bastet Egyptian cat goddess graceful gold jewelry elegant",
            "Ptah": "Ptah Egyptian creator god mummy form skull cap divine",
            "Odin": "Odin Norse god one eye ravens Gungnir spear wisdom",
            "Thor": "Thor Norse god thunder Mjolnir hammer red beard lightning",
            "Loki": "Loki Norse god trickery green horns mischievous smile magic",
            "Freya": "Freya Norse goddess love falcon cloak gold jewelry beauty",
            "Tyr": "Tyr Norse god justice one hand sword shield honor",
            "Heimdall": "Heimdall Norse god watchman horn rainbow bridge golden teeth",
            "Frigg": "Frigg Norse goddess marriage spinning wheel crown wise",
            "Baldr": "Baldr Norse god light golden hair mistletoe radiant pure",
            "Skadi": "Skadi Norse goddess winter bow mountains snow hunting",
            "Vidar": "Vidar Norse god vengeance thick shoe silent strong armor",
            "Cronus": "Cronus Greek titan time scythe dark cosmic power ancient",
            "Gaia": "Gaia Greek goddess earth mother nature vines mountains cosmic",
            "Prometheus": "Prometheus Greek titan fire chains eagle defiant heroic",
            "Hecate": "Hecate Greek goddess magic torches crossroads moon mystical",
            "Persephone": "Persephone Greek goddess spring pomegranate flowers underworld crown",
            "Dionysus": "Dionysus Greek god wine grapes thyrsus staff revelry purple",
            "Eros": "Eros Greek god love golden bow arrows wings youthful",
            "Nike": "Nike Greek goddess victory wings laurel wreath golden armor",
            "Morpheus": "Morpheus Greek god dreams poppy flowers sleep wings ethereal",
            "Fuxi": "Fuxi Chinese god creation eight trigrams serpent body cosmic",
            "Shennong": "Shennong Chinese god agriculture herbs ox horns green robes",
            "Xiwangmu": "Xiwangmu Chinese goddess immortality peaches phoenix crown celestial",
            "Huangdi": "Huangdi Chinese Yellow Emperor dragon robes sword throne imperial",
            "Lei Gong": "Lei Gong Chinese god thunder hammer chisel lightning wrath",
            "Amun": "Amun Egyptian god hidden ram horns crown cosmic mystery",
            "Hathor": "Hathor Egyptian goddess love cow horns sun disk music",
            "Khepri": "Khepri Egyptian scarab god sunrise beetle head golden light",
            "Ma'at": "Ma'at Egyptian goddess truth feather scales balance white robes",
            "Sobek": "Sobek Egyptian crocodile god water scales teeth fierce warrior",
            "Seshat": "Seshat Egyptian goddess writing reed pen scroll wisdom",
            "Ymir": "Ymir Norse primordial giant ice frost beard mountain size",
            "Hel": "Hel Norse goddess death half alive half decayed underworld",
            "Njord": "Njord Norse god sea ships wind wealth coastal throne",
            "Sif": "Sif Norse goddess golden hair wheat field fertility graceful",
            "Ullr": "Ullr Norse god skiing bow winter snow mountains hunting",
            "Bragi": "Bragi Norse god poetry harp mead hall wisdom beard",
        }
        base = god_specific.get(self.name, "epic fantasy god portrait")
        suffix = "dramatic lighting, digital painting, fantasy art style"
        return f"{base}, {suffix}, detailed character portrait, 4k"

    _image_url_cache: str | None = None

    @property
    def image_url(self) -> str:
        """Get image URL for this god (static if available, AI fallback)."""
        if self._image_url_cache is not None:
            return self._image_url_cache

        import urllib.parse

        filename_base = self.name.lower().replace(" ", "_")
        static_dir = settings.BASE_DIR / "static" / "images" / "gods"

        for ext in [".png", ".webp", ".jpg", ".jpeg"]:
            path = static_dir / f"{filename_base}{ext}"
            if path.exists():
                self._image_url_cache = f"{settings.STATIC_URL}images/gods/{filename_base}{ext}"
                return self._image_url_cache

        prompt = self.GOD_PROMPTS.get(self.name, "epic fantasy god portrait")
        encoded = urllib.parse.quote(prompt)
        seed = abs(hash(self.name)) % 10000
        base = "https://image.pollinations.ai/prompt"
        params = f"width=400&height=300&nologo=true&seed={seed}&model=flux"
        self._image_url_cache = f"{base}/{encoded}?{params}"
        return self._image_url_cache

    @property
    def visual_class(self) -> str:
        """Get CSS class for visual representation."""
        return f"visual-{self.pantheon}-{self.role}"

    @property
    def skills(self) -> list[dict]:
        """Get skills for this god based on name."""
        skills_data = GOD_SKILLS.get(self.name, DEFAULT_SKILLS)
        level = 1

        skills = []
        for key, skill in [
            ("basic1", skills_data["basic1"]),
            ("basic2", skills_data["basic2"]),
            ("ultimate", skills_data["ultimate"]),
        ]:
            multiplier = float(skill["multiplier"])
            desc = str(skill["desc"])
            dmg = int(self.base_attack * multiplier * (1 + level * 0.15))
            skills.append(
                {
                    "name": skill["name"],
                    "desc": desc.format(dmg=dmg),
                    "type": "basic" if key.startswith("basic") else "ultimate",
                }
            )

        return skills


ASCENSION_COSTS = {
    1: 15,
    2: 40,
    3: 100,
    4: 250,
}

ESSENCE_REWARDS = {
    Rarity.COMMON: 1,
    Rarity.RARE: 2,
    Rarity.EPIC: 5,
    Rarity.LEGENDARY: 10,
    Rarity.MYTHIC: 25,
}

QUALITY_NAMES = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
}


class PlayerGod(models.Model):
    """Represents a god owned by a player with progression."""

    player = models.ForeignKey(
        "core.PlayerProfile", on_delete=models.CASCADE, related_name="gods"
    )
    god = models.ForeignKey(God, on_delete=models.CASCADE, related_name="player_owners")
    level = models.PositiveIntegerField(default=1)
    experience = models.PositiveIntegerField(default=0)
    essence = models.PositiveIntegerField(default=0)
    quality_tier = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-level", "god__name"]
        unique_together = ["player", "god"]

    def __str__(self) -> str:
        return f"{self.god.name} (Lv.{self.level})"

    @property
    def quality_roman(self) -> str:
        """Return roman numeral for quality tier."""
        return QUALITY_NAMES.get(self.quality_tier, "I")

    @property
    def ascension_cost(self) -> int:
        """Get essence cost for next ascension."""
        if self.quality_tier >= 5:
            return 0
        return ASCENSION_COSTS.get(self.quality_tier, 0)

    @property
    def can_ascend(self) -> bool:
        """Check if this god can be ascended."""
        return self.quality_tier < 5 and self.essence >= self.ascension_cost

    def ascend(self) -> bool:
        """Spend essence to ascend this god to next quality tier."""
        if not self.can_ascend:
            return False
        self.essence -= self.ascension_cost
        self.quality_tier += 1
        self.save(update_fields=["essence", "quality_tier"])
        return True

    def add_essence(self, amount: int) -> None:
        """Add essence from duplicate pulls."""
        self.essence += amount
        self.save(update_fields=["essence"])

    @property
    def quality_multiplier(self) -> float:
        """Get stat multiplier based on quality tier."""
        return 1.0 + (self.quality_tier - 1) * 0.15

    def _equipment_list(self) -> list:
        """Get cached list of equipped items to avoid repeated DB queries."""
        if not hasattr(self, "_cached_equipment"):
            self._cached_equipment = list(self.equipped_items.select_related("item").all())
        return self._cached_equipment

    @property
    def total_attack(self) -> int:
        """Calculate total attack including equipment bonuses and quality."""
        base = self.god.base_attack * self.quality_multiplier * (1 + self.level * 0.1)
        eqs = self._equipment_list()
        equipment_bonus = sum(eq.item.attack_bonus * eq.level for eq in eqs)
        passive_bonus = sum(
            eq.item.passive_atk * eq.level
            for eq in eqs
            if eq.item.has_passive_for(self.god.name)
        )
        return int(base) + equipment_bonus + passive_bonus

    @property
    def total_defense(self) -> int:
        """Calculate total defense including equipment bonuses and quality."""
        base = self.god.base_defense * self.quality_multiplier * (1 + self.level * 0.1)
        eqs = self._equipment_list()
        equipment_bonus = sum(eq.item.defense_bonus * eq.level for eq in eqs)
        passive_bonus = sum(
            eq.item.passive_def * eq.level
            for eq in eqs
            if eq.item.has_passive_for(self.god.name)
        )
        return int(base) + equipment_bonus + passive_bonus

    @property
    def total_hp(self) -> int:
        """Calculate total HP including equipment bonuses and quality."""
        base = self.god.base_hp * self.quality_multiplier * (1 + self.level * 0.1)
        eqs = self._equipment_list()
        equipment_bonus = sum(eq.item.hp_bonus * eq.level for eq in eqs)
        passive_bonus = sum(
            eq.item.passive_hp * eq.level
            for eq in eqs
            if eq.item.has_passive_for(self.god.name)
        )
        return int(base) + equipment_bonus + passive_bonus

    @property
    def total_speed(self) -> int:
        """Calculate total speed including equipment bonuses and quality."""
        base = self.god.base_speed * self.quality_multiplier * (1 + self.level * 0.02)
        eqs = self._equipment_list()
        equipment_bonus = sum(eq.item.speed_bonus * eq.level for eq in eqs)
        passive_bonus = sum(
            eq.item.passive_spd * eq.level
            for eq in eqs
            if eq.item.has_passive_for(self.god.name)
        )
        return int(base) + equipment_bonus + passive_bonus

    def add_experience(self, amount: int) -> bool:
        """Add experience and level up if needed."""
        self.experience += amount
        xp_needed = self.level * 100
        leveled_up = False

        while self.experience >= xp_needed:
            self.experience -= xp_needed
            self.level += 1
            leveled_up = True
            xp_needed = self.level * 100

        self.save(update_fields=["level", "experience"])
        return leveled_up

    @property
    def skills(self) -> list[dict]:
        """Get skills for this god scaled to current level."""
        skills_data = GOD_SKILLS.get(self.god.name, DEFAULT_SKILLS)
        skills = []
        for key, skill in [
            ("basic1", skills_data["basic1"]),
            ("basic2", skills_data["basic2"]),
            ("ultimate", skills_data["ultimate"]),
        ]:
            multiplier = float(skill["multiplier"])
            desc = str(skill["desc"])
            dmg = int(self.god.base_attack * multiplier * (1 + self.level * 0.15))
            skills.append(
                {
                    "name": skill["name"],
                    "desc": desc.format(dmg=dmg),
                    "type": "basic" if key.startswith("basic") else "ultimate",
                }
            )

        return skills

    @property
    def gold_upgrade_cost(self) -> int:
        """Gold cost to level up this god by one level."""
        return self.level * 200

    def level_up_with_gold(self) -> bool:
        """Spend gold to level up. Returns True if successful."""
        cost = self.gold_upgrade_cost
        if self.player.gold < cost:
            return False
        self.player.spend_gold(cost)
        self.level += 1
        self.save(update_fields=["level"])
        return True

    @property
    def weapon(self):
        """Get equipped weapon."""
        for eq in self._equipment_list():
            if eq.item.item_type == "weapon":
                return eq
        return None

    @property
    def armor(self):
        """Get equipped armor."""
        for eq in self._equipment_list():
            if eq.item.item_type == "armor":
                return eq
        return None

    @property
    def amulet(self):
        """Get equipped amulet."""
        for eq in self._equipment_list():
            if eq.item.item_type == "amulet":
                return eq
        return None

    @property
    def active_passives(self) -> list[dict]:
        """Get list of active item passives for this god."""
        passives = []
        for eq in self._equipment_list():
            if eq.item.has_passive_for(self.god.name):
                passives.append(
                    {
                        "name": eq.item.passive_name,
                        "desc": eq.item.passive_desc,
                        "item_name": eq.item.name,
                        "bonuses": {
                            "atk": eq.item.passive_atk * eq.level,
                            "def": eq.item.passive_def * eq.level,
                            "hp": eq.item.passive_hp * eq.level,
                            "spd": eq.item.passive_spd * eq.level,
                        },
                    }
                )
        return passives
