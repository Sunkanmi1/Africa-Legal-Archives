from fastapi import APIRouter, Query

from models import MediaResponse
from services.commons_service import CommonsService

router = APIRouter()
commons_service = CommonsService()


@router.get("/api/media")
async def get_media(
	query: str = Query("", description="Optional Wikimedia Commons search term"),
	category: str = Query("Category:1st GOIF-Effutu workshop 2023", description="Wikimedia Commons category"),
	limit: int = Query(500, ge=1, le=500, description="Number of media items to return"),
):
	items = (
		await commons_service.category_media(category, limit)
		if not query.strip()
		else await commons_service.search_media(query, limit)
	)
	return MediaResponse(success=True, items=items)
