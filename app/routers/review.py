from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.review import Review
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut

router = APIRouter(tags=["reviews"])


@router.post("/restaurants/{restaurant_id}/reviews", response_model=ReviewOut)
def create_review(
    restaurant_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    new_review = Review(**review.model_dump(), user_id=current_user.id, restaurant_id=restaurant_id)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@router.get("/restaurants/{restaurant_id}/reviews", response_model=list[ReviewOut])
def get_reviews(restaurant_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.restaurant_id == restaurant_id).all()


@router.patch("/reviews/{id}", response_model=ReviewOut)
def update_review(
    id: int,
    updated: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.id == id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own review")

    for key, value in updated.model_dump().items():
        setattr(review, key, value)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/reviews/{id}")
def delete_review(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.id == id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own review")

    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}