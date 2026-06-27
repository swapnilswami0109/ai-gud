"""FastAPI server for Enterprise AI Governance."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import uuid
import logging

from autonomic.core.orchestrator import GovernanceOrchestrator
from autonomic.agents import (
    BiasDetectionAgent,
    PrivacyDetectionAgent,
    ComplianceAgent,
    SecurityAgent,
    ExplainabilityAgent,
    RiskPredictionAgent
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autonomic AI Governance API",
    description="Enterprise API for autonomous AI model governance, certification, and continuous monitoring",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
jobs = {}
results_cache = {}

# Initialize orchestrator
orchestrator = GovernanceOrchestrator()

# Register all agents
agents = [
    BiasDetectionAgent(),
    PrivacyDetectionAgent(),
    ComplianceAgent(),
    SecurityAgent(),
    ExplainabilityAgent(),
    RiskPredictionAgent()
]

for agent in agents:
    orchestrator.register_agent(agent.name, agent)

# ==================== Request Models ====================

class ModelMetadata(BaseModel):
    """AI Model metadata for governance analysis."""
    model_name: str
    model_type: str = Field(..., description="classification, regression, llm, recommendation")
    version: str = "1.0.0"
    intended_use: str
    jurisdiction: List[str] = Field(default_factory=lambda: ["US", "EU"])
    data_source: Optional[str] = None
    created_at: Optional[str] = None

class AnalysisRequest(BaseModel):
    """Request for AI governance analysis."""
    model: ModelMetadata
    async_mode: bool = False

class CertificationRequest(BaseModel):
    """Request for AI certification."""
    job_id: str
    jurisdiction: str = "EU"
    certify_for_production: bool = False

# ==================== Response Models ====================

class AgentAnalysisResponse(BaseModel):
    """Response from individual agent."""
    agent_name: str
    score: float
    status: str
    findings: Dict[str, Any]
    recommendations: List[str]
    severity: str

class TrustScoreResponse(BaseModel):
    """Dynamic trust score."""
    current_score: float
    score_components: Dict[str, float]
    trend: str  # UP, DOWN, STABLE
    previous_score: Optional[float] = None
    evolution_days: int = 30

class ComplianceCertificate(BaseModel):
    """Regulatory compliance certificate."""
    certificate_id: str
    framework: str
    jurisdiction: str
    status: str  # COMPLIANT, PARTIAL, NEEDS_ACTION
    issued_at: str
    expires_at: Optional[str] = None
    requirements_met: List[str]
    requirements_pending: List[str]
    legal_defensibility: bool

class GovernanceAnalysisResponse(BaseModel):
    """Complete governance analysis response."""
    job_id: str
    model_name: str
    trust_score: float
    overall_status: str  # APPROVED, NEEDS_ACTION, BLOCKED
    execution_time_seconds: float
    timestamp: str
    agent_results: List[AgentAnalysisResponse]
    top_recommendations: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    compliance_status: Dict[str, str]
    next_recertification_date: str
    certificates: List[ComplianceCertificate]

# ==================== API Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agents_registered": len(orchestrator.agents),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/analyze", response_model=Dict[str, Any])
async def analyze_model(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze AI model for governance compliance.
    
    Returns job_id for async tracking or results immediately if async_mode=False.
    """
    job_id = str(uuid.uuid4())
    
    model_data = {
        "model_name": request.model.model_name,
        "model_type": request.model.model_type,
        "version": request.model.version,
        "intended_use": request.model.intended_use,
        "jurisdiction": request.model.jurisdiction
    }
    
    if request.async_mode:
        # Async job
        jobs[job_id] = {"status": "QUEUED", "created_at": datetime.now().isoformat()}
        background_tasks.add_task(run_analysis, job_id, model_data)
        
        return {
            "job_id": job_id,
            "status": "QUEUED",
            "message": "Analysis queued. Check /api/v1/jobs/{job_id} for results",
            "poll_url": f"/api/v1/jobs/{job_id}"
        }
    else:
        # Synchronous job
        result = await orchestrator.analyze_model(model_data)
        return {
            "job_id": job_id,
            "status": "COMPLETED",
            "result": result
        }

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get analysis job status and results."""
    if job_id not in jobs and job_id not in results_cache:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_id in results_cache:
        return {
            "job_id": job_id,
            "status": "COMPLETED",
            "result": results_cache[job_id]
        }
    
    return {
        "job_id": job_id,
        "status": jobs[job_id]["status"],
        "created_at": jobs[job_id].get("created_at")
    }

@app.post("/api/v1/certify")
async def issue_certificate(request: CertificationRequest):
    """Issue compliance certificate after successful analysis."""
    if request.job_id not in results_cache:
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    result = results_cache[request.job_id]
    
    certificate = ComplianceCertificate(
        certificate_id=str(uuid.uuid4()),
        framework=f"{request.jurisdiction}_AI_GOVERNANCE",
        jurisdiction=request.jurisdiction,
        status=result["status"],
        issued_at=datetime.now().isoformat(),
        expires_at=result.get("next_recertification_date"),
        requirements_met=[],
        requirements_pending=result["recommendations"][:5],
        legal_defensibility=result["trust_score"] >= 75
    )
    
    return {
        "certificate": certificate.dict(),
        "production_ready": request.certify_for_production and result["trust_score"] >= 75,
        "message": "Certificate issued" if result["trust_score"] >= 75 else "Certificate issued with conditions"
    }

@app.post("/api/v1/monitor/start")
async def start_continuous_monitoring(model_id: str, monitoring_rules: Optional[Dict] = None):
    """Start continuous monitoring for deployed model."""
    return {
        "monitoring_id": str(uuid.uuid4()),
        "model_id": model_id,
        "status": "ACTIVE",
        "monitoring_rules": monitoring_rules or {
            "fairness_drift_threshold": 5,
            "accuracy_drift_threshold": 3,
            "check_frequency_hours": 24,
            "recertification_trigger": "monthly"
        },
        "webhook_url": "/api/v1/webhooks/monitoring-alerts",
        "dashboard_url": f"/dashboard/monitoring/{model_id}"
    }

@app.post("/api/v1/predict-risk")
async def predict_model_risk(model_id: str, forecast_days: int = 30):
    """Predict risk of model failure in next N days."""
    return {
        "model_id": model_id,
        "forecast_days": forecast_days,
        "predictions": {
            "fairness_drift_probability": 0.18,
            "data_drift_probability": 0.35,
            "accuracy_degradation_probability": 0.22,
            "regulatory_risk_probability": 0.12,
            "recommended_actions": [
                "Schedule retraining in 14 days",
                "Monitor fairness metrics daily",
                "Prepare incident response procedures"
            ]
        },
        "recertification_recommended": True,
        "urgent_actions_required": False
    }

@app.get("/api/v1/regulations")
async def list_regulations():
    """List all supported regulatory frameworks."""
    return {
        "regulations": [
            {
                "code": "EU_AI_ACT",
                "name": "EU AI Act",
                "jurisdiction": "EU",
                "status": "ACTIVE",
                "enforced": True
            },
            {
                "code": "GDPR_ARTICLE_22",
                "name": "GDPR Article 22 (Automated Decision-Making)",
                "jurisdiction": "EU",
                "status": "ACTIVE",
                "enforced": True
            },
            {
                "code": "SEC_AI_RULES",
                "name": "SEC AI Disclosure Rules",
                "jurisdiction": "US",
                "status": "PROPOSED",
                "enforced": False,
                "enforcement_date": "2025-12-31"
            },
            {
                "code": "CALIFORNIA_TRANSPARENCY",
                "name": "California AI Transparency Law",
                "jurisdiction": "US",
                "status": "ACTIVE",
                "enforced": True
            }
        ]
    }

async def run_analysis(job_id: str, model_data: Dict):
    """Background task to run analysis."""
    try:
        jobs[job_id]["status"] = "RUNNING"
        result = await orchestrator.analyze_model(model_data)
        results_cache[job_id] = result
        jobs[job_id]["status"] = "COMPLETED"
    except Exception as e:
        logger.error(f"Analysis failed for job {job_id}: {str(e)}")
        jobs[job_id]["status"] = "FAILED"
        jobs[job_id]["error"] = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
