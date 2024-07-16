from backend.Types.Theme import Theme

Available_Themes = [
    Theme(
        name="fantasy",
        fields={
            "race": ["Elf", "Dwarf", "Human", "Orc", "Half-Elf", "Goblin", "Dark-One"],
            "profession": ["Archer", "Warrior", "Mage", "Rogue", "Bard", "Druid", "Cleric", "Paladin", "Ranger", "Monk", "Barbarian", "Dragon-Rider"]
        },
        extra_inventory_categories=[
            {"field": "profession", "value": ["Archer", "Ranger"], "categories": ["quiver"]},
            {"field": "profession", "value": ["Mage", "Druid", "Dragon-Rider"], "categories": ["spells"]},
            {"field": "profession", "value": ["Dragon-Rider"], "categories": ["dragon"]},
        ],
        extra_fields=[
            {"field": "profession", "value": ["Barbarian"], "extra_field": "Tribe", "extra_field_value": "the player's tribe name"},
            {"field": "profession", "value": ["Mage"], "extra_field": "Magic School", "extra_field_value": "the player's magic school"},
        ]
    ),
    Theme(
        name="sci-fi",
        fields={
            "profession": ["Spaceship Pilot", "Spaceship Captain", "Scientist", "Soldier", "Merchant", "Bounty Hunter", "Smuggler", "Detective"],
            "affiliation": ["Federation", "Empire", "Republic", "Martian", "Earth", "Belter", "Freelancer"]
        },
        extra_inventory_categories=[
            {"field": "profession", "value": ["Spaceship Captain", "Spaceship Pilot"], "categories": ["spaceship", "spaceship_crew"]},
            {"field": "profession", "value": ["Bounty Hunter"], "categories": ["spaceship"]},
        ]
    ),
    Theme(
        name="wild west",
        fields={
            "profession": ["Cowboy", "Sheriff", "Outlaw", "Bounty Hunter", "Gunslinger", "Prospector", "Rancher", "Saloon Owner", "Banker", "Preacher", "Doctor", "Indian"]
        },
        skills=["SHOOTING", "HORSE RIDING", "SURVIVAL", "CHARISMA", "PERCEPTION", "LUCK"],
        extra_inventory_categories=[
            {"field": "profession", "value": "ALL", "categories": ["horse"]},
        ],
        extra_fields=[
            {"field": "profession", "value": ["Indian"], "extra_field": "Tribe", "extra_field_value": "the player's tribe name"},
            {"field": "profession", "value": ["Saloon Owner"], "extra_field": "Saloon_Name", "extra_field_value": "the player's Saloon name"}
        ]
    ),
    Theme(
        name="superheroes",
        fields={
            "profession": ["Superhero", "Villain", "Sidekick", "Reporter"]
        },
        extra_inventory_categories=[
            {"field": "profession", "value": ["Superhero", "Villain", "Sidekick"], "categories": ["superpowers"]},
        ],
        extra_fields=[
            {"field": "profession", "value": ["Superhero", "Villain"], "extra_field": "real_name", "extra_field_value": "the player's secret identity"},
        ]
    ),
]


def get_theme(name: str) -> Theme:
    for theme in Available_Themes:
        if theme.name == name:
            return theme
    raise ValueError(f"Theme {name} not found!")
