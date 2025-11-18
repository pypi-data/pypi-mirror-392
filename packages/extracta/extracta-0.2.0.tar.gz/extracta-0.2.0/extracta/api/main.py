from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
import os
from extracta.lenses import get_lens_for_file
from extracta.analyzers import get_analyzer_for_content


def create_app() -> FastAPI:
    app = FastAPI(
        title="Extracta API",
        description="Modular content analysis and insight generation",
        version="0.1.0",
    )

    @app.post("/extract")
    async def extract_content(file: UploadFile = File(...)):
        """Extract content from uploaded file"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(file.filename).suffix
            ) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name

            try:
                file_path = Path(temp_path)

                # Get appropriate lens
                lens = get_lens_for_file(file_path)
                if not lens:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No lens available for {file_path.suffix}",
                    )

                # Extract content
                result = lens.extract(file_path)
                if not result["success"]:
                    raise HTTPException(status_code=400, detail=result["error"])

                return result["data"]

            finally:
                # Clean up temp file
                os.unlink(temp_path)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/analyze")
    async def analyze_content(file: UploadFile = File(...), mode: str = "assessment"):
        """Analyze uploaded content"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(file.filename).suffix
            ) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name

            try:
                file_path = Path(temp_path)

                # Get appropriate lens
                lens = get_lens_for_file(file_path)
                if not lens:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No lens available for {file_path.suffix}",
                    )

                # Extract content
                extract_result = lens.extract(file_path)
                if not extract_result["success"]:
                    raise HTTPException(status_code=400, detail=extract_result["error"])

                # Get analyzer
                analyzer = get_analyzer_for_content(
                    extract_result["data"]["content_type"]
                )
                if not analyzer:
                    # Return extraction result without analysis
                    return extract_result["data"]

                # Analyze content
                if extract_result["data"]["content_type"] == "image":
                    analysis = analyzer.analyze(
                        extract_result["data"]["file_path"], mode
                    )
                else:
                    analysis = analyzer.analyze(
                        extract_result["data"]["raw_content"], mode
                    )

                extract_result["data"]["analysis"] = analysis
                return extract_result["data"]

            finally:
                # Clean up temp file
                os.unlink(temp_path)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "version": "0.1.0"}

    return app
