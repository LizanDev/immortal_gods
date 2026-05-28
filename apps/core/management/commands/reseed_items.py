"""Management command to reseed god-specific items."""
from django.core.management.base import BaseCommand

from apps.gods.models import God, Pantheon, Rarity, Role
from apps.items.models import Item, ItemType


ITEMS_DATA = [
    # Greek Gods - Zeus (3 items)
    {"name": "Thunder Sword", "item_type": ItemType.WEAPON, "attack_bonus": 50, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 10, "belongs_to_god": "Zeus", "passive_name": "Storm Caller", "passive_desc": "Lightning strikes deal double damage", "passive_atk": 30, "passive_def": 0, "passive_hp": 0, "passive_spd": 5},
    {"name": "Aegis of Zeus", "item_type": ItemType.ARMOR, "attack_bonus": 10, "defense_bonus": 70, "hp_bonus": 250, "speed_bonus": 0, "belongs_to_god": "Zeus", "passive_name": "Divine Shield", "passive_desc": "Creates an impenetrable barrier", "passive_atk": 0, "passive_def": 40, "passive_hp": 150, "passive_spd": 0},
    {"name": "Crown of Zeus", "item_type": ItemType.AMULET, "attack_bonus": 20, "defense_bonus": 30, "hp_bonus": 100, "speed_bonus": 10, "belongs_to_god": "Zeus", "passive_name": "King's Authority", "passive_desc": "Commands respect from all gods", "passive_atk": 15, "passive_def": 15, "passive_hp": 50, "passive_spd": 5},

    # Greek Gods - Poseidon (3 items)
    {"name": "Poseidon's Trident", "item_type": ItemType.WEAPON, "attack_bonus": 60, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 5, "belongs_to_god": "Poseidon", "passive_name": "Ocean's Wrath", "passive_desc": "Tidal waves crash on enemies", "passive_atk": 25, "passive_def": 0, "passive_hp": 100, "passive_spd": 0},
    {"name": "Sea King's Armor", "item_type": ItemType.ARMOR, "attack_bonus": 5, "defense_bonus": 55, "hp_bonus": 350, "speed_bonus": -5, "belongs_to_god": "Poseidon", "passive_name": "Ocean's Depth", "passive_desc": "Underwater pressure strengthens defense", "passive_atk": 0, "passive_def": 30, "passive_hp": 200, "passive_spd": 0},
    {"name": "Neptune's Pendant", "item_type": ItemType.AMULET, "attack_bonus": 15, "defense_bonus": 15, "hp_bonus": 150, "speed_bonus": 15, "belongs_to_god": "Poseidon", "passive_name": "Tidal Blessing", "passive_desc": "Currents guide all actions", "passive_atk": 10, "passive_def": 10, "passive_hp": 100, "passive_spd": 10},

    # Greek Gods - Hades (3 items)
    {"name": "Hades' Scythe", "item_type": ItemType.WEAPON, "attack_bonus": 70, "defense_bonus": 0, "hp_bonus": -50, "speed_bonus": 15, "belongs_to_god": "Hades", "passive_name": "Soul Reaper", "passive_desc": "Steals life from fallen enemies", "passive_atk": 40, "passive_def": 0, "passive_hp": 0, "passive_spd": 10},
    {"name": "Underworld Cloak", "item_type": ItemType.ARMOR, "attack_bonus": 0, "defense_bonus": 50, "hp_bonus": 300, "speed_bonus": 0, "belongs_to_god": "Hades", "passive_name": "Death's Embrace", "passive_desc": "Shadows provide protection", "passive_atk": 0, "passive_def": 35, "passive_hp": 150, "passive_spd": 0},
    {"name": "Helm of Darkness", "item_type": ItemType.AMULET, "attack_bonus": 20, "defense_bonus": 20, "hp_bonus": 100, "speed_bonus": 5, "belongs_to_god": "Hades", "passive_name": "Shadow Walk", "passive_desc": "Moves unseen through shadows", "passive_atk": 15, "passive_def": 10, "passive_hp": 50, "passive_spd": 5},

    # Greek Gods - Ares (3 items)
    {"name": "Blades of Chaos", "item_type": ItemType.WEAPON, "attack_bonus": 65, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 10, "belongs_to_god": "Ares", "passive_name": "Bloodlust", "passive_desc": "Gains strength from bloodshed", "passive_atk": 35, "passive_def": 0, "passive_hp": 0, "passive_spd": 5},
    {"name": "War Lord's Plate", "item_type": ItemType.ARMOR, "attack_bonus": 15, "defense_bonus": 60, "hp_bonus": 200, "speed_bonus": -5, "belongs_to_god": "Ares", "passive_name": "Battle Hardened", "passive_desc": "Victory breeds resilience", "passive_atk": 10, "passive_def": 30, "passive_hp": 100, "passive_spd": 0},
    {"name": "Skull Pendant", "item_type": ItemType.AMULET, "attack_bonus": 25, "defense_bonus": 10, "hp_bonus": 80, "speed_bonus": 10, "belongs_to_god": "Ares", "passive_name": "Warmonger", "passive_desc": "The god of war demands blood", "passive_atk": 15, "passive_def": 5, "passive_hp": 50, "passive_spd": 5},

    # Greek Gods - Athena (3 items)
    {"name": "Spear of Athena", "item_type": ItemType.WEAPON, "attack_bonus": 55, "defense_bonus": 10, "hp_bonus": 50, "speed_bonus": 5, "belongs_to_god": "Athena", "passive_name": "Divine Wisdom", "passive_desc": "Strategic advantage in battle", "passive_atk": 25, "passive_def": 15, "passive_hp": 50, "passive_spd": 5},
    {"name": "Aegis Shield", "item_type": ItemType.ARMOR, "attack_bonus": 0, "defense_bonus": 65, "hp_bonus": 250, "speed_bonus": -5, "belongs_to_god": "Athena", "passive_name": "Divine Protection", "passive_desc": "Shield reflects 20% of damage", "passive_atk": 0, "passive_def": 35, "passive_hp": 150, "passive_spd": 0},
    {"name": "Owl Eye Amulet", "item_type": ItemType.AMULET, "attack_bonus": 15, "defense_bonus": 25, "hp_bonus": 100, "speed_bonus": 10, "belongs_to_god": "Athena", "passive_name": "Wisdom's Eye", "passive_desc": "Sees through all deception", "passive_atk": 10, "passive_def": 15, "passive_hp": 50, "passive_spd": 10},

    # Greek Gods - Apollo (3 items)
    {"name": "Apollo's Bow", "item_type": ItemType.WEAPON, "attack_bonus": 55, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 20, "belongs_to_god": "Apollo", "passive_name": "Sun Piercer", "passive_desc": "Arrows burn through armor", "passive_atk": 20, "passive_def": 0, "passive_hp": 0, "passive_spd": 15},
    {"name": "Solar Armor", "item_type": ItemType.ARMOR, "attack_bonus": 10, "defense_bonus": 50, "hp_bonus": 200, "speed_bonus": 5, "belongs_to_god": "Apollo", "passive_name": "Radiant Body", "passive_desc": "Light provides protection", "passive_atk": 5, "passive_def": 30, "passive_hp": 100, "passive_spd": 5},
    {"name": "Laurel Crown", "item_type": ItemType.AMULET, "attack_bonus": 20, "defense_bonus": 15, "hp_bonus": 80, "speed_bonus": 15, "belongs_to_god": "Apollo", "passive_name": "Sun's Blessing", "passive_desc": "The sun guides all paths", "passive_atk": 15, "passive_def": 10, "passive_hp": 50, "passive_spd": 10},

    # Greek Gods - Artemis (3 items)
    {"name": "Moonlit Bow", "item_type": ItemType.WEAPON, "attack_bonus": 50, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 25, "belongs_to_god": "Artemis", "passive_name": "Moonlight Arrow", "passive_desc": "Silver arrows never miss", "passive_atk": 25, "passive_def": 0, "passive_hp": 0, "passive_spd": 15},
    {"name": "Hunter's Guard", "item_type": ItemType.ARMOR, "attack_bonus": 5, "defense_bonus": 45, "hp_bonus": 180, "speed_bonus": 10, "belongs_to_god": "Artemis", "passive_name": "Beast's Instinct", "passive_desc": "Animal agility protects", "passive_atk": 0, "passive_def": 25, "passive_hp": 100, "passive_spd": 10},
    {"name": "Moonstone Pendant", "item_type": ItemType.AMULET, "attack_bonus": 15, "defense_bonus": 15, "hp_bonus": 100, "speed_bonus": 20, "belongs_to_god": "Artemis", "passive_name": "Lunar Grace", "passive_desc": "The moon empowers all actions", "passive_atk": 10, "passive_def": 10, "passive_hp": 50, "passive_spd": 15},

    # Greek Gods - Hermes (3 items)
    {"name": "Caduceus Staff", "item_type": ItemType.WEAPON, "attack_bonus": 45, "defense_bonus": 5, "hp_bonus": 0, "speed_bonus": 30, "belongs_to_god": "Hermes", "passive_name": "Swift Strike", "passive_desc": "Lightning fast attacks", "passive_atk": 20, "passive_def": 0, "passive_hp": 0, "passive_spd": 20},
    {"name": "Winged Boots", "item_type": ItemType.ARMOR, "attack_bonus": 5, "defense_bonus": 30, "hp_bonus": 100, "speed_bonus": 20, "belongs_to_god": "Hermes", "passive_name": "Wind Walker", "passive_desc": "As light as the wind", "passive_atk": 0, "passive_def": 20, "passive_hp": 50, "passive_spd": 15},
    {"name": "Hermes' Sandals", "item_type": ItemType.AMULET, "attack_bonus": 10, "defense_bonus": 10, "hp_bonus": 50, "speed_bonus": 40, "belongs_to_god": "Hermes", "passive_name": "Messenger's Swiftness", "passive_desc": "Moves faster than thought itself", "passive_atk": 5, "passive_def": 5, "passive_hp": 0, "passive_spd": 30},

    # Greek Gods - Hephaestus (3 items)
    {"name": "Forge Hammer", "item_type": ItemType.WEAPON, "attack_bonus": 60, "defense_bonus": 15, "hp_bonus": 50, "speed_bonus": -5, "belongs_to_god": "Hephaestus", "passive_name": "Molten Strike", "passive_desc": "Fire enhances every blow", "passive_atk": 35, "passive_def": 10, "passive_hp": 0, "passive_spd": 0},
    {"name": "Divine Forged Plate", "item_type": ItemType.ARMOR, "attack_bonus": 10, "defense_bonus": 70, "hp_bonus": 300, "speed_bonus": -10, "belongs_to_god": "Hephaestus", "passive_name": "Fire Protection", "passive_desc": "Forged in celestial flames", "passive_atk": 0, "passive_def": 40, "passive_hp": 200, "passive_spd": 0},
    {"name": "Iron Boots", "item_type": ItemType.AMULET, "attack_bonus": 5, "defense_bonus": 30, "hp_bonus": 100, "speed_bonus": -5, "belongs_to_god": "Hephaestus", "passive_name": "Forge Walker", "passive_desc": "Immune to lava and fire", "passive_atk": 0, "passive_def": 20, "passive_hp": 50, "passive_spd": 0},

    # Greek Gods - Demeter (3 items)
    {"name": "Harvest Scythe", "item_type": ItemType.WEAPON, "attack_bonus": 45, "defense_bonus": 5, "hp_bonus": 50, "speed_bonus": 5, "belongs_to_god": "Demeter", "passive_name": "Nature's Wrath", "passive_desc": "Plants entangle enemies", "passive_atk": 20, "passive_def": 5, "passive_hp": 50, "passive_spd": 5},
    {"name": "Nature's Mantle", "item_type": ItemType.ARMOR, "attack_bonus": 5, "defense_bonus": 45, "hp_bonus": 250, "speed_bonus": 5, "belongs_to_god": "Demeter", "passive_name": "Earth's Embrace", "passive_desc": "Nature provides shelter", "passive_atk": 0, "passive_def": 25, "passive_hp": 150, "passive_spd": 5},
    {"name": "Seed of Life", "item_type": ItemType.AMULET, "attack_bonus": 10, "defense_bonus": 20, "hp_bonus": 200, "speed_bonus": 5, "belongs_to_god": "Demeter", "passive_name": "Regeneration", "passive_desc": "Life energy constantly heals", "passive_atk": 0, "passive_def": 10, "passive_hp": 150, "passive_spd": 0},

    # Zodiac - Leo (3)
    {"name": "Leo Claw", "item_type": ItemType.WEAPON, "attack_bonus": 60, "defense_bonus": 5, "hp_bonus": 0, "speed_bonus": 15, "belongs_to_god": "Leo", "passive_name": "King's Strike", "passive_desc": "The lion strikes with authority", "passive_atk": 35, "passive_def": 0, "passive_hp": 0, "passive_spd": 10},
    {"name": "Royal Mane Armor", "item_type": ItemType.ARMOR, "attack_bonus": 10, "defense_bonus": 55, "hp_bonus": 250, "speed_bonus": 0, "belongs_to_god": "Leo", "passive_name": "Pride's Strength", "passive_desc": "The king of beasts cannot be defeated", "passive_atk": 5, "passive_def": 30, "passive_hp": 150, "passive_spd": 0},
    {"name": "Zodiac Crown", "item_type": ItemType.AMULET, "attack_bonus": 20, "defense_bonus": 20, "hp_bonus": 100, "speed_bonus": 20, "belongs_to_god": "Leo", "passive_name": "Star Alignment", "passive_desc": "Constellations empower the wearer", "passive_atk": 10, "passive_def": 10, "passive_hp": 50, "passive_spd": 10},

    # Zodiac - Aries (3)
    {"name": "Ram Horn Blade", "item_type": ItemType.WEAPON, "attack_bonus": 55, "defense_bonus": 10, "hp_bonus": 0, "speed_bonus": 15, "belongs_to_god": "Aries", "passive_name": "Ram Charge", "passive_desc": "Never retreat, always charge forward", "passive_atk": 30, "passive_def": 5, "passive_hp": 0, "passive_spd": 10},
    {"name": "Wool Coat", "item_type": ItemType.ARMOR, "attack_bonus": 5, "defense_bonus": 50, "hp_bonus": 200, "speed_bonus": 5, "belongs_to_god": "Aries", "passive_name": "Fiery Wool", "passive_desc": "Warmth provides protection", "passive_atk": 0, "passive_def": 30, "passive_hp": 100, "passive_spd": 5},
    {"name": "Golden Fleece", "item_type": ItemType.AMULET, "attack_bonus": 15, "defense_bonus": 25, "hp_bonus": 150, "speed_bonus": 10, "belongs_to_god": "Aries", "passive_name": "Mythic Shield", "passive_desc": "Legendary protection from all harm", "passive_atk": 10, "passive_def": 15, "passive_hp": 100, "passive_spd": 5},

    # Zodiac - Taurus (3)
    {"name": "Bull Horns", "item_type": ItemType.WEAPON, "attack_bonus": 50, "defense_bonus": 15, "hp_bonus": 100, "speed_bonus": -5, "belongs_to_god": "Taurus", "passive_name": "Immovable Force", "passive_desc": "As strong as the earth itself", "passive_atk": 25, "passive_def": 15, "passive_hp": 100, "passive_spd": 0},
    {"name": "Stone Skin", "item_type": ItemType.ARMOR, "attack_bonus": 0, "defense_bonus": 70, "hp_bonus": 350, "speed_bonus": -10, "belongs_to_god": "Taurus", "passive_name": "Mountain's Defense", "passive_desc": "Unmovable and unbreakable", "passive_atk": 0, "passive_def": 45, "passive_hp": 200, "passive_spd": 0},
    {"name": "Earth Gem", "item_type": ItemType.AMULET, "attack_bonus": 10, "defense_bonus": 30, "hp_bonus": 200, "speed_bonus": 0, "belongs_to_god": "Taurus", "passive_name": "Earth's Blessing", "passive_desc": "The earth provides strength", "passive_atk": 5, "passive_def": 20, "passive_hp": 150, "passive_spd": 0},

    # Zodiac - Scorpio (3)
    {"name": "Venomous Stinger", "item_type": ItemType.WEAPON, "attack_bonus": 65, "defense_bonus": 0, "hp_bonus": -30, "speed_bonus": 10, "belongs_to_god": "Scorpio", "passive_name": "Deadly Poison", "passive_desc": "Poison weakens all enemies", "passive_atk": 40, "passive_def": 0, "passive_hp": 0, "passive_spd": 5},
    {"name": "Scorpion Shell", "item_type": ItemType.ARMOR, "attack_bonus": 5, "defense_bonus": 55, "hp_bonus": 200, "speed_bonus": 0, "belongs_to_god": "Scorpio", "passive_name": "Venom Shield", "passive_desc": "Poisonous carapace protects", "passive_atk": 5, "passive_def": 35, "passive_hp": 100, "passive_spd": 0},
    {"name": "Stinger Pendant", "item_type": ItemType.AMULET, "attack_bonus": 20, "defense_bonus": 15, "hp_bonus": 80, "speed_bonus": 15, "belongs_to_god": "Scorpio", "passive_name": "Ambush Master", "passive_desc": "Strikes when least expected", "passive_atk": 15, "passive_def": 10, "passive_hp": 50, "passive_spd": 10},

    # Zodiac - Sagittarius (3)
    {"name": "Celestial Bow", "item_type": ItemType.WEAPON, "attack_bonus": 60, "defense_bonus": 0, "hp_bonus": 0, "speed_bonus": 20, "belongs_to_god": "Sagittarius", "passive_name": "Star Arrow", "passive_desc": "Arrows fall like meteors", "passive_atk": 35, "passive_def": 0, "passive_hp": 0, "passive_spd": 15},
    {"name": "Centaur Hooves", "item_type": ItemType.ARMOR, "attack_bonus": 10, "defense_bonus": 45, "hp_bonus": 180, "speed_bonus": 10, "belongs_to_god": "Sagittarius", "passive_name": "Swift Movement", "passive_desc": "Gallop across the battlefield", "passive_atk": 5, "passive_def": 25, "passive_hp": 100, "passive_spd": 10},
    {"name": "Arrow Charm", "item_type": ItemType.AMULET, "attack_bonus": 20, "defense_bonus": 10, "hp_bonus": 80, "speed_bonus": 20, "belongs_to_god": "Sagittarius", "passive_name": "Perfect Aim", "passive_desc": "Never misses the target", "passive_atk": 15, "passive_def": 5, "passive_hp": 50, "passive_spd": 15},

    # Zodiac - Aquarius (3)
    {"name": "Water Bearer Vessel", "item_type": ItemType.WEAPON, "attack_bonus": 50, "defense_bonus": 10, "hp_bonus": 50, "speed_bonus": 15, "belongs_to_god": "Aquarius", "passive_name": "Tidal Wave", "passive_desc": "Water crushes all obstacles", "passive_atk": 25, "passive_def": 5, "passive_hp": 50, "passive_spd": 10},
    {"name": "Cosmic Armor", "item_type": ItemType.ARMOR, "attack_bonus": 10, "defense_bonus": 50, "hp_bonus": 250, "speed_bonus": 5, "belongs_to_god": "Aquarius", "passive_name": "Star Protection", "passive_desc": "Cosmic water shields the body", "passive_atk": 5, "passive_def": 30, "passive_hp": 150, "passive_spd": 5},
    {"name": "Aquarius Ring", "item_type": ItemType.AMULET, "attack_bonus": 15, "defense_bonus": 20, "hp_bonus": 150, "speed_bonus": 15, "belongs_to_god": "Aquarius", "passive_name": "Water Spirit", "passive_desc": "Flows like water in battle", "passive_atk": 10, "passive_def": 10, "passive_hp": 100, "passive_spd": 10},

    # Zodiac - Pisces (3)
    {"name": "Fish Staff", "item_type": ItemType.WEAPON, "attack_bonus": 45, "defense_bonus": 15, "hp_bonus": 80, "speed_bonus": 10, "belongs_to_god": "Pisces", "passive_name": "Ocean's Call", "passive_desc": "The sea answers every call", "passive_atk": 20, "passive_def": 10, "passive_hp": 80, "passive_spd": 5},
    {"name": "Fish Scale Mail", "item_type": ItemType.ARMOR, "attack_bonus": 5, "defense_bonus": 50, "hp_bonus": 280, "speed_bonus": 0, "belongs_to_god": "Pisces", "passive_name": "Deep Sea Shield", "passive_desc": "The depths protect their own", "passive_atk": 0, "passive_def": 30, "passive_hp": 180, "passive_spd": 0},
    {"name": "Moonfish Pendant", "item_type": ItemType.AMULET, "attack_bonus": 15, "defense_bonus": 20, "hp_bonus": 150, "speed_bonus": 10, "belongs_to_god": "Pisces", "passive_name": "Dream Walker", "passive_desc": "Dreams become reality", "passive_atk": 10, "passive_def": 10, "passive_hp": 100, "passive_spd": 5},

    # Zodiac - Gemini (3)
    {"name": "Twin Blades", "item_type": ItemType.WEAPON, "attack_bonus": 55, "defense_bonus": 5, "hp_bonus": 0, "speed_bonus": 20, "belongs_to_god": "Gemini", "passive_name": "Twin Strike", "passive_desc": "Two strikes for the price of one", "passive_atk": 30, "passive_def": 0, "passive_hp": 0, "passive_spd": 15},
    {"name": "Dual Shield", "item_type": ItemType.ARMOR, "attack_bonus": 10, "defense_bonus": 55, "hp_bonus": 200, "speed_bonus": 5, "belongs_to_god": "Gemini", "passive_name": "Mirror Image", "passive_desc": "Creates copies to confuse enemies", "passive_atk": 5, "passive_def": 35, "passive_hp": 100, "passive_spd": 5},
    {"name": "Twin Star Amulet", "item_type": ItemType.AMULET, "attack_bonus": 20, "defense_bonus": 15, "hp_bonus": 100, "speed_bonus": 20, "belongs_to_god": "Gemini", "passive_name": "Star Power", "passive_desc": "The stars align for victory", "passive_atk": 15, "passive_def": 10, "passive_hp": 50, "passive_spd": 15},

    # Zodiac - Virgo (3)
    {"name": "Wheat Sickle", "item_type": ItemType.WEAPON, "attack_bonus": 45, "defense_bonus": 10, "hp_bonus": 50, "speed_bonus": 10, "belongs_to_god": "Virgo", "passive_name": "Harvest Blessing", "passive_desc": "Abundance empowers all actions", "passive_atk": 20, "passive_def": 5, "passive_hp": 50, "passive_spd": 5},
    {"name": "Pure White Robes", "item_type": ItemType.ARMOR, "attack_bonus": 5, "defense_bonus": 50, "hp_bonus": 220, "speed_bonus": 5, "belongs_to_god": "Virgo", "passive_name": "Purification", "passive_desc": "Purity shields from harm", "passive_atk": 0, "passive_def": 30, "passive_hp": 120, "passive_spd": 5},
    {"name": "Harvest Amulet", "item_type": ItemType.AMULET, "attack_bonus": 15, "defense_bonus": 20, "hp_bonus": 150, "speed_bonus": 10, "belongs_to_god": "Virgo", "passive_name": "Earth Mother's Gift", "passive_desc": "Nature's bounty is endless", "passive_atk": 10, "passive_def": 10, "passive_hp": 100, "passive_spd": 5},

    # Zodiac - Libra (3)
    {"name": "Scale Sword", "item_type": ItemType.WEAPON, "attack_bonus": 50, "defense_bonus": 10, "hp_bonus": 50, "speed_bonus": 10, "belongs_to_god": "Libra", "passive_name": "Balance Strike", "passive_desc": "Perfect balance in every attack", "passive_atk": 25, "passive_def": 5, "passive_hp": 50, "passive_spd": 10},
    {"name": "Balance Shield", "item_type": ItemType.ARMOR, "attack_bonus": 10, "defense_bonus": 50, "hp_bonus": 200, "speed_bonus": 5, "belongs_to_god": "Libra", "passive_name": "Justice's Guard", "passive_desc": "Justice protects the righteous", "passive_atk": 5, "passive_def": 30, "passive_hp": 100, "passive_spd": 5},
    {"name": "Scales Pendant", "item_type": ItemType.AMULET, "attack_bonus": 15, "defense_bonus": 20, "hp_bonus": 120, "speed_bonus": 15, "belongs_to_god": "Libra", "passive_name": "Equality", "passive_desc": "All forces are in harmony", "passive_atk": 10, "passive_def": 10, "passive_hp": 70, "passive_spd": 10},

    # Zodiac - Cancer (3)
    {"name": "Crab Claws", "item_type": ItemType.WEAPON, "attack_bonus": 45, "defense_bonus": 15, "hp_bonus": 100, "speed_bonus": 0, "belongs_to_god": "Cancer", "passive_name": "Shell Crack", "passive_desc": "Hard shell crushes all defenses", "passive_atk": 20, "passive_def": 10, "passive_hp": 100, "passive_spd": 0},
    {"name": "Shell Armor", "item_type": ItemType.ARMOR, "attack_bonus": 0, "defense_bonus": 60, "hp_bonus": 300, "speed_bonus": -5, "belongs_to_god": "Cancer", "passive_name": "Tide Turner", "passive_desc": "The moon controls the tides", "passive_atk": 0, "passive_def": 40, "passive_hp": 200, "passive_spd": 0},
    {"name": "Moon Shell Pendant", "item_type": ItemType.AMULET, "attack_bonus": 10, "defense_bonus": 25, "hp_bonus": 180, "speed_bonus": 5, "belongs_to_god": "Cancer", "passive_name": "Lunar Protection", "passive_desc": "The moon provides strength", "passive_atk": 5, "passive_def": 15, "passive_hp": 120, "passive_spd": 5},

    # Zodiac - Capricorn (3)
    {"name": "Goat Horn Spear", "item_type": ItemType.WEAPON, "attack_bonus": 50, "defense_bonus": 15, "hp_bonus": 50, "speed_bonus": 5, "belongs_to_god": "Capricorn", "passive_name": "Mountain Climb", "passive_desc": "Never stops until the top", "passive_atk": 25, "passive_def": 10, "passive_hp": 50, "passive_spd": 5},
    {"name": "Sea Goat Coat", "item_type": ItemType.ARMOR, "attack_bonus": 10, "defense_bonus": 55, "hp_bonus": 280, "speed_bonus": 0, "belongs_to_god": "Capricorn", "passive_name": "Adaptability", "passive_desc": "Adapts to any environment", "passive_atk": 5, "passive_def": 35, "passive_hp": 180, "passive_spd": 0},
    {"name": "Mountain Peak Charm", "item_type": ItemType.AMULET, "attack_bonus": 15, "defense_bonus": 25, "hp_bonus": 150, "speed_bonus": 10, "belongs_to_god": "Capricorn", "passive_name": "Ambition", "passive_desc": "Reaches heights unknown", "passive_atk": 10, "passive_def": 15, "passive_hp": 100, "passive_spd": 5},
]


class Command(BaseCommand):
    """Reseed god-specific items."""

    help = "Delete and recreate all god-specific items"

    def handle(self, *args, **options):
        deleted, _ = Item.objects.filter(belongs_to_god__isnull=False).exclude(belongs_to_god='').delete()
        self.stdout.write(f"Deleted {deleted} god-specific items")

        created = 0
        for data in ITEMS_DATA:
            Item.objects.create(**data)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} god-specific items"))
