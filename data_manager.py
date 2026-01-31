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
                "fighter_wins": 0,
                "dice_record": 0,
                "snake": 0,  # Добавлена поддержка snake
            },
            "total_games": 0,
            "player_stats": {"wins": 0, "losses": 0},
            "achievements": [],
            "settings": {"volume": 1.0, "difficulty": "Medium"},
        }
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Глубокое обновление для новых ключей
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

        if game_type == "tanks":
            if score > self.data["high_scores"]["tanks"]:
                self.data["high_scores"]["tanks"] = score
                new_record = True
        elif game_type == "fighter":
            if won:
                self.data["player_stats"]["wins"] += 1
            else:
                self.data["player_stats"]["losses"] += 1
        elif game_type == "dice":
            if score > self.data["high_scores"]["dice_record"]:
                self.data["high_scores"]["dice_record"] = score
                new_record = True
        elif game_type == "snake":
            if score > self.data["high_scores"]["snake"]:
                self.data["high_scores"]["snake"] = score
                new_record = True

        self.save()
        return new_record

    def get_high_score(self, game_type):
        """Получить рекорд для конкретной игры"""
        mapping = {"tanks": "tanks", "fighter": "fighter_wins", "dice": "dice_record", "snake": "snake"}
        key = mapping.get(game_type, game_type)
        return self.data["high_scores"].get(key, 0)
