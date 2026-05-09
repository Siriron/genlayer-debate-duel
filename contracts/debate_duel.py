# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from dataclasses import dataclass
import typing
import json


class DebateDuel(gl.Contract):
    owner: Address
    storage_contract: str
    stat_contract: str
    match_counter: u256
    error: str

    def __init__(self, storage_contract: str, stat_contract: str) -> None:
        self.owner = gl.message.sender_address
        self.storage_contract = storage_contract
        self.stat_contract = stat_contract
        self.match_counter = 0
        self.error = "None"

    @gl.public.write
    async def create_match(self, player_a: str, player_b: str, match_id: str, created_at: str) -> typing.Any:
        topic_result = await gl.eq_principle.strict_eq(
            lambda: "",
            lambda _: gl.exec_prompt("""You are a debate topic generator. Generate ONE thought-provoking debate topic.

STRICT RULES — topic must NOT involve:
- Gambling, betting, lotteries, or games of chance
- Alcohol, drugs, or intoxicants
- Interest-based finance, usury, or speculation
- Sexual content or relationships
- Religious controversy or sectarian conflict
- Partisan political figures by name
- Violence or war glorification

Good topic areas: technology ethics, environment, education policy, social media, science, space exploration, AI regulation, urban planning, food systems, privacy, healthcare access.

Respond with ONLY a JSON object, no markdown, no explanation:
{
  "topic": "a clear debatable proposition",
  "side_a_position": "FOR: one sentence affirmative position",
  "side_b_position": "AGAINST: one sentence opposing position"
}""")
        )

        try:
            topic_data = json.loads(topic_result)
        except Exception:
            topic_data = {
                "topic": "Artificial intelligence will do more good than harm for society",
                "side_a_position": "FOR: AI will vastly improve human quality of life and solve major problems",
                "side_b_position": "AGAINST: AI poses serious societal risks that outweigh its potential benefits"
            }

        match_data = {
            "match_id": match_id,
            "player_a": player_a,
            "player_b": player_b,
            "topic": topic_data.get("topic", ""),
            "side_a_position": topic_data.get("side_a_position", ""),
            "side_b_position": topic_data.get("side_b_position", ""),
            "score_a": "0",
            "score_b": "0",
            "current_round": "1",
            "status": "active",
            "winner": "",
            "created_at": created_at,
        }

        storage = gl.contract(self.storage_contract)
        await storage.save_match(match_data)

        self.match_counter += 1
        self.error = "Match created: " + match_id

    @gl.public.write
    async def submit_arguments(self, match_id: str, round_num: str, arg_a: str, arg_b: str) -> typing.Any:
        storage = gl.contract(self.storage_contract)
        match = await storage.get_match(match_id)

        if "error" in match:
            self.error = "Match not found: " + match_id
            return

        if match.get("status") != "active":
            self.error = "Match already finished"
            return

        topic = match.get("topic", "")
        side_a_pos = match.get("side_a_position", "")
        side_b_pos = match.get("side_b_position", "")

        prompt = f"""You are an impartial debate judge. Score two debaters on the following topic.

TOPIC: {topic}

PLAYER A argues: {side_a_pos}
PLAYER A argument: {arg_a}

PLAYER B argues: {side_b_pos}
PLAYER B argument: {arg_b}

Score each player on three axes from 0 to 10:
1. Logic: Is the reasoning sound and coherent?
2. Evidence: Does the argument use concrete facts, examples, or well-reasoned support?
3. Persuasion: Is the argument compelling and well-communicated?

RULES:
- Be fair and impartial
- If an argument is blank or under 10 words, score it 0 across all axes
- Total = Logic + Evidence + Persuasion (max 30)
- Round winner = higher total. If tied, declare "draw"

Respond with ONLY a JSON object, no markdown:
{{
  "logic_a": <0-10>,
  "evidence_a": <0-10>,
  "persuasion_a": <0-10>,
  "total_a": <0-30>,
  "logic_b": <0-10>,
  "evidence_b": <0-10>,
  "persuasion_b": <0-10>,
  "total_b": <0-30>,
  "round_winner": "a or b or draw",
  "judgment": "2-3 sentence explanation of the verdict"
}}"""

        judgment_result = await gl.eq_principle.strict_eq(
            lambda: "",
            lambda _: gl.exec_prompt(prompt)
        )

        try:
            j = json.loads(judgment_result)
        except Exception:
            j = {
                "logic_a": 5, "evidence_a": 5, "persuasion_a": 5, "total_a": 15,
                "logic_b": 5, "evidence_b": 5, "persuasion_b": 5, "total_b": 15,
                "round_winner": "draw",
                "judgment": "Both arguments were evaluated equally."
            }

        round_winner = j.get("round_winner", "draw")

        round_data = {
            "match_id": match_id,
            "round_num": round_num,
            "arg_a": arg_a,
            "arg_b": arg_b,
            "logic_a": str(j.get("logic_a", 0)),
            "evidence_a": str(j.get("evidence_a", 0)),
            "persuasion_a": str(j.get("persuasion_a", 0)),
            "total_a": str(j.get("total_a", 0)),
            "logic_b": str(j.get("logic_b", 0)),
            "evidence_b": str(j.get("evidence_b", 0)),
            "persuasion_b": str(j.get("persuasion_b", 0)),
            "total_b": str(j.get("total_b", 0)),
            "round_winner": round_winner,
            "judgment": j.get("judgment", ""),
        }

        await storage.save_round(round_data)

        score_a = int(match.get("score_a", "0"))
        score_b = int(match.get("score_b", "0"))

        if round_winner == "a":
            score_a += 1
        elif round_winner == "b":
            score_b += 1

        next_round = str(int(round_num) + 1)
        match_status = "active"
        match_winner = ""

        if score_a == 2:
            match_status = "finished"
            match_winner = match.get("player_a", "")
        elif score_b == 2:
            match_status = "finished"
            match_winner = match.get("player_b", "")
        elif int(round_num) >= 3:
            match_status = "finished"
            if score_a > score_b:
                match_winner = match.get("player_a", "")
            elif score_b > score_a:
                match_winner = match.get("player_b", "")
            else:
                match_winner = "draw"

        updated_match = {
            "match_id": match_id,
            "score_a": str(score_a),
            "score_b": str(score_b),
            "current_round": next_round,
            "status": match_status,
            "winner": match_winner,
        }
        await storage.save_match(updated_match)

        if match_status == "finished":
            stat = gl.contract(self.stat_contract)
            player_a = match.get("player_a", "")
            player_b = match.get("player_b", "")

            result_a = "win" if match_winner == player_a else ("draw" if match_winner == "draw" else "loss")
            result_b = "win" if match_winner == player_b else ("draw" if match_winner == "draw" else "loss")

            await stat.record_match_result(player_a, result_a, u256(score_a), u256(0), u256(0), u256(0))
            await stat.record_match_result(player_b, result_b, u256(score_b), u256(0), u256(0), u256(0))

        self.error = "Round " + round_num + " submitted for match " + match_id

    @gl.public.view
    def get_config(self) -> dict:
        return {
            "owner": self.owner.as_hex,
            "storage_contract": self.storage_contract,
            "stat_contract": self.stat_contract,
            "total_matches": str(self.match_counter),
        }

    @gl.public.view
    def get_error(self) -> str:
        return self.error
