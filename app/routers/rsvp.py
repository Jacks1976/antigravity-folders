from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.rsvp_service import RSVPService
from app.schemas.rsvp import RSVPCreate, RSVPInDB
from app.core.auth import get_current_user
from typing import List

router = APIRouter(prefix="/rsvp", tags=["rsvp"])

@router.post("/events/{event_id}/rsvp", response_model=RSVPInDB)
def create_rsvp(
    event_id: int,
    rsvp_data: RSVPCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Confirmar ou recusar presença em evento"""
    service = RSVPService(db)
    # Garantir que o event_id na URL seja usado
    rsvp_data.event_id = event_id
    result = service.create_rsvp(current_user.id, rsvp_data)
    if not result:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return result

@router.get("/events/{event_id}/rsvps", response_model=List[RSVPInDB])
def get_event_rsvps(
    event_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Ver quem confirmou presença (apenas admin/organizador)"""
    service = RSVPService(db)
    return service.get_event_rsvps(event_id)

@router.get("/user/rsvps", response_model=List[RSVPInDB])
def get_user_rsvps(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Meus eventos confirmados"""
    service = RSVPService(db)
    return service.get_user_rsvps(current_user.id)

@router.get("/events/{event_id}/my-rsvp")
def get_my_rsvp(
    event_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Ver minha confirmação para um evento específico"""
    service = RSVPService(db)
    rsvp = service.get_rsvp_by_user_and_event(current_user.id, event_id)
    if not rsvp:
        return {"status": "not_responded"}
    return rsvp

@router.delete("/{rsvp_id}")
def delete_rsvp(
    rsvp_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancelar minha confirmação"""
    service = RSVPService(db)
    success = service.delete_rsvp(rsvp_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Confirmação não encontrada")
    return {"message": "Confirmação cancelada com sucesso"}