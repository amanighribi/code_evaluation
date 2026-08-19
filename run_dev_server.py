import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        reload=True,
        reload_dirs=[
            "backend",
            "static_analysis",
            "rag",
            "llm",
            "exam_mode",
            "project_utils",
            "knowledge_base",
        ],
    )