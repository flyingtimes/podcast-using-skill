from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

app = FastAPI(title="文章管理系统", description="管理文章信息的API接口")
db_manager = DatabaseManager()

class EssayData(BaseModel):
    title: str
    subtitle: Optional[str] = None
    author: Optional[str] = None
    url: str
    content: Optional[str] = None
    entry_time: Optional[str] = None

class EssayRequest(BaseModel):
    essays: List[EssayData]

class EssayResponse(BaseModel):
    success_count: int
    skipped_count: int
    successful_titles: List[str]
    message: str

class EssayUpdate(BaseModel):
    url: str
    content: str

class UpdateResponse(BaseModel):
    success: bool
    message: str

@app.post("/api/essays", response_model=EssayResponse)
async def add_essays(request: EssayRequest):
    """
    添加文章到数据库

    - **essays**: 文章列表，每篇文章包含标题、副标题、作者、录入时间
    """
    successful_titles = []
    skipped_titles = []

    for essay in request.essays:
        # 解析录入时间
        entry_time = None
        if essay.entry_time:
            try:
                entry_time = datetime.fromisoformat(essay.entry_time.replace('Z', '+00:00'))
            except ValueError:
                try:
                    entry_time = datetime.strptime(essay.entry_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    entry_time = datetime.now()
        else:
            entry_time = datetime.now()

        # 尝试添加文章
        try:
            success = db_manager.add_essay(
                title=essay.title,
                url=essay.url,
                subtitle=essay.subtitle,
                author=essay.author,
                content=essay.content,
                entry_time=entry_time
            )

            if success:
                successful_titles.append(essay.title)
            else:
                skipped_titles.append(essay.title)

        except Exception as e:
            print(f"添加文章 '{essay.title}' 时出错: {str(e)}")
            skipped_titles.append(essay.title)

    return EssayResponse(
        success_count=len(successful_titles),
        skipped_count=len(skipped_titles),
        successful_titles=successful_titles,
        message=f"成功添加 {len(successful_titles)} 篇文章，跳过 {len(skipped_titles)} 篇重复URL的文章"
    )

@app.get("/api/essays")
async def get_all_essays():
    """获取所有文章列表"""
    session = db_manager.get_session()
    try:
        from database import Essay
        essays = session.query(Essay).all()
        return {
            "count": len(essays),
            "essays": [
                {
                    "id": essay.id,
                    "title": essay.title,
                    "subtitle": essay.subtitle,
                    "author": essay.author,
                    "url": essay.url,
                    "content": essay.content,
                    "entry_time": essay.entry_time.isoformat() if essay.entry_time else None,
                    "created_at": essay.created_at.isoformat()
                }
                for essay in essays
            ]
        }
    finally:
        session.close()

@app.put("/api/essays/content", response_model=UpdateResponse)
async def update_essay_content(update: EssayUpdate):
    """
    更新文章内容

    - **url**: 文章URL
    - **content**: 文章内容
    """
    try:
        success = db_manager.update_essay_content(update.url, update.content)
        if success:
            return UpdateResponse(
                success=True,
                message="文章内容更新成功"
            )
        else:
            return UpdateResponse(
                success=False,
                message="未找到对应URL的文章"
            )
    except Exception as e:
        return UpdateResponse(
            success=False,
            message=f"更新失败: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "文章管理系统运行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)