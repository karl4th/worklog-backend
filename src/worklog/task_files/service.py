import os
import uuid
import traceback
from fastapi import UploadFile
from pathlib import Path

from src.worklog.task_files.models import TaskFiles
from .schemas import TaskFileResponse, TaskFileList
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession



    

class TaskFilesService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.UPLOADS_DIR = 'uploads'

    async def _save_uploaded_file(self, uploaded_file) -> dict:
        """
        Save an uploaded file to the uploads directory with a unique filename.
        
        Args:
            file: The uploaded file
            
        Returns:
            A dictionary containing the original filename and the new unique filename
        """
        try:
            file_new = uploaded_file.file            
            original_filename = uploaded_file.filename
            file_extension = os.path.splitext(original_filename)[1]
            
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create the full file path
            file_path = f"{self.UPLOADS_DIR}/{unique_filename}"
            
            # Save the file
            with open(file_path, "wb") as buffer:
                content = file_new.read()
                buffer.write(content)
            
            return {
                "original_filename": original_filename,
                "unique_filename": unique_filename
            }
        except Exception as e:
            error_details = traceback.format_exc()
            raise Exception(f"Failed to save uploaded file: {str(e)}\nDetails: {error_details}")

    async def create_task_file(self, task_id: int, uploaded_file: dict, created_by: int) -> TaskFileResponse:
        try:
        
            task_file = TaskFiles(
                task_id=task_id,
                original_filename=uploaded_file["original_filename"],
                new_filename=uploaded_file["unique_filename"],
                created_by=created_by
            )

            self.db.add(task_file)
            await self.db.commit()
            await self.db.refresh(task_file)

            return TaskFileResponse(
                id=task_file.id,
                task_id=task_file.task_id,
                original_filename=task_file.original_filename,
                new_filename=task_file.new_filename,
                created_by=task_file.created_by,
                created_at=task_file.created_at,
                updated_at=task_file.updated_at
            )
        except Exception as e:
            await self.db.rollback()
            error_details = traceback.format_exc()
            raise Exception(f"Failed to create task file: {str(e)}\nDetails: {error_details}")

    async def get_task_files(self, task_id: int) -> TaskFileList:
        try:
            result = await self.db.execute(
                select(TaskFiles).where(TaskFiles.task_id == task_id)
            )
            task_files = result.scalars().all()
            
            # Convert TaskFiles objects to TaskFileResponse objects
            files = [
                TaskFileResponse(
                    id=file.id,
                    task_id=file.task_id,
                    original_filename=file.original_filename,
                    new_filename=file.new_filename,
                    created_by=file.created_by,
                    created_at=file.created_at,
                    updated_at=file.updated_at
                )
                for file in task_files
            ]
            
            return TaskFileList(files=files, total=len(files))
        except Exception as e:
            error_details = traceback.format_exc()
            raise Exception(f"Failed to get task files: {str(e)}\nDetails: {error_details}")

