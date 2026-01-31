from typing import Any


from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import easyocr
import io
import numpy as np
from PIL import Image
import uvicorn

app = FastAPI(title="PDF & OCR API")

# CORS 설정 (Streamlit과 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# EasyOCR reader 초기화 (한국어, 영어)
reader = easyocr.Reader(['ko', 'en'], gpu=False)


@app.get("/")
async def root():
    return {"message": "PDF & OCR API is running"}


@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    """
    PDF 파일을 업로드받아 PyPDF2로 텍스트를 추출합니다.
    """
    try:
        # 파일 확장자 검증
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
        
        # PDF 파일 읽기
        contents = await file.read()
        pdf_file = io.BytesIO(contents)
        
        # PyPDF2로 텍스트 추출
        ########################################
        ### 필수과제 1-(2): PyPDF2로 텍스트 추출

        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        
        extracted_text = ""
        page_texts = []
        total_pages = len(pdf_reader.pages)
        
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            page_texts.append({
                "page_number": page_num + 1,
                "text": page_text
            })
            extracted_text += f"\n--- 페이지 {page_num + 1} ---\n"
            extracted_text += page_text
        
        return {
            "success": True,
            "filename": file.filename,
            "total_pages": total_pages,
            "extracted_text": extracted_text,
            "pages": page_texts,
            "text_length": len(extracted_text)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 파싱 중 오류 발생: {str(e)}")


@app.post("/ocr-image")
async def ocr_image(file: UploadFile = File(...)):
    """
    이미지 파일을 업로드받아 EasyOCR로 텍스트를 추출합니다.
    """
    try:
        # 파일 확장자 검증
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail="이미지 파일만 업로드 가능합니다. (jpg, jpeg, png, bmp, gif, webp)"
            )
        
        # 이미지 파일 읽기
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # numpy array로 변환
        img_array = np.array(image)
        
        ########################################
        ### 필수과제 2-(2): EasyOCR로 텍스트 추출

        reader = easyocr.Reader(["ko", "en"])
        extracted_data = reader.readtext(img_array, detail=1, paragraph=False)
    
        result_simple = [item[1] for item in extracted_data]

        # result_simple = []
        # for item in extracted_data:
        #   result_simple.append(item[1])
        #  ====> 간단히 줄여 쓴 문법
        # result_simple = [item[1] for item in extracted_data] 

        
        # item[1]인 이유 
        # ---> extracted_data는 리스트 형태 [ [bbox, text, confidence], [], [] ]
        # bbox = 글자 영역 좌표값, text = 실제 텍스트, confidence = 신뢰도 


        # 모든 텍스트를 하나로 합치기
        full_text = " ".join(result_simple)
        
        # extracted_data를 return했더니 Numpy오류 발생하여 int형 변환
        # numpy.int32, numpy.float32 와 같은 Numpy객체라 json 변환 X
        # -> json 변환 가능한 형태로 가공
        
        detailed_results = []
        for bbox, text, conf in extracted_data:
            bbox_py = [[int(x), int(y)] for x, y in bbox]
            detailed_results.append({
                "bbox": bbox_py,
                "text": str(text),
                "confidence": float(conf)
            })
        

        return {
            "success": True,
            "filename": file.filename,
            "extracted_text": full_text,
            "detailed_results": detailed_results,
            "total_detections": len(detailed_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR 처리 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

