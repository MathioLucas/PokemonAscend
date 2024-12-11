import random
from typing import List, Dict, Tuple
from app.models.pokemon_team import Pokemon
from pydantic import BaseModel

class BattleOutcome(BaseModel):
    winner: Pokemon
    loser: Pokemon
    rounds: int
    damage_dealt: Dict[str, int]

class TypeEffectivenessMatrix:
    """
    Defines type effectiveness for Pokemon battles
    Multipliers determine damage calculation
    """
    EFFECTIVENESS = {
        # Simplified type effectiveness matrix
        'Fire': {'Grass': 2.0, 'Water': 0.5, 'Normal': 1.0},
        'Water': {'Fire': 2.0, 'Grass': 0.5, 'Normal': 1.0},
        'Grass': {'Water': 2.0, 'Fire': 0.5, 'Normal': 1.0},
        'Normal': {'Fire': 1.0, 'Water': 1.0, 'Grass': 1.0}
    }

    @classmethod
    def get_type_multiplier(cls, attacker_type: str, defender_type: str) -> float:
        return cls.EFFECTIVENESS.get(attacker_type, {}).get(defender_type, 1.0)

class PokemonBattleService:
    @staticmethod
    def calculate_damage(
        attacker: Pokemon, 
        defender: Pokemon, 
        is_critical_hit: bool = False
    ) -> int:
        """
        Calculate damage based on attacker and defender stats
        Incorporates type effectiveness and potential critical hits
        """
        base_damage = attacker.attack - (defender.defense / 2)
        type_multiplier = TypeEffectivenessMatrix.get_type_multiplier(
            attacker.type_1, defender.type_1
        )
        
        critical_multiplier = 1.5 if is_critical_hit else 1.0
        
        damage = max(1, int(base_damage * type_multiplier * critical_multiplier))
        return damage

    @staticmethod
    def simulate_battle(
        pokemon1: Pokemon, 
        pokemon2: Pokemon, 
        max_rounds: int = 20
    ) -> BattleOutcome:
        """
        Simulate a battle between two Pokemon
        Uses probabilistic damage calculation and turn-based mechanics
        """
        p1_hp = pokemon1.hp
        p2_hp = pokemon2.hp
        
        damage_dealt = {
            pokemon1.name: 0,
            pokemon2.name: 0
        }
        
        for round in range(1, max_rounds + 1):
            # Randomize critical hit chance
            p1_critical = random.random() < 0.0625  # 1/16 chance of critical hit
            p2_critical = random.random() < 0.0625
            
            # Pokemon 1's turn
            p1_damage = PokemonBattleService.calculate_damage(
                pokemon1, pokemon2, p1_critical
            )
            p2_hp -= p1_damage
            damage_dealt[pokemon1.name] += p1_damage
            
            if p2_hp <= 0:
                return BattleOutcome(
                    winner=pokemon1, 
                    loser=pokemon2, 
                    rounds=round, 
                    damage_dealt=damage_dealt
                )
            
            # Pokemon 2's turn
            p2_damage = PokemonBattleService.calculate_damage(
                pokemon2, pokemon1, p2_critical
            )
            p1_hp -= p2_damage
            damage_dealt[pokemon2.name] += p2_damage
            
            if p1_hp <= 0:
                return BattleOutcome(
                    winner=pokemon2, 
                    loser=pokemon1, 
                    rounds=round, 
                    damage_dealt=damage_dealt
                )
        
        # If max rounds reached, determine winner by remaining HP
        return BattleOutcome(
            winner=pokemon1 if p1_hp > p2_hp else pokemon2,
            loser=pokemon2 if p1_hp > p2_hp else pokemon1,
            rounds=max_rounds,
            damage_dealt=damage_dealt
        )