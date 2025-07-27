from datetime import datetime
from typing import List
from fastapi import HTTPException
from config import get_rag_system

async def add_knowledge(documents: List[str], source: str = "manual"):
    """Endpoint para adicionar documentos à base de conhecimento"""
    try:
        rag_system = get_rag_system()
        metadatas = [{"source": source, "added_at": datetime.now().isoformat()} for _ in documents]
        await rag_system.add_documents_to_rag(documents, metadatas)
        return {"status": "success", "added": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))