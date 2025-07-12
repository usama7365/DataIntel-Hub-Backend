from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.data_intel_hub
reports_collection = db.reports

class ReportBase(BaseModel):
    """Base report model"""
    user_id: str = Field(..., description="User ID who created the report")
    source_type: str = Field(..., description="Source type: csv, postgres, google_sheet")
    report_title: str = Field(..., description="Title of the report")
    report_content: str = Field(..., description="Markdown content of the report")
    file_path: Optional[str] = Field(None, description="Path to the original file")
    file_name: Optional[str] = Field(None, description="Original file name")
    table_names: Optional[List[str]] = Field(None, description="Names of tables analyzed (for PostgreSQL)")
    record_count: Optional[int] = Field(None, description="Number of records analyzed")
    processing_time: Optional[float] = Field(None, description="Time taken to process in seconds")
    status: str = Field(default="completed", description="Report status: completed, failed, processing")

    class Config:
        validate_by_name = True

class ReportCreate(ReportBase):
    """Model for creating a new report"""
    pass

class ReportUpdate(BaseModel):
    """Model for updating report information"""
    report_title: Optional[str] = None
    report_content: Optional[str] = None
    status: Optional[str] = None
    processing_time: Optional[float] = None

class ReportResponse(BaseModel):
    """Model for report response"""
    id: str
    user_id: str
    source_type: str
    report_title: str
    report_content: str
    file_path: Optional[str]
    file_name: Optional[str]
    table_names: Optional[List[str]]
    record_count: Optional[int]
    processing_time: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReportAnalytics(BaseModel):
    """Model for report analytics"""
    total_reports: int
    reports_by_source: Dict[str, int]
    average_processing_time: float
    most_used_source: str
    recent_reports: List[ReportResponse]

class Report:
    """
    Report model for tracking user report history using MongoDB
    """
    
    def __init__(self, **kwargs):
        self._id = kwargs.get('_id')
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.user_id = kwargs.get('user_id')
        self.source_type = kwargs.get('source_type')
        self.report_title = kwargs.get('report_title')
        self.report_content = kwargs.get('report_content')
        self.file_path = kwargs.get('file_path')
        self.file_name = kwargs.get('file_name')
        self.table_names = kwargs.get('table_names', [])
        self.record_count = kwargs.get('record_count')
        self.processing_time = kwargs.get('processing_time')
        self.status = kwargs.get('status', 'completed')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @classmethod
    async def create(cls, **kwargs):
        """Create a new report"""
        # Generate UUID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        
        # Set timestamps
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        
        # Create report instance
        report = cls(**kwargs)
        
        # Prepare data for MongoDB
        report_dict = {
            "id": report.id,
            "user_id": report.user_id,
            "source_type": report.source_type,
            "report_title": report.report_title,
            "report_content": report.report_content,
            "file_path": report.file_path,
            "file_name": report.file_name,
            "table_names": report.table_names,
            "record_count": report.record_count,
            "processing_time": report.processing_time,
            "status": report.status,
            "created_at": report.created_at,
            "updated_at": report.updated_at
        }
        
        # Save to MongoDB
        result = await reports_collection.insert_one(report_dict)
        report._id = result.inserted_id
        
        return report
    
    @classmethod
    async def find_by_user_id(cls, user_id: str, source_type: Optional[str] = None, limit: int = 50):
        """Find reports by user ID with optional source type filter"""
        query = {"user_id": user_id}
        if source_type:
            query["source_type"] = source_type
        
        reports = []
        cursor = reports_collection.find(query).sort("created_at", -1).limit(limit)
        async for report_data in cursor:
            reports.append(cls(**report_data))
        return reports
    
    @classmethod
    async def find_by_id(cls, report_id: str):
        """Find a report by ID"""
        report_data = await reports_collection.find_one({"id": report_id})
        if report_data:
            return cls(**report_data)
        return None
    
    @classmethod
    async def get_analytics(cls, user_id: str):
        """Get analytics for a user's reports"""
        # Get all reports for the user
        reports = await cls.find_by_user_id(user_id, limit=1000)
        
        if not reports:
            return ReportAnalytics(
                total_reports=0,
                reports_by_source={},
                average_processing_time=0,
                most_used_source="",
                recent_reports=[]
            )
        
        # Calculate analytics
        total_reports = len(reports)
        reports_by_source = {}
        total_processing_time = 0
        processing_count = 0
        
        for report in reports:
            # Count by source
            source = report.source_type
            reports_by_source[source] = reports_by_source.get(source, 0) + 1
            
            # Calculate average processing time
            if report.processing_time:
                total_processing_time += report.processing_time
                processing_count += 1
        
        average_processing_time = total_processing_time / processing_count if processing_count > 0 else 0
        
        # Find most used source
        most_used_source = max(reports_by_source.items(), key=lambda x: x[1])[0] if reports_by_source else ""
        
        # Get recent reports (last 10)
        recent_reports = reports[:10]
        
        return ReportAnalytics(
            total_reports=total_reports,
            reports_by_source=reports_by_source,
            average_processing_time=average_processing_time,
            most_used_source=most_used_source,
            recent_reports=recent_reports
        )
    
    async def save(self):
        """Save report to database"""
        self.updated_at = datetime.utcnow()
        
        # Convert to dict and remove _id for update
        report_dict = self.to_dict()
        report_dict['updated_at'] = self.updated_at
        
        # Update in MongoDB
        await reports_collection.update_one(
            {"_id": self._id},
            {"$set": report_dict}
        )
        return self
    
    async def delete(self):
        """Delete report from database"""
        await reports_collection.delete_one({"_id": self._id})
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for JSON response"""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "source_type": self.source_type,
            "report_title": self.report_title,
            "report_content": self.report_content,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "table_names": self.table_names,
            "record_count": self.record_count,
            "processing_time": self.processing_time,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ReportHistoryRequest(BaseModel):
    """Request model for getting report history"""
    source_type: Optional[str] = Field(None, description="Filter by source type")
    limit: Optional[int] = Field(50, description="Number of reports to return")

class ReportDeleteRequest(BaseModel):
    """Request model for deleting a report"""
    report_id: str = Field(..., description="ID of the report to delete")

class ReportDownloadRequest(BaseModel):
    """Request model for downloading a report"""
    report_id: str = Field(..., description="ID of the report to download")
    format: str = Field(default="markdown", description="Download format: markdown, csv, json") 