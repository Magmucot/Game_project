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
            "fighter_games": {"first_won": 0, "second_won": 0},
            "chess_games": {"white_won": 0, "black_won": 0},
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
        else:
            self.data = default
            self.save()
        return default

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def record_game(self, key, score, won=False):
        """Записать результат игры. Возвращает True если новый рекорд."""
        self.data["total_games"] += 1
        new_record = False

        if key == "fighter":
            self.data["high_scores"]["fighter_cnt"] += 1
            if won:
                self.data["fighter_games"]["first_won"] += 1
            else:
                self.data["fighter_games"]["second_won"] += 1
        elif key == "chess":
            self.data["high_scores"]["chess_cnt"] += 1
            if won:
                self.data["chess_games"]["white_won"] += 1
            else:
                self.data["chess_games"]["black_won"] += 1
        else:
            if score > self.data["high_scores"][key] and key not in ("tanks"):
                self.data["high_scores"][key] = score
                new_record = True

        self.save()
        return new_record

    def get_stats(self, key):
        """Получение данных"""
        try:
            if key in ["first_won", "second_won"]:
                return self.data["fighter_games"].get(key, 0)
            elif key in ["white_won", "black_won"]:
                return self.data["chess_games"].get(key, 0)

            return self.data["high_scores"].get(key, 0)
        except Exception:
            return 0
