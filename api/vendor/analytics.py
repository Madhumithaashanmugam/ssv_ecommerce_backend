
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db.session import get_db
from service.vendor.analytics_service import get_analytics_data
from utils.jwt_handler import get_current_vendor

analytics_router = APIRouter()


@analytics_router.get("/analytics", status_code=status.HTTP_200_OK)
def analytics(
    db: Session = Depends(get_db),
    current_vendor: dict = Depends(get_current_vendor)  # ✅ Auth required
):
    print("✅ Vendor Authenticated:", current_vendor)
    """
    Get platform-wide analytics including revenue, order stats, customer insights, and inventory data.
    """
    try:
        analytics_data = get_analytics_data(db)

        if not analytics_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No analytics data found"
            )

        return {
            "success": True,
            "message": "Analytics data fetched successfully",
            "data": analytics_data
        }

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong while fetching analytics: {str(e)}"
        )