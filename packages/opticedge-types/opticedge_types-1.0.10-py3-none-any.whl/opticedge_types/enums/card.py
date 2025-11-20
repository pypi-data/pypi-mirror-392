from enum import IntEnum, Enum

class ApprovalStatus(IntEnum):
    RESCAN = -2
    PENDING = -1
    FAILED = 0
    APPROVED = 1
    PENDING_BY_XIMILAR = 2
    APPROVING = 999


class GradingType(IntEnum):
    UNKNOWN = 0
    COLLECTION = 1
    ADDED = 2
    SOLD = 3
    CARD_CENTERING = 6


class GradingField(Enum):
    GRADING = "grading"
    CENTER  = "centering_grading"
    SURFACE = "surface_grading"
    EDGE    = "edge_grading"
    CORNER  = "corner_grading"
    ENVIRONMENT = "grading_environment"
    CONFIDENCE = "grading_confidence"
    STRUCTURE = "card_structure"


class CardType(Enum):
    POKEMON = "pokemon"
    LORCANA = "lorcana"
    MAGIC = "magic"
    YUGIOH = "yugioh"
    VIDEO_GAMES = "video_games"
    DIGIMON = "digimon"
    DRAGON_BALL = "dragon_ball"
    ONE_PIECE = "one_piece"
