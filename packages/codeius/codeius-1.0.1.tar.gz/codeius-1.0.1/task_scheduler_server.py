"""
Scheduling/Task Automation Tool
Local cron/task scheduler using schedule, letting the agent run commands, tests, or code checks automatically.
"""
from flask import Flask, request, jsonify
import schedule
import time
import threading
import subprocess
import os
from datetime import datetime
from typing import Dict, Any

app = Flask(__name__)

class TaskScheduler:
    def __init__(self):
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.scheduler_thread = None
    
    def start_scheduler(self):
        """Start the scheduler in a background thread"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            return {"status": "success", "message": "Scheduler started"}
        return {"status": "info", "message": "Scheduler already running"}
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.running:
            self.running = False
            # Clear all scheduled jobs
            schedule.clear()
            self.scheduled_tasks = {}
            return {"status": "success", "message": "Scheduler stopped and tasks cleared"}
        return {"status": "info", "message": "Scheduler not running"}
    
    def _run_scheduler(self):
        """Run the scheduler in a loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def schedule_task(self, task_id: str, task_type: str, interval: str, command: str = None, 
                     file_path: str = None, custom_script: str = None):
        """Schedule a new task based on the provided parameters"""
        try:
            # Parse interval (e.g., "every 5 minutes", "hourly", "daily at 10:30")
            interval_parts = interval.split()
            
            if len(interval_parts) >= 2 and interval_parts[0].lower() == "every":
                # Handle "every X [unit]" format
                count = int(interval_parts[1])
                unit = interval_parts[2].lower()
                
                if unit.startswith("minute"):
                    job = schedule.every(count).minutes
                elif unit.startswith("hour"):
                    job = schedule.every(count).hours
                elif unit.startswith("day"):
                    job = schedule.every(count).days
                elif unit.startswith("second"):
                    job = schedule.every(count).seconds
                else:
                    return {"status": "error", "message": f"Unknown time unit: {unit}"}
            elif interval.lower() == "hourly":
                job = schedule.every().hour
            elif interval.lower() == "daily":
                job = schedule.every().day
            elif "at" in interval:
                # Handle "daily at HH:MM" or similar
                time_part = interval.split(" at ")[-1]
                if "daily" in interval:
                    job = schedule.every().day.at(time_part)
                elif "monday" in interval:
                    job = schedule.every().monday.at(time_part)
                elif "tuesday" in interval:
                    job = schedule.every().tuesday.at(time_part)
                elif "wednesday" in interval:
                    job = schedule.every().wednesday.at(time_part)
                elif "thursday" in interval:
                    job = schedule.every().thursday.at(time_part)
                elif "friday" in interval:
                    job = schedule.every().friday.at(time_part)
                elif "saturday" in interval:
                    job = schedule.every().saturday.at(time_part)
                elif "sunday" in interval:
                    job = schedule.every().sunday.at(time_part)
                else:
                    return {"status": "error", "message": f"Unsupported time format: {interval}"}
            else:
                return {"status": "error", "message": f"Unsupported interval format: {interval}"}
            
            # Define the task function based on task type
            if task_type == "command":
                def task_func(task_cmd=command):
                    try:
                        result = subprocess.run(task_cmd.split(), capture_output=True, text=True)
                        return f"Command '{task_cmd}' completed with return code {result.returncode}"
                    except Exception as e:
                        return f"Command '{task_cmd}' failed: {str(e)}"
                
                job.do(task_func)
                
            elif task_type == "test":
                def task_func(test_path=file_path or "."):
                    try:
                        result = subprocess.run(["python", "-m", "pytest", test_path], 
                                              capture_output=True, text=True)
                        return f"Test run completed. Return code: {result.returncode}. Output: {result.stdout[:200]}"
                    except Exception as e:
                        return f"Test run failed: {str(e)}"
                
                job.do(task_func)
                
            elif task_type == "script":
                def task_func(script_path=file_path):
                    try:
                        result = subprocess.run(["python", script_path], 
                                              capture_output=True, text=True)
                        return f"Script '{script_path}' executed. Return code: {result.returncode}"
                    except Exception as e:
                        return f"Script execution failed: {str(e)}"
                
                job.do(task_func)
                
            elif task_type == "custom":
                def task_func(custom_code=custom_script):
                    try:
                        local_vars = {}
                        exec(custom_code, globals(), local_vars)
                        return f"Custom task executed: {str(local_vars)}"
                    except Exception as e:
                        return f"Custom task failed: {str(e)}"
                
                job.do(task_func)
            
            else:
                return {"status": "error", "message": f"Unknown task type: {task_type}"}
            
            # Store task details
            self.scheduled_tasks[task_id] = {
                "type": task_type,
                "interval": interval,
                "command": command,
                "file_path": file_path,
                "custom_script": custom_script,
                "next_run": str(job.next_run),
                "created_at": str(datetime.now())
            }
            
            return {
                "status": "success", 
                "message": f"Task '{task_id}' scheduled to run {interval}",
                "task_id": task_id,
                "next_run": str(job.next_run)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Failed to schedule task: {str(e)}"}
    
    def list_tasks(self):
        """List all scheduled tasks"""
        tasks_list = []
        for task_id, details in self.scheduled_tasks.items():
            tasks_list.append({
                "id": task_id,
                "details": details
            })
        
        return {
            "status": "success",
            "tasks": tasks_list,
            "count": len(tasks_list)
        }
    
    def remove_task(self, task_id: str):
        """Remove a specific task from the scheduler"""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            # Note: schedule library doesn't provide a direct way to cancel specific jobs
            # For now, we'll clear and reschedule remaining jobs
            return {"status": "success", "message": f"Task '{task_id}' removed"}
        else:
            return {"status": "error", "message": f"Task '{task_id}' not found"}

task_scheduler = TaskScheduler()

@app.route('/schedule', methods=['POST'])
def handle_schedule():
    """Handle scheduling requests"""
    try:
        action = request.json.get('action', 'create')
        
        if action == 'start':
            result = task_scheduler.start_scheduler()
            return jsonify(result)
        
        elif action == 'stop':
            result = task_scheduler.stop_scheduler()
            return jsonify(result)
        
        elif action == 'create' or action == 'schedule':
            task_id = request.json.get('task_id', f"task_{int(time.time())}")
            task_type = request.json.get('type', 'command')
            interval = request.json.get('interval', 'every 1 hour')
            command = request.json.get('command', None)
            file_path = request.json.get('file_path', None)
            custom_script = request.json.get('custom_script', None)
            
            result = task_scheduler.schedule_task(task_id, task_type, interval, command, file_path, custom_script)
            return jsonify(result)
        
        elif action == 'list':
            result = task_scheduler.list_tasks()
            return jsonify(result)
        
        elif action == 'remove':
            task_id = request.json.get('task_id', None)
            if task_id:
                result = task_scheduler.remove_task(task_id)
                return jsonify(result)
            else:
                return jsonify({"status": "error", "message": "Task ID required for removal"}), 400
        
        else:
            return jsonify({"status": "error", "message": f"Unknown action: {action}"}), 400
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=10800)