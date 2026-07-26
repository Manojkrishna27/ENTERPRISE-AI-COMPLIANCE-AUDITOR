import uuid
import time

class TaskStatus:
    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"

class BackgroundTaskManager:
    def __init__(self):
        self.jobs = {}

    def create_job(self, task_type: str, metadata: dict = None) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "job_id": job_id,
            "task_type": task_type,
            "status": TaskStatus.QUEUED,
            "progress": 0.0,
            "metadata": metadata or {},
            "error": None,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        return job_id

    def update_job(self, job_id: str, status: str = None, progress: float = None, error: str = None):
        if job_id in self.jobs:
            if status:
                self.jobs[job_id]["status"] = status
            if progress is not None:
                self.jobs[job_id]["progress"] = progress
            if error:
                self.jobs[job_id]["error"] = error
            self.jobs[job_id]["updated_at"] = time.time()

    def get_job(self, job_id: str) -> dict:
        return self.jobs.get(job_id)

    def retry_job(self, job_id: str) -> bool:
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = TaskStatus.QUEUED,
            self.jobs[job_id]["progress"] = 0.0
            self.jobs[job_id]["error"] = None
            self.jobs[job_id]["updated_at"] = time.time()
            return True
        return False

task_manager = BackgroundTaskManager()
