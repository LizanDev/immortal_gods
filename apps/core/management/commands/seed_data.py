"""Management command to seed game data."""
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from apps.gods.models import God, Pantheon, Rarity, Role
from apps.items.models import Item, ItemType
from apps.campaign.models import FactionLadder, FactionStage


FACTION_TRIAL_NAMES = {
    "greek": [
        "Olympus Gate", "Temple of Zeus", "Hades' Domain", "Poseidon's Depths",
        "Athena's Wisdom", "Ares' Battlefield", "Apollo's Light", "Artemis' Hunt",
        "Hermes' Trial", "Hephaestus' Forge", "Demeter's Harvest", "Dionysus' Feast",
        "Persephone's Return", "Prometheus' Fire", "Atlas' Burden", "Nike's Victory",
        "Eros' Arrow", "Thanatos' Touch", "Nemesis' Judgment", "Helios' Chariot",
        "Selene's Glow", "Iris' Rainbow", "Hestia's Flame", "Hera's Wrath",
        "Leto's Grace", "Astraeus' Stars", "Oceanus' Tides", "Hyperion's Light",
        "Theia's Sight", "Coeus' Mind", "Crius' Might", "Iapetus' Chain",
        "Rhea's Flow", "Mnemosyne's Memory", "Phoebe's Moon", "Themis' Law",
        "Cronus' Fall", "Gaia's Blessing", "Uranus' Sky", "Tartarus' Pit",
    ],
    "zodiac": [
        "Aries Flame", "Taurus Ground", "Gemini Twin", "Cancer Shell",
        "Leo Roar", "Virgo Harvest", "Libra Scale", "Scorpio Sting",
        "Sagittarius Arrow", "Capricorn Climb", "Aquarius Wave", "Pisces Dream",
        "Star Forge", "Constellation Path", "Zodiac Wheel", "Celestial Map",
        "Horizon Line", "Eclipse Gate", "Meteor Shower", "Nova Burst",
        "Comet Trail", "Nebula Cloud", "Aurora Light", "Solar Wind",
        "Lunar Tide", "Planetary Ring", "Galaxy Core", "Void Star",
        "Cosmic Dust", "Dark Matter", "Light Year", "Time Warp",
        "Space Bend", "Gravity Well", "Pulsar Beat", "Quasar Glow",
        "Black Hole", "White Dwarf", "Red Giant", "Supernova",
    ],
    "chinese": [
        "Jade Palace", "Monkey Mountain", "Lotus Pond", "Dragon Gate",
        "Phoenix Nest", "Tiger Valley", "Crane Peak", "Turtle Island",
        "Silk Road", "Tea House", "Bamboo Forest", "Paper Lantern",
        "Incense Temple", "Kung Fu Dojo", "Yin Yang Hall", "Tai Chi Garden",
        "Great Wall", "Forbidden City", "Heavenly Market", "Earthly Branch",
        "Celestial River", "Moon Rabbit", "Sun Crow", "Cloud Dragon",
        "Wind Tiger", "Fire Bird", "Water Snake", "Metal Ox",
        "Wood Snake", "Stone Monkey", "Gold Rooster", "Silver Rat",
        "Jade Rabbit", "Pearl Dragon", "Crystal Phoenix", "Amber Tiger",
        "Obsidian Snake", "Ruby Dragon", "Emerald Crane", "Sapphire Turtle",
    ],
    "egyptian": [
        "Ra's Sunrise", "Osiris' Tomb", "Anubis' Scale", "Horus' Eye",
        "Isis' Magic", "Set's Storm", "Thoth's Library", "Sekhmet's Fury",
        "Bastet's Grace", "Ptah's Craft", "Ma'at's Feather", "Hathor's Song",
        "Sobek's River", "Khonsu's Moon", "Nut's Sky", "Geb's Earth",
        "Shu's Wind", "Tefnut's Rain", "Atum's Creation", "Nefertem's Lotus",
        "Wadjet's Cobra", "Nekhbet's Wing", "Serqet's Sting", "Neith's Web",
        "Seshat's Mark", "Imhotep's Stone", "Djedi's Spell", "Kheruef's Key",
        "Nefertari's Crown", "Cleopatra's Pearl", "Ramses' Sword", "Thutmose' Shield",
        "Akhenaten's Sun", "Tutankhamun's Gold", "Hatshepsut's Obelisk", "Seti's Star",
        "Ptolemy's Map", "Alexander's Flame", "Caesar's Shadow", "Nile's Flood",
    ],
    "nordic": [
        "Odin's Eye", "Thor's Hammer", "Loki's Trick", "Freya's Love",
        "Tyr's Hand", "Heimdall's Watch", "Frigg's Wisdom", "Baldr's Light",
        "Skadi's Snow", "Vidar's Vengeance", "Idun's Apple", "Sif's Hair",
        "Ullr's Bow", "Forseti's Court", "Bragi's Song", "Eir's Healing",
        "Gefjon's Plow", "Njord's Ship", "Ran's Net", "Aegir's Brew",
        "Hel's Gate", "Fenrir's Chain", "Jormungandr's Coil", "Sleipnir's Ride",
        "Ragnarok's Dawn", "Yggdrasil's Root", "Bifrost's Arc", "Valhalla's Hall",
        "Folkvangr's Field", "Niflheim's Ice", "Muspelheim's Fire", "Asgard's Wall",
        "Midgard's Shield", "Jotunheim's Frost", "Vanaheim's Bloom", "Alfheim's Glow",
        "Svartalfheim's Forge", "Helheim's Mist", "Ginnungagap's Void", "Wyrd's Thread",
    ],
}


GODS_DATA = [
    # Greek Gods
    {"name": "Zeus", "pantheon": Pantheon.GREEK, "role": Role.MAGE, "rarity": Rarity.LEGENDARY, "base_attack": 250, "base_defense": 150, "base_hp": 1800, "base_speed": 120},
    {"name": "Poseidon", "pantheon": Pantheon.GREEK, "role": Role.MAGE, "rarity": Rarity.LEGENDARY, "base_attack": 230, "base_defense": 160, "base_hp": 1900, "base_speed": 110},
    {"name": "Hades", "pantheon": Pantheon.GREEK, "role": Role.ASSASSIN, "rarity": Rarity.LEGENDARY, "base_attack": 280, "base_defense": 130, "base_hp": 1600, "base_speed": 140},
    {"name": "Ares", "pantheon": Pantheon.GREEK, "role": Role.ASSASSIN, "rarity": Rarity.EPIC, "base_attack": 220, "base_defense": 140, "base_hp": 1500, "base_speed": 130},
    {"name": "Athena", "pantheon": Pantheon.GREEK, "role": Role.SUPPORT, "rarity": Rarity.EPIC, "base_attack": 180, "base_defense": 200, "base_hp": 1700, "base_speed": 115},
    {"name": "Apollo", "pantheon": Pantheon.GREEK, "role": Role.ARCHER, "rarity": Rarity.EPIC, "base_attack": 210, "base_defense": 120, "base_hp": 1400, "base_speed": 135},
    {"name": "Artemis", "pantheon": Pantheon.GREEK, "role": Role.ARCHER, "rarity": Rarity.RARE, "base_attack": 190, "base_defense": 110, "base_hp": 1300, "base_speed": 140},
    {"name": "Hermes", "pantheon": Pantheon.GREEK, "role": Role.ASSASSIN, "rarity": Rarity.RARE, "base_attack": 180, "base_defense": 100, "base_hp": 1200, "base_speed": 160},
    {"name": "Hephaestus", "pantheon": Pantheon.GREEK, "role": Role.TANK, "rarity": Rarity.RARE, "base_attack": 160, "base_defense": 220, "base_hp": 2000, "base_speed": 90},
    {"name": "Demeter", "pantheon": Pantheon.GREEK, "role": Role.SUPPORT, "rarity": Rarity.COMMON, "base_attack": 140, "base_defense": 150, "base_hp": 1600, "base_speed": 100},

    # Zodiac Gods
    {"name": "Aries", "pantheon": Pantheon.ZODIAC, "role": Role.ASSASSIN, "rarity": Rarity.EPIC, "base_attack": 210, "base_defense": 130, "base_hp": 1400, "base_speed": 145},
    {"name": "Taurus", "pantheon": Pantheon.ZODIAC, "role": Role.TANK, "rarity": Rarity.EPIC, "base_attack": 170, "base_defense": 230, "base_hp": 2200, "base_speed": 85},
    {"name": "Gemini", "pantheon": Pantheon.ZODIAC, "role": Role.MAGE, "rarity": Rarity.RARE, "base_attack": 190, "base_defense": 120, "base_hp": 1300, "base_speed": 130},
    {"name": "Cancer", "pantheon": Pantheon.ZODIAC, "role": Role.SUPPORT, "rarity": Rarity.RARE, "base_attack": 150, "base_defense": 180, "base_hp": 1800, "base_speed": 100},
    {"name": "Leo", "pantheon": Pantheon.ZODIAC, "role": Role.ASSASSIN, "rarity": Rarity.LEGENDARY, "base_attack": 260, "base_defense": 140, "base_hp": 1700, "base_speed": 135},
    {"name": "Virgo", "pantheon": Pantheon.ZODIAC, "role": Role.SUPPORT, "rarity": Rarity.COMMON, "base_attack": 140, "base_defense": 160, "base_hp": 1500, "base_speed": 110},
    {"name": "Libra", "pantheon": Pantheon.ZODIAC, "role": Role.MAGE, "rarity": Rarity.RARE, "base_attack": 180, "base_defense": 150, "base_hp": 1400, "base_speed": 120},
    {"name": "Scorpio", "pantheon": Pantheon.ZODIAC, "role": Role.ASSASSIN, "rarity": Rarity.EPIC, "base_attack": 230, "base_defense": 120, "base_hp": 1350, "base_speed": 140},
    {"name": "Sagittarius", "pantheon": Pantheon.ZODIAC, "role": Role.ARCHER, "rarity": Rarity.EPIC, "base_attack": 220, "base_defense": 110, "base_hp": 1300, "base_speed": 150},
    {"name": "Capricorn", "pantheon": Pantheon.ZODIAC, "role": Role.TANK, "rarity": Rarity.RARE, "base_attack": 160, "base_defense": 210, "base_hp": 1900, "base_speed": 95},
    {"name": "Aquarius", "pantheon": Pantheon.ZODIAC, "role": Role.MAGE, "rarity": Rarity.LEGENDARY, "base_attack": 240, "base_defense": 140, "base_hp": 1600, "base_speed": 125},
    {"name": "Pisces", "pantheon": Pantheon.ZODIAC, "role": Role.SUPPORT, "rarity": Rarity.COMMON, "base_attack": 130, "base_defense": 170, "base_hp": 1700, "base_speed": 105},

    # Chinese Gods
    {"name": "Jade Emperor", "pantheon": Pantheon.CHINESE, "role": Role.SUPPORT, "rarity": Rarity.MYTHIC, "base_attack": 200, "base_defense": 200, "base_hp": 2500, "base_speed": 130},
    {"name": "Sun Wukong", "pantheon": Pantheon.CHINESE, "role": Role.ASSASSIN, "rarity": Rarity.LEGENDARY, "base_attack": 270, "base_defense": 150, "base_hp": 1800, "base_speed": 155},
    {"name": "Nezha", "pantheon": Pantheon.CHINESE, "role": Role.ARCHER, "rarity": Rarity.EPIC, "base_attack": 220, "base_defense": 120, "base_hp": 1400, "base_speed": 145},
    {"name": "Erlang Shen", "pantheon": Pantheon.CHINESE, "role": Role.ASSASSIN, "rarity": Rarity.EPIC, "base_attack": 230, "base_defense": 140, "base_hp": 1500, "base_speed": 135},
    {"name": "Chang'e", "pantheon": Pantheon.CHINESE, "role": Role.SUPPORT, "rarity": Rarity.RARE, "base_attack": 150, "base_defense": 160, "base_hp": 1600, "base_speed": 115},
    {"name": "Dragon King", "pantheon": Pantheon.CHINESE, "role": Role.TANK, "rarity": Rarity.LEGENDARY, "base_attack": 200, "base_defense": 240, "base_hp": 2300, "base_speed": 100},
    {"name": "Guan Yu", "pantheon": Pantheon.CHINESE, "role": Role.ASSASSIN, "rarity": Rarity.EPIC, "base_attack": 240, "base_defense": 160, "base_hp": 1700, "base_speed": 120},
    {"name": "Nuwa", "pantheon": Pantheon.CHINESE, "role": Role.MAGE, "rarity": Rarity.MYTHIC, "base_attack": 260, "base_defense": 180, "base_hp": 2000, "base_speed": 125},
    {"name": "Zhong Kui", "pantheon": Pantheon.CHINESE, "role": Role.TANK, "rarity": Rarity.RARE, "base_attack": 170, "base_defense": 200, "base_hp": 1900, "base_speed": 90},
    {"name": "Caishen", "pantheon": Pantheon.CHINESE, "role": Role.SUPPORT, "rarity": Rarity.COMMON, "base_attack": 140, "base_defense": 150, "base_hp": 1500, "base_speed": 105},

    # Egyptian Gods
    {"name": "Ra", "pantheon": Pantheon.EGYPTIAN, "role": Role.MAGE, "rarity": Rarity.LEGENDARY, "base_attack": 250, "base_defense": 140, "base_hp": 1700, "base_speed": 125},
    {"name": "Osiris", "pantheon": Pantheon.EGYPTIAN, "role": Role.SUPPORT, "rarity": Rarity.LEGENDARY, "base_attack": 190, "base_defense": 180, "base_hp": 2100, "base_speed": 110},
    {"name": "Anubis", "pantheon": Pantheon.EGYPTIAN, "role": Role.ASSASSIN, "rarity": Rarity.EPIC, "base_attack": 230, "base_defense": 130, "base_hp": 1500, "base_speed": 140},
    {"name": "Horus", "pantheon": Pantheon.EGYPTIAN, "role": Role.ARCHER, "rarity": Rarity.EPIC, "base_attack": 220, "base_defense": 130, "base_hp": 1450, "base_speed": 145},
    {"name": "Isis", "pantheon": Pantheon.EGYPTIAN, "role": Role.SUPPORT, "rarity": Rarity.EPIC, "base_attack": 170, "base_defense": 190, "base_hp": 1800, "base_speed": 120},
    {"name": "Set", "pantheon": Pantheon.EGYPTIAN, "role": Role.ASSASSIN, "rarity": Rarity.RARE, "base_attack": 200, "base_defense": 120, "base_hp": 1400, "base_speed": 135},
    {"name": "Thoth", "pantheon": Pantheon.EGYPTIAN, "role": Role.MAGE, "rarity": Rarity.RARE, "base_attack": 190, "base_defense": 140, "base_hp": 1300, "base_speed": 125},
    {"name": "Sekhmet", "pantheon": Pantheon.EGYPTIAN, "role": Role.ASSASSIN, "rarity": Rarity.RARE, "base_attack": 210, "base_defense": 110, "base_hp": 1350, "base_speed": 140},
    {"name": "Bastet", "pantheon": Pantheon.EGYPTIAN, "role": Role.SUPPORT, "rarity": Rarity.COMMON, "base_attack": 140, "base_defense": 150, "base_hp": 1500, "base_speed": 115},
    {"name": "Ptah", "pantheon": Pantheon.EGYPTIAN, "role": Role.TANK, "rarity": Rarity.COMMON, "base_attack": 150, "base_defense": 190, "base_hp": 1800, "base_speed": 95},

    # Nordic Gods
    {"name": "Odin", "pantheon": Pantheon.NORDIC, "role": Role.TANK, "rarity": Rarity.MYTHIC, "base_attack": 240, "base_defense": 220, "base_hp": 2500, "base_speed": 120},
    {"name": "Thor", "pantheon": Pantheon.NORDIC, "role": Role.TANK, "rarity": Rarity.LEGENDARY, "base_attack": 240, "base_defense": 220, "base_hp": 2100, "base_speed": 105},
    {"name": "Loki", "pantheon": Pantheon.NORDIC, "role": Role.ASSASSIN, "rarity": Rarity.LEGENDARY, "base_attack": 250, "base_defense": 130, "base_hp": 1500, "base_speed": 150},
    {"name": "Freya", "pantheon": Pantheon.NORDIC, "role": Role.SUPPORT, "rarity": Rarity.EPIC, "base_attack": 180, "base_defense": 170, "base_hp": 1700, "base_speed": 125},
    {"name": "Tyr", "pantheon": Pantheon.NORDIC, "role": Role.TANK, "rarity": Rarity.EPIC, "base_attack": 190, "base_defense": 230, "base_hp": 2000, "base_speed": 100},
    {"name": "Heimdall", "pantheon": Pantheon.NORDIC, "role": Role.ARCHER, "rarity": Rarity.EPIC, "base_attack": 210, "base_defense": 150, "base_hp": 1500, "base_speed": 140},
    {"name": "Frigg", "pantheon": Pantheon.NORDIC, "role": Role.SUPPORT, "rarity": Rarity.RARE, "base_attack": 150, "base_defense": 180, "base_hp": 1700, "base_speed": 110},
    {"name": "Baldr", "pantheon": Pantheon.NORDIC, "role": Role.MAGE, "rarity": Rarity.RARE, "base_attack": 190, "base_defense": 140, "base_hp": 1400, "base_speed": 120},
    {"name": "Skadi", "pantheon": Pantheon.NORDIC, "role": Role.ARCHER, "rarity": Rarity.RARE, "base_attack": 200, "base_defense": 120, "base_hp": 1350, "base_speed": 135},
    {"name": "Vidar", "pantheon": Pantheon.NORDIC, "role": Role.ASSASSIN, "rarity": Rarity.COMMON, "base_attack": 160, "base_defense": 130, "base_hp": 1300, "base_speed": 125},
]

ITEMS_DATA = [
    # Weapons
    {
        "name": _("Thunder Sword"), "item_type": ItemType.WEAPON,
        "attack_bonus": 50, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 10,
        "belongs_to_god": "Zeus", "passive_name": _("Storm Caller"),
        "passive_desc": _("Lightning strikes deal double damage"),
        "passive_atk": 30, "passive_def": 0, "passive_hp": 0, "passive_spd": 5,
    },
    {
        "name": _("Poseidon's Trident"), "item_type": ItemType.WEAPON,
        "attack_bonus": 60, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 5,
        "belongs_to_god": "Poseidon", "passive_name": _("Ocean's Wrath"),
        "passive_desc": _("Tidal waves crash on enemies"),
        "passive_atk": 25, "passive_def": 0, "passive_hp": 100, "passive_spd": 0,
    },
    {
        "name": _("Hades' Scythe"), "item_type": ItemType.WEAPON,
        "attack_bonus": 70, "defense_bonus": 0, "hp_bonus": -50, "speed_bonus": 15,
        "belongs_to_god": "Hades", "passive_name": _("Soul Reaper"),
        "passive_desc": _("Steals life from fallen enemies"),
        "passive_atk": 40, "passive_def": 0, "passive_hp": 0, "passive_spd": 10,
    },
    {
        "name": _("Apollo's Bow"), "item_type": ItemType.WEAPON,
        "attack_bonus": 55, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 20,
        "belongs_to_god": "Apollo", "passive_name": _("Sun Piercer"),
        "passive_desc": _("Arrows burn through armor"),
        "passive_atk": 20, "passive_def": 0, "passive_hp": 0, "passive_spd": 15,
    },
    {
        "name": _("Sun Wukong's Staff"), "item_type": ItemType.WEAPON,
        "attack_bonus": 65, "defense_bonus": 10, "hp_bonus": 0, "speed_bonus": 15,
        "belongs_to_god": "Sun Wukong", "passive_name": _("Monkey King's Fury"),
        "passive_desc": _("Staff extends to strike all enemies"),
        "passive_atk": 35, "passive_def": 5, "passive_hp": 0, "passive_spd": 10,
    },
    {
        "name": _("Ra's Sun Blade"), "item_type": ItemType.WEAPON,
        "attack_bonus": 60, "defense_bonus": 0, "hp_bonus": 50, "speed_bonus": 10,
        "belongs_to_god": "Ra", "passive_name": _("Solar Flare"),
        "passive_desc": _("Blinding light weakens enemies"),
        "passive_atk": 25, "passive_def": 0, "passive_hp": 50, "passive_spd": 5,
    },
    {
        "name": _("Mjolnir"), "item_type": ItemType.WEAPON,
        "attack_bonus": 75, "defense_bonus": 5, "hp_bonus": 0, "speed_bonus": 0,
        "belongs_to_god": "Thor", "passive_name": _("Thunder God's Might"),
        "passive_desc": _("Lightning chains between enemies"),
        "passive_atk": 30, "passive_def": 10, "passive_hp": 0, "passive_spd": 0,
    },
    {
        "name": _("Gungnir"), "item_type": ItemType.WEAPON,
        "attack_bonus": 55, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 25,
        "belongs_to_god": "Odin", "passive_name": _("Allfather's Aim"),
        "passive_desc": _("Spear never misses its target"),
        "passive_atk": 20, "passive_def": 0, "passive_hp": 0, "passive_spd": 20,
    },

    # Armor
    {
        "name": _("Aegis Shield"), "item_type": ItemType.ARMOR,
        "attack_bonus": 0, "defense_bonus": 60, "hp_bonus": 200, "speed_bonus": -5,
        "belongs_to_god": "Athena", "passive_name": _("Divine Protection"),
        "passive_desc": _("Shield reflects 20% of damage"),
        "passive_atk": 0, "passive_def": 30, "passive_hp": 100, "passive_spd": 0,
    },
    {
        "name": _("Dragon Scale Mail"), "item_type": ItemType.ARMOR,
        "attack_bonus": 10, "defense_bonus": 50, "hp_bonus": 300, "speed_bonus": -10,
        "belongs_to_god": "Dragon King", "passive_name": _("Dragon's Hide"),
        "passive_desc": _("Scales harden against fire"),
        "passive_atk": 5, "passive_def": 25, "passive_hp": 150, "passive_spd": 0,
    },
    {
        "name": _("Osiris' Robe"), "item_type": ItemType.ARMOR,
        "attack_bonus": 0, "defense_bonus": 40, "hp_bonus": 400, "speed_bonus": 0,
        "belongs_to_god": "Osiris", "passive_name": _("Afterlife Ward"),
        "passive_desc": _("Death's embrace grants resilience"),
        "passive_atk": 0, "passive_def": 20, "passive_hp": 200, "passive_spd": 0,
    },
    {
        "name": _("Valkyrie Armor"), "item_type": ItemType.ARMOR,
        "attack_bonus": 15, "defense_bonus": 45, "hp_bonus": 250, "speed_bonus": 5,
        "belongs_to_god": "Freya", "passive_name": _("Warrior's Grace"),
        "passive_desc": _("Battle spirit enhances movement"),
        "passive_atk": 10, "passive_def": 15, "passive_hp": 100, "passive_spd": 5,
    },
    {
        "name": _("Jade Armor"), "item_type": ItemType.ARMOR,
        "attack_bonus": 5, "defense_bonus": 55, "hp_bonus": 350, "speed_bonus": -5,
        "belongs_to_god": "Jade Emperor", "passive_name": _("Celestial Jade"),
        "passive_desc": _("Jade absorbs heavenly energy"),
        "passive_atk": 0, "passive_def": 25, "passive_hp": 150, "passive_spd": 0,
    },

    # Helmets
    {
        "name": _("Crown of Zeus"), "item_type": ItemType.HELMET,
        "attack_bonus": 20, "defense_bonus": 30, "hp_bonus": 100, "speed_bonus": 10,
        "belongs_to_god": "Zeus", "passive_name": _("King's Authority"),
        "passive_desc": _("Commands respect from all gods"),
        "passive_atk": 15, "passive_def": 15, "passive_hp": 50, "passive_spd": 5,
    },
    {
        "name": _("Anubis' Mask"), "item_type": ItemType.HELMET,
        "attack_bonus": 25, "defense_bonus": 20, "hp_bonus": 50, "speed_bonus": 15,
        "belongs_to_god": "Anubis", "passive_name": _("Jackal's Sight"),
        "passive_desc": _("Sees the weakness of souls"),
        "passive_atk": 15, "passive_def": 10, "passive_hp": 0, "passive_spd": 10,
    },
    {
        "name": _("Odin's Helm"), "item_type": ItemType.HELMET,
        "attack_bonus": 30, "defense_bonus": 25, "hp_bonus": 150, "speed_bonus": 5,
        "belongs_to_god": "Odin", "passive_name": _("Raven's Wisdom"),
        "passive_desc": _("Two ravens whisper battle tactics"),
        "passive_atk": 10, "passive_def": 15, "passive_hp": 50, "passive_spd": 5,
    },
    {
        "name": _("Dragon Horn Helm"), "item_type": ItemType.HELMET,
        "attack_bonus": 15, "defense_bonus": 35, "hp_bonus": 200, "speed_bonus": 0,
        "belongs_to_god": "Dragon King", "passive_name": _("Dragon's Crown"),
        "passive_desc": _("Horns channel ancient dragon power"),
        "passive_atk": 5, "passive_def": 20, "passive_hp": 100, "passive_spd": 0,
    },
    {
        "name": _("Zodiac Crown"), "item_type": ItemType.HELMET,
        "attack_bonus": 20, "defense_bonus": 20, "hp_bonus": 100, "speed_bonus": 20,
        "belongs_to_god": "Leo", "passive_name": _("Star Alignment"),
        "passive_desc": _("Constellations empower the wearer"),
        "passive_atk": 10, "passive_def": 10, "passive_hp": 50, "passive_spd": 10,
    },

    # Boots
    {
        "name": _("Hermes' Sandals"), "item_type": ItemType.BOOTS,
        "attack_bonus": 0, "defense_bonus": 10, "hp_bonus": 0, "speed_bonus": 50,
        "belongs_to_god": "Hermes", "passive_name": _("Messenger's Swiftness"),
        "passive_desc": _("Moves faster than thought itself"),
        "passive_atk": 0, "passive_def": 5, "passive_hp": 0, "passive_spd": 30,
    },
    {
        "name": _("Wind Walkers"), "item_type": ItemType.BOOTS,
        "attack_bonus": 5, "defense_bonus": 15, "hp_bonus": 50, "speed_bonus": 40,
        "belongs_to_god": "Skadi", "passive_name": _("Winter's Step"),
        "passive_desc": _("Leaves trails of frost"),
        "passive_atk": 0, "passive_def": 10, "passive_hp": 0, "passive_spd": 20,
    },
    {
        "name": _("Shadow Steps"), "item_type": ItemType.BOOTS,
        "attack_bonus": 10, "defense_bonus": 5, "hp_bonus": 0, "speed_bonus": 45,
        "belongs_to_god": "Loki", "passive_name": _("Trickster's Path"),
        "passive_desc": _("Walks between shadows unseen"),
        "passive_atk": 10, "passive_def": 0, "passive_hp": 0, "passive_spd": 25,
    },
    {
        "name": _("Iron Boots"), "item_type": ItemType.BOOTS,
        "attack_bonus": 0, "defense_bonus": 30, "hp_bonus": 100, "speed_bonus": -10,
        "belongs_to_god": "Hephaestus", "passive_name": _("Forge Walker"),
        "passive_desc": _("Immune to lava and fire"),
        "passive_atk": 0, "passive_def": 20, "passive_hp": 50, "passive_spd": 0,
    },
    {
        "name": _("Cloud Walkers"), "item_type": ItemType.BOOTS,
        "attack_bonus": 5, "defense_bonus": 10, "hp_bonus": 80, "speed_bonus": 35,
        "belongs_to_god": "Sun Wukong", "passive_name": _("Cloud Somersault"),
        "passive_desc": _("Leaps 108,000 li in one bound"),
        "passive_atk": 5, "passive_def": 5, "passive_hp": 0, "passive_spd": 20,
    },

    # Accessories
    {
        "name": _("Eye of Horus"), "item_type": ItemType.ACCESSORY,
        "attack_bonus": 25, "defense_bonus": 25, "hp_bonus": 100, "speed_bonus": 10,
        "belongs_to_god": "Horus", "passive_name": _("All-Seeing Eye"),
        "passive_desc": _("Perceives all threats before they happen"),
        "passive_atk": 15, "passive_def": 15, "passive_hp": 50, "passive_spd": 5,
    },
    {
        "name": _("Phoenix Feather"), "item_type": ItemType.ACCESSORY,
        "attack_bonus": 15, "defense_bonus": 15, "hp_bonus": 200, "speed_bonus": 15,
        "belongs_to_god": "Ra", "passive_name": _("Rebirth Flame"),
        "passive_desc": _("Rises from ashes with renewed strength"),
        "passive_atk": 10, "passive_def": 10, "passive_hp": 100, "passive_spd": 10,
    },
    {
        "name": _("Yggdrasil Seed"), "item_type": ItemType.ACCESSORY,
        "attack_bonus": 10, "defense_bonus": 20, "hp_bonus": 300, "speed_bonus": 5,
        "belongs_to_god": "Odin", "passive_name": _("World Tree's Blessing"),
        "passive_desc": _("Connected to all nine realms"),
        "passive_atk": 5, "passive_def": 15, "passive_hp": 150, "passive_spd": 0,
    },
    {
        "name": _("Taiji Amulet"), "item_type": ItemType.ACCESSORY,
        "attack_bonus": 20, "defense_bonus": 20, "hp_bonus": 150, "speed_bonus": 20,
        "belongs_to_god": "Nuwa", "passive_name": _("Yin Yang Balance"),
        "passive_desc": _("Harmonizes opposing forces"),
        "passive_atk": 10, "passive_def": 10, "passive_hp": 50, "passive_spd": 10,
    },
    {
        "name": _("Olympus Ring"), "item_type": ItemType.ACCESSORY,
        "attack_bonus": 30, "defense_bonus": 10, "hp_bonus": 100, "speed_bonus": 15,
        "belongs_to_god": "Zeus", "passive_name": _("Divine Authority"),
        "passive_desc": _("Commands the power of Olympus"),
        "passive_atk": 20, "passive_def": 5, "passive_hp": 50, "passive_spd": 10,
    },
]

CAMPAIGN_LEVELS_DATA = [
    # Easy (1-5)
    {"name": _("Temple Entrance"), "difficulty": "easy", "order": 1, "energy_cost": 5, "gold_reward": 100, "gems_reward": 5, "exp_reward": 30, "required_power": 300},
    {"name": _("Forest of Shadows"), "difficulty": "easy", "order": 2, "energy_cost": 5, "gold_reward": 120, "gems_reward": 5, "exp_reward": 35, "required_power": 400},
    {"name": _("River Crossing"), "difficulty": "easy", "order": 3, "energy_cost": 8, "gold_reward": 150, "gems_reward": 8, "exp_reward": 40, "required_power": 500},
    {"name": _("Abandoned Village"), "difficulty": "easy", "order": 4, "energy_cost": 8, "gold_reward": 170, "gems_reward": 8, "exp_reward": 45, "required_power": 600},
    {"name": _("Whispering Woods"), "difficulty": "easy", "order": 5, "energy_cost": 10, "gold_reward": 200, "gems_reward": 10, "exp_reward": 50, "required_power": 700},

    # Normal (6-12)
    {"name": _("Mountain Pass"), "difficulty": "normal", "order": 6, "energy_cost": 10, "gold_reward": 220, "gems_reward": 10, "exp_reward": 55, "required_power": 850},
    {"name": _("Ancient Ruins"), "difficulty": "normal", "order": 7, "energy_cost": 12, "gold_reward": 250, "gems_reward": 12, "exp_reward": 60, "required_power": 1000},
    {"name": _("Dark Cave"), "difficulty": "normal", "order": 8, "energy_cost": 12, "gold_reward": 280, "gems_reward": 12, "exp_reward": 65, "required_power": 1150},
    {"name": _("Swamp of Decay"), "difficulty": "normal", "order": 9, "energy_cost": 14, "gold_reward": 300, "gems_reward": 14, "exp_reward": 70, "required_power": 1300},
    {"name": _("Guardian's Gate"), "difficulty": "normal", "order": 10, "energy_cost": 15, "gold_reward": 350, "gems_reward": 15, "exp_reward": 80, "required_power": 1500, "is_boss_level": True},
    {"name": _("Crystal Caverns"), "difficulty": "normal", "order": 11, "energy_cost": 15, "gold_reward": 380, "gems_reward": 15, "exp_reward": 85, "required_power": 1700},
    {"name": _("Enchanted Garden"), "difficulty": "normal", "order": 12, "energy_cost": 18, "gold_reward": 420, "gems_reward": 18, "exp_reward": 90, "required_power": 1900},

    # Hard (13-22)
    {"name": _("Volcanic Wastes"), "difficulty": "hard", "order": 13, "energy_cost": 18, "gold_reward": 450, "gems_reward": 18, "exp_reward": 95, "required_power": 2100},
    {"name": _("Frozen Peaks"), "difficulty": "hard", "order": 14, "energy_cost": 20, "gold_reward": 500, "gems_reward": 20, "exp_reward": 100, "required_power": 2400},
    {"name": _("Storm Valley"), "difficulty": "hard", "order": 15, "energy_cost": 20, "gold_reward": 520, "gems_reward": 20, "exp_reward": 105, "required_power": 2700},
    {"name": _("Shadow Fortress"), "difficulty": "hard", "order": 16, "energy_cost": 22, "gold_reward": 550, "gems_reward": 22, "exp_reward": 110, "required_power": 3000},
    {"name": _("Cursed Battlefield"), "difficulty": "hard", "order": 17, "energy_cost": 22, "gold_reward": 580, "gems_reward": 22, "exp_reward": 115, "required_power": 3300},
    {"name": _("Dragon's Lair"), "difficulty": "hard", "order": 18, "energy_cost": 25, "gold_reward": 650, "gems_reward": 25, "exp_reward": 130, "required_power": 3800, "is_boss_level": True},
    {"name": _("Phantom Citadel"), "difficulty": "hard", "order": 19, "energy_cost": 25, "gold_reward": 680, "gems_reward": 25, "exp_reward": 135, "required_power": 4100},
    {"name": _("Lava Temple"), "difficulty": "hard", "order": 20, "energy_cost": 28, "gold_reward": 720, "gems_reward": 28, "exp_reward": 140, "required_power": 4500},
    {"name": _("Astral Plane"), "difficulty": "hard", "order": 21, "energy_cost": 28, "gold_reward": 750, "gems_reward": 28, "exp_reward": 145, "required_power": 4800},
    {"name": _("Titan's Graveyard"), "difficulty": "hard", "order": 22, "energy_cost": 30, "gold_reward": 800, "gems_reward": 30, "exp_reward": 150, "required_power": 5200, "is_boss_level": True},

    # Hell (23-30)
    {"name": _("Celestial Realm"), "difficulty": "hell", "order": 23, "energy_cost": 30, "gold_reward": 850, "gems_reward": 30, "exp_reward": 160, "required_power": 5600},
    {"name": _("Abyss of Chaos"), "difficulty": "hell", "order": 24, "energy_cost": 32, "gold_reward": 900, "gems_reward": 32, "exp_reward": 170, "required_power": 6000},
    {"name": _("Void Dimension"), "difficulty": "hell", "order": 25, "energy_cost": 35, "gold_reward": 950, "gems_reward": 35, "exp_reward": 180, "required_power": 6500},
    {"name": _("Infernal Gates"), "difficulty": "hell", "order": 26, "energy_cost": 35, "gold_reward": 1000, "gems_reward": 35, "exp_reward": 190, "required_power": 7000},
    {"name": _("Netherworld"), "difficulty": "hell", "order": 27, "energy_cost": 38, "gold_reward": 1100, "gems_reward": 38, "exp_reward": 200, "required_power": 7500},
    {"name": _("Pandemonium"), "difficulty": "hell", "order": 28, "energy_cost": 40, "gold_reward": 1200, "gems_reward": 40, "exp_reward": 220, "required_power": 8200, "is_boss_level": True},
    {"name": _("Eternal Darkness"), "difficulty": "hell", "order": 29, "energy_cost": 42, "gold_reward": 1300, "gems_reward": 42, "exp_reward": 240, "required_power": 9000},
    {"name": _("Throne of Gods"), "difficulty": "hell", "order": 30, "energy_cost": 50, "gold_reward": 1500, "gems_reward": 50, "exp_reward": 300, "required_power": 10000, "is_boss_level": True},
]


class Command(BaseCommand):
    """Seed the database with initial game data."""

    help = "Seed the database with gods, items, and campaign levels"

    def handle(self, *args, **options):
        """Execute the seeding command."""
        self.stdout.write("Seeding gods...")
        gods_created = 0
        for data in GODS_DATA:
            _, created = God.objects.get_or_create(name=data["name"], defaults=data)
            if created:
                gods_created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {gods_created} gods"))

        self.stdout.write("Seeding items...")
        items_created = 0
        for data in ITEMS_DATA:
            _, created = Item.objects.get_or_create(name=data["name"], defaults=data)
            if created:
                items_created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {items_created} items"))

        self.stdout.write("Seeding campaign levels...")
        from apps.campaign.models import CampaignLevel

        levels_created = 0
        for data in CAMPAIGN_LEVELS_DATA:
            _, created = CampaignLevel.objects.get_or_create(
                order=data["order"], defaults=data
            )
            if created:
                levels_created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {levels_created} campaign levels"))

        self.stdout.write("Seeding faction ladders...")
        ladders_created = 0
        for pantheon_value, pantheon_label in Pantheon.choices:
            ladder, created = FactionLadder.objects.get_or_create(
                pantheon=pantheon_value,
                defaults={
                    "name": f"{pantheon_label} Trials",
                    "description": f"Challenge the {pantheon_label} pantheon",
                    "color": "#4a9eff",
                }
            )
            if created:
                ladders_created += 1

            stages_created = 0
            trial_names = FACTION_TRIAL_NAMES.get(pantheon_value, [])
            for floor, name in enumerate(trial_names, start=1):
                _, created = FactionStage.objects.get_or_create(
                    ladder=ladder,
                    floor=floor,
                    defaults={
                        "name": name,
                        "required_power": 500 + (floor * 250),
                        "is_boss": floor % 10 == 0,
                    }
                )
                if created:
                    stages_created += 1
            self.stdout.write(f"  {pantheon_label}: {stages_created} stages")

        self.stdout.write(self.style.SUCCESS(f"Created {ladders_created} faction ladders"))
        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
