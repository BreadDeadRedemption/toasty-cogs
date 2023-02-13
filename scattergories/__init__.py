class Scattergories(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.categories = [
            "Fruits",
            "Animals",
            "Countries",
            "Things found in the kitchen",
            "Colors",
            "Types of shoes",
            "Sports",
            "Musical instruments",
            "School subjects",
            "Flowers",
            "Things that are round",
            "Types of cheese",
            "Items you can wear",
            "Words ending in 'ing'",
            "Famous people",
            "Things that are cold",
            "Things you find in a park",
            "Vegetables",
            "Things that are sticky",
            "Items you find in a grocery store",
            "Things you can drink",
            "Insects",
            "TV shows",
            "Items you find in a toolbox"
        ]
        self.players = []
        self.answers = {}
        self.current_category = None
        self.current_letter = None
        self.round_timer = None
        self.voting_time = 60
