from typing import List, Dict
import random
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.user import User
from src.core.joggy_ai import JoggyAI

class MatchingSystem:
    def __init__(self):
        self.joggy_ai = JoggyAI()

    def calculate_compatibility_score(self, user1: User, user2: User) -> float:
        """Calcule le score de compatibilité entre deux utilisateurs"""
        score = 0.0
        
        # Comparaison des intérêts
        user1_interests = set(user1.interests.split(','))
        user2_interests = set(user2.interests.split(','))
        common_interests = user1_interests & user2_interests
        score += len(common_interests) * 15
        
        # Comparaison des valeurs
        user1_values = set(user1.values.split(','))
        user2_values = set(user2.values.split(','))
        common_values = user1_values & user2_values
        score += len(common_values) * 20
        
        # Facteur géographique
        if user1.city == user2.city:
            score += 25
            
        # Facteur âge
        age1 = (datetime.now() - user1.birth_date).days // 365
        age2 = (datetime.now() - user2.birth_date).days // 365
        age_diff = abs(age1 - age2)
        if age_diff <= 5:
            score += 20
        elif age_diff <= 10:
            score += 10
            
        # Normalisation du score
        return min(max(score, 0), 100)

    def find_daily_matches(self, db: Session, user: User, limit: int = 25) -> List[Dict]:
        """Trouve les matchs quotidiens pour un utilisateur"""
        # Récupération des utilisateurs potentiels
        potential_matches = db.query(User).filter(
            User.id != user.id,
            User.is_active == True
        ).all()
        
        # Calcul des scores de compatibilité
        matches = []
        for potential_match in potential_matches:
            compatibility = self.calculate_compatibility_score(user, potential_match)
            if compatibility > 60:  # Seuil minimum de compatibilité
                matches.append({
                    'user': potential_match,
                    'compatibility': compatibility,
                    'prediction': self.joggy_ai.generate_prediction({'interests': potential_match.interests}),
                    'icebreaker': self.generate_icebreaker(user, potential_match)
                })
        
        # Tri par compatibilité et limitation du nombre de résultats
        matches.sort(key=lambda x: x['compatibility'], reverse=True)
        return matches[:limit]

    def generate_icebreaker(self, user1: User, user2: User) -> str:
        """Génère une suggestion de conversation personnalisée"""
        user1_interests = set(user1.interests.split(','))
        user2_interests = set(user2.interests.split(','))
        common_interests = user1_interests & user2_interests
        
        if common_interests:
            common_interest = random.choice(list(common_interests))
            icebreakers = [
                f"Je vois que vous partagez une passion pour {common_interest}. Qu'est-ce qui vous inspire le plus dans ce domaine ?",
                f"Parlons de {common_interest} ! Quelle a été votre dernière découverte ?",
                f"Entre passionnés de {common_interest}, quel est votre meilleur souvenir lié à cette activité ?"
            ]
        else:
            icebreakers = [
                "Si vous pouviez voyager n'importe où demain, où iriez-vous ?",
                "Quel est le dernier film qui vous a vraiment marqué ?",
                "Quelle est votre définition d'une journée parfaite ?"
            ]
        
        return random.choice(icebreakers)

    def blind_match(self, db: Session, user: User) -> Dict:
        """Crée un match aveugle sans photo"""
        matches = self.find_daily_matches(db, user, limit=5)
        if matches:
            match = random.choice(matches)
            return {
                'compatibility': match['compatibility'],
                'common_interests_count': len(set(user.interests.split(',')) & set(match['user'].interests.split(','))),
                'icebreaker': match['icebreaker'],
                'prediction': match['prediction']
            }
        return None