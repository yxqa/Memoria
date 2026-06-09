from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Memory


async def get_search_memoria(db: AsyncSession, user_id: str, q: str, page: int, page_size: int):

    """全文搜索当前用户记忆"""
    offset = (page - 1) * page_size

    #匹配度表达式
    # relevance_expr = text("MATCH(content) AGAINST(:q IN BOOLEAN MODE)")
    query = text("""
        SELECT id, content, mood, created_at,
            MATCH(content, mood, location) AGAINST(:q IN BOOLEAN MODE) as relevance
        FROM memories
        WHERE user_id = :user_id
            AND MATCH(content, mood, location) AGAINST(:q IN BOOLEAN MODE) > 0
        ORDER BY relevance DESC
        LIMIT :limit OFFSET :offset
    """)

    #查总数
    count_query = text("""
            SELECT COUNT(*) FROM memories
            WHERE user_id = :user_id
                AND MATCH(content, mood, location) AGAINST(:q IN BOOLEAN MODE) > 0
        """)

    result = await db.execute(query, {"q": q, "user_id": user_id, "limit": page_size, "offset": offset})
    row = result.all()

    total_result = await db.execute(count_query, {"q": q, "user_id": user_id})
    total = total_result.scalar()

    item = []
    for r in row:
        item.append({
            "id": r.id,
            "content": r.content,
            "mood": r.mood,
            "relevance": round(float(r.relevance), 4),
            "created_at": r.created_at.isoformat(),
        })
    return {
        "items": item,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


