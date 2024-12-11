import random
from typing import List, Dict, Tuple, Optional
from enum import Enum
from pydantic import BaseModel
from app.models.pokemon_team import Pokemon
from app.services.battle_service import PokemonBattleService

class TournamentType(Enum):
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"

class TournamentParticipant(BaseModel):
    """
    Represents a tournament participant with additional metadata
    """
    team: List[Pokemon]
    name: Optional[str] = None
    wins: int = 0
    losses: int = 0
    eliminated: bool = False

class TournamentMatch(BaseModel):
    """
    Represents a single match in a tournament
    """
    participants: Tuple[TournamentParticipant, TournamentParticipant]
    winner: Optional[TournamentParticipant] = None
    loser: Optional[TournamentParticipant] = None
    round_number: int
    match_details: Dict = {}

class TournamentBracket(BaseModel):
    """
    Represents the entire tournament structure
    """
    tournament_type: TournamentType
    participants: List[TournamentParticipant]
    matches: List[TournamentMatch] = []
    current_round: int = 1
    champion: Optional[TournamentParticipant] = None

class AdvancedTournamentService:
    @classmethod
    def create_tournament_bracket(
        cls, 
        participants: List[List[Pokemon]], 
        tournament_type: TournamentType = TournamentType.SINGLE_ELIMINATION
    ) -> TournamentBracket:
        """
        Create a comprehensive tournament bracket
        
        Args:
            participants: List of Pokemon teams
            tournament_type: Type of tournament to simulate
        
        Returns:
            Fully structured tournament bracket
        """
        # Pad participants to nearest power of 2 for standard brackets
        padded_participants = cls._pad_participants(participants)
        
        # Convert to tournament participants
        tournament_participants = [
            TournamentParticipant(
                team=team, 
                name=f"Team {idx+1}"  # Default naming
            ) for idx, team in enumerate(padded_participants)
        ]
        
        # Shuffle participants for random initial matchups
        random.shuffle(tournament_participants)
        
        # Initialize tournament bracket
        tournament_bracket = TournamentBracket(
            tournament_type=tournament_type,
            participants=tournament_participants
        )
        
        return tournament_bracket
    
    @classmethod
    def simulate_tournament(
        cls, 
        tournament_bracket: TournamentBracket
    ) -> TournamentBracket:
        """
        Simulate the entire tournament progression
        
        Args:
            tournament_bracket: Initial tournament bracket
        
        Returns:
            Completed tournament bracket with final results
        """
        # Create initial round of matches
        current_participants = tournament_bracket.participants.copy()
        
        while len(current_participants) > 1:
            next_round_participants = []
            
            # Pair participants for matches
            for i in range(0, len(current_participants), 2):
                if i + 1 < len(current_participants):
                    # Simulate match between two participants
                    match = cls._simulate_match(
                        current_participants[i], 
                        current_participants[i+1],
                        tournament_bracket.current_round
                    )
                    
                    # Add match to tournament matches
                    tournament_bracket.matches.append(match)
                    
                    # Add winner to next round
                    next_round_participants.append(match.winner)
                    
                    # Update participant stats
                    match.winner.wins += 1
                    match.loser.losses += 1
                    match.loser.eliminated = True
            
            # Update participants and round
            current_participants = next_round_participants
            tournament_bracket.current_round += 1
        
        # Set tournament champion
        tournament_bracket.champion = current_participants[0]
        
        return tournament_bracket
    
    @staticmethod
    def _simulate_match(
        participant1: TournamentParticipant, 
        participant2: TournamentParticipant,
        round_number: int
    ) -> TournamentMatch:
        """
        Simulate a single match between two participants
        
        Args:
            participant1: First team in the match
            participant2: Second team in the match
            round_number: Current tournament round
        
        Returns:
            Detailed match information
        """
        # Simulate battle using first Pokemon from each team
        battle_result = PokemonBattleService.simulate_battle(
            participant1.team[0], 
            participant2.team[0]
        )
        
        # Determine winner and loser
        winner = (participant1 if battle_result.winner == participant1.team[0] 
                  else participant2)
        loser = (participant2 if winner == participant1 
                 else participant1)
        
        # Create match details
        match = TournamentMatch(
            participants=(participant1, participant2),
            winner=winner,
            loser=loser,
            round_number=round_number,
            match_details={
                "rounds": battle_result.rounds,
                "damage_dealt": battle_result.damage_dealt
            }
        )
        
        return match
    
    @staticmethod
    def _pad_participants(
        participants: List[List[Pokemon]]
    ) -> List[List[Pokemon]]:
        """
        Pad participant list to nearest power of 2
        
        Args:
            participants: Original list of participants
        
        Returns:
            Padded list of participants
        """
        # Find next power of 2
        next_power_of_two = 2 ** ((len(participants) - 1).bit_length())
        
        # If already a power of 2, return original
        if len(participants) == next_power_of_two:
            return participants
        
        # Create placeholder teams to fill bracket
        placeholder_teams = [
            [Pokemon(name=f"Bye Team {i}", type_1="Normal", level=1)] 
            for i in range(next_power_of_two - len(participants))
        ]
        
        return participants + placeholder_teams