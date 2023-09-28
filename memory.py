import random
from typing import List
from enum import Enum
from utils.database import Memory
from utils.timeop import getTimestampForDawn, getDaysBetweenTimestamp


class Action(Enum):
    memorized = 1
    blurred = 2
    forgetful = 3


class MemoryQueue:
    def __init__(self, session, lastUpdateTime):
        self.word_total: List[Memory] = session.query(Memory).filter(Memory.word.is_memorized == False).order_by(Memory.word.word).all()
        self.word_queue: List[Memory] = []
        self.memory_decay_daily(lastUpdateTime)

    @staticmethod
    def memory_decay(days, half_life_days, score):
        return int(pow(0.5, days / half_life_days) * score)

    def memory_decay_daily(self, lastUpdateTime):
        days = getDaysBetweenTimestamp(lastUpdateTime, getTimestampForDawn())
        for word in self.word_total:
            score = word.word.score
            if score > 0 and days >= 1:
                # 重新赋值单词记忆分
                word.word.score = self.memory_decay(days, word.word.half_life_days, score)
                if word.word.score < 150:
                    self.word_queue.append(word)
            else:
                self.word_queue.append(word)

    def pop_memory(self) -> Memory:
        return self.word_queue.pop(0)

    def modify_memory(self, memo: Memory, action: Action):
        if not memo.word.is_exposed:
            if action == Action.memorized:
                memo.word.is_memorized = True
                memo.word.is_exposed = True
            elif action == Action.blurred:
                memo.word.is_exposed = True
                memo.word.score = 100
                self._add_to_queue(memo)
            elif action == Action.forgetful:
                memo.word.is_exposed = True
                memo.word.score += 0
                self._add_to_queue(memo)
        if memo.word.is_exposed:
            if action == Action.memorized:
                memo.word.score += 200
                if memo.word.score >= 300:
                    memo.word.score = 300
                    memo.word.half_life_days *= 2
                else:
                    self._add_to_queue(memo)
            if action == Action.blurred:
                memo.word.score += 50
                if memo.word.score >= 300:
                    memo.word.score = 300
                self._add_to_queue(memo)
            if action == Action.forgetful:
                self._add_to_queue(memo)

    def _add_to_queue(self, memo: Memory):
        r = random.randint(5, 10)
        if len(self.word_queue) < r:
            self.word_queue.insert(r, memo)
        else:
            self.word_queue.append(memo)
