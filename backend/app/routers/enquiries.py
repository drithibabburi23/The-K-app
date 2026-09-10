from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enquiry import Enquiry
from app.schemas.enquiry import EnquiryCreate, EnquiryRead, EnquiryUpdate
from app.services.crud import create_item, delete_item, get_or_404, list_items, update_item

router = APIRouter(prefix="/enquiries", tags=["enquiries"])


@router.post("", response_model=EnquiryRead, status_code=status.HTTP_201_CREATED)
def create_enquiry(payload: EnquiryCreate, db: Session = Depends(get_db)):
    return create_item(db, Enquiry, payload.model_dump())


@router.get("", response_model=list[EnquiryRead])
def read_enquiries(db: Session = Depends(get_db)):
    return list_items(db, Enquiry)


@router.get("/{enquiry_id}", response_model=EnquiryRead)
def read_enquiry(enquiry_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Enquiry, enquiry_id)


@router.patch("/{enquiry_id}", response_model=EnquiryRead)
def update_enquiry(enquiry_id: int, payload: EnquiryUpdate, db: Session = Depends(get_db)):
    enquiry = get_or_404(db, Enquiry, enquiry_id)
    return update_item(db, enquiry, payload.model_dump(exclude_unset=True))


@router.delete("/{enquiry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enquiry(enquiry_id: int, db: Session = Depends(get_db)):
    delete_item(db, get_or_404(db, Enquiry, enquiry_id))
