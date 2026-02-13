"""
Service for importing assignments from JSON files.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import Assignment, Task, TestCase

User = get_user_model()


class AssignmentImportError(Exception):
    """Custom exception for import errors."""
    pass


class AssignmentImporter:
    """Handles importing assignments from JSON format."""
    
    REQUIRED_FIELDS = ['title', 'tasks']
    TASK_REQUIRED_FIELDS = ['title', 'description']
    VALID_TASK_TYPES = ['DESCRIPTION_ONLY', 'CODING']
    VALID_VALIDATION_TYPES = ['MANUAL', 'AUTO']
    
    def __init__(self, teacher_user: User):
        """
        Initialize the importer with a teacher user.
        
        Args:
            teacher_user: The User object who will own the imported assignment
        """
        if not teacher_user.is_teacher():
            raise AssignmentImportError(f"User {teacher_user.username} is not a teacher")
        self.teacher = teacher_user
    
    def validate_json_structure(self, data: Dict) -> None:
        """
        Validate the JSON structure.
        
        Args:
            data: Parsed JSON data
            
        Raises:
            AssignmentImportError: If validation fails
        """
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                raise AssignmentImportError(f"Missing required field: {field}")
        
        # Validate tasks is a list
        if not isinstance(data['tasks'], list):
            raise AssignmentImportError("'tasks' must be a list")
        
        if len(data['tasks']) == 0:
            raise AssignmentImportError("Assignment must have at least one task")
        
        # Validate each task
        for idx, task in enumerate(data['tasks'], 1):
            self._validate_task(task, idx)
    
    def _validate_task(self, task: Dict, task_num: int) -> None:
        """Validate a single task structure."""
        # Check required fields
        for field in self.TASK_REQUIRED_FIELDS:
            if field not in task:
                raise AssignmentImportError(
                    f"Task {task_num}: Missing required field '{field}'"
                )
        
        # Validate task_type if provided
        if 'task_type' in task and task['task_type'] not in self.VALID_TASK_TYPES:
            raise AssignmentImportError(
                f"Task {task_num}: Invalid task_type '{task['task_type']}'. "
                f"Must be one of: {', '.join(self.VALID_TASK_TYPES)}"
            )
        
        # Validate validation_type if provided
        if 'validation_type' in task and task['validation_type'] not in self.VALID_VALIDATION_TYPES:
            raise AssignmentImportError(
                f"Task {task_num}: Invalid validation_type '{task['validation_type']}'. "
                f"Must be one of: {', '.join(self.VALID_VALIDATION_TYPES)}"
            )
        
        # Validate test_cases if provided
        if 'test_cases' in task:
            if not isinstance(task['test_cases'], list):
                raise AssignmentImportError(
                    f"Task {task_num}: 'test_cases' must be a list"
                )
            
            for tc_idx, test_case in enumerate(task['test_cases'], 1):
                self._validate_test_case(test_case, task_num, tc_idx)
    
    def _validate_test_case(self, test_case: Dict, task_num: int, tc_num: int) -> None:
        """Validate a single test case structure."""
        if 'expected_output' not in test_case:
            raise AssignmentImportError(
                f"Task {task_num}, Test Case {tc_num}: Missing required field 'expected_output'"
            )
    
    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """
        Parse datetime string to datetime object.
        
        Args:
            dt_string: ISO format datetime string or None
            
        Returns:
            datetime object or None
        """
        if not dt_string:
            return None
        
        try:
            # Try parsing ISO format
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except ValueError as e:
            raise AssignmentImportError(f"Invalid datetime format: {dt_string}. Use ISO format (e.g., 2026-02-15T10:00:00Z)")
    
    @transaction.atomic
    def import_from_dict(self, data: Dict) -> Assignment:
        """
        Import assignment from dictionary.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            Created Assignment object
            
        Raises:
            AssignmentImportError: If import fails
        """
        # Validate structure
        self.validate_json_structure(data)
        
        # Parse datetime fields
        start_time = self._parse_datetime(data.get('start_time'))
        end_time = self._parse_datetime(data.get('end_time'))
        
        # Create assignment
        assignment = Assignment.objects.create(
            teacher=self.teacher,
            title=data['title'],
            description=data.get('description', ''),
            start_time=start_time,
            end_time=end_time
        )
        
        # Create tasks
        for task_data in data['tasks']:
            task = Task.objects.create(
                assignment=assignment,
                title=task_data['title'],
                description=task_data['description'],
                task_type=task_data.get('task_type', 'CODING'),
                validation_type=task_data.get('validation_type', 'MANUAL'),
                order=task_data.get('order', 0)
            )
            
            # Create test cases if provided
            if 'test_cases' in task_data:
                for tc_data in task_data['test_cases']:
                    TestCase.objects.create(
                        task=task,
                        input_data=tc_data.get('input_data', ''),
                        expected_output=tc_data['expected_output']
                    )
        
        return assignment
    
    def import_from_file(self, file_path: str) -> Assignment:
        """
        Import assignment from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Created Assignment object
            
        Raises:
            AssignmentImportError: If import fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise AssignmentImportError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise AssignmentImportError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise AssignmentImportError(f"Error reading file: {e}")
        
        return self.import_from_dict(data)
    
    def import_from_uploaded_file(self, uploaded_file) -> Assignment:
        """
        Import assignment from Django uploaded file.
        
        Args:
            uploaded_file: Django UploadedFile object
            
        Returns:
            Created Assignment object
            
        Raises:
            AssignmentImportError: If import fails
        """
        try:
            content = uploaded_file.read().decode('utf-8')
            data = json.loads(content)
        except UnicodeDecodeError:
            raise AssignmentImportError("File must be UTF-8 encoded")
        except json.JSONDecodeError as e:
            raise AssignmentImportError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise AssignmentImportError(f"Error reading file: {e}")
        
        return self.import_from_dict(data)
