from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid

@dataclass
class Report:
    """A work report produced by an agent"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    author_id: str
    title: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    parent_report_id: Optional[str] = None
    child_report_ids: List[str] = field(default_factory=list)
    status: str = "draft"  # draft, submitted, accepted, rejected
    feedback: Optional[str] = None
    
    def add_child_report(self, report_id: str):
        """Add a child report reference"""
        if report_id not in self.child_report_ids:
            self.child_report_ids.append(report_id)
    
    def submit(self):
        """Submit the report for review"""
        self.status = "submitted"
    
    def accept(self, feedback: Optional[str] = None):
        """Accept the report"""
        self.status = "accepted"
        self.feedback = feedback
    
    def reject(self, feedback: str):
        """Reject the report with feedback"""
        self.status = "rejected"
        self.feedback = feedback
