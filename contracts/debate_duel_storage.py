# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from dataclasses import dataclass
from itertools import islice
import typing
import json


@allow_storage
@dataclass
class Match:
    match_id: str
    player_a: str
    player_b: str
    topic: str
    side_a_position: str
    side_b_position: str
    score_a: u256
    score_b: u256
    current_round: u256
    status: str
    winner: str
    created_at: str

    def to_dict(self):
        return {
            "match_id": self.match_id,
            "player_a": self.player_a,
            "player_b": self.player_b,
            "topic": self.topic,
            "side_a_position": self.side_a_position,
            "side_b_position": self.side_b_position,
            "score_a": str(self.score_a),
            "score_b": str(self.score_b),
            "current_round": str(self.current_round),
            "status": self.status,
            "winner": self.winner,
            "created_at": self.created_at,
        }


@allow_storage
@dataclass
class DebateRound:
    match_id: str
    round_num: u256
    arg_a: str
    arg_b: str
    logic_a: u256
    evidence_a: u256
    persuasion_a: u256
    total_a: u256
    logic_b: u256
    evidence_b: u256
    persuasion_b: u256
    total_b: u256
    round_winner: str
    judgment: str

    def to_dict(self):
        return {
            "match_id": self.match_id,
            "round_num": str(self.round_num),
            "arg_a": self.arg_a,
            "arg_b": self.arg_b,
            "logic_a": str(self.logic_a),
            "evidence_a": str(self.evidence_a),
            "persuasion_a": str(self.persuasion_a),
            "total_a": str(self.total_a),
            "logic_b": str(self.logic_b),
            "evidence_b": str(self.evidence_b),
            "persuasion_b": str(self.persuasion_b),
            "total_b": str(self.total_b),
            "round_winner": self.round_winner,
            "judgment": self.judgment,
        }


class DebateDuelStorage(gl.Contract):
    owner: Address
    admins: DynArray[Address]
    matches: TreeMap[str, Match]
    rounds: TreeMap[str, DebateRound]
    total_matches: u256
    error: str

    def __init__(self) -> None:
        self.owner = gl.message.sender_address
        self.admins.append(gl.message.sender_address)
        self.total_matches = 0
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
    def save_match(self, data: dict) -> None:
        if gl.message.sender_address not in self.admins:
            raise Exception("Not admin")
        match_id = data.get("match_id", "")
        if match_id in self.matches:
            m = self.matches[match_id]
            m.score_a = int(data.get("score_a", str(m.score_a)))
            m.score_b = int(data.get("score_b", str(m.score_b)))
            m.current_round = int(data.get("current_round", str(m.current_round)))
            m.status = data.get("status", m.status)
            m.winner = data.get("winner", m.winner)
            self.error = "Match updated: " + match_id
            return
        try:
            m = Match(
                match_id=match_id,
                player_a=data.get("player_a", ""),
                player_b=data.get("player_b", ""),
                topic=data.get("topic", ""),
                side_a_position=data.get("side_a_position", ""),
                side_b_position=data.get("side_b_position", ""),
                score_a=0,
                score_b=0,
                current_round=1,
                status="active",
                winner="",
                created_at=data.get("created_at", "0"),
            )
            self.matches[match_id] = m
            self.total_matches += 1
            self.error = "Match saved: " + match_id
        except Exception as e:
            self.error = "save_match error: " + str(e)

    @gl.public.write
    def save_round(self, data: dict) -> None:
        if gl.message.sender_address not in self.admins:
            raise Exception("Not admin")
        key = data.get("match_id", "") + "_" + data.get("round_num", "")
        if key in self.rounds:
            self.error = "Round already exists: " + key
            return
        try:
            r = DebateRound(
                match_id=data.get("match_id", ""),
                round_num=int(data.get("round_num", 0)),
                arg_a=data.get("arg_a", ""),
                arg_b=data.get("arg_b", ""),
                logic_a=int(data.get("logic_a", 0)),
                evidence_a=int(data.get("evidence_a", 0)),
                persuasion_a=int(data.get("persuasion_a", 0)),
                total_a=int(data.get("total_a", 0)),
                logic_b=int(data.get("logic_b", 0)),
                evidence_b=int(data.get("evidence_b", 0)),
                persuasion_b=int(data.get("persuasion_b", 0)),
                total_b=int(data.get("total_b", 0)),
                round_winner=data.get("round_winner", "draw"),
                judgment=data.get("judgment", ""),
            )
            self.rounds[key] = r
            self.error = "Round saved: " + key
        except Exception as e:
            self.error = "save_round error: " + str(e)

    @gl.public.view
    def get_match(self, match_id: str) -> dict:
        m = self.matches.get(match_id)
        if m is None:
            return {"error": "Match not found"}
        return m.to_dict()

    @gl.public.view
    def get_round(self, match_id: str, round_num: str) -> dict:
        key = match_id + "_" + round_num
        r = self.rounds.get(key)
        if r is None:
            return {"error": "Round not found"}
        return r.to_dict()

    @gl.public.view
    def get_recent_matches(self, limit: int) -> str:
        try:
            result = []
            for k, v in islice(
                sorted(self.matches.items(), key=lambda x: float(x[1].created_at), reverse=True),
                limit,
            ):
                result.append(v.to_dict())
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @gl.public.view
    def get_total_matches(self) -> str:
        return str(self.total_matches)

    @gl.public.view
    def get_admins(self) -> str:
        return json.dumps([{"address": a.as_hex} for a in self.admins])

    @gl.public.view
    def get_error(self) -> str:
        return self.error
