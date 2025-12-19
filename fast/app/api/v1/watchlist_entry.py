"""
Watchlist Entry endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.db.database import get_db
from app.models import WatchlistEntry
from app.schemas import WatchlistEntryCreate, WatchlistEntryUpdate, WatchlistEntryResponse
from app.routers.dependencies import get_current_user

router = APIRouter(prefix="/watchlist-entries", tags=["watchlist-entries"])


@router.get("", response_model=list[WatchlistEntryResponse])
async def list_watchlist_entries(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List all entries for a specific watchlist"""
    entries = db.query(WatchlistEntry).filter(
        WatchlistEntry.watchlist_id == watchlist_id
    ).all()
    return entries


@router.get("/{entry_id}", response_model=WatchlistEntryResponse)
async def get_watchlist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get a specific watchlist entry"""
    entry = db.query(WatchlistEntry).filter(
        WatchlistEntry.id == entry_id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist entry not found"
        )
    
    return entry


@router.post("", response_model=WatchlistEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist_entry(
    entry: WatchlistEntryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Create a new watchlist entry"""
    db_entry = WatchlistEntry(
        date=entry.date,
        symbol=entry.symbol,
        company_name=entry.company_name,
        price=entry.price,
        atr=entry.atr,
        volume=entry.volume,
        avg_volume=entry.avg_volume,
        market_cap=entry.market_cap,
        float_shares=entry.float_shares,
        per=entry.per,
        eps=entry.eps,
        current_ratio=entry.current_ratio,
        exchange=entry.exchange,
        sector=entry.sector,
        industry=entry.industry,
        country=entry.country,
        score=entry.score,
        description=entry.description,
        negative_action=entry.negative_action,
        hashtags=entry.hashtags,
        risk_reward=entry.risk_reward,
        profit_target=entry.profit_target,
        other_notes=entry.other_notes,
        date_exit=entry.date_exit,
        watchlist_id=entry.watchlist_id,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.put("/{entry_id}", response_model=WatchlistEntryResponse)
async def update_watchlist_entry(
    entry_id: int,
    entry_update: WatchlistEntryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Update a watchlist entry"""
    entry = db.query(WatchlistEntry).filter(
        WatchlistEntry.id == entry_id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist entry not found"
        )
    
    # Update fields if provided
    update_data = entry_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Delete a watchlist entry"""
    entry = db.query(WatchlistEntry).filter(
        WatchlistEntry.id == entry_id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist entry not found"
        )
    
    db.delete(entry)
    db.commit()
