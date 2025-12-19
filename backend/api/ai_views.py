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
    """
    Sends a prompt to the Google Gemini API and returns the response.

    This function checks for the availability of the Gemini API and the API key
    before making a request. It uses the 'gemini-2.0-flash-exp' model.

    Args:
        prompt (str): The prompt to send to the Gemini API.

    Returns:
        dict: A dictionary containing either the 'result' from the API or an 'error' message.
    """
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
    Analyzes a compliance checklist using the Gemini AI.

    This endpoint expects a 'checklist' in the request data and returns
    an AI-generated analysis of it.

    Args:
        request (Request): The request object, containing the checklist data.

    Returns:
        Response: A response object with the AI's analysis or an error.
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
    Categorizes a list of compliance indicators using the Gemini AI.

    This endpoint expects a list of 'indicators' in the request data and
    returns AI-generated categories for them.

    Args:
        request (Request): The request object, containing the indicators list.

    Returns:
        Response: A response object with the AI's categorization or an error.
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
    Answers a compliance-related question using the Gemini AI.

    This endpoint expects a 'question' in the request data and returns a
    detailed answer from the AI assistant.

    Args:
        request (Request): The request object, containing the user's question.

    Returns:
        Response: A response object with the AI's answer or an error.
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
    Generates a summary report from compliance data using the Gemini AI.

    This endpoint expects 'data' in the request data and returns a
    comprehensive summary report.

    Args:
        request (Request): The request object, containing the compliance data.

    Returns:
        Response: A response object with the AI-generated summary or an error.
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
    Converts document content to a specified format using the Gemini AI.

    This endpoint expects 'content' and an optional 'target_format' in the
    request data.

    Args:
        request (Request): The request object, containing the document content
                         and target format.

    Returns:
        Response: A response object with the converted document or an error.
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
    Generates a compliance guide for a standard or regulation using the Gemini AI.

    This endpoint expects a 'standard' name in the request data.

    Args:
        request (Request): The request object, containing the standard name.

    Returns:
        Response: A response object with the AI-generated guide or an error.
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
    Analyzes a list of tasks and provides optimization recommendations using the Gemini AI.

    This endpoint expects a list of 'tasks' in the request data.

    Args:
        request (Request): The request object, containing the list of tasks.

    Returns:
        Response: A response object with the AI's analysis or an error.
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