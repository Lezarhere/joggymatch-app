from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.database.database import get_db
from src.core.matching_system import MatchingSystem
from src.models.user import User

router = APIRouter()
matching_system = MatchingSystem()

@router.get("/matches/{user_id}")
async def get_daily_matches(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return matching_system.find_daily_matches(db, user)

@router.get("/blind-match/{user_id}")
async def get_blind_match(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return matching_system.blind_match(db, user)
