#!/usr/bin/env python3

import os
import jwt
import hashlib
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="PRECEDENT Legal Research API", version="1.0.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secret key for JWT
SECRET_KEY = os.environ.get('SECRET_KEY', 'precedent-secret-key-2025')

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenRequest(BaseModel):
    token: str

class LegalAnalysisRequest(BaseModel):
    crime_code: str
    jurisdiction: str
    additional_info: str = ""

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    username: Optional[str] = None
    message: Optional[str] = None

class VerifyResponse(BaseModel):
    success: bool
    username: Optional[str] = None
    message: Optional[str] = None

# MongoDB connection
try:
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/precedent')
    client = MongoClient(mongo_url)
    db = client.precedent
    logger.info(f"Connected to MongoDB at {mongo_url}")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")
    db = None

# Test credentials
TEST_USER = "onebaldegg"
TEST_PASSWORD = "4life"

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(username):
    """Create JWT token for user"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current user from token"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization required"
        )
    
    token = authorization.split(' ')[1]
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return username

# Routes
@app.get('/api/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if db is not None else 'disconnected'
    }

@app.post('/api/auth/login', response_model=LoginResponse)
def login(request: LoginRequest):
    """User login endpoint"""
    try:
        if request.username == TEST_USER and request.password == TEST_PASSWORD:
            token = create_token(request.username)
            return LoginResponse(
                success=True,
                token=token,
                username=request.username
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post('/api/auth/verify', response_model=VerifyResponse)
def verify(request: TokenRequest):
    """Verify token endpoint"""
    try:
        username = verify_token(request.token)
        if username:
            return VerifyResponse(
                success=True,
                username=username
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Multi-Agent AI System Routes (Mock Implementation)
class ParalegalOrchestrator:
    """Central orchestrator for legal analysis"""
    
    def __init__(self):
        self.legal_decompiler = LegalDecompilerAgent()
        self.analytics_engine = AnalyticsEngineAgent()
        self.precedent_explorer = PrecedentExplorerAgent()
    
    def process_legal_query(self, crime_code, jurisdiction, additional_info):
        """Process legal query using all agents"""
        try:
            # Step 1: Decompose legal code
            legal_explanation = self.legal_decompiler.explain_crime(crime_code, jurisdiction)
            
            # Step 2: Generate analytics
            analytics = self.analytics_engine.analyze_case(crime_code, jurisdiction, additional_info)
            
            # Step 3: Find relevant precedents
            precedents = self.precedent_explorer.find_cases(crime_code, jurisdiction, additional_info)
            
            # Step 4: Synthesize response
            return {
                'legal_explanation': legal_explanation,
                'analytics': analytics,
                'precedents': precedents,
                'summary': self._generate_summary(legal_explanation, analytics, precedents)
            }
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                'error': 'Failed to process legal query',
                'details': str(e)
            }
    
    def _generate_summary(self, explanation, analytics, precedents):
        """Generate executive summary"""
        return {
            'key_points': [
                f"Crime: {explanation['crime_name']}",
                f"Severity: {explanation['severity']}",
                f"Most common defense: {analytics['common_defenses'][0]['strategy'] if analytics['common_defenses'] else 'None identified'}",
                f"Success rate: {analytics['success_rates']['dismissal']}%",
                f"Relevant cases found: {len(precedents['cases'])}"
            ],
            'recommended_actions': [
                "Consult with a qualified attorney",
                "Review similar case outcomes in your jurisdiction",
                "Consider common defense strategies",
                "Gather evidence to support your case"
            ]
        }

class LegalDecompilerAgent:
    """Agent for explaining legal codes in plain language"""
    
    def explain_crime(self, crime_code, jurisdiction):
        """Explain crime in simple terms"""
        # Mock responses - will be replaced with real API
        mock_explanations = {
            "DUI": {
                "crime_name": "Driving Under the Influence (DUI)",
                "simple_explanation": "This means driving a car when you've had too much alcohol or drugs. It's like trying to ride a bike when you're dizzy - it's dangerous and not allowed.",
                "what_prosecution_must_prove": [
                    "You were driving or in control of a vehicle",
                    "You had alcohol or drugs in your system above the legal limit",
                    "Your ability to drive safely was impaired"
                ],
                "penalties": {
                    "first_offense": {
                        "fines": "$390 - $2000+ (with fees)",
                        "jail_time": "Up to 6 months",
                        "license_suspension": "4 months to 1 year",
                        "programs": "DUI education program (3-9 months)"
                    }
                },
                "severity": "Misdemeanor (first offense)",
                "legal_process": [
                    "Arrest and booking",
                    "DMV hearing (within 10 days to challenge license suspension)",
                    "Arraignment (first court appearance)",
                    "Pre-trial conference",
                    "Trial or plea agreement"
                ]
            },
            "ASSAULT": {
                "crime_name": "Assault",
                "simple_explanation": "This means threatening to hurt someone or actually touching them in a way they don't want. It's like when someone raises their hand to hit you, even if they don't actually do it.",
                "what_prosecution_must_prove": [
                    "You intended to cause harmful or offensive contact",
                    "You had the ability to carry out the threat",
                    "The victim reasonably feared immediate harm"
                ],
                "penalties": {
                    "misdemeanor": {
                        "fines": "Up to $1000",
                        "jail_time": "Up to 6 months",
                        "probation": "Up to 3 years"
                    }
                },
                "severity": "Misdemeanor or Felony (depending on circumstances)",
                "legal_process": [
                    "Arrest and booking",
                    "Arraignment",
                    "Pre-trial conference",
                    "Trial or plea agreement"
                ]
            }
        }
        
        # Extract crime type from code
        crime_type = self._extract_crime_type(crime_code)
        
        if crime_type in mock_explanations:
            explanation = mock_explanations[crime_type].copy()
            explanation['jurisdiction'] = jurisdiction
            explanation['code'] = crime_code
            return explanation
        else:
            return {
                "crime_name": f"Criminal Code {crime_code}",
                "simple_explanation": "This is a crime that breaks the law in your area. Like breaking a rule at school, but more serious because it affects other people's safety or rights.",
                "what_prosecution_must_prove": [
                    "You committed the specific acts described in the law",
                    "You did so intentionally or recklessly",
                    "The acts meet all elements of the crime"
                ],
                "penalties": {
                    "general": {
                        "fines": "Varies by jurisdiction",
                        "jail_time": "Varies by severity",
                        "other": "May include probation, community service, or other requirements"
                    }
                },
                "severity": "To be determined based on specific code",
                "legal_process": [
                    "Investigation",
                    "Arrest (if applicable)",
                    "Court proceedings",
                    "Resolution"
                ],
                "jurisdiction": jurisdiction,
                "code": crime_code
            }
    
    def _extract_crime_type(self, crime_code):
        """Extract crime type from code"""
        code_upper = crime_code.upper()
        if 'DUI' in code_upper or '23152' in code_upper:
            return 'DUI'
        elif 'ASSAULT' in code_upper or '240' in code_upper:
            return 'ASSAULT'
        else:
            return 'UNKNOWN'

class AnalyticsEngineAgent:
    """Agent for generating statistical insights"""
    
    def analyze_case(self, crime_code, jurisdiction, additional_info):
        """Generate analytics for the case"""
        # Mock analytics data
        return {
            'jurisdiction_stats': {
                'total_cases_last_year': 1247,
                'conviction_rate': 73.2,
                'average_sentence_days': 45,
                'average_fine': 1850
            },
            'common_defenses': [
                {
                    'strategy': 'Challenge traffic stop legality',
                    'success_rate': 35.4,
                    'frequency': 68.2
                },
                {
                    'strategy': 'Question test accuracy',
                    'success_rate': 28.7,
                    'frequency': 45.1
                },
                {
                    'strategy': 'Field sobriety test issues',
                    'success_rate': 22.3,
                    'frequency': 38.9
                }
            ],
            'success_rates': {
                'dismissal': 24.3,
                'reduction_to_lesser': 31.7,
                'full_conviction': 44.0
            },
            'judicial_patterns': {
                'average_fine_by_judge': {
                    'Judge Smith': 1650,
                    'Judge Johnson': 1950,
                    'Judge Williams': 1750
                },
                'sentencing_variations': {
                    'first_offense': 'Usually probation + fine',
                    'repeat_offense': 'Jail time more likely',
                    'high_bac': 'Enhanced penalties'
                }
            },
            'timing_factors': {
                'case_duration_average_days': 89,
                'best_plea_timing': 'Pre-trial conference',
                'trial_vs_plea_rates': {
                    'plea_bargain': 82.1,
                    'trial': 17.9
                }
            }
        }

class PrecedentExplorerAgent:
    """Agent for finding relevant case law"""
    
    def find_cases(self, crime_code, jurisdiction, additional_info):
        """Find relevant precedent cases"""
        # Mock case law data
        return {
            'total_cases_found': 23,
            'cases': [
                {
                    'case_name': 'People v. Martinez (2023)',
                    'jurisdiction': jurisdiction,
                    'relevance_score': 94.2,
                    'key_issue': 'Breathalyzer calibration errors',
                    'outcome': 'Dismissed - evidence suppressed',
                    'summary': 'Court found breathalyzer machine not properly calibrated, making BAC reading inadmissible.',
                    'legal_principle': 'Evidence obtained through faulty equipment violates due process',
                    'citation': '2023 Cal. App. 4th 156'
                },
                {
                    'case_name': 'State v. Thompson (2022)', 
                    'jurisdiction': jurisdiction,
                    'relevance_score': 87.6,
                    'key_issue': 'Illegal traffic stop',
                    'outcome': 'Evidence suppressed',
                    'summary': 'Officer lacked reasonable suspicion for initial traffic stop. All subsequent evidence excluded.',
                    'legal_principle': 'Fourth Amendment protections against unreasonable searches',
                    'citation': '2022 Cal. App. 3rd 289'
                },
                {
                    'case_name': 'People v. Rodriguez (2023)',
                    'jurisdiction': jurisdiction,
                    'relevance_score': 82.1,
                    'key_issue': 'Field sobriety test reliability',
                    'outcome': 'Conviction upheld',
                    'summary': 'Court found field sobriety tests properly administered despite defendant medical condition claims.',
                    'legal_principle': 'FST reliability when properly conducted',
                    'citation': '2023 Cal. App. 2nd 445'
                }
            ],
            'search_strategy': {
                'keywords_used': ['DUI', jurisdiction, 'breathalyzer', 'traffic stop'],
                'databases_searched': ['Westlaw (mock)', 'LexisNexis (mock)', 'Google Scholar'],
                'filters_applied': [
                    'Jurisdiction: ' + jurisdiction,
                    'Date range: 2020-2024',
                    'Case type: Criminal'
                ]
            },
            'related_statutes': [
                {
                    'code': 'Vehicle Code § 23152(b)',
                    'title': 'Driving with 0.08% or higher BAC',
                    'relevance': 'Primary statute'
                },
                {
                    'code': 'Penal Code § 1538.5',
                    'title': 'Motion to suppress evidence',
                    'relevance': 'Common defense motion'
                }
            ]
        }

# Initialize orchestrator
orchestrator = ParalegalOrchestrator()

def count_words(text):
    """Count words in text"""
    if not text or text.strip() == '':
        return 0
    return len(text.strip().split())

@app.post('/api/legal/analyze')
def analyze_legal_case(request: LegalAnalysisRequest, current_user: str = Depends(get_current_user)):
    """Main endpoint for legal analysis"""
    try:
        if not request.crime_code or not request.jurisdiction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crime code and jurisdiction are required"
            )
        
        # Validate word count for additional_info
        if request.additional_info and count_words(request.additional_info) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Additional information must be 1000 words or less"
            )
        
        # Process with orchestrator
        result = orchestrator.process_legal_query(
            request.crime_code, 
            request.jurisdiction, 
            request.additional_info
        )
        
        # Save analysis to database if available
        if db is not None:
            try:
                analysis_record = {
                    'username': current_user,
                    'crime_code': request.crime_code,
                    'jurisdiction': request.jurisdiction,
                    'additional_info': request.additional_info,
                    'result': result,
                    'timestamp': datetime.utcnow()
                }
                db.analyses.insert_one(analysis_record)
            except Exception as e:
                logger.warning(f"Failed to save analysis to database: {e}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process legal analysis"
        )

@app.post('/api/legal/confirm')
def confirm_analysis(request: LegalAnalysisRequest, current_user: str = Depends(get_current_user)):
    """Confirm analysis details with user"""
    try:
        # Generate confirmation summary
        confirmation = {
            'summary': f"I understand you're asking about {request.crime_code} in {request.jurisdiction}.",
            'key_details': [
                f"Crime/Penal Code: {request.crime_code}",
                f"Jurisdiction: {request.jurisdiction}",
                f"Additional information provided: {'Yes' if request.additional_info else 'No'}"
            ],
            'questions': [
                "Is this the correct crime code you're asking about?",
                "Is this the right jurisdiction (city, county, or state)?",
                "Have you provided all relevant details about your situation?"
            ],
            'next_steps': "If this information is correct, I'll analyze your case using our Legal Decompiler, Analytics Engine, and Precedent Explorer."
        }
        
        return confirmation
        
    except Exception as e:
        logger.error(f"Confirmation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate confirmation"
        )

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8001))
    uvicorn.run(app, host='0.0.0.0', port=port)