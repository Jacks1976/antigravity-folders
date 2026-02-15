from sqlalchemy.orm import Session
from app.models import Event, RSVP, User
from app.schemas.rsvp import RSVPCreate
from datetime import datetime
from typing import List, Optional

class RSVPService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_rsvp(self, user_id: int, rsvp_data: RSVPCreate):
        """Registrar confirmação de presença"""
        # Verificar se evento existe
        event = self.db.query(Event).filter(Event.id == rsvp_data.event_id).first()
        if not event:
            return None
        
        # Verificar se já confirmou
        existing = self.db.query(RSVP).filter(
            RSVP.user_id == user_id,
            RSVP.event_id == rsvp_data.event_id
        ).first()
        
        if existing:
            # Atualizar existente
            existing.status = rsvp_data.status
            existing.guests_count = rsvp_data.guests_count
            existing.notes = rsvp_data.notes
            existing.updated_at = datetime.now()
        else:
            # Criar novo
            existing = RSVP(
                user_id=user_id,
                event_id=rsvp_data.event_id,
                status=rsvp_data.status,
                guests_count=rsvp_data.guests_count,
                notes=rsvp_data.notes,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(existing)
        
        # Atualizar contagem no evento
        if rsvp_data.status == "confirmed":
            # Calcular total de confirmados
            confirmed_count = self.db.query(RSVP).filter(
                RSVP.event_id == rsvp_data.event_id,
                RSVP.status == "confirmed"
            ).count()
            event.confirmed_count = confirmed_count
        
        self.db.commit()
        self.db.refresh(existing)
        return existing
    
    def get_event_rsvps(self, event_id: int) -> List[RSVP]:
        """Listar confirmações de um evento"""
        return self.db.query(RSVP).filter(RSVP.event_id == event_id).all()
    
    def get_user_rsvps(self, user_id: int) -> List[RSVP]:
        """Listar eventos que usuário confirmou"""
        return self.db.query(RSVP).filter(RSVP.user_id == user_id).all()
    
    def get_rsvp_by_user_and_event(self, user_id: int, event_id: int) -> Optional[RSVP]:
        """Verificar se usuário já confirmou evento específico"""
        return self.db.query(RSVP).filter(
            RSVP.user_id == user_id,
            RSVP.event_id == event_id
        ).first()
    
    def delete_rsvp(self, rsvp_id: int, user_id: int) -> bool:
        """Cancelar confirmação"""
        rsvp = self.db.query(RSVP).filter(
            RSVP.id == rsvp_id,
            RSVP.user_id == user_id
        ).first()
        
        if rsvp:
            self.db.delete(rsvp)
            self.db.commit()
            return True
        return False