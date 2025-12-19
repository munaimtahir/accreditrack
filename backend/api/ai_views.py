"""
AI endpoints using Google Gemini API for compliance assistance.
"""
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

# Import Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def get_gemini_response(prompt):
    """Helper function to get response from Gemini API."""
    if not GEMINI_AVAILABLE:
        return {"error": "Gemini API is not available. Please install google-generativeai package."}
    
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return {"error": "GEMINI_API_KEY is not configured."}
    
    try:
        genai.configure(api_key=api_key)
        # Use Gemini 2.0 Flash model for faster and more efficient responses
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception as e:
        return {"error": f"Gemini API error: {str(e)}"}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_checklist(request):
    """
    Analyze a compliance checklist and provide insights.
    
    Expected input: { "checklist": "text or structured data" }
    """
    checklist_data = request.data.get('checklist', '')
    
    if not checklist_data:
        return Response(
            {"error": "Checklist data is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    prompt = f"""
    As a compliance expert, analyze the following checklist and provide:
    1. Key compliance areas identified
    2. Potential gaps or missing requirements
    3. Priority recommendations
    
    Checklist:
    {checklist_data}
    """
    
    result = get_gemini_response(prompt)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_categorization(request):
    """
    Categorize indicators into logical groups.
    
    Expected input: { "indicators": ["list", "of", "indicators"] }
    """
    indicators = request.data.get('indicators', [])
    
    if not indicators:
        return Response(
            {"error": "Indicators list is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    prompt = f"""
    Categorize the following compliance indicators into logical groups:
    
    Indicators:
    {chr(10).join(f'- {ind}' for ind in indicators)}
    
    Provide categories with explanations.
    """
    
    result = get_gemini_response(prompt)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_assistant(request):
    """
    Ask the AI assistant a compliance-related question.
    
    Expected input: { "question": "your question here" }
    """
    question = request.data.get('question', '')
    
    if not question:
        return Response(
            {"error": "Question is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    prompt = f"""
    As a compliance and accreditation expert for medical institutions, laboratories, and universities,
    answer the following question:
    
    Question: {question}
    
    Provide a detailed, accurate, and helpful answer.
    """
    
    result = get_gemini_response(prompt)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_summary(request):
    """
    Generate a summary report from compliance data.
    
    Expected input: { "data": "compliance data to summarize" }
    """
    data = request.data.get('data', '')
    
    if not data:
        return Response(
            {"error": "Data is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    prompt = f"""
    Create a comprehensive summary report for the following compliance data:
    
    Data:
    {data}
    
    Include:
    1. Executive summary
    2. Key findings
    3. Compliance status
    4. Recommendations
    """
    
    result = get_gemini_response(prompt)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convert_document(request):
    """
    Convert documents between formats or extract information.
    
    Expected input: { "content": "document content", "target_format": "desired format" }
    """
    content = request.data.get('content', '')
    target_format = request.data.get('target_format', 'structured')
    
    if not content:
        return Response(
            {"error": "Content is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    prompt = f"""
    Convert the following document to {target_format} format:
    
    Content:
    {content}
    
    Ensure all important information is preserved.
    """
    
    result = get_gemini_response(prompt)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compliance_guide(request):
    """
    Generate a compliance guide for a specific standard or regulation.
    
    Expected input: { "standard": "name of standard/regulation" }
    """
    standard = request.data.get('standard', '')
    
    if not standard:
        return Response(
            {"error": "Standard/regulation name is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    prompt = f"""
    Create a comprehensive compliance guide for the {standard} standard/regulation.
    
    Include:
    1. Overview and purpose
    2. Key requirements
    3. Implementation steps
    4. Common pitfalls
    5. Best practices
    """
    
    result = get_gemini_response(prompt)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_tasks(request):
    """
    Analyze tasks and provide optimization recommendations.
    
    Expected input: { "tasks": ["task1", "task2", ...] }
    """
    tasks = request.data.get('tasks', [])
    
    if not tasks:
        return Response(
            {"error": "Tasks list is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    prompt = f"""
    Analyze the following compliance tasks and provide:
    1. Priority ranking
    2. Dependencies
    3. Time estimates
    4. Resource recommendations
    
    Tasks:
    {chr(10).join(f'- {task}' for task in tasks)}
    """
    
    result = get_gemini_response(prompt)
    return Response(result)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def evidence_assistance(request, indicator_id=None):
    """
    Get AI assistance for evidence collection for a specific indicator.
    
    GET: Get all assistance options
    POST: Get specific assistance type
    
    Expected input for POST:
    {
        "indicator_id": 123,
        "assistance_type": "suggestions" | "sop" | "form" | "gaps" | "requirements"
    }
    """
    from .models import Indicator
    from .ai_evidence_service import (
        analyze_indicator_evidence_requirements,
        generate_evidence_suggestions,
        draft_sop_or_policy,
        suggest_digital_form,
        explain_compliance_gaps
    )
    
    if request.method == 'GET':
        indicator_id = request.query_params.get('indicator_id')
    
    if request.method == 'POST':
        indicator_id = request.data.get('indicator_id')
    
    if not indicator_id:
        return Response(
            {"error": "indicator_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        indicator = Indicator.objects.get(pk=indicator_id)
    except Indicator.DoesNotExist:
        return Response(
            {"error": "Indicator not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    assistance_type = request.data.get('assistance_type', 'suggestions') if request.method == 'POST' else 'suggestions'
    
    if assistance_type == 'requirements':
        result = analyze_indicator_evidence_requirements(indicator)
    elif assistance_type == 'suggestions':
        suggestions = generate_evidence_suggestions(indicator)
        result = {'suggestions': suggestions}
    elif assistance_type == 'sop':
        doc_type = request.data.get('document_type', 'SOP')
        result = draft_sop_or_policy(indicator, doc_type)
    elif assistance_type == 'form':
        result = suggest_digital_form(indicator)
    elif assistance_type == 'gaps':
        result = explain_compliance_gaps(indicator)
    else:
        return Response(
            {"error": f"Unknown assistance_type: {assistance_type}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response(result)