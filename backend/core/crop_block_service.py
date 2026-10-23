from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.db.models.core.crop_block import CropBlock, BlockStatus
from backend.schemas.crop_block import CropBlockCreate, CropBlockUpdate


def create_crop_block(db: Session, farm_id: str, data: CropBlockCreate) -> CropBlock:
    payload_dict = data.model_dump()
    payload_dict["farm_id"] = str(farm_id)
    block = CropBlock(**payload_dict)
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


def get_crop_block(db: Session, crop_block_id: str) -> CropBlock:
    block = db.query(CropBlock).filter(CropBlock.id == str(crop_block_id)).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop block not found",
        )
    return block


def list_crop_blocks_for_farm(db: Session, farm_id: str) -> list[CropBlock]:
    return (
        db.query(CropBlock)
        .filter(CropBlock.farm_id == str(farm_id))
        .order_by(CropBlock.planting_date.asc())
        .all()
    )


def update_crop_block(db: Session, crop_block_id: str, data: CropBlockUpdate) -> CropBlock:
    block = get_crop_block(db, crop_block_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(block, field, value)
    db.commit()
    db.refresh(block)
    return block


def update_crop_block_status(db: Session, crop_block_id: str, new_status: BlockStatus) -> CropBlock:
    block = get_crop_block(db, crop_block_id)
    block.status = new_status
    db.commit()
    db.refresh(block)
    return block
