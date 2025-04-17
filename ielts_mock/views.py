from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.db.models import Max, Min, Avg

from .models import MockTest, TestQuestion, ImprovementPlan, WritingPractice
from .gpt_service import GPTService
from core.models import UserProfile

import json
import uuid
import random
import os
import base64
import tempfile
import datetime
import logging
import pdfkit

logger = logging.getLogger(__name__)

@login_required
def mock_test_home(request):
    """Home page for the IELTS mock test"""
    # Get user's tests
    user_tests = MockTest.objects.filter(user=request.user).order_by('-created_at')

    # Get user's coin balance
    try:
        profile = request.user.profile
        coins = profile.coins
    except:
        coins = 0

    context = {
        'user_tests': user_tests,
        'coins': coins,
        'active_page': 'ielts_mock'
    }

    return render(request, 'ielts_mock/home.html', context)

@login_required
def start_test(request):
    """Start a new IELTS mock test"""
    if request.method == 'POST':
        test_type = request.POST.get('test_type', 'academic')

        # Check if user has enough coins (100 coins per test)
        try:
            profile = request.user.profile
            if profile.coins < 100:
                messages.error(request, "You don't have enough coins. You need 100 coins to take a mock test.")
                return redirect('mock_test_home')

            # Deduct coins
            profile.coins -= 100
            profile.save()
        except:
            messages.error(request, "Error checking coin balance. Please try again.")
            return redirect('mock_test_home')

        # Create a new test
        test = MockTest.objects.create(
            user=request.user,
            test_type=test_type,
            status='not_started'
        )

        # Generate test content using GPT
        gpt_service = GPTService()

        # Generate reading content
        reading_content = gpt_service.generate_reading_test(test_type)
        test.reading_content = reading_content

        # Generate listening content
        listening_content = gpt_service.generate_listening_test(test_type)
        test.listening_content = listening_content

        # Generate writing content
        writing_content = gpt_service.generate_writing_test(test_type)
        test.writing_content = writing_content

        # Update test status
        test.status = 'in_progress'
        test.started_at = timezone.now()
        test.save()

        # Create TestQuestion objects for each question
        create_test_questions(test)

        # No longer need to generate audio files
        # The scripts will be used directly for browser text-to-speech

        # Redirect to reading test
        return redirect('reading_test', test_id=test.id)

    return render(request, 'ielts_mock/start_test.html')

# Remove or comment out the generate_listening_audio function since we won't be using it anymore
# def generate_listening_audio(test):
#     """Generate audio files for listening section using gTTS"""
#     ...

def create_test_questions(test):
    """Create TestQuestion objects for each question in the test"""
    # Create reading questions
    if test.reading_content and 'sections' in test.reading_content:
        for section_idx, section in enumerate(test.reading_content['sections']):
            for question_idx, question in enumerate(section.get('questions', [])):
                TestQuestion.objects.create(
                    test=test,
                    section_type='reading',
                    section_number=section_idx + 1,
                    question_number=question.get('id'),
                    question_type=question.get('type', 'other'),
                    question_text=question.get('text', ''),
                    options=question.get('options'),
                    correct_answer=question.get('answer', '')
                )

    # Create listening questions
    if test.listening_content and 'sections' in test.listening_content:
        for section_idx, section in enumerate(test.listening_content['sections']):
            for question_idx, question in enumerate(section.get('questions', [])):
                TestQuestion.objects.create(
                    test=test,
                    section_type='listening',
                    section_number=section_idx + 1,
                    question_number=question.get('id'),
                    question_type=question.get('type', 'other'),
                    question_text=question.get('text', ''),
                    options=question.get('options') if 'options' in question else None,
                    correct_answer=question.get('answer', '')
                )

# Since we're using browser-based text-to-speech, we need to keep this function
# for backward compatibility with existing URLs, but it will just return an error message
@login_required
def get_listening_audio(request, test_id, section_number):
    """Inform the user that audio files are no longer served from the server"""
    return HttpResponse(
        "This endpoint is no longer in use. The application now uses browser-based text-to-speech for listening tests.",
        content_type="text/plain"
    )

def get_fallback_reading_content():
    """Provide fallback reading content when database content is missing or invalid"""
    return {
        'sections': [
            {
                'title': 'The Impact of Urbanization on Biodiversity',
                'passage': """<p>Urbanization has become one of the most significant environmental changes of the past century. As cities expand, natural habitats are destroyed, leading to a decline in biodiversity. Many species are unable to adapt to the rapid changes in their environment, resulting in extinction. Studies have shown that urban areas often support fewer species than their rural counterparts. However, some species thrive in urban settings, demonstrating resilience and adaptability. For instance, birds and certain mammals have adapted to urban life by altering their behaviors and diets. Furthermore, urban green spaces, such as parks and gardens, can provide refuge for various species, promoting biodiversity in metropolitan areas. Despite the negative impacts of urbanization, sustainable city planning can help mitigate these effects, allowing for the coexistence of urban development and biodiversity conservation.</p>""",
                'questions': [
                    {
                        'id': 1,
                        'type': 'true_false_not_given',
                        'text': 'Urbanization has no effect on biodiversity.',
                        'options': ['TRUE', 'FALSE', 'NOT GIVEN'],
                        'answer': 'FALSE'
                    },
                    {
                        'id': 2,
                        'type': 'multiple_choice',
                        'text': 'What is a consequence of urbanization mentioned in the passage?',
                        'options': ['Increase in species diversity', 'Destruction of natural habitats', 'Improvement of urban green spaces', 'Growth of rural areas'],
                        'answer': 'Destruction of natural habitats'
                    },
                    {
                        'id': 3,
                        'type': 'true_false_not_given',
                        'text': 'Some species can thrive in urban environments.',
                        'options': ['TRUE', 'FALSE', 'NOT GIVEN'],
                        'answer': 'TRUE'
                    }
                ]
            },
            {
                'title': 'The Future of Renewable Energy',
                'passage': """<p>The transition to renewable energy is crucial for combating climate change and ensuring a sustainable future. As fossil fuels deplete and their environmental impact becomes increasingly evident, countries worldwide are investing in alternatives such as solar, wind, and hydroelectric power. These energy sources are not only sustainable but also provide opportunities for job creation in the green energy sector. Innovations in technology have led to more efficient energy systems, reducing costs and increasing accessibility. However, challenges remain, including the need for infrastructure development and energy storage solutions. Governments, industries, and communities must collaborate to overcome these obstacles and accelerate the shift toward a renewable energy future. Public awareness and education play vital roles in fostering support for renewable energy initiatives, making it essential to inform and engage citizens in the transition.</p>""",
                'questions': [
                    {
                        'id': 4,
                        'type': 'true_false_not_given',
                        'text': 'Renewable energy is important for fighting climate change.',
                        'options': ['TRUE', 'FALSE', 'NOT GIVEN'],
                        'answer': 'TRUE'
                    },
                    {
                        'id': 5,
                        'type': 'multiple_choice',
                        'text': 'What is a consequence of depleting fossil fuels?',
                        'options': ['Increased emissions', 'Investment in renewable energy', 'Job losses', 'Reduced energy consumption'],
                        'answer': 'Investment in renewable energy'
                    },
                    {
                        'id': 6,
                        'type': 'true_false_not_given',
                        'text': 'Renewable energy sources are only solar and wind.',
                        'options': ['TRUE', 'FALSE', 'NOT GIVEN'],
                        'answer': 'FALSE'
                    }
                ]
            }
        ]
    }

@login_required
def reading_test(request, test_id):
    """Display the reading section of the IELTS mock test"""
    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # If test is completed, redirect to results
    if test.status == 'completed':
        return redirect('test_results', test_id=test.id)

    # Get reading content
    reading_content = test.get_reading_content()

    # Debug logging
    logger.debug(f"Reading content structure: {reading_content}")

    # Check if reading_content has the expected structure and data
    has_valid_content = (
            reading_content and
            'sections' in reading_content and
            reading_content['sections'] and
            all('passage' in section for section in reading_content['sections'])
    )

    if not has_valid_content:
        logger.warning(f"Invalid or missing reading content for test {test_id}. Using fallback content.")
        reading_content = get_fallback_reading_content()

    # Prepare the data in the format expected by the template
    passages = []
    questions = []

    # Extract passages and questions from sections
    for section_idx, section in enumerate(reading_content.get('sections', [])):
        # Add passage
        passage = {
            'section': section_idx + 1,
            'title': section.get('title', f'Section {section_idx + 1}'),
            'content': section.get('passage', '')
        }
        passages.append(passage)

        # Add questions
        section_questions = section.get('questions', [])
        for question in section_questions:
            question['section_number'] = section_idx + 1
            questions.append(question)

    # Create a properly structured reading_content for the template
    formatted_reading_content = {
        'passages': passages,
        'questions': questions
    }

    context = {
        'test': test,
        'reading_content': formatted_reading_content,
        'time_limit': 60,  # 60 minutes for reading test
        'active_page': 'ielts_mock'
    }

    return render(request, 'ielts_mock/reading_test.html', context)

@login_required
def listening_test(request, test_id):
    """Display the listening section of the IELTS mock test"""
    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # If test is completed, redirect to results
    if test.status == 'completed':
        return redirect('test_results', test_id=test.id)

    # Get listening content
    listening_content = test.get_listening_content()

    # Extract scripts for each section to pass to the template
    section_scripts = []
    if listening_content and 'sections' in listening_content:
        for section in listening_content['sections']:
            section_scripts.append(section.get('script', ''))

    context = {
        'test': test,
        'listening_content': listening_content,
        'section_scripts': section_scripts,  # Pass the scripts to the template
        'test_id': test_id,
        'active_page': 'ielts_mock'
    }

    return render(request, 'ielts_mock/listening_test.html', context)

@login_required
def writing_test(request, test_id):
    """Display the writing section of the IELTS mock test"""
    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # If test is completed, redirect to results
    if test.status == 'completed':
        return redirect('test_results', test_id=test.id)

    # Get writing content
    writing_content = test.get_writing_content()

    context = {
        'test': test,
        'writing_content': writing_content,
        'active_page': 'ielts_mock'
    }

    return render(request, 'ielts_mock/writing_test.html', context)

@login_required
@csrf_exempt
def submit_reading(request, test_id):
    """Submit answers for the reading section"""
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # Get responses from form
    responses = {}
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            responses[question_id] = value

    # Save responses
    test.save_reading_responses(responses)

    # Update TestQuestion objects with user answers
    for question_id, answer in responses.items():
        try:
            # Find questions by test, section_type, and question_number
            questions = TestQuestion.objects.filter(
                test=test,
                section_type='reading',
                question_number=int(question_id)
            )

            # If multiple questions found, update all of them
            # This can happen if question IDs are not unique across sections
            for question in questions:
                question.user_answer = answer
                question.check_answer()
        except Exception as e:
            print(f"Error updating question {question_id}: {str(e)}")

    # Calculate score
    reading_score = test.calculate_reading_score()
    test.reading_score = reading_score
    test.save()

    # Redirect to listening test
    return redirect('listening_test', test_id=test.id)

@login_required
@csrf_exempt
def submit_listening(request, test_id):
    """Submit answers for the listening section"""
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # Get responses from form
    responses = {}
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            responses[question_id] = value

    # Save responses
    test.save_listening_responses(responses)

    # Update TestQuestion objects with user answers
    for question_id, answer in responses.items():
        try:
            # Find questions by test, section_type, and question_number
            questions = TestQuestion.objects.filter(
                test=test,
                section_type='listening',
                question_number=int(question_id)
            )

            # If multiple questions found, update all of them
            # This can happen if question IDs are not unique across sections
            for question in questions:
                question.user_answer = answer
                question.check_answer()
        except Exception as e:
            print(f"Error updating question {question_id}: {str(e)}")

    # Calculate score
    listening_score = test.calculate_listening_score()
    test.listening_score = listening_score
    test.save()

    # Redirect to writing test
    return redirect('writing_test', test_id=test.id)

@login_required
@csrf_exempt
def submit_writing(request, test_id):
    """Submit answers for the writing section"""
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # Get responses from form
    task1_response = request.POST.get('task1_response', '')
    task2_response = request.POST.get('task2_response', '')

    # Save responses
    writing_responses = {
        'task1': task1_response,
        'task2': task2_response
    }
    test.save_writing_responses(writing_responses)

    # Evaluate writing using GPT
    gpt_service = GPTService()
    writing_content = test.get_writing_content()

    # Evaluate Task 1
    task1_prompt = writing_content.get('task1', {}).get('instructions', '')
    task1_evaluation = gpt_service.evaluate_writing(task1_prompt, task1_response)

    # Evaluate Task 2
    task2_prompt = writing_content.get('task2', {}).get('instructions', '')
    task2_evaluation = gpt_service.evaluate_writing(task2_prompt, task2_response)

    # Calculate overall writing score
    writing_score = (task1_evaluation.get('overall_score', 0) + task2_evaluation.get('overall_score', 0)) / 2
    test.writing_score = writing_score

    # Save feedback
    feedback = {
        'task1': task1_evaluation,
        'task2': task2_evaluation
    }
    test.feedback = feedback

    # For demo purposes, generate a random speaking score
    # In a real implementation, this would come from a speaking test
    test.speaking_score = round(random.uniform(5.0, 8.0) * 2) / 2

    # Calculate overall score
    test.overall_score = test.calculate_overall_score()

    # Perform final analysis
    test.finalize_results()

    # Create improvement plan
    create_improvement_plan(test)

    # Mark test as completed
    test.status = 'completed'
    test.completed_at = timezone.now()
    test.save()

    # Redirect to results page
    return redirect('test_results', test_id=test.id)

def create_improvement_plan(test):
    """Create a personalized improvement plan based on test results"""
    # Check if user already has an improvement plan
    existing_plan = ImprovementPlan.objects.filter(
        user=test.user,
        is_completed=False
    ).first()

    if existing_plan:
        # Update existing plan
        existing_plan.test = test
        existing_plan.reading_recommendations = test.improvement_plan.get('reading', [])
        existing_plan.listening_recommendations = test.improvement_plan.get('listening', [])
        existing_plan.writing_recommendations = test.improvement_plan.get('writing', [])
        existing_plan.speaking_recommendations = test.improvement_plan.get('speaking', [])
        existing_plan.general_recommendations = test.improvement_plan.get('general', [])
        existing_plan.updated_at = timezone.now()
        existing_plan.save()
    else:
        # Create new plan
        ImprovementPlan.objects.create(
            user=test.user,
            test=test,
            reading_recommendations=test.improvement_plan.get('reading', []),
            listening_recommendations=test.improvement_plan.get('listening', []),
            writing_recommendations=test.improvement_plan.get('writing', []),
            speaking_recommendations=test.improvement_plan.get('speaking', []),
            general_recommendations=test.improvement_plan.get('general', [])
        )

@login_required
def improvement_plan(request, test_id):
    """Display the improvement plan for a specific test"""
    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # If test is not completed, redirect to appropriate section
    if test.status != 'completed':
        return redirect('ielts_mock')

    # Get the improvement plan
    plan = ImprovementPlan.objects.filter(
        user=request.user,
        test=test,
        is_completed=False
    ).first()

    if not plan:
        # If no plan exists, create one
        plan = ImprovementPlan.objects.create(
            user=request.user,
            test=test,
            reading_recommendations=test.improvement_plan.get('reading', []),
            listening_recommendations=test.improvement_plan.get('listening', []),
            writing_recommendations=test.improvement_plan.get('writing', []),
            speaking_recommendations=test.improvement_plan.get('speaking', []),
            general_recommendations=test.improvement_plan.get('general', [])
        )

    context = {
        'test': test,
        'plan': plan,
        'active_page': 'ielts_mock'
    }

    return render(request, 'ielts_mock/improvement_plan.html', context)

@login_required
def test_results(request, test_id):
    """Display the results of the IELTS mock test"""
    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # If test is not completed, redirect to appropriate section
    if test.status != 'completed':
        return redirect('ielts_mock')

    # Get strengths and areas for improvement
    strengths = test.strengths if test.strengths else []
    areas_for_improvement = test.areas_for_improvement if test.areas_for_improvement else []

    # Get detailed analysis for each section
    reading_analysis = test.reading_analysis if test.reading_analysis else {}
    listening_analysis = test.listening_analysis if test.listening_analysis else {}
    writing_analysis = test.writing_analysis if test.writing_analysis else {}

    # Prepare question type performance data for charts
    if reading_analysis and 'question_types' in reading_analysis:
        question_type_performance = {}
        for q_type, data in reading_analysis['question_types'].items():
            if data['total'] > 0:
                question_type_performance[q_type] = data['accuracy']
        reading_analysis['question_type_performance'] = question_type_performance

    if listening_analysis and 'question_types' in listening_analysis:
        question_type_performance = {}
        for q_type, data in listening_analysis['question_types'].items():
            if data['total'] > 0:
                question_type_performance[q_type] = data['accuracy']
        listening_analysis['question_type_performance'] = question_type_performance

    # Generate score interpretation
    score_interpretation = f"Your overall band score of {test.overall_score} indicates that you are a competent user of English. You generally have effective command of the language despite some inaccuracies and misunderstandings. You can use and understand fairly complex language, particularly in familiar situations."

    # Get user answers and correct answers for each section
    reading_questions = TestQuestion.objects.filter(
        test=test,
        section_type='reading'
    ).order_by('section_number', 'question_number')

    listening_questions = TestQuestion.objects.filter(
        test=test,
        section_type='listening'
    ).order_by('section_number', 'question_number')

    # Add these to the context
    context = {
        'test': test,
        'strengths': strengths,
        'areas_for_improvement': areas_for_improvement,
        'reading_analysis': reading_analysis,
        'listening_analysis': listening_analysis,
        'writing_analysis': writing_analysis,
        'score_interpretation': score_interpretation,
        'improvement_plan': test.improvement_plan if test.improvement_plan else {},
        'reading_questions': reading_questions,
        'listening_questions': listening_questions,
    }

    return render(request, 'ielts_mock/test_results.html', context)

@login_required
def section_analysis(request, test_id, section):
    """Display detailed analysis for a specific section of the test"""
    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # If test is not completed, redirect to appropriate section
    if test.status != 'completed':
        return redirect('ielts_mock')

    # Get analysis for the requested section
    if section == 'reading':
        section_analysis = test.reading_analysis if test.reading_analysis else {}
        section_score = test.reading_score
        section_title = "Reading"
    elif section == 'listening':
        section_analysis = test.listening_analysis if test.listening_analysis else {}
        section_score = test.listening_score
        section_title = "Listening"
    elif section == 'writing':
        section_analysis = test.writing_analysis if test.writing_analysis else {}
        section_score = test.writing_score
        section_title = "Writing"
    elif section == 'speaking':
        # For demo purposes, we don't have detailed speaking analysis
        section_analysis = {}
        section_score = test.speaking_score
        section_title = "Speaking"
    else:
        # Invalid section
        return redirect('test_results', test_id=test.id)

    # Prepare question type performance data for charts if available
    if section in ['reading', 'listening'] and section_analysis and 'question_types' in section_analysis:
        question_type_performance = {}
        for q_type, data in section_analysis['question_types'].items():
            if data['total'] > 0:
                question_type_performance[q_type] = data['accuracy']
        section_analysis['question_type_performance'] = question_type_performance

    # Get section-specific recommendations from improvement plan
    recommendations = []
    if test.improvement_plan and section in test.improvement_plan:
        recommendations = test.improvement_plan[section]

    context = {
        'test': test,
        'section': section,
        'section_title': section_title,
        'section_score': section_score,
        'section_analysis': section_analysis,
        'recommendations': recommendations,
        'active_page': 'ielts_mock'
    }

    return render(request, 'ielts_mock/section_analysis.html', context)

@login_required
def writing_analysis(request, test_id):
    """Display detailed analysis for the writing section of the test"""
    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # If test is not completed, redirect to appropriate section
    if test.status != 'completed':
        return redirect('ielts_mock')

    # Get writing content and responses
    writing_content = test.get_writing_content()
    writing_responses = test.get_writing_responses()

    # Get writing feedback
    feedback = test.feedback if test.feedback else {}

    # Get task-specific data
    task1_prompt = writing_content.get('task1', {}).get('instructions', '')
    task1_response = writing_responses.get('task1', '')
    task1_feedback = feedback.get('task1', {})

    task2_prompt = writing_content.get('task2', {}).get('instructions', '')
    task2_response = writing_responses.get('task2', '')
    task2_feedback = feedback.get('task2', {})

    # Get writing analysis
    writing_analysis = test.writing_analysis if test.writing_analysis else {}

    # Get writing-specific recommendations from improvement plan
    recommendations = []
    if test.improvement_plan and 'writing' in test.improvement_plan:
        recommendations = test.improvement_plan['writing']

    context = {
        'test': test,
        'writing_score': test.writing_score,
        'task1_prompt': task1_prompt,
        'task1_response': task1_response,
        'task1_feedback': task1_feedback,
        'task2_prompt': task2_prompt,
        'task2_response': task2_response,
        'task2_feedback': task2_feedback,
        'writing_analysis': writing_analysis,
        'recommendations': recommendations,
        'active_page': 'ielts_mock'
    }

    return render(request, 'ielts_mock/writing_analysis.html', context)

@login_required
def download_results(request, test_id):
    """Generate and download test results as PDF using wkhtmltopdf via pdfkit"""
    test = get_object_or_404(MockTest, id=test_id, user=request.user)

    # Get strengths and areas for improvement
    strengths = test.strengths if test.strengths else []
    areas_for_improvement = test.areas_for_improvement if test.areas_for_improvement else []

    # Get detailed analysis for each section
    reading_analysis = test.reading_analysis if test.reading_analysis else {}
    listening_analysis = test.listening_analysis if test.listening_analysis else {}
    writing_analysis = test.writing_analysis if test.writing_analysis else {}

    # Generate score interpretation
    score_interpretation = f"Your overall band score of {test.overall_score} indicates that you are a competent user of English. You generally have effective command of the language despite some inaccuracies and misunderstandings. You can use and understand fairly complex language, particularly in familiar situations."

    # Get the path to the logo
    logo_path = os.path.join(settings.STATIC_URL, 'images', 'logo.png')

    # Prepare the HTML content
    context = {
        'test': test,
        'strengths': strengths,
        'areas_for_improvement': areas_for_improvement,
        'reading_analysis': reading_analysis,
        'listening_analysis': listening_analysis,
        'writing_analysis': writing_analysis,
        'score_interpretation': score_interpretation,
        'improvement_plan': test.improvement_plan if test.improvement_plan else {},
        'logo_path': request.build_absolute_uri(logo_path),
        'now': timezone.now(),
        'STATIC_URL': settings.STATIC_URL,
        'request': request,
    }

    # Render the HTML template
    html_string = render_to_string('ielts_mock/pdf_results.html', context)

    # Configure pdfkit options
    options = {
        'page-size': 'A4',
        'margin-top': '2cm',
        'margin-right': '2cm',
        'margin-bottom': '2cm',
        'margin-left': '2cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': None,
    }

    # Generate PDF from HTML
    pdf = pdfkit.from_string(html_string, False, options=options)

    # Create the HTTP response with PDF content
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ielts_results_{test.id}.pdf"'

    return response

@login_required
def test_history(request):
    """View for displaying the complete test history and overview"""
    # Get all completed tests for the user
    user_tests = MockTest.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-completed_at')

    # Get the first and latest test for comparison
    first_test = user_tests.order_by('completed_at').first()
    latest_test = user_tests.order_by('-completed_at').first()

    # Calculate improvements
    improvements = {}
    if first_test and latest_test and first_test != latest_test:
        improvements = {
            'overall': round(latest_test.overall_score - first_test.overall_score, 1),
            'reading': round(latest_test.reading_score - first_test.reading_score, 1),
            'listening': round(latest_test.listening_score - first_test.listening_score, 1),
            'writing': round(latest_test.writing_score - first_test.writing_score, 1),
            'speaking': round(latest_test.speaking_score - first_test.speaking_score if (latest_test.speaking_score and first_test.speaking_score) else 0),
        }

        # Get current scores (from latest test)
        current_scores = {
            'overall': latest_test.overall_score if latest_test else 0,
            'reading': latest_test.reading_score if latest_test else 0,
            'listening': latest_test.listening_score if latest_test else 0,
            'writing': latest_test.writing_score if latest_test else 0,
            'speaking': latest_test.speaking_score if latest_test else 0,
        }

        # Get previous scores (for "from" display)
        previous_scores = {
            'overall': first_test.overall_score if first_test else 0,
            'reading': first_test.reading_score if first_test else 0,
            'listening': first_test.listening_score if first_test else 0,
            'writing': first_test.writing_score if first_test else 0,
            'speaking': first_test.speaking_score if first_test else 0,
        }

        # Prepare data for the score progression chart
        chart_data = prepare_chart_data(user_tests)

        # Identify key improvements and areas to focus
        key_improvements, focus_areas = identify_improvements_and_focus(user_tests, latest_test)

        context = {
            'user_tests': user_tests,
            'current_scores': current_scores,
            'previous_scores': previous_scores,
            'improvements': improvements,
            'chart_data': chart_data,
            'key_improvements': key_improvements,
            'focus_areas': focus_areas,
            'active_page': 'history',
            'active_tab': 'overview'
        }

    return render(request, 'ielts_mock/test_history.html', context)

@login_required
def test_comparison(request):
    """View for comparing first and latest test results"""
    # Get all completed tests for the user
    user_tests = MockTest.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-completed_at')

    # Get the first and latest test for comparison
    first_test = user_tests.order_by('completed_at').first()
    latest_test = user_tests.order_by('-completed_at').first()

    # Calculate improvements
    improvements = {}
    if first_test and latest_test and first_test != latest_test:
        improvements = {
            'overall': round(latest_test.overall_score - first_test.overall_score, 1),
            'reading': round(latest_test.reading_score - first_test.reading_score, 1),
            'listening': round(latest_test.listening_score - first_test.listening_score, 1),
            'writing': round(latest_test.writing_score - first_test.writing_score, 1),
            'speaking': round(latest_test.speaking_score - first_test.speaking_score if (latest_test.speaking_score and first_test.speaking_score) else 0),
        }

        context = {
            'first_test': first_test,
            'latest_test': latest_test,
            'improvements': improvements,
            'active_page': 'history',
            'active_tab': 'comparison'
        }

    return render(request, 'ielts_mock/test_comparison.html', context)

@login_required
def progress_overview(request):
    """View for displaying progress overview and charts"""
    # Get all completed tests for the user
    user_tests = MockTest.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-completed_at')

    # Prepare data for the score progression chart
    chart_data = prepare_chart_data(user_tests)

    # Get statistics
    stats = {
        'total_tests': user_tests.count(),
        'avg_score': user_tests.aggregate(Avg('overall_score'))['overall_score__avg'] or 0,
        'max_score': user_tests.aggregate(Max('overall_score'))['overall_score__max'] or 0,
        'min_score': user_tests.aggregate(Min('overall_score'))['overall_score__min'] or 0,
    }

    context = {
        'user_tests': user_tests,
        'chart_data': chart_data,
        'stats': stats,
        'active_page': 'history',
        'active_tab': 'progress'
    }

    return render(request, 'ielts_mock/progress_overview.html', context)

@login_required
def writing_practice(request):
    """Display the writing practice page"""
    # Get user's previous writing practices
    user_practices = WritingPractice.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    # Get GPT service to generate a new prompt
    gpt_service = GPTService()

    # Default to task2 (essay) if not specified
    task_type = request.GET.get('task_type', 'task2')

    # Generate a new prompt based on task type
    if task_type == 'task1':
        prompt = gpt_service.generate_writing_task1_prompt()
        task_title = "Task 1: Report Writing"
        task_description = "You should spend about 20 minutes on this task. Write at least 150 words."
        time_limit = 20  # minutes
    else:  # task2
        prompt = gpt_service.generate_writing_task2_prompt()
        task_title = "Task 2: Essay Writing"
        task_description = "You should spend about 40 minutes on this task. Write at least 250 words."
        time_limit = 40  # minutes

    # Create a new writing practice
    practice = WritingPractice.objects.create(
        user=request.user,
        task_type=task_type,
        prompt=prompt
    )

    context = {
        'practice': practice,
        'task_title': task_title,
        'task_description': task_description,
        'time_limit': time_limit,
        'user_practices': user_practices,
        'active_page': 'writing'
    }

    return render(request, 'ielts_mock/writing_practice.html', context)

@login_required
@csrf_exempt
def submit_writing_practice(request):
    """Submit a writing practice response"""
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    practice_id = request.POST.get('practice_id')
    response = request.POST.get('response', '')

    practice = get_object_or_404(WritingPractice, id=practice_id, user=request.user)

    # Save the response
    practice.response = response
    practice.save()

    # Evaluate the response
    gpt_service = GPTService()
    practice.evaluate(gpt_service)

    # Redirect to results page
    return redirect('writing_practice_results', practice_id=practice.id)

@login_required
def writing_practice_results(request, practice_id):
    """Display the results of a writing practice"""
    practice = get_object_or_404(WritingPractice, id=practice_id, user=request.user)

    # If not evaluated yet, evaluate now
    if not practice.feedback and practice.response:
        gpt_service = GPTService()
        practice.evaluate(gpt_service)

    # Get feedback
    feedback = practice.feedback if practice.feedback else {}

    # Generate score interpretation
    score_interpretation = f"Your overall band score of {practice.overall_score} indicates "

    if practice.overall_score >= 8.0:
        score_interpretation += "that you are a very good user of English. You have full operational command of the language with only occasional unsystematic inaccuracies."
    elif practice.overall_score >= 7.0:
        score_interpretation += "that you are a good user of English. You have operational command of the language, though with occasional inaccuracies and misunderstandings."
    elif practice.overall_score >= 6.0:
        score_interpretation += "that you are a competent user of English. You generally have effective command of the language despite some inaccuracies and misunderstandings."
    elif practice.overall_score >= 5.0:
        score_interpretation += "that you are a modest user of English. You have partial command of the language and cope with overall meaning in most situations."
    else:
        score_interpretation += "that you are a limited user of English. Your basic competence is limited to familiar situations."

    # Get improvement suggestions
    improvements = feedback.get('improvements', [])

    context = {
        'practice': practice,
        'feedback': feedback,
        'score_interpretation': score_interpretation,
        'improvements': improvements,
        'active_page': 'writing'
    }

    return render(request, 'ielts_mock/writing_practice_results.html', context)

# Helper functions
def prepare_chart_data(user_tests):
    """Prepare data for the score progression chart"""
    dates = []
    overall_scores = []
    reading_scores = []
    listening_scores = []
    writing_scores = []
    speaking_scores = []

    # Get data for up to the last 10 tests
    for test in user_tests.order_by('completed_at')[:10]:
        if test.completed_at:
            dates.append(test.completed_at.strftime('%b %d, %Y'))
            overall_scores.append(test.overall_score)
            reading_scores.append(test.reading_score)
            listening_scores.append(test.listening_score)
            writing_scores.append(test.writing_score)
            speaking_scores.append(test.speaking_score if test.speaking_score else 0)

    return {
        'dates': dates,
        'overall': overall_scores,
        'reading': reading_scores,
        'listening': listening_scores,
        'writing': writing_scores,
        'speaking': speaking_scores
    }

def identify_improvements_and_focus(user_tests, latest_test):
    """Identify key improvements and areas to focus"""
    if not latest_test or user_tests.count() < 2:
        return [], []

    # Get the second-to-last test for comparison
    previous_test = user_tests.exclude(id=latest_test.id).order_by('-completed_at').first()
    if not previous_test:
        return [], []

    # Calculate improvements for each section
    improvements = {
        'overall': latest_test.overall_score - previous_test.overall_score,
        'reading': latest_test.reading_score - previous_test.reading_score,
        'listening': latest_test.listening_score - previous_test.listening_score,
        'writing': latest_test.writing_score - previous_test.writing_score,
        'speaking': latest_test.speaking_score - previous_test.speaking_score if (latest_test.speaking_score and previous_test.speaking_score) else 0,
    }

    # Identify key improvements (positive changes)
    key_improvements = []
    for section, change in improvements.items():
        if change >= 0.5:  # Significant improvement
            if section == 'reading':
                key_improvements.append({
                    'section': 'Reading',
                    'change': change,
                    'message': f'Improved by {change} bands',
                    'from_score': previous_test.reading_score,
                    'to_score': latest_test.reading_score
                })
            elif section == 'listening':
                key_improvements.append({
                    'section': 'Listening',
                    'change': change,
                    'message': f'Improved by {change} bands',
                    'from_score': previous_test.listening_score,
                    'to_score': latest_test.listening_score
                })
            elif section == 'writing':
                key_improvements.append({
                    'section': 'Writing',
                    'change': change,
                    'message': f'Improved by {change} bands',
                    'from_score': previous_test.writing_score,
                    'to_score': latest_test.writing_score
                })
            elif section == 'speaking':
                key_improvements.append({
                    'section': 'Speaking',
                    'change': change,
                    'message': f'Improved by {change} bands',
                    'from_score': previous_test.speaking_score,
                    'to_score': latest_test.speaking_score
                })

    # Identify areas to focus (lowest scores or negative changes)
    focus_areas = []
    section_scores = {
        'reading': latest_test.reading_score,
        'listening': latest_test.listening_score,
        'writing': latest_test.writing_score,
        'speaking': latest_test.speaking_score if latest_test.speaking_score else 0,
    }

    # Find the lowest scoring section
    lowest_section = min(section_scores, key=section_scores.get)
    lowest_score = section_scores[lowest_section]

    # Add the lowest scoring section to focus areas
    if lowest_section == 'reading':
        focus_areas.append({
            'section': 'Reading',
            'score': lowest_score,
            'message': 'Your reading score is currently your lowest.'
        })
    elif lowest_section == 'listening':
        focus_areas.append({
            'section': 'Listening',
            'score': lowest_score,
            'message': 'Your listening score is currently your lowest.'
        })
    elif lowest_section == 'writing':
        focus_areas.append({
            'section': 'Writing',
            'score': lowest_score,
            'message': 'Your writing score is currently your lowest.'
        })
    elif lowest_section == 'speaking':
        focus_areas.append({
            'section': 'Speaking',
            'score': lowest_score,
            'message': 'Your speaking score is currently your lowest.'
        })

    # Also add sections with negative changes
    for section, change in improvements.items():
        if change < 0 and section != 'overall' and section != lowest_section:  # Negative change and not already added
            if section == 'reading':
                focus_areas.append({
                    'section': 'Reading',
                    'score': latest_test.reading_score,
                    'message': f'Decreased by {abs(change)} bands from previous test.'
                })
            elif section == 'listening':
                focus_areas.append({
                    'section': 'Listening',
                    'score': latest_test.listening_score,
                    'message': f'Decreased by {abs(change)} bands from previous test.'
                })
            elif section == 'writing':
                focus_areas.append({
                    'section': 'Writing',
                    'score': latest_test.writing_score,
                    'message': f'Decreased by {abs(change)} bands from previous test.'
                })
            elif section == 'speaking':
                focus_areas.append({
                    'section': 'Speaking',
                    'score': latest_test.speaking_score,
                    'message': f'Decreased by {abs(change)} bands from previous test.'
                })

    return key_improvements, focus_areas
