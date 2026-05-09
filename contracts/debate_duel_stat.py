# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from dataclasses import dataclass
import typing
import json


@allow_storage
@dataclass
class DebaterProfile:
    wallet: str
    nickname: str
    matches_played: u256
    matches_won: u256
    matches_lost: u256
    matches_drawn: u256
    rounds_won: u256
    total_logic_score: u256
    total_evidence_score: u256
    total_persuasion_score: u256
    win_streak: u256
    best_streak: u256

    def to_dict(self):
        played = int(self.matches_played)
        won = int(self.matches_won)
        win_rate = str(round((won / played * 100), 1)) if played > 0 else "0"
        total_score = int(self.total_logic_score) + int(self.total_evidence_score) + int(self.total_persuasion_score)
        rounds = int(self.rounds_won) if int(self.rounds_won) > 0 else 1
        avg_score = str(round(total_score / rounds, 1))
        return {
            "wallet": self.wallet,
            "nickname": self.nickname,
            "matches_played": str(self.matches_played),
            "matches_won": str(self.matches_won),
            "matches_lost": str(self.matches_lost),
            "matches_drawn": str(self.matches_drawn),
            "rounds_won": str(self.rounds_won),
            "total_logic_score": str(self.total_logic_score),
            "total_evidence_score": str(self.total_evidence_score),
            "total_persuasion_score": str(self.total_persuasion_score),
            "win_rate": win_rate,
            "avg_score_per_round": avg_score,
            "win_streak": str(self.win_streak),
            "best_streak": str(self.best_streak),
        }


class DebateDuelStat(gl.Contract):
    owner: Address
    admins: DynArray[Address]
    profiles: TreeMap[Address, DebaterProfile]
    nicknames: TreeMap[Address, str]
    error: str

    def __init__(self) -> None:
        self.owner = gl.message.sender_address
        self.admins.append(gl.message.sender_address)
        self.error = "None"

    @gl.public.write
    def add_admin(self, admin_contract: str) -> None:
        if self.owner != gl.message.sender_address:
            raise Exception("Not owner")
        self.admins.append(Address(admin_contract))

    @gl.public.write
    def clear_admins(self) -> None:
        if self.owner != gl.message.sender_address:
            raise Exception("Not owner")
        self.admins.clear()
        self.admins.append(gl.message.sender_address)

    @gl.public.write
    def set_nickname(self, nick: str) -> None:
        self.nicknames[gl.message.sender_address] = _truncate(nick, 25)
        addr = gl.message.sender_address
        if addr in self.profiles:
            self.profiles[addr].nickname = _truncate(nick, 25)

    @gl.public.write
    def record_match_result(
        self,
        player_address: str,
        result: str,
        rounds_won: u256,
        logic_score: u256,
        evidence_score: u256,
        persuasion_score: u256,
    ) -> None:
        if gl.message.sender_address not in self.admins:
            raise Exception("Not admin")
        pa = Address(player_address)
        nick = self.nicknames.get(pa, "")
        if pa not in self.profiles:
            self.profiles[pa] = DebaterProfile(
                wallet=player_address,
                nickname=nick,
                matches_played=0,
                matches_won=0,
                matches_lost=0,
                matches_drawn=0,
                rounds_won=0,
                total_logic_score=0,
                total_evidence_score=0,
                total_persuasion_score=0,
                win_streak=0,
                best_streak=0,
            )
        p = self.profiles[pa]
        p.matches_played += 1
        p.rounds_won += rounds_won
        p.total_logic_score += logic_score
        p.total_evidence_score += evidence_score
        p.total_persuasion_score += persuasion_score
        if result == "win":
            p.matches_won += 1
            p.win_streak += 1
            if p.win_streak > p.best_streak:
                p.best_streak = p.win_streak
        elif result == "loss":
            p.matches_lost += 1
            p.win_streak = 0
        else:
            p.matches_drawn += 1
            p.win_streak = 0
        self.error = "Recorded: " + player_address

    @gl.public.view
    def get_profile(self, player_address: str) -> dict:
        pa = Address(player_address)
        p = self.profiles.get(pa)
        if p is None:
            return {"error": "Profile not found"}
        return p.to_dict()

    @gl.public.view
    def get_my_profile(self) -> dict:
        p = self.profiles.get(gl.message.sender_address)
        if p is None:
            return {"error": "No profile yet"}
        return p.to_dict()

    @gl.public.view
    def get_leaderboard(self, limit: int) -> str:
        try:
            result = []
            sorted_profiles = sorted(
                self.profiles.items(),
                key=lambda kv: (int(kv[1].matches_won), int(kv[1].rounds_won)),
                reverse=True,
            )
            for k, v in sorted_profiles[:limit]:
                result.append(v.to_dict())
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @gl.public.view
    def get_nicknames(self) -> dict:
        return {k.as_hex: v for k, v in self.nicknames.items()}

    @gl.public.view
    def get_admins(self) -> str:
        return json.dumps([{"address": a.as_hex} for a in self.admins])

    @gl.public.view
    def get_error(self) -> str:
        return self.error


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "…"
