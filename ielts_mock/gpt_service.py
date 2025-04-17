from openai import OpenAI

import json
import random
from django.conf import settings
from bandbooster.settings import GPT_MODEL

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class GPTService:

    def __init__(self):
        pass

    # Initialize with your API key from settings

    def generate_reading_test(self, test_type='academic'):
        """Generate a complete IELTS reading test with passages and questions"""

        prompt = f"""
        Generate a complete IELTS {test_type} Reading test with 3 passages and questions.
        
        For each passage:
        1. Create a title and a realistic passage of appropriate length and difficulty
        2. Create 13-14 questions of various types (multiple choice, true/false/not given, matching, etc.)
        3. Include the correct answers
        
        Format the response as a JSON object with this structure:
        {{
            "sections": [
                {{
                    "title": "Passage title",
                    "text": "Full passage text...",
                    "questions": [
                        {{
                            "id": 1,
                            "type": "true_false_not_given",
                            "text": "Question text",
                            "options": ["TRUE", "FALSE", "NOT GIVEN"],
                            "answer": "TRUE"
                        }},
                        {{
                            "id": 2,
                            "type": "multiple_choice",
                            "text": "Question text",
                            "options": ["A", "B", "C", "D"],
                            "answer": "B"
                        }}
                    ]
                }}
            ]
        }}
        """

        try:
            response = client.chat.completions.create(model=GPT_MODEL,
                                                      messages=[
                                                          {"role": "system",
                                                           "content": "You are an expert IELTS test creator."},
                                                          {"role": "user", "content": prompt}
                                                      ],
                                                      temperature=0.7,
                                                      max_tokens=4000)

            content = response.choices[0].message.content
            content = content.replace("```json", "")
            content = content.replace("```", "")
            print(content)
            return json.loads(content)
        except Exception as e:
            print(f"Error generating reading test: {e}")
            # Return a fallback test in case of API failure
            return self._get_fallback_reading_test(test_type)

    def generate_listening_test(self, test_type='academic'):
        """Generate a complete IELTS listening test with 4 sections"""

        prompt = f"""
        Generate a complete IELTS Listening test with 4 sections.
        
        For each section:
        1. Create a script for what would be heard in the audio
        2. Create 10 questions based on the audio (form filling, multiple choice, etc.)
        3. Include the correct answers
        
        Format the response as a JSON object with this structure:
        {{
            "sections": [
                {{
                    "title": "Section 1",
                    "description": "A conversation between two people...",
                    "script": "Full transcript of what would be in the audio...",
                    "questions": [
                        {{
                            "id": 1,
                            "type": "fill_in_blank",
                            "text": "The student's name is _______.",
                            "answer": "Johnson"
                        }},
                        {{
                            "id": 2,
                            "type": "multiple_choice",
                            "text": "What is the purpose of the call?",
                            "options": ["A", "B", "C", "D"],
                            "answer": "B"
                        }}
                    ]
                }}
            ]
        }}
        """

        try:
            response = client.chat.completions.create(model=GPT_MODEL,
                                                      messages=[
                                                          {"role": "system",
                                                           "content": "You are an expert IELTS test creator."},
                                                          {"role": "user", "content": prompt}
                                                      ],
                                                      temperature=0.7,
                                                      max_tokens=4000)

            content = response.choices[0].message.content
            content = content.replace("```json", "")
            content = content.replace("```", "")
            return json.loads(content)
        except Exception as e:
            print(f"Error generating listening test: {e}")
            # Return a fallback test in case of API failure
            return self._get_fallback_listening_test()

    def generate_writing_test(self, test_type='academic'):
        """Generate IELTS writing tasks"""

        prompt = f"""
        Generate two IELTS {test_type} Writing tasks.
        
        For Task 1 ({test_type}):
        - If academic: Create a chart/graph description task with sample data
        - If general: Create a letter writing task
        
        For Task 2:
        - Create an essay question on a common IELTS topic
        
        Format the response as a JSON object with this structure:
        {{
            "task1": {{
                "title": "Task 1",
                "instructions": "The chart below shows...",
                "chart_data": {{}} or null,
                "word_count": 150
            }},
            "task2": {{
                "title": "Task 2",
                "instructions": "Some people believe that...",
                "word_count": 250
            }}
        }}
        """

        try:
            response = client.chat.completions.create(model=GPT_MODEL,
                                                      messages=[
                                                          {"role": "system",
                                                           "content": "You are an expert IELTS test creator."},
                                                          {"role": "user", "content": prompt}
                                                      ],
                                                      temperature=0.7,
                                                      max_tokens=1000)

            content = response.choices[0].message.content
            content = content.replace("```json", "")
            content = content.replace("```", "")
            return json.loads(content)
        except Exception as e:
            print(f"Error generating writing test: {e}")
            # Return a fallback test in case of API failure
            return self._get_fallback_writing_test(test_type)

    def evaluate_writing(self, task_prompt, user_response):
        """Evaluate a user's writing response and provide a score and feedback"""

        prompt = f"""
        Evaluate the following IELTS writing response based on the IELTS writing assessment criteria:
        - Task Achievement/Response
        - Coherence and Cohesion
        - Lexical Resource
        - Grammatical Range and Accuracy
        
        Task prompt: {task_prompt}
        
        User's response: {user_response}
        
        Provide a band score (0-9) for each criterion and an overall band score.
        Also provide specific feedback on strengths and areas for improvement.
        
        Format your response as a JSON object with this structure:
        {{
            "task_achievement": 7.0,
            "coherence_cohesion": 6.5,
            "lexical_resource": 7.0,
            "grammatical_range": 6.5,
            "overall_score": 6.5,
            "strengths": ["Good understanding of the task", "Logical structure"],
            "improvements": ["Limited use of cohesive devices", "Some grammatical errors"]
        }}
        """

        try:
            response = client.chat.completions.create(model=GPT_MODEL,
                                                      messages=[
                                                          {"role": "system",
                                                           "content": "You are an expert IELTS examiner."},
                                                          {"role": "user", "content": prompt}
                                                      ],
                                                      temperature=0.3,
                                                      max_tokens=1000)

            content = response.choices[0].message.content
            content = content.replace("```json", "")
            content = content.replace("```", "")
            return json.loads(content)
        except Exception as e:
            print(f"Error evaluating writing: {e}")
            # Return a fallback evaluation
            return {
                "task_achievement": 6.0,
                "coherence_cohesion": 6.0,
                "lexical_resource": 6.0,
                "grammatical_range": 6.0,
                "overall_score": 6.0,
                "strengths": ["Attempted to address the task"],
                "improvements": ["Please try again later for a more detailed evaluation"]
            }

    def _get_fallback_reading_test(self, test_type):
        """Return a pre-made fallback reading test in case the API fails"""
        return {
            "sections": [
                {
                    "title": "The History of Tea",
                    "text": "Tea is one of the most widely consumed beverages in the world, second only to water. Its origins can be traced back to ancient China, where legend has it that Emperor Shen Nong discovered tea when leaves from a wild tree blew into his pot of boiling water. The earliest credible record of tea drinking dates to the 3rd century AD, in a medical text written by Hua Tuo. Tea was first introduced to Portuguese priests and merchants in China during the 16th century. Drinking tea became popular in Britain during the 17th century. The British introduced tea production, as well as tea consumption, to India, in order to compete with the Chinese monopoly on the product.\n\nTea has played a significant role in Asian culture for centuries as a staple beverage, a curative, and a status symbol. It is not only a beverage but also a symbol of status, hospitality, and even religious significance in many societies. The tea ceremony, for example, is a cultural activity involving the ceremonial preparation and presentation of tea. The Japanese tea ceremony, also called the Way of Tea, is a Japanese cultural activity involving the ceremonial preparation and presentation of matcha, powdered green tea. In China, tea is often served as a sign of respect, and the tea ceremony is a time-honored tradition.\n\nTea has also been an important part of the economy and politics of many countries. The British East India Company had a monopoly over the tea industry in England in the 18th century. The Boston Tea Party was an American political protest in 1773 when colonists destroyed a shipment of tea to protest a tax on tea. The Opium Wars between China and Britain were also partly due to trade disputes over tea.\n\nToday, tea continues to be an important part of many cultures around the world. It is grown in more than 30 countries, with China, India, Kenya, Sri Lanka, and Turkey being the largest producers. Different types of tea are produced, including black, green, white, oolong, and herbal teas, each with its own unique flavor and characteristics. The health benefits of tea have also been widely studied, with research suggesting that it may help reduce the risk of heart disease, cancer, and other conditions.",
                    "questions": [
                        {
                            "id": 1,
                            "type": "true_false_not_given",
                            "text": "Tea is the most widely consumed beverage in the world.",
                            "options": ["TRUE", "FALSE", "NOT GIVEN"],
                            "answer": "FALSE"
                        },
                        {
                            "id": 2,
                            "type": "true_false_not_given",
                            "text": "Emperor Shen Nong intentionally put tea leaves in his boiling water.",
                            "options": ["TRUE", "FALSE", "NOT GIVEN"],
                            "answer": "FALSE"
                        },
                        {
                            "id": 3,
                            "type": "true_false_not_given",
                            "text": "The earliest record of tea drinking is from the 3rd century AD.",
                            "options": ["TRUE", "FALSE", "NOT GIVEN"],
                            "answer": "TRUE"
                        },
                        {
                            "id": 4,
                            "type": "multiple_choice",
                            "text": "When did tea become popular in Britain?",
                            "options": ["16th century", "17th century", "18th century", "19th century"],
                            "answer": "17th century"
                        },
                        {
                            "id": 5,
                            "type": "multiple_choice",
                            "text": "Why did the British introduce tea production to India?",
                            "options": ["To create jobs for Indian workers", "To compete with China's monopoly",
                                        "To improve relations with India", "To reduce transportation costs"],
                            "answer": "To compete with China's monopoly"
                        }
                    ]
                }
            ]
        }

    def _get_fallback_listening_test(self):
        """Return a pre-made fallback listening test in case the API fails"""
        return {
            "sections": [
                {
                    "title": "Section 1",
                    "description": "A conversation between a student and a university accommodation officer",
                    "script": "Officer: Good morning, University Accommodation Office. How can I help you?\nStudent: Hi, I'm calling about on-campus accommodation for the upcoming semester. I'm a new international student.\nOfficer: Welcome! I'd be happy to help. Could I get your name please?\nStudent: Yes, it's Sarah Johnson.\nOfficer: And do you have your student ID number?\nStudent: Yes, it's 985421.\nOfficer: Great, thank you. So you're looking for accommodation starting in September, is that right?\nStudent: Yes, that's right. I'll be arriving on September 3rd.\nOfficer: Perfect. We have several options available. Are you looking for a single room or shared?\nStudent: I'd prefer a single room if possible.\nOfficer: We have single rooms available in three different halls: Parkview, Riverside, and Central Hall. Parkview is our newest building with en-suite bathrooms, but it's also the most expensive at £175 per week. Riverside is £145 per week with shared bathrooms. Central Hall is our most affordable option at £125 per week, but it's a bit further from the main campus buildings.\nStudent: I think Riverside sounds like a good balance. What facilities are included?\nOfficer: Riverside has shared kitchen facilities on each floor, free WiFi, laundry room in the basement, and a common room with TV and pool table. All utility bills are included in the price.\nStudent: That sounds good. How long is the contract?\nOfficer: The standard contract is for 42 weeks, covering the full academic year including holidays.\nStudent: Perfect. And is there a deposit?\nOfficer: Yes, there's a £300 deposit required to secure your room, which is refundable at the end of your stay, assuming there's no damage.\nStudent: OK. How do I apply?\nOfficer: You can apply online through the student portal. The deadline for applications is July 15th.\nStudent: Great, thank you for your help.",
                    "questions": [
                        {
                            "id": 1,
                            "type": "fill_in_blank",
                            "text": "The student's name is _______.",
                            "answer": "Sarah Johnson"
                        },
                        {
                            "id": 2,
                            "type": "fill_in_blank",
                            "text": "The student's ID number is _______.",
                            "answer": "985421"
                        },
                        {
                            "id": 3,
                            "type": "fill_in_blank",
                            "text": "The student will arrive on _______ (date).",
                            "answer": "September 3rd"
                        },
                        {
                            "id": 4,
                            "type": "multiple_choice",
                            "text": "Which accommodation option did the student prefer?",
                            "options": ["Parkview", "Riverside", "Central Hall"],
                            "answer": "Riverside"
                        },
                        {
                            "id": 5,
                            "type": "fill_in_blank",
                            "text": "The price of the chosen accommodation is £_______ per week.",
                            "answer": "145"
                        }
                    ]
                }
            ]
        }

    def _get_fallback_writing_test(self, test_type):
        """Return a pre-made fallback writing test in case the API fails"""
        if test_type == 'academic':
            return {
                "task1": {
                    "title": "Task 1",
                    "instructions": "The chart below shows the percentage of households with access to the internet in three different countries between 2000 and 2020.\n\nSummarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                    "chart_data": {
                        "countries": ["USA", "Japan", "Brazil"],
                        "years": [2000, 2005, 2010, 2015, 2020],
                        "percentages": {
                            "USA": [42, 58, 71, 83, 92],
                            "Japan": [30, 52, 78, 86, 91],
                            "Brazil": [8, 16, 35, 58, 74]
                        }
                    },
                    "word_count": 150
                },
                "task2": {
                    "title": "Task 2",
                    "instructions": "Some people believe that universities should focus more on academic subjects, while others think they should also teach practical skills for future employment.\n\nDiscuss both views and give your own opinion.",
                    "word_count": 250
                }
            }
        else:  # general
            return {
                "task1": {
                    "title": "Task 1",
                    "instructions": "You recently stayed at a hotel and were not satisfied with the service. Write a letter to the hotel manager. In your letter:\n- Explain when you stayed at the hotel\n- Describe the problems you experienced\n- Say what action you would like the manager to take",
                    "word_count": 150
                },
                "task2": {
                    "title": "Task 2",
                    "instructions": "In many countries, the number of people who continue working beyond the traditional retirement age is increasing.\n\nWhat are the reasons for this trend? Do you think this is a positive or negative development?",
                    "word_count": 250
                }
            }
