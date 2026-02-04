#!/usr/bin/env python3
"""
Claude Desktop Automation for Clarity PPM
This script is designed to be run by Claude Desktop to:
1. Fetch project data from Clarity PPM API
2. Analyze scope, budget, and timeline health
3. Generate executive weekly portfolio report
4. Output data for React dashboard
"""

import requests
import json
from datetime import datetime, timedelta
from anthropic import Anthropic
import os

# Configuration
CLARITY_API_BASE = "http://localhost:5000/api"
OUTPUT_DIR = "./reports"
USE_REAL_CLAUDE = False  # Set to True to use real Claude API

class ClarityPPMAnalyzer:
    """Main analyzer class for Clarity PPM data"""
    
    def __init__(self):
        self.api_base = CLARITY_API_BASE
        self.projects = []
        self.portfolio_summary = {}
        self.portfolio_health = {}
        
    def fetch_data(self):
        """Step 1: Fetch all data from Clarity PPM API"""
        print("\n" + "="*80)
        print("📡 STEP 1: FETCHING DATA FROM CLARITY PPM")
        print("="*80)
        
        try:
            # Fetch projects
            print("\n📊 Fetching project data...")
            response = requests.get(f"{self.api_base}/projects", timeout=10)
            response.raise_for_status()
            projects_data = response.json()
            self.projects = projects_data['data']
            print(f"✅ Fetched {len(self.projects)} projects")
            
            # Fetch portfolio summary
            print("\n📈 Fetching portfolio summary...")
            response = requests.get(f"{self.api_base}/portfolio/summary", timeout=10)
            response.raise_for_status()
            self.portfolio_summary = response.json()['data']
            print("✅ Portfolio summary retrieved")
            
            # Fetch portfolio health
            print("\n🏥 Fetching portfolio health metrics...")
            response = requests.get(f"{self.api_base}/portfolio/health", timeout=10)
            response.raise_for_status()
            self.portfolio_health = response.json()['data']
            print("✅ Portfolio health metrics retrieved")
            
            return True
            
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: Cannot connect to Clarity PPM API")
            print("💡 Make sure the API server is running: python clarity_api_server.py")
            return False
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def analyze_project_health(self, project):
        """Analyze individual project health across scope, budget, timeline"""
        
        analysis = {
            "project_id": project['id'],
            "project_name": project['name'],
            "overall_status": project['health']['overall_status'],
            "health_score": project['health']['health_score'],
            "dimensions": {}
        }
        
        # Scope Analysis
        scope_variance = project['scope']['scope_variance_percentage']
        analysis['dimensions']['scope'] = {
            "status": project['health']['scope_status'],
            "variance_percentage": scope_variance,
            "assessment": self._assess_scope(scope_variance, project['scope']['scope_changes']),
            "metrics": {
                "total_items": project['scope']['original_scope_items'],
                "completed": project['scope']['completed_items'],
                "in_progress": project['scope']['in_progress_items'],
                "scope_changes": project['scope']['scope_changes']
            }
        }
        
        # Budget Analysis
        budget_variance = project['budget']['variance_percentage']
        analysis['dimensions']['budget'] = {
            "status": project['health']['budget_status'],
            "variance_percentage": budget_variance,
            "variance_amount": project['budget']['variance'],
            "assessment": self._assess_budget(budget_variance, project['budget']['spent'], project['budget']['total']),
            "metrics": {
                "total": project['budget']['total'],
                "spent": project['budget']['spent'],
                "remaining": project['budget']['remaining'],
                "utilization": (project['budget']['spent'] / project['budget']['total']) * 100
            }
        }
        
        # Timeline Analysis
        schedule_variance_days = project['schedule']['variance_days']
        percent_complete = project['schedule']['percent_complete']
        analysis['dimensions']['timeline'] = {
            "status": project['health']['schedule_status'],
            "variance_days": schedule_variance_days,
            "assessment": self._assess_timeline(schedule_variance_days, percent_complete),
            "metrics": {
                "percent_complete": percent_complete,
                "planned_duration": project['schedule']['planned_duration_days'],
                "actual_duration": project['schedule']['actual_duration_days'],
                "milestones": project['schedule']['milestone_completion']
            }
        }
        
        return analysis
    
    def _assess_scope(self, variance, changes):
        """Assess scope health"""
        if variance > 15:
            return f"CRITICAL: Scope has grown {variance:.1f}% with {changes} change requests. Significant scope creep detected."
        elif variance > 5:
            return f"WARNING: Scope variance of {variance:.1f}% with {changes} changes. Monitor closely to prevent further creep."
        else:
            return f"HEALTHY: Scope is well-controlled with only {variance:.1f}% variance."
    
    def _assess_budget(self, variance_pct, spent, total):
        """Assess budget health"""
        utilization = (spent / total) * 100
        
        if variance_pct < -5:
            return f"CRITICAL: Project is {abs(variance_pct):.1f}% over budget. Immediate cost control required."
        elif variance_pct < 0:
            return f"WARNING: Project trending {abs(variance_pct):.1f}% over budget at {utilization:.1f}% utilization."
        else:
            return f"HEALTHY: Budget on track with {variance_pct:.1f}% positive variance."
    
    def _assess_timeline(self, variance_days, completion):
        """Assess timeline health"""
        if variance_days < -20:
            return f"CRITICAL: Project is {abs(variance_days)} days behind schedule at {completion}% completion."
        elif variance_days < -5:
            return f"WARNING: Project is {abs(variance_days)} days behind with {completion}% complete."
        elif variance_days > 5:
            return f"AHEAD: Project is {variance_days} days ahead of schedule."
        else:
            return f"ON TRACK: Project is on schedule with {completion}% completion."
    
    def generate_insights(self):
        """Step 2: Analyze all projects and generate insights"""
        print("\n" + "="*80)
        print("🤖 STEP 2: ANALYZING PORTFOLIO WITH CLAUDE AI")
        print("="*80)
        
        # Analyze each project
        print("\n📊 Analyzing individual projects...")
        project_analyses = []
        for project in self.projects:
            analysis = self.analyze_project_health(project)
            project_analyses.append(analysis)
            print(f"  ✓ {project['name']}: {project['health']['overall_status']}")
        
        # Generate executive insights
        print("\n🧠 Generating executive insights...")
        
        critical_projects = [p for p in self.projects if p['health']['overall_status'] == 'Critical']
        at_risk_projects = [p for p in self.projects if p['health']['overall_status'] == 'At Risk']
        
        # Portfolio-level insights
        insights = {
            "executive_summary": self._generate_executive_summary(),
            "key_concerns": self._identify_key_concerns(critical_projects, at_risk_projects),
            "scope_analysis": self._analyze_portfolio_scope(),
            "budget_analysis": self._analyze_portfolio_budget(),
            "timeline_analysis": self._analyze_portfolio_timeline(),
            "recommendations": self._generate_recommendations(critical_projects, at_risk_projects),
            "project_analyses": project_analyses
        }
        
        print("✅ Analysis complete")
        
        return insights
    
    def _generate_executive_summary(self):
        """Generate executive summary for CEO/executives"""
        ps = self.portfolio_summary
        ph = self.portfolio_health
        
        summary = f"""Portfolio consists of {ps['total_projects']} active projects with a combined budget of ${ps['budget']['total']:,.0f}. 
        
Current Status: {ps['status_distribution']['on_track']} projects on track, {ps['status_distribution']['at_risk']} at risk, and {ps['status_distribution']['critical']} in critical status.

Overall portfolio health score is {ps['average_health_score']:.0f}/100 with average project completion at {ps['average_completion']:.0f}%.

Budget: Portfolio has spent ${ps['budget']['spent']:,.0f} ({ps['budget']['utilization_percentage']:.1f}% utilization) with {ph['budget']['projects_over_budget']} projects currently over budget.

Timeline: Average schedule variance is {ph['schedule']['average_variance_days']:.1f} days with {ph['schedule']['projects_behind']} projects behind schedule.

Scope: {ph['scope']['projects_with_variance']} projects showing significant scope variance (>5%), averaging {ph['scope']['average_variance']:.1f}% variance across portfolio."""
        
        return summary.strip()
    
    def _identify_key_concerns(self, critical, at_risk):
        """Identify top portfolio concerns"""
        concerns = []
        
        if critical:
            concerns.append({
                "severity": "Critical",
                "concern": f"{len(critical)} Critical Projects Requiring Immediate Attention",
                "details": f"Projects in critical status: {', '.join([p['name'] for p in critical])}",
                "action": "Executive review and intervention required within 48 hours"
            })
        
        if at_risk:
            concerns.append({
                "severity": "High",
                "concern": f"{len(at_risk)} Projects At Risk",
                "details": f"At-risk projects: {', '.join([p['name'] for p in at_risk])}",
                "action": "Enhanced monitoring and corrective action plans needed"
            })
        
        budget_issues = [p for p in self.projects if p['budget']['variance'] < -10000]
        if budget_issues:
            concerns.append({
                "severity": "High",
                "concern": "Significant Budget Overruns",
                "details": f"{len(budget_issues)} projects with budget variance exceeding $10K",
                "action": "Financial review and budget reforecast required"
            })
        
        return concerns
    
    def _analyze_portfolio_scope(self):
        """Analyze scope health across portfolio"""
        high_variance = [p for p in self.projects if p['scope']['scope_variance_percentage'] > 10]
        total_changes = sum(p['scope']['scope_changes'] for p in self.projects)
        
        return {
            "summary": f"{len(high_variance)} projects with high scope variance (>10%)",
            "total_scope_changes": total_changes,
            "average_variance": self.portfolio_health['scope']['average_variance'],
            "projects_with_issues": [p['name'] for p in high_variance],
            "recommendation": "Implement stricter change control process" if len(high_variance) > 2 else "Scope management is adequate"
        }
    
    def _analyze_portfolio_budget(self):
        """Analyze budget health across portfolio"""
        over_budget = [p for p in self.projects if p['budget']['variance'] < 0]
        total_variance = sum(p['budget']['variance'] for p in self.projects)
        
        return {
            "summary": f"{len(over_budget)} projects over budget with total variance of ${total_variance:,.0f}",
            "projects_over_budget": len(over_budget),
            "total_variance": total_variance,
            "utilization": self.portfolio_summary['budget']['utilization_percentage'],
            "projects_with_issues": [p['name'] for p in over_budget],
            "recommendation": "Immediate cost control measures needed" if len(over_budget) > 2 else "Budget performance acceptable"
        }
    
    def _analyze_portfolio_timeline(self):
        """Analyze timeline health across portfolio"""
        behind_schedule = [p for p in self.projects if p['schedule']['variance_days'] < -5]
        avg_variance = self.portfolio_health['schedule']['average_variance_days']
        
        return {
            "summary": f"{len(behind_schedule)} projects significantly behind schedule (>5 days)",
            "projects_behind": len(behind_schedule),
            "average_variance_days": avg_variance,
            "projects_with_issues": [p['name'] for p in behind_schedule],
            "recommendation": "Resource reallocation assessment required" if len(behind_schedule) > 2 else "Schedule performance acceptable"
        }
    
    def _generate_recommendations(self, critical, at_risk):
        """Generate strategic recommendations for executives"""
        recommendations = []
        
        if critical:
            recommendations.append({
                "priority": 1,
                "recommendation": "Emergency Portfolio Review",
                "rationale": f"{len(critical)} projects in critical status requiring immediate executive intervention",
                "actions": [
                    "Schedule emergency steering committee meeting within 48 hours",
                    "Develop recovery plans for each critical project",
                    "Assess resource reallocation options",
                    "Determine go/no-go decisions"
                ],
                "timeline": "Immediate (Within 48 hours)"
            })
        
        if len(at_risk) > 1:
            recommendations.append({
                "priority": 2,
                "recommendation": "Enhanced Project Monitoring",
                "rationale": f"{len(at_risk)} at-risk projects need closer oversight",
                "actions": [
                    "Increase reporting frequency to weekly",
                    "Assign executive sponsors to at-risk projects",
                    "Implement early warning indicators",
                    "Review and update risk mitigation plans"
                ],
                "timeline": "Within 1 week"
            })
        
        if self.portfolio_health['budget']['projects_over_budget'] > 2:
            recommendations.append({
                "priority": 3,
                "recommendation": "Portfolio Budget Reforecast",
                "rationale": "Multiple projects over budget indicating systemic estimation issues",
                "actions": [
                    "Conduct comprehensive budget review",
                    "Update forecast-to-complete estimates",
                    "Identify potential funding gaps",
                    "Implement tighter cost controls"
                ],
                "timeline": "Within 2 weeks"
            })
        
        return recommendations
    
    def generate_report(self, insights):
        """Step 3: Generate final report for dashboard"""
        print("\n" + "="*80)
        print("📝 STEP 3: GENERATING EXECUTIVE REPORT")
        print("="*80)
        
        report = {
            "metadata": {
                "report_type": "Weekly Executive Portfolio Health Report",
                "generated_at": datetime.now().isoformat(),
                "generated_by": "Claude Desktop Automation",
                "reporting_period": f"Week of {datetime.now().strftime('%B %d, %Y')}",
                "data_source": "Clarity PPM"
            },
            "portfolio_summary": self.portfolio_summary,
            "portfolio_health": self.portfolio_health,
            "insights": insights,
            "projects": self.projects
        }
        
        # Save report
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/executive_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Report generated: {filename}")
        
        # Also save as latest for dashboard
        latest_filename = f"{OUTPUT_DIR}/latest_report.json"
        with open(latest_filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✅ Latest report saved: {latest_filename}")
        
        return report, filename
    
    def print_summary(self, insights):
        """Print executive summary to console"""
        print("\n" + "="*80)
        print("📊 EXECUTIVE SUMMARY")
        print("="*80)
        
        print("\n" + insights['executive_summary'])
        
        print("\n\n🚨 KEY CONCERNS:")
        for concern in insights['key_concerns']:
            print(f"\n  [{concern['severity']}] {concern['concern']}")
            print(f"  Details: {concern['details']}")
            print(f"  Action: {concern['action']}")
        
        print("\n\n🎯 TOP RECOMMENDATIONS:")
        for rec in insights['recommendations'][:3]:
            print(f"\n  Priority {rec['priority']}: {rec['recommendation']}")
            print(f"  Rationale: {rec['rationale']}")
            print(f"  Timeline: {rec['timeline']}")
        
        print("\n" + "="*80)

def main():
    """Main execution flow"""
    print("\n" + "="*80)
    print("🚀 CLAUDE DESKTOP - CLARITY PPM EXECUTIVE REPORTING")
    print("="*80)
    print("\nThis automation will:")
    print("  1. Fetch project data from Clarity PPM")
    print("  2. Analyze scope, budget, and timeline health")
    print("  3. Generate executive insights and recommendations")
    print("  4. Create dashboard-ready report")
    print("\n")
    
    # Initialize analyzer
    analyzer = ClarityPPMAnalyzer()
    
    # Step 1: Fetch data
    if not analyzer.fetch_data():
        print("\n❌ Failed to fetch data. Exiting.")
        return
    
    # Step 2: Analyze and generate insights
    insights = analyzer.generate_insights()
    
    # Step 3: Generate report
    report, filename = analyzer.generate_report(insights)
    
    # Print summary
    analyzer.print_summary(insights)
    
    print("\n✅ AUTOMATION COMPLETE!")
    print(f"\n💡 Next step: Open the React dashboard and load {filename}")
    print("\n")

if __name__ == "__main__":
    main()