#!/usr/bin/env python3

import os
import jwt
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'precedent-secret-key-2025')

# Enable CORS for frontend communication
CORS(app, origins=['*'])

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
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if db else 'disconnected'
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username == TEST_USER and password == TEST_PASSWORD:
            token = create_token(username)
            return jsonify({
                'success': True,
                'token': token,
                'username': username
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    """Verify token endpoint"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        username = verify_token(token)
        if username:
            return jsonify({
                'success': True,
                'username': username
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
            
    except Exception as e:
        logger.error(f"Verify error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

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

@app.route('/api/legal/analyze', methods=['POST'])
def analyze_legal_case():
    """Main endpoint for legal analysis"""
    try:
        # Verify authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        username = verify_token(token)
        if not username:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get request data
        data = request.get_json()
        crime_code = data.get('crime_code', '').strip()
        jurisdiction = data.get('jurisdiction', '').strip()
        additional_info = data.get('additional_info', '').strip()
        
        if not crime_code or not jurisdiction:
            return jsonify({
                'error': 'Crime code and jurisdiction are required'
            }), 400
        
        # Process with orchestrator
        result = orchestrator.process_legal_query(crime_code, jurisdiction, additional_info)
        
        # Save analysis to database if available
        if db:
            try:
                analysis_record = {
                    'username': username,
                    'crime_code': crime_code,
                    'jurisdiction': jurisdiction,
                    'additional_info': additional_info,
                    'result': result,
                    'timestamp': datetime.utcnow()
                }
                db.analyses.insert_one(analysis_record)
            except Exception as e:
                logger.warning(f"Failed to save analysis to database: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({
            'error': 'Failed to process legal analysis',
            'details': str(e)
        }), 500

@app.route('/api/legal/confirm', methods=['POST'])
def confirm_analysis():
    """Confirm analysis details with user"""
    try:
        # Verify authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
            
        token = auth_header.split(' ')[1]
        username = verify_token(token)
        if not username:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        data = request.get_json()
        crime_code = data.get('crime_code')
        jurisdiction = data.get('jurisdiction')
        additional_info = data.get('additional_info')
        
        # Generate confirmation summary
        confirmation = {
            'summary': f"I understand you're asking about {crime_code} in {jurisdiction}.",
            'key_details': [
                f"Crime/Penal Code: {crime_code}",
                f"Jurisdiction: {jurisdiction}",
                f"Additional information provided: {'Yes' if additional_info else 'No'}"
            ],
            'questions': [
                "Is this the correct crime code you're asking about?",
                "Is this the right jurisdiction (city, county, or state)?",
                "Have you provided all relevant details about your situation?"
            ],
            'next_steps': "If this information is correct, I'll analyze your case using our Legal Decompiler, Analytics Engine, and Precedent Explorer."
        }
        
        return jsonify(confirmation)
        
    except Exception as e:
        logger.error(f"Confirmation error: {e}")
        return jsonify({
            'error': 'Failed to generate confirmation',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=True)