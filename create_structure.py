import os

regions = [
    "UttarPradesh",
    "Bihar",
    "Delhi",
    "Rajasthan",
    "Haryana",
    "MadhyaPradesh"
]

categories = [
    "Speech",
    "Music",
    "Environment",
    "Mixed"
]

for region in regions:
    for category in categories:
        path = os.path.join("dataset", region, category)
        os.makedirs(path, exist_ok=True)

print("Dataset structure created!")
speech = [
    "Conversation",
    "Interview",
    "Announcement",
    "Storytelling",
    "Debate"
]

music = [
    "Folk",
    "Classical",
    "Devotional",
    "Fusion"
]

environment = [
    "RailwayStation",
    "Market",
    "Temple",
    "Village",
    "Traffic"
]

mixed = [
    "Wedding",
    "Festival",
    "TempleTraffic",
    "MarketMusic"
]
speech = [
    "Conversation",
    "Interview",
    "Announcement",
    "Storytelling",
    "Debate"
]

music = [
    "Folk",
    "Classical",
    "Devotional",
    "Fusion"
]

environment = [
    "RailwayStation",
    "Market",
    "Temple",
    "Village",
    "Traffic"
]

mixed = [
    "Wedding",
    "Festival",
    "TempleTraffic",
    "MarketMusic"
]
import os

for region in regions:

    for sub in speech:
        os.makedirs(
            os.path.join("dataset", region, "Speech", sub),
            exist_ok=True
        )

    for sub in music:
        os.makedirs(
            os.path.join("dataset", region, "Music", sub),
            exist_ok=True
        )

    for sub in environment:
        os.makedirs(
            os.path.join("dataset", region, "Environment", sub),
            exist_ok=True
        )

    for sub in mixed:
        os.makedirs(
            os.path.join("dataset", region, "Mixed", sub),
            exist_ok=True
        )

print("Complete dataset structure created!")
import os

regions = [
    "UttarPradesh",
    "Bihar",
    "Delhi",
    "Rajasthan",
    "Haryana",
    "MadhyaPradesh"
]

music_structure = {
    "Classical": [
        "Hindustani_Vocal",
        "Khayal",
        "Dhrupad",
        "Thumri",
        "Sitar",
        "Sarod",
        "Bansuri",
        "Tabla_Solo"
    ],

    "Folk": [
        "Kajri",
        "Chaiti",
        "Sohar",
        "Bhojpuri_Folk",
        "Rajasthani_Folk",
        "Bihu",
        "Baul",
        "Lavani",
        "Garba",
        "Giddha"
    ],

    "Devotional": [
        "Bhajan",
        "Kirtan",
        "Aarti",
        "Qawwali",
        "Hanuman_Chalisa",
        "Temple_Chants"
    ],

    "Fusion": [
        "Folk_Fusion",
        "Classical_Fusion",
        "Bollywood_Fusion",
        "Electronic_Fusion"
    ]
}

for region in regions:
    for main_cat, subs in music_structure.items():
        for sub in subs:
            path = os.path.join(
                "dataset",
                region,
                "Music",
                main_cat,
                sub
            )
            os.makedirs(path, exist_ok=True)

print("Music structure created successfully!")