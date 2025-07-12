from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
import time
import json
import csv
import io
from datetime import datetime
from models.reportModel import (
    Report, ReportCreate, ReportResponse, ReportAnalytics,
    ReportHistoryRequest, ReportDeleteRequest, ReportDownloadRequest
)
from models.userModel import User
from middleware.authentication import is_authenticated_user

router = APIRouter()

@router.post("/reports", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    user_id: str = Depends(is_authenticated_user)
):
    """Create a new report record"""
    try:
        # Create report with user ID
        report = await Report.create(
            user_id=user_id,
            **report_data.dict()
        )
        
        return ReportResponse(**report.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

@router.get("/reports", response_model=List[ReportResponse])
async def get_report_history(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    limit: int = Query(50, description="Number of reports to return"),
    user_id: str = Depends(is_authenticated_user)
):
    """Get user's report history with optional filtering"""
    try:
        reports = await Report.find_by_user_id(
            user_id=user_id,
            source_type=source_type,
            limit=limit
        )
        
        return [ReportResponse(**report.to_dict()) for report in reports]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report history: {str(e)}")

@router.get("/reports/analytics", response_model=ReportAnalytics)
async def get_report_analytics(
    user_id: str = Depends(is_authenticated_user)
):
    """Get analytics for user's reports"""
    try:
        analytics = await Report.get_analytics(user_id=user_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report_by_id(
    report_id: str,
    user_id: str = Depends(is_authenticated_user)
):
    """Get a specific report by ID"""
    try:
        report = await Report.find_by_id(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Ensure user can only access their own reports
        if report.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return ReportResponse(**report.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: str,
    user_id: str = Depends(is_authenticated_user)
):
    """Delete a report"""
    try:
        report = await Report.find_by_id(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Ensure user can only delete their own reports
        if report.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await report.delete()
        
        return {"message": "Report deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: str,
    format: str = Query("markdown", description="Download format: markdown, csv, json"),
    user_id: str = Depends(is_authenticated_user)
):
    """Download a report in specified format"""
    try:
        report = await Report.find_by_id(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Ensure user can only download their own reports
        if report.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report.report_title.replace(' ', '_')}_{timestamp}"
        
        if format == "markdown":
            content = report.report_content
            media_type = "text/markdown"
            filename += ".md"
        elif format == "json":
            # Convert markdown to structured JSON
            content = json.dumps({
                "title": report.report_title,
                "source_type": report.source_type,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "content": report.report_content,
                "metadata": {
                    "file_path": report.file_path,
                    "file_name": report.file_name,
                    "table_names": report.table_names,
                    "record_count": report.record_count,
                    "processing_time": report.processing_time
                }
            }, indent=2)
            media_type = "application/json"
            filename += ".json"
        elif format == "csv":
            # Extract table data from markdown and convert to CSV
            content = convert_markdown_to_csv(report.report_content)
            media_type = "text/csv"
            filename += ".csv"
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use: markdown, csv, json")
        
        return {
            "content": content,
            "filename": filename,
            "media_type": media_type,
            "format": format
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")

def convert_markdown_to_csv(markdown_content: str) -> str:
    """Convert markdown tables to CSV format"""
    lines = markdown_content.split('\n')
    csv_data = []
    current_table = []
    in_table = False
    
    for line in lines:
        if line.strip().startswith('|') and '|' in line[1:]:
            # This is a table row
            if not in_table:
                in_table = True
            
            # Clean up the line and split by |
            cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
            current_table.append(cells)
        elif in_table and not line.strip().startswith('|'):
            # End of table
            if current_table:
                # Convert table to CSV
                csv_buffer = io.StringIO()
                csv_writer = csv.writer(csv_buffer)
                csv_writer.writerows(current_table)
                csv_data.append(csv_buffer.getvalue())
                current_table = []
            in_table = False
    
    # Handle last table if still in table
    if current_table:
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerows(current_table)
        csv_data.append(csv_buffer.getvalue())
    
    return '\n\n'.join(csv_data) if csv_data else "No table data found"

@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    report_data: ReportCreate,
    user_id: str = Depends(is_authenticated_user)
):
    """Update a report"""
    try:
        report = await Report.find_by_id(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Ensure user can only update their own reports
        if report.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update report fields
        for field, value in report_data.dict().items():
            setattr(report, field, value)
        
        await report.save()
        
        return ReportResponse(**report.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update report: {str(e)}")

# Helper function to create report from analysis result
async def create_report_from_analysis(
    user_id: str,
    source_type: str,
    report_content: str,
    file_path: Optional[str] = None,
    file_name: Optional[str] = None,
    table_names: Optional[List[str]] = None,
    record_count: Optional[int] = None,
    processing_time: Optional[float] = None
) -> Report:
    """Helper function to create a report from analysis result"""
    # Generate title based on source type and timestamp
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    if source_type == "csv":
        title = f"CSV Analysis Report - {timestamp}"
    elif source_type == "postgres":
        title = f"PostgreSQL Analysis Report - {timestamp}"
    elif source_type == "google_sheet":
        title = f"Google Sheets Analysis Report - {timestamp}"
    else:
        title = f"Data Analysis Report - {timestamp}"
    
    # Create report
    report = await Report.create(
        user_id=user_id,
        source_type=source_type,
        report_title=title,
        report_content=report_content,
        file_path=file_path,
        file_name=file_name,
        table_names=table_names,
        record_count=record_count,
        processing_time=processing_time,
        status="completed"
    )
    
    return report 