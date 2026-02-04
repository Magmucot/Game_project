import json
import os


class GameDataManager:
    def __init__(self):
        self.file_path = "game_stats.json"
        self.data = self._load()

    def _load(self):
        default = {
            "high_scores": {
                "tanks": 0,
                "fighter_cnt": 0,
                "dice": 0,
                "snake": 0,
                "chess": 0,
                "chess_cnt": 0,
            },
            "total_games": 0,
            "player_stats": {"first_won": 0, "second_won": 0},
            "achievements": [],
            "settings": {"volume": 1.0, "difficulty": "Medium"},
        }
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)

                    for key in default:
                        if key not in loaded:
                            loaded[key] = default[key]
                        elif isinstance(default[key], dict):
                            for subkey in default[key]:
                                if subkey not in loaded[key]:
                                    loaded[key][subkey] = default[key][subkey]
                    return loaded
            except Exception:
                return default
        return default

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def record_game(self, game_type, score, won=False):
        """Записать результат игры. Возвращает True если новый рекорд."""
        self.data["total_games"] += 1
        new_record = False

        if game_type == "fighter":
            self.data["high_scores"]["fighter_cnt"] += 1
            if won:
                self.data["player_stats"]["first_won"] += 1
            else:
                self.data["player_stats"]["second_won"] += 1

        else:
            if score > self.data["high_scores"][game_type]:
                self.data["high_scores"][game_type] = score
                new_record = True

        self.save()
        return new_record

    def get_high_score(self, game_type):
        """Получить рекорд для конкретной игры"""
        mapping = {"tanks": "tanks", "fighter_cnt": "fighter_cnt", "dice": "dice", "snake": "snake", "chess": "chess"}
        key = mapping.get(game_type, game_type)
        return self.data["high_scores"].get(key, 0)
