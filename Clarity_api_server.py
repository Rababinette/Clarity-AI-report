#!/usr/bin/env python3
"""
Mock Clarity PPM API Server
Simulates Clarity PPM REST API for demo purposes
Run this to simulate your actual Clarity PPM instance
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# Mock Clarity PPM Project Data
PROJECTS_DATA = [
    {
        "id": "PRJ001",
        "name": "Digital Transformation Initiative",
        "code": "DTI-2024",
        "manager": "John Smith",
        "sponsor": "Sarah Williams",
        "department": "IT",
        "priority": "High",
        "start_date": "2024-01-15",
        "planned_end_date": "2025-06-30",
        "current_end_date": "2025-07-12",
        "budget": {
            "total": 750000,
            "spent": 625000,
            "remaining": 125000,
            "variance": -30000,
            "variance_percentage": -4.0
        },
        "schedule": {
            "planned_duration_days": 532,
            "actual_duration_days": 544,
            "percent_complete": 68,
            "variance_days": -12,
            "milestone_completion": "8/12"
        },
        "scope": {
            "original_scope_items": 45,
            "completed_items": 28,
            "in_progress_items": 12,
            "pending_items": 5,
            "scope_changes": 3,
            "scope_variance_percentage": 6.7
        },
        "health": {
            "overall_status": "At Risk",
            "scope_status": "Yellow",
            "budget_status": "Red",
            "schedule_status": "Yellow",
            "health_score": 65
        },
        "risks": {
            "total": 5,
            "critical": 2,
            "high": 1,
            "medium": 1,
            "low": 1
        },
        "team": {
            "size": 15,
            "utilization": 85
        }
    },
    {
        "id": "PRJ002",
        "name": "Cloud Migration Project",
        "code": "CMP-2024",
        "manager": "Michael Chen",
        "sponsor": "David Brown",
        "department": "Infrastructure",
        "priority": "High",
        "start_date": "2024-03-01",
        "planned_end_date": "2025-03-31",
        "current_end_date": "2025-03-28",
        "budget": {
            "total": 450000,
            "spent": 280000,
            "remaining": 170000,
            "variance": 15000,
            "variance_percentage": 3.3
        },
        "schedule": {
            "planned_duration_days": 365,
            "actual_duration_days": 362,
            "percent_complete": 72,
            "variance_days": 3,
            "milestone_completion": "6/8"
        },
        "scope": {
            "original_scope_items": 32,
            "completed_items": 23,
            "in_progress_items": 7,
            "pending_items": 2,
            "scope_changes": 1,
            "scope_variance_percentage": 3.1
        },
        "health": {
            "overall_status": "On Track",
            "scope_status": "Green",
            "budget_status": "Green",
            "schedule_status": "Green",
            "health_score": 88
        },
        "risks": {
            "total": 2,
            "critical": 0,
            "high": 0,
            "medium": 1,
            "low": 1
        },
        "team": {
            "size": 12,
            "utilization": 78
        }
    },
    {
        "id": "PRJ003",
        "name": "Customer Portal Redesign",
        "code": "CPR-2024",
        "manager": "Emily Rodriguez",
        "sponsor": "Robert Taylor",
        "department": "Marketing",
        "priority": "Critical",
        "start_date": "2024-02-01",
        "planned_end_date": "2024-11-30",
        "current_end_date": "2024-12-25",
        "budget": {
            "total": 320000,
            "spent": 305000,
            "remaining": 15000,
            "variance": -20000,
            "variance_percentage": -6.25
        },
        "schedule": {
            "planned_duration_days": 303,
            "actual_duration_days": 328,
            "percent_complete": 85,
            "variance_days": -25,
            "milestone_completion": "8/10"
        },
        "scope": {
            "original_scope_items": 28,
            "completed_items": 22,
            "in_progress_items": 4,
            "pending_items": 7,
            "scope_changes": 5,
            "scope_variance_percentage": 17.9
        },
        "health": {
            "overall_status": "Critical",
            "scope_status": "Red",
            "budget_status": "Red",
            "schedule_status": "Red",
            "health_score": 42
        },
        "risks": {
            "total": 8,
            "critical": 4,
            "high": 2,
            "medium": 1,
            "low": 1
        },
        "team": {
            "size": 10,
            "utilization": 95
        }
    },
    {
        "id": "PRJ004",
        "name": "Data Warehouse Modernization",
        "code": "DWM-2024",
        "manager": "James Wilson",
        "sponsor": "Linda Martinez",
        "department": "Data Analytics",
        "priority": "Medium",
        "start_date": "2024-04-15",
        "planned_end_date": "2025-08-15",
        "current_end_date": "2025-08-15",
        "budget": {
            "total": 580000,
            "spent": 385000,
            "remaining": 195000,
            "variance": 15000,
            "variance_percentage": 2.6
        },
        "schedule": {
            "planned_duration_days": 488,
            "actual_duration_days": 488,
            "percent_complete": 55,
            "variance_days": 0,
            "milestone_completion": "8/15"
        },
        "scope": {
            "original_scope_items": 52,
            "completed_items": 28,
            "in_progress_items": 18,
            "pending_items": 6,
            "scope_changes": 2,
            "scope_variance_percentage": 3.8
        },
        "health": {
            "overall_status": "On Track",
            "scope_status": "Green",
            "budget_status": "Green",
            "schedule_status": "Green",
            "health_score": 92
        },
        "risks": {
            "total": 3,
            "critical": 1,
            "high": 0,
            "medium": 1,
            "low": 1
        },
        "team": {
            "size": 18,
            "utilization": 68
        }
    },
    {
        "id": "PRJ005",
        "name": "Mobile App Development",
        "code": "MAD-2024",
        "manager": "Amanda Lee",
        "sponsor": "Thomas Anderson",
        "department": "Product",
        "priority": "High",
        "start_date": "2024-05-01",
        "planned_end_date": "2025-02-28",
        "current_end_date": "2025-03-08",
        "budget": {
            "total": 420000,
            "spent": 310000,
            "remaining": 110000,
            "variance": -5000,
            "variance_percentage": -1.2
        },
        "schedule": {
            "planned_duration_days": 304,
            "actual_duration_days": 312,
            "percent_complete": 62,
            "variance_days": -8,
            "milestone_completion": "5/9"
        },
        "scope": {
            "original_scope_items": 38,
            "completed_items": 23,
            "in_progress_items": 11,
            "pending_items": 8,
            "scope_changes": 4,
            "scope_variance_percentage": 10.5
        },
        "health": {
            "overall_status": "At Risk",
            "scope_status": "Yellow",
            "budget_status": "Yellow",
            "schedule_status": "Yellow",
            "health_score": 58
        },
        "risks": {
            "total": 4,
            "critical": 1,
            "high": 1,
            "medium": 1,
            "low": 1
        },
        "team": {
            "size": 14,
            "utilization": 82
        }
    }
]

@app.route('/api/health', methods=['GET'])
def health_check():
    """API Health check"""
    return jsonify({
        "status": "ok",
        "service": "Clarity PPM Mock API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    return jsonify({
        "success": True,
        "total": len(PROJECTS_DATA),
        "timestamp": datetime.now().isoformat(),
        "data": PROJECTS_DATA
    })

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get specific project by ID"""
    project = next((p for p in PROJECTS_DATA if p['id'] == project_id), None)
    if project:
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": project
        })
    return jsonify({
        "success": False,
        "error": "Project not found"
    }), 404

@app.route('/api/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """Get portfolio summary statistics"""
    total_budget = sum(p['budget']['total'] for p in PROJECTS_DATA)
    total_spent = sum(p['budget']['spent'] for p in PROJECTS_DATA)
    
    on_track = len([p for p in PROJECTS_DATA if p['health']['overall_status'] == 'On Track'])
    at_risk = len([p for p in PROJECTS_DATA if p['health']['overall_status'] == 'At Risk'])
    critical = len([p for p in PROJECTS_DATA if p['health']['overall_status'] == 'Critical'])
    
    avg_health = sum(p['health']['health_score'] for p in PROJECTS_DATA) / len(PROJECTS_DATA)
    avg_completion = sum(p['schedule']['percent_complete'] for p in PROJECTS_DATA) / len(PROJECTS_DATA)
    
    return jsonify({
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "total_projects": len(PROJECTS_DATA),
            "budget": {
                "total": total_budget,
                "spent": total_spent,
                "remaining": total_budget - total_spent,
                "utilization_percentage": (total_spent / total_budget) * 100
            },
            "status_distribution": {
                "on_track": on_track,
                "at_risk": at_risk,
                "critical": critical
            },
            "average_health_score": round(avg_health, 1),
            "average_completion": round(avg_completion, 1),
            "total_risks": sum(p['risks']['total'] for p in PROJECTS_DATA),
            "critical_risks": sum(p['risks']['critical'] for p in PROJECTS_DATA)
        }
    })

@app.route('/api/portfolio/health', methods=['GET'])
def get_portfolio_health():
    """Get detailed portfolio health metrics"""
    projects_over_budget = len([p for p in PROJECTS_DATA if p['budget']['variance'] < 0])
    projects_behind_schedule = len([p for p in PROJECTS_DATA if p['schedule']['variance_days'] < 0])
    projects_scope_variance = len([p for p in PROJECTS_DATA if p['scope']['scope_variance_percentage'] > 5])
    
    return jsonify({
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "scope": {
                "projects_with_variance": projects_scope_variance,
                "average_variance": round(sum(p['scope']['scope_variance_percentage'] for p in PROJECTS_DATA) / len(PROJECTS_DATA), 2)
            },
            "budget": {
                "projects_over_budget": projects_over_budget,
                "total_variance": sum(p['budget']['variance'] for p in PROJECTS_DATA),
                "average_variance_percentage": round(sum(p['budget']['variance_percentage'] for p in PROJECTS_DATA) / len(PROJECTS_DATA), 2)
            },
            "schedule": {
                "projects_behind": projects_behind_schedule,
                "average_variance_days": round(sum(p['schedule']['variance_days'] for p in PROJECTS_DATA) / len(PROJECTS_DATA), 1)
            }
        }
    })

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 CLARITY PPM MOCK API SERVER")
    print("=" * 80)
    print("\nStarting server...")
    print("\nAvailable endpoints:")
    print("  GET  http://localhost:5000/api/health")
    print("  GET  http://localhost:5000/api/projects")
    print("  GET  http://localhost:5000/api/projects/<id>")
    print("  GET  http://localhost:5000/api/portfolio/summary")
    print("  GET  http://localhost:5000/api/portfolio/health")
    print("\n" + "=" * 80)
    print("\n💡 This simulates your actual Clarity PPM instance")
    print("💡 Claude Desktop will fetch data from these endpoints")
    print("\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)