import json
import os


class GameDataManager:
    def __init__(self):
        self.file_path = "game_stats.json"
        self.data = self._load()

    def _load(self):
        default = {
            "high_scores": {"tanks": 0, "fighter_wins": 0, "dice_record": 0},
            "total_games": 0,
            "player_stats": {"wins": 0, "losses": 0},
            "achievements": [],
            "settings": {"volume": 1.0, "difficulty": "Medium"},
        }
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    default.update(loaded)
                    return default
            except Exception:
                return default
        return default

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def record_game(self, game_type, score, won):
        self.data["total_games"] += 1
        if game_type == "tanks" and score > self.data["high_scores"]["tanks"]:
            self.data["high_scores"]["tanks"] = score
        elif game_type == "fighter" and won:
            self.data["player_stats"]["wins"] += 1
        elif game_type == "dice" and score > self.data["high_scores"]["dice_record"]:
            self.data["high_scores"]["dice_record"] = score
            return True
        self.save()
        return False
