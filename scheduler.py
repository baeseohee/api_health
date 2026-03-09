import schedule
import time
import threading
import subprocess
import sys
import os
import json
from datetime import datetime

class HealthCheckScheduler:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.interval_minutes = 5  # Default interval
        self.last_run = None
        self.next_run = None
        self.history = []
        self.max_history = 100
        
    def run_health_check(self):
        """Execute health check"""
        try:
            print(f"[Scheduler] Running health check at {datetime.now()}")
            self.last_run = datetime.now().isoformat()
            
            # Run pytest
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/test_dynamic.py"],
                cwd=os.getcwd(),
                capture_output=True,
                text=True
            )
            
            # Load results
            results_path = "data/health_check_results.json"
            if os.path.exists(results_path):
                with open(results_path, "r", encoding="utf-8") as f:
                    results = json.load(f)
                    
                # Calculate summary
                total = len(results)
                passed = sum(1 for r in results if r.get('success'))
                failed = total - passed
                
                # Add to history
                history_entry = {
                    "timestamp": self.last_run,
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "success_rate": round((passed / total * 100) if total > 0 else 0, 2)
                }
                
                self.history.append(history_entry)
                
                # Keep only recent history
                if len(self.history) > self.max_history:
                    self.history = self.history[-self.max_history:]
                
                # Save history
                self._save_history()
                
                print(f"[Scheduler] Check completed: {passed}/{total} passed")
                
        except Exception as e:
            print(f"[Scheduler] Error during health check: {e}")
    
    def _save_history(self):
        """Save history to file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/scheduler_history.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"[Scheduler] Error saving history: {e}")
    
    def _load_history(self):
        """Load history from file"""
        try:
            if os.path.exists("data/scheduler_history.json"):
                with open("data/scheduler_history.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"[Scheduler] Error loading history: {e}")
            self.history = []
    
    def _schedule_loop(self):
        """Background thread for scheduler"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def start(self, interval_minutes=5):
        """Start the scheduler"""
        if self.is_running:
            return {"status": "already_running"}
        
        self.interval_minutes = interval_minutes
        self._load_history()
        
        # Clear existing jobs
        schedule.clear()
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(self.run_health_check)
        
        # Calculate next run
        self.next_run = datetime.now()
        
        # Start background thread
        self.is_running = True
        self.thread = threading.Thread(target=self._schedule_loop, daemon=True)
        self.thread.start()
        
        print(f"[Scheduler] Started with {interval_minutes} minute interval")
        return {"status": "started", "interval": interval_minutes}
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return {"status": "not_running"}
        
        self.is_running = False
        schedule.clear()
        
        if self.thread:
            self.thread.join(timeout=2)
        
        print("[Scheduler] Stopped")
        return {"status": "stopped"}
    
    def get_status(self):
        """Get scheduler status"""
        next_run_str = None
        if self.is_running and schedule.jobs:
            next_run_str = schedule.next_run().isoformat() if schedule.next_run() else None
        
        return {
            "is_running": self.is_running,
            "interval_minutes": self.interval_minutes,
            "last_run": self.last_run,
            "next_run": next_run_str,
            "history_count": len(self.history)
        }
    
    def get_history(self, limit=50):
        """Get recent history"""
        return self.history[-limit:] if self.history else []

# Global scheduler instance
scheduler = HealthCheckScheduler()
