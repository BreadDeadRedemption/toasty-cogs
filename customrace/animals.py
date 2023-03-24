import random

racers = [
    ("<:RacerJoey:1088014015860592670>", "fast"),
    ("<a:nyanbredbackwards:1088540722422087801>", "fast"),
    ("<:CocaCola:976820077909401630>", "fast"),
    ("<:aprilol:1088114800535535656>", "steady"),
    ("<:gdog:1088341853440573491>", "steady"),
    ("<:Fanta:976820089892515921>", "steady"),
    ("<:klomaan:977917650309115914>", "slow"),
    ("<a:FishDrive:1081599668489822238>", "abberant"),
    ("<:itsbritneybitch:971484640533684275>", "abberant"),
    ("<a:EdRunLeft:1087942478356815925>", "abberant"),
    ("<:batmangeorge:1064612251023196232>", "predator"),
    ("<:falldog:1088110387217571930>", "predator"),
    ("<:ShrekMMM:975784786100617267>", "predator"),
    ("<:giraffe:1058395728327749724>", "special"),
    ("<:shyguy:1088342845867446352>", "special"),
    ("<a:shewalksleft:1087942457922170960>", "slow"),
    ("<:Jacknonymous:1086388929718136935>", "predator"),
    ("<:maxracer:1088350968128737300>", "slow")
]


class Animal:
    def __init__(self, emoji, _type):
        self.emoji = str(emoji)
        self._type = _type
        self.track = "•   " * 20
        self.position = 80
        self.turn = 0
        self.current = self.track + self.emoji

    def move(self):
        self._update_postion()
        self.turn += 1
        return self.current

    def _update_postion(self):
        distance = self._calculate_movement()
        self.current = "".join(
            (
                self.track[: max(0, self.position - distance)],
                self.emoji,
                self.track[max(0, self.position - distance) :],
            )
        )
        self.position = self._get_position()

    def _get_position(self):
        return self.current.find(self.emoji)

    def _calculate_movement(self):
        if self._type == "slow":
            return random.randint(1, 3) * 3
        elif self._type == "fast":
            return random.randint(0, 4) * 3

        elif self._type == "steady":
            return 2 * 3

        elif self._type == "abberant":
            if random.randint(1, 100) >= 90:
                return 5 * 3
            else:
                return random.randint(0, 2) * 3

        elif self._type == "predator":
            if self.turn % 2 == 0:
                return 0
            else:
                return random.randint(2, 5) * 3

        elif self._type == "special":
            if self.turn % 3:
                return random.choice([len("blue"), len("red"), len("green")]) * 3
            else:
                return 0
        else:
            if self.turn == 1:
                return 14 * 3
            elif self.turn == 2:
                return 0
            else:
                return random.randint(0, 2) * 3
