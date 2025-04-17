from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
import requests
import json
import os
from .forms import CustomLoginForm, CustomRegistrationForm
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import get_backends
import random
from django.contrib import messages
from ielts_mock.models import MockTest
from django.db.models import Avg, Max, Min, Count
import datetime

def index(request):
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Sample data for top performers
    top_performers = [
        {'name': 'Sarah Cooper', 'country': 'United Kingdom', 'score': 8.5},
        {'name': 'James Peterson', 'country': 'Australia', 'score': 8.0},
        {'name': 'Tina Wilson', 'country': 'Canada', 'score': 7.5},
        {'name': 'Mark Anderson', 'country': 'United States', 'score': 7.5},
        {'name': 'Sophia Jackson', 'country': 'New Zealand', 'score': 7.0},
    ]

    # Sample testimonials
    testimonials = [
        {
            'name': 'Aisha Rahman',
            'country': 'Pakistan',
            'text': 'BandBooster helped me reach my IELTS target score of 7.5. The practice tests were incredibly similar to the real exam!'
        },
        {
            'name': 'Marco Santos',
            'country': 'Brazil',
            'text': 'After using this website for 3 months, my speaking improved from 6.0 to 7.5. The detailed feedback was invaluable!'
        },
        {
            'name': 'Olivia Peterson',
            'country': 'Sweden',
            'text': 'As a non-native English speaker, I was struggling with writing. BandBooster\'s resources helped me improve my score dramatically!'
        },
    ]

    # Sample pricing plans
    pricing_plans = {
        'basic': {
            'name': 'Basic',
            'price': '9.99',
            'period': '/month',
            'features': [
                'Full access to study bank',
                'Progress tracking',
                'Basic writing feedback',
                'Email support'
            ]
        },
        'premium': {
            'name': 'Premium',
            'price': '29.99',
            'period': '/month',
            'features': [
                'All basic plan features',
                'Advanced writing feedback',
                'Speaking practice sessions',
                'Mock interviews',
                'Priority support',
                'Progress reports',
                'Mobile app access'
            ]
        },
        'institutions': {
            'name': 'Institutions',
            'price': 'Custom',
            'period': '',
            'features': [
                'All premium features',
                'Bulk student accounts',
                'Teacher dashboard',
                'Custom branding',
                'API access',
                'Dedicated support'
            ]
        }
    }

    # FAQ items
    faqs = [
        {
            'question': 'How accurate are the mock tests compared to the real IELTS exam?',
            'answer': 'Our mock tests are designed by experienced IELTS trainers and exam item writers for maximum authenticity. Many of our users report that our practice tests closely match the format, difficulty level, and timing of the real exam.'
        },
        {
            'question': 'How quickly can I expect to improve my IELTS score?',
            'answer': 'Most students see a band score improvement of 0.5-1.0 within 4-6 weeks of consistent practice. However, this varies based on your starting level, study consistency, and learning style. Our personalized study plans help you maximize your improvement rate.'
        },
        {
            'question': 'Do you offer personalized feedback on writing and speaking?',
            'answer': 'Yes! Premium subscribers receive detailed feedback on their writing tasks and speaking responses from certified IELTS examiners within 24-48 hours of submission.'
        },
        {
            'question': 'Is BandBooster suitable for both Academic and General Training IELTS?',
            'answer': 'Yes, our comprehensive platform is suitable for both Academic and General Training IELTS. You can select your exam type when creating your account to receive tailored preparation materials.'
        },
        {
            'question': 'Can I access BandBooster on mobile devices?',
            'answer': 'Yes, BandBooster is fully responsive and works on all devices. We also offer dedicated mobile apps for iOS and Android for Premium subscribers.'
        },
    ]

    context = {
        'top_performers': top_performers,
        'testimonials': testimonials,
        'pricing_plans': pricing_plans,
        'faqs': faqs,
    }

    return render(request, 'core/index.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')

            # Try to authenticate with both backends directly
            user = None
            backend_path = None

            # First try the EmailBackend
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Login the user with the specific backend
                login(request, user)

                if not remember_me:
                    request.session.set_expiry(0)

                # Ensure user has a profile
                try:
                    # Just access the profile to check if it exists
                    profile = user.profile
                except User.profile.RelatedObjectDoesNotExist:
                    # Create profile if it doesn't exist
                    UserProfile.objects.create(user=user, coins=random.randint(100, 500))

                # Redirect to dashboard
                next_url = request.POST.get('next', 'dashboard')
                return redirect(next_url)
            else:
                # Add a non-field error to the form
                form.add_error(None, "Invalid email or password. Please try again.")
    else:
        form = CustomLoginForm()

    return render(request, 'core/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            # Check if a user with this email already exists
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
                form.add_error('email', 'A user with this email already exists.')
                return render(request, 'core/register.html', {'form': form})

            # Save the user - UserProfile will be created by the signal
            user = form.save()

            # Login the user directly after registration
            user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)

            # Give new users some starting coins (100-500 random)
            try:
                profile = user.profile
                profile.coins = random.randint(100, 500)
                profile.save()
            except User.profile.RelatedObjectDoesNotExist:
                profile = UserProfile.objects.create(user=user, coins=random.randint(100, 500))

            # Redirect to dashboard
            next_url = request.POST.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = CustomRegistrationForm()

    return render(request, 'core/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    # Ensure user has a profile before rendering dashboard
    try:
        # Just access the profile to check if it exists
        profile = request.user.profile
    except User.profile.RelatedObjectDoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user, coins=random.randint(100, 500))

    # Get user's test history
    user_tests = MockTest.objects.filter(user=request.user).order_by('-created_at')

    # Calculate statistics from test history
    test_stats = {
        'total_tests': user_tests.count(),
        'tests_completed': user_tests.filter(status='completed').count(),
        'latest_test': user_tests.first() if user_tests.exists() else None,
    }

    # Calculate score trends if user has completed tests
    completed_tests = user_tests.filter(status='completed')
    score_trends = None

    if completed_tests.exists():
        # Get the last 6 completed tests (or fewer if user hasn't taken that many)
        recent_tests = completed_tests.order_by('-completed_at')[:6]

        # Prepare data for charts
        score_trends = {
            'dates': [test.completed_at.strftime('%b %d') for test in recent_tests],
            'overall': [test.overall_score for test in recent_tests],
            'reading': [test.reading_score for test in recent_tests],
            'listening': [test.listening_score for test in recent_tests],
            'writing': [test.writing_score for test in recent_tests],
            'speaking': [test.speaking_score for test in recent_tests if test.speaking_score],
        }

        # Reverse the lists to show chronological order
        for key in score_trends:
            score_trends[key] = list(reversed(score_trends[key]))

    # Calculate current scores (average of last 3 tests or fewer)
    current_scores = {
        'overall': 0,
        'reading': 0,
        'listening': 0,
        'writing': 0,
        'speaking': 0,
    }

    if completed_tests.exists():
        recent_for_avg = completed_tests.order_by('-completed_at')[:3]

        current_scores = {
            'overall': round(recent_for_avg.aggregate(Avg('overall_score'))['overall_score__avg'] or 0, 1),
            'reading': round(recent_for_avg.aggregate(Avg('reading_score'))['reading_score__avg'] or 0, 1),
            'listening': round(recent_for_avg.aggregate(Avg('listening_score'))['listening_score__avg'] or 0, 1),
            'writing': round(recent_for_avg.aggregate(Avg('writing_score'))['writing_score__avg'] or 0, 1),
            'speaking': round(recent_for_avg.aggregate(Avg('speaking_score'))['speaking_score__avg'] or 0, 1),
        }

    # Calculate improvement areas based on test history
    improvement_areas = []

    if completed_tests.count() >= 2:
        # Compare the most recent test with previous tests
        latest_test = completed_tests.latest('completed_at')

        # Check reading performance
        if latest_test.reading_score < current_scores['overall']:
            improvement_areas.append({
                'section': 'Reading',
                'score': latest_test.reading_score,
                'message': 'Your reading score is below your overall average.'
            })

        # Check listening performance
        if latest_test.listening_score < current_scores['overall']:
            improvement_areas.append({
                'section': 'Listening',
                'score': latest_test.listening_score,
                'message': 'Your listening score is below your overall average.'
            })

        # Check writing performance
        if latest_test.writing_score < current_scores['overall']:
            improvement_areas.append({
                'section': 'Writing',
                'score': latest_test.writing_score,
                'message': 'Your writing score is below your overall average.'
            })

        # Check speaking performance if available
        if latest_test.speaking_score and latest_test.speaking_score < current_scores['overall']:
            improvement_areas.append({
                'section': 'Speaking',
                'score': latest_test.speaking_score,
                'message': 'Your speaking score is below your overall average.'
            })

    # Get upcoming tests if any are in progress
    upcoming_tests = user_tests.filter(status='in_progress')

    # User data for the dashboard
    user_data = {
        'overall_score': current_scores['overall'],
        'reading_score': {
            'score': current_scores['reading'],
            'change': 0.5,  # This would be calculated from historical data
            'period': 'month'
        },
        'listening_score': {
            'score': current_scores['listening'],
            'change': 0.5,
            'period': 'month'
        },
        'writing_score': {
            'score': current_scores['writing'],
            'change': 0.0,
            'period': 'month'
        },
        'speaking_score': {
            'score': current_scores['speaking'],
            'change': 0.5,
            'period': 'month'
        },
        'target_score': profile.target_score if hasattr(profile, 'target_score') else 7.5,
        'coins': profile.coins,
        'tests_taken': test_stats['total_tests'],
        'tests_completed': test_stats['tests_completed'],
        'improvement_areas': improvement_areas[:3],  # Top 3 improvement areas
    }

    # Monthly progress data for chart
    progress_data = {
        'months': score_trends['dates'] if score_trends else ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'reading': score_trends['reading'] if score_trends else [5.0, 5.5, 5.5, 6.0, 6.5, 7.0],
        'listening': score_trends['listening'] if score_trends else [5.5, 6.0, 6.0, 6.5, 7.0, 6.5],
        'writing': score_trends['writing'] if score_trends else [5.0, 5.5, 5.5, 6.0, 6.5, 6.0],
        'speaking': score_trends['speaking'] if score_trends else [5.0, 5.0, 5.5, 6.0, 6.5, 6.5],
        'overall': score_trends['overall'] if score_trends else [5.0, 5.5, 6.0, 6.5, 7.0, 6.5]
    }

    # Recent test history for dashboard
    recent_tests_data = []
    for test in user_tests[:5]:  # Show last 5 tests
        recent_tests_data.append({
            'id': test.id,
            'date': test.completed_at.strftime('%b %d, %Y') if test.completed_at else test.created_at.strftime('%b %d, %Y'),
            'type': test.test_type,
            'status': test.status,
            'overall_score': test.overall_score if test.overall_score else '-',
            'reading_score': test.reading_score if test.reading_score else '-',
            'listening_score': test.listening_score if test.listening_score else '-',
            'writing_score': test.writing_score if test.writing_score else '-',
            'speaking_score': test.speaking_score if test.speaking_score else '-',
        })

    context = {
        'user_data': user_data,
        'progress_data': progress_data,
        'section_scores': {
            'reading': current_scores['reading'],
            'listening': current_scores['listening'],
            'writing': current_scores['writing'],
            'speaking': current_scores['speaking']
        },
        'recent_tests': recent_tests_data,
        'upcoming_tests': upcoming_tests,
        'active_page': 'dashboard'
    }

    return render(request, 'core/dashboard.html', context)

@login_required
def ielts_mock(request):
    """
    View for the IELTS Mock Test page
    """
    if request.method == 'POST':
        test_type = request.POST.get('test_type', 'academic')
        full_screen = request.POST.get('full_screen') == 'true'

        # Create a new test or redirect to the test page
        # This is a placeholder - in a real implementation, you would create a test in the database
        # and redirect to the first section of the test

        # For now, we'll just render the same template with the selected options
        context = {
            'active_page': 'ielts_mock',
            'test_type': test_type,
            'full_screen': full_screen,
        }
        return render(request, 'core/ielts_mock.html', context)

    context = {
        'active_page': 'ielts_mock',
    }
    return render(request, 'core/ielts_mock.html', context)

def google_auth(request):
    # Placeholder for Google authentication
    return redirect('dashboard')

def google_callback(request):
    # Placeholder for Google authentication callback
    return redirect('dashboard')
