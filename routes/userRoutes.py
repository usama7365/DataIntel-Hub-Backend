from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
from typing import Optional
import subprocess
import os
from tempfile import NamedTemporaryFile
from pydantic import BaseModel

from controllers.userController import UserController
from middleware.authentication import is_authenticated_user
from utils.s3upload import upload_csv_to_local
# Remove this import as we're implementing the logic directly in the endpoint
from models.userModel import UserCreate, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, UpdatePasswordRequest, ResendEmailRequest, UserUpdate
from utils.postgres_utils import create_postgres_engine, list_postgres_tables, extract_table_data
import uuid
import pandas as pd

user_router = APIRouter()

# Initialize user controller
user_controller = UserController()

class GoogleSheetUploadRequest(BaseModel):
    file_type: str
    sheet_url: str

@user_router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...), 
    file_type: str = Form(...),
    user_id: str = Depends(is_authenticated_user)
):
    """
    Upload CSV file and process with Python crew
    """
    try:
        print("[UPLOAD-CSV] Received upload request.")
        if not file:
            print("[UPLOAD-CSV] No file uploaded.")
            raise HTTPException(status_code=400, detail="No file uploaded")
        if file_type != "csv":
            print(f"[UPLOAD-CSV] Invalid file_type: {file_type}")
            raise HTTPException(status_code=400, detail="file_type must be 'csv'")
        
        # Save uploaded file to sheet_dump
        file_buffer = await file.read()
        print("[UPLOAD-CSV] Saving file to local sheet_dump...")
        file_path = await upload_csv_to_local(file_buffer, file.filename)
        print(f"[UPLOAD-CSV] File saved at: {file_path}")
        
        # Call the Python crew function with the uploaded file path
        import time
        start_time = time.time()
        python_result = await call_python_crew(file_path)
        processing_time = time.time() - start_time
        print("[UPLOAD-CSV] Crew result received.")
        
        # Create report record
        from controllers.reportController import create_report_from_analysis
        import pandas as pd
        
        # Get record count from CSV
        try:
            df = pd.read_csv(file_path)
            record_count = len(df)
        except:
            record_count = None
        
        # Create report record
        report = await create_report_from_analysis(
            user_id=user_id,
            source_type="csv",
            report_content=python_result,
            file_path=file_path,
            file_name=file.filename,
            record_count=record_count,
            processing_time=processing_time
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Uploaded successfully",
                "fileType": file_type,
                "filePath": file_path,
                "crewResult": python_result,
                "report_id": report.id
            }
        )
    except Exception as e:
        print(f"[UPLOAD-CSV] Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/upload-google-sheet")
async def upload_google_sheet(
    payload: GoogleSheetUploadRequest = Body(...),
    user_id: str = Depends(is_authenticated_user)
):
    """
    Accept a Google Sheets URL, fetch as CSV, save to sheet_dump, and process with crew.py
    """
    try:
        print("[UPLOAD-GOOGLE-SHEET] Received upload request.")
        if payload.file_type != "google_sheet":
            print(f"[UPLOAD-GOOGLE-SHEET] Invalid file_type: {payload.file_type}")
            raise HTTPException(status_code=400, detail="file_type must be 'google_sheet'")
        
        # Save Google Sheet as CSV to sheet_dump
        import uuid
        unique_name = f"{uuid.uuid4()}.csv"
        from utils.s3upload import create_sheet_dump_directory
        sheet_dump_dir = create_sheet_dump_directory()
        file_path = str(sheet_dump_dir / unique_name)
        print(f"[UPLOAD-GOOGLE-SHEET] Downloading Google Sheet to: {file_path}")
        
        import pandas as pd
        import re
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', payload.sheet_url)
        gid_match = re.search(r'gid=([0-9]+)', payload.sheet_url)
        if not match:
            print("[UPLOAD-GOOGLE-SHEET] Invalid Google Sheet URL.")
            raise HTTPException(status_code=400, detail="Invalid Google Sheet URL")
        
        file_id = match.group(1)
        gid = gid_match.group(1) if gid_match else '0'
        export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"
        print(f"[UPLOAD-GOOGLE-SHEET] Export URL: {export_url}")
        df = pd.read_csv(export_url)
        df.to_csv(file_path, index=False)
        print(f"[UPLOAD-GOOGLE-SHEET] File saved at: {file_path}")
        
        # Call the Python crew function with the saved file path
        import time
        start_time = time.time()
        python_result = await call_python_crew(file_path)
        processing_time = time.time() - start_time
        print("[UPLOAD-GOOGLE-SHEET] Crew result received.")
        
        # Create report record
        from controllers.reportController import create_report_from_analysis
        
        # Get record count from DataFrame
        record_count = len(df)
        
        # Create report record
        report = await create_report_from_analysis(
            user_id=user_id,
            source_type="google_sheet",
            report_content=python_result,
            file_path=file_path,
            file_name=f"google_sheet_{file_id}.csv",
            record_count=record_count,
            processing_time=processing_time
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Google Sheet processed successfully",
                "fileType": payload.file_type,
                "filePath": file_path,
                "crewResult": python_result,
                "report_id": report.id
            }
        )
    except Exception as e:
        print(f"[UPLOAD-GOOGLE-SHEET] Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def call_python_crew(file_path: str):
    """
    Call Python crew function with file path and filter output to only return the final user-facing report.
    """
    try:
        print(f"[CREW] Calling crew.py with file_path: {file_path}")
        result = subprocess.run(
            ['python', 'crew.py', '--file-path', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[CREW] crew.py STDOUT: {result.stdout}")
        print(f"[CREW] crew.py STDERR: {result.stderr}")
        # Filter output: only return the text after 'Result:'
        output = result.stdout
        if 'Result:' in output:
            # Get everything after 'Result:'
            filtered = output.split('Result:', 1)[1]
            # Remove any trailing logs after the markdown (e.g., 'Final report has been saved...')
            if "Final report has been saved" in filtered:
                filtered = filtered.split("Final report has been saved", 1)[0]
            filtered = filtered.strip()
            return filtered
        else:
            # If 'Result:' not found, return the whole output (fallback)
            return output.strip()
    except subprocess.CalledProcessError as e:
        print(f"[CREW] crew.py failed: {e.stderr}")
        raise HTTPException(
            status_code=500, 
            detail=f"Python crew process failed: {e.stderr}"
        )

# User registration and login routes
@user_router.post("/register")
async def register_user(user_data: UserCreate):
    """
    Register a new user
    """
    return await user_controller.register_user(user_data.dict())

@user_router.get("/verify/{token}")
async def verify_email(token: str):
    """
    Verify user email with token
    """
    return await user_controller.verify_email(token)

@user_router.post("/email/resend")
async def resend_verification_email(email_data: ResendEmailRequest):
    """
    Resend verification email
    """
    return await user_controller.resend_verification_email(email_data.dict())

@user_router.post("/login")
async def login_user(login_data: LoginRequest):
    """
    Login user
    """
    return await user_controller.login_user(login_data.dict())

@user_router.post("/password/forgot")
async def forgot_password(email_data: ForgotPasswordRequest):
    """
    Send forgot password email
    """
    return await user_controller.forgot_password(email_data.dict())

@user_router.put("/password/reset/{token}")
async def reset_password(token: str, password_data: ResetPasswordRequest):
    """
    Reset password with token
    """
    return await user_controller.reset_password(token, password_data.dict())

@user_router.get("/logout")
async def logout():
    """
    Logout user
    """
    return await user_controller.logout()

@user_router.get("/me")
async def get_user_details(user_id: str = Depends(is_authenticated_user)):
    """
    Get current user details
    """
    print(f"[ME] User ID from token: {user_id}")
    return await user_controller.get_user_details(user_id)

@user_router.get("/test-auth")
async def test_auth(user_id: str = Depends(is_authenticated_user)):
    """
    Test authentication endpoint
    """
    print(f"[TEST-AUTH] User ID from token: {user_id}")
    return {"message": "Authentication successful", "user_id": user_id}

@user_router.put("/me/update")
async def update_user(user_data: UserUpdate, user_id: str = Depends(is_authenticated_user)):
    """
    Update user profile
    """
    return await user_controller.update_user(user_id, user_data.dict())

@user_router.put("/password/update")
async def update_password(password_data: UpdatePasswordRequest, user_id: str = Depends(is_authenticated_user)):
    """
    Update user password
    """
    return await user_controller.update_password(user_id, password_data.dict())

@user_router.post("/upload-sheet")
async def upload_sheet(file: UploadFile = File(...)):
    """
    Upload a CSV file and save it to the sheet_dump_dir folder
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        from utils.s3upload import upload_csv_to_local
        file_buffer = await file.read()
        file_path = await upload_csv_to_local(file_buffer, file.filename)
        return {"message": "File uploaded successfully", "filePath": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin routes
@user_router.get("/admin/users")
async def get_all_users(user_id: str = Depends(is_authenticated_user)):
    """
    Get all users (admin only)
    """
    return await user_controller.get_all_users(user_id) 

class PostgresConnectRequest(BaseModel):
    host: str
    port: int
    dbname: str
    user: str
    password: str

class PostgresAnalyzeRequest(PostgresConnectRequest):
    tables: list

@user_router.post("/postgres/connect")
async def postgres_connect(payload: PostgresConnectRequest):
    """
    Connect to PostgreSQL and return list of table names.
    """
    try:
        engine = create_postgres_engine(
            payload.host, payload.port, payload.dbname, payload.user, payload.password
        )
        tables = list_postgres_tables(engine)
        return {"tables": tables}
    except Exception as e:
        print(f"[POSTGRES-CONNECT] Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/postgres/analyze")
async def postgres_analyze(
    payload: PostgresAnalyzeRequest,
    user_id: str = Depends(is_authenticated_user)
):
    """
    Extract data from selected tables, save as CSV, and process with crew.py
    """
    try:
        engine = create_postgres_engine(
            payload.host, payload.port, payload.dbname, payload.user, payload.password
        )
        # Combine all selected tables into one DataFrame
        dfs = []
        total_records = 0
        for table in payload.tables:
            df = extract_table_data(engine, table)
            df['__table__'] = table  # Add table name column for context
            dfs.append(df)
            total_records += len(df)
        
        if not dfs:
            raise HTTPException(status_code=400, detail="No tables selected or tables are empty.")
        
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Save to CSV in sheet_dump
        from utils.s3upload import create_sheet_dump_directory
        sheet_dump_dir = create_sheet_dump_directory()
        unique_name = f"{uuid.uuid4()}.csv"
        file_path = str(sheet_dump_dir / unique_name)
        combined_df.to_csv(file_path, index=False)
        
        # Call crew.py for analysis
        import time
        start_time = time.time()
        python_result = await call_python_crew(file_path)
        processing_time = time.time() - start_time
        
        # Create report record
        from controllers.reportController import create_report_from_analysis
        
        # Create report record
        report = await create_report_from_analysis(
            user_id=user_id,
            source_type="postgres",
            report_content=python_result,
            file_path=file_path,
            file_name=f"postgres_tables_{len(payload.tables)}.csv",
            table_names=payload.tables,
            record_count=total_records,
            processing_time=processing_time
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "PostgreSQL table(s) analyzed successfully",
                "fileType": "postgres",
                "filePath": file_path,
                "crewResult": python_result,
                "report_id": report.id
            }
        )
    except Exception as e:
        print(f"[POSTGRES-ANALYZE] Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 