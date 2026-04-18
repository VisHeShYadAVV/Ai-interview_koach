import os
import json
import urllib.request
import urllib.error

class OpenAIService:
    # Constants for difficulty progression
    MIN_QUESTIONS_FOR_ADJUSTMENT = 4
    ROLLING_WINDOW_SIZE = 5
    PROMOTE_THRESHOLD = 0.80  # 80% accuracy to promote difficulty (stricter)
    DEMOTE_THRESHOLD = 0.40   # 40% accuracy to demote difficulty
    
    # Constants for answer evaluation
    MIN_ANSWER_LENGTH = 10
    POSITIVE_INDICATORS = ["correct", "excellent", "great", "good", "right", "accurate", "well done", "perfect"]
    NEGATIVE_INDICATORS = ["incorrect", "wrong", "not quite", "missing", "error", "mistake", "need to", "should have"]
    
    # OpenAI REST API configuration
    OPENAI_API_BASE = "https://api.openai.com/v1"
    OPENAI_MODEL = "gpt-3.5-turbo"  # Stable, widely available model for chat
    ADAPTIVE_DIFFICULTIES = {"easy", "medium", "hard"}
    START_KEYWORDS = {"start", "begin", "start interview", "begin interview", "lets start", "let's start", "ready", "start now"}
    FOLLOW_UP_HINTS = ["hint", "explain", "clarify", "repeat", "rephrase", "example", "what do you mean", "can you", "help me"]
    
    # Domain constraints to prevent drift - strictly enforce topic boundaries
    DOMAIN_CONSTRAINTS = {
        "DSA": "Data Structures and Algorithms ONLY. Topics: arrays, linked lists, trees, graphs, sorting, searching, dynamic programming, recursion, time/space complexity. NO other subjects.",
        "ML": "Machine Learning ONLY. Topics: supervised/unsupervised learning, neural networks, regression, classification, clustering, deep learning, model training. NO other subjects.",
        "DBMS": "Database Management Systems ONLY. Topics: SQL, relational databases, normalization, transactions, indexing, queries, NoSQL. NO other subjects.",
        "OS": "Operating Systems ONLY. Topics: processes, threads, scheduling, memory management, file systems, deadlocks, synchronization. NO other subjects.",
        "English": "English Language ONLY. Topics: grammar, vocabulary, comprehension, writing, speaking, sentence structure, tenses, punctuation. NO programming, NO computer science, NO technical topics.",
        "Botany": "Botany and Plant Biology ONLY. Topics: plant structure, photosynthesis, plant taxonomy, ecology, reproduction, physiology. NO other sciences, NO technical topics.",
        "Math": "Mathematics ONLY. Topics: algebra, calculus, geometry, trigonometry, statistics, number theory, equations. NO programming, NO computer science."
    }
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.conversation_history = []
        self.question_history = []  # Track recent questions for difficulty progression
        self.current_difficulty = "Easy"  # Start with Easy difficulty
        self.interview_started = False
    
    def _update_difficulty(self, is_correct: bool):
        """
        Update difficulty based on recent performance using a rolling window.
        Maintains 4-5 recent questions and adjusts difficulty gradually.
        Only promotes with sustained high accuracy, prevents promotion on wrong answers.
        """
        # Add the result to question history
        self.question_history.append(is_correct)
        
        # Keep only the last N questions
        if len(self.question_history) > self.ROLLING_WINDOW_SIZE:
            self.question_history.pop(0)
        
        # Need at least MIN_QUESTIONS_FOR_ADJUSTMENT to start adjusting
        if len(self.question_history) < self.MIN_QUESTIONS_FOR_ADJUSTMENT:
            return
        
        # Calculate accuracy ratio
        correct_count = sum(self.question_history)
        total_count = len(self.question_history)
        accuracy = correct_count / total_count
        
        # Check if the most recent answer was correct
        recent_answer_correct = self.question_history[-1]
        
        # Stricter difficulty progression rules:
        # 1. Can only promote if recent answer was correct AND high sustained accuracy
        # 2. Wrong answers prevent promotion regardless of historical accuracy
        # 3. Mixed performance (between thresholds) keeps difficulty unchanged
        
        if accuracy >= self.PROMOTE_THRESHOLD and recent_answer_correct:
            # Only promote if both conditions met: high accuracy AND recent answer correct
            if self.current_difficulty == "Easy":
                self.current_difficulty = "Medium"
            elif self.current_difficulty == "Medium":
                self.current_difficulty = "Hard"
        elif accuracy <= self.DEMOTE_THRESHOLD:
            # Demote on consistently low accuracy
            if self.current_difficulty == "Hard":
                self.current_difficulty = "Medium"
            elif self.current_difficulty == "Medium":
                self.current_difficulty = "Easy"
        # else: Mixed performance (0.40 < accuracy < 0.80) - keep difficulty unchanged
    
    def generate_interview_response(self, user_message: str, domain: str, difficulty: str) -> str:
        """
        Generate AI interview coach response based on user input.
        
        Args:
            user_message: The user's answer or question
            domain: Technical domain (DSA, ML, DBMS, OS, English, Botany, Math)
            difficulty: Question difficulty (Easy, Medium, Hard) - for initial preference
        
        Returns:
            AI generated interview feedback
        """
        requested_difficulty = difficulty
        use_adaptive_difficulty = (
            requested_difficulty.lower() in self.ADAPTIVE_DIFFICULTIES and
            len(self.question_history) >= self.MIN_QUESTIONS_FOR_ADJUSTMENT
        )

        # Keep custom/numeric difficulties fixed; only auto-adjust canonical Easy/Medium/Hard
        active_difficulty = self.current_difficulty if use_adaptive_difficulty else requested_difficulty
        
        interaction_type = self._classify_interaction(user_message)

        # Get domain-specific constraint from class constant
        domain_constraint = self.DOMAIN_CONSTRAINTS.get(domain, f"{domain} ONLY. Do not introduce topics from other domains.")

        if interaction_type == "start":
            system_prompt = f"""You are SmartKoach, an AI Interview Coach.

CRITICAL DOMAIN CONSTRAINT:
Your response must be EXCLUSIVELY about: {domain_constraint}

DIFFICULTY CONSTRAINT:
The first interview question must be at EXACTLY {active_difficulty} level.

This is the interview initialization step. Do NOT evaluate the user's message.
Ask the first interview question directly in {domain} at {active_difficulty} level.
Keep the response concise and interview-focused.
"""
        elif interaction_type == "follow_up":
            system_prompt = f"""You are SmartKoach, an AI Interview Coach. You MUST strictly follow these rules:

CRITICAL DOMAIN CONSTRAINT:
Your response must be EXCLUSIVELY about: {domain_constraint}

DIFFICULTY CONSTRAINT:
Keep all interview questions at EXACTLY {active_difficulty} level.

This is a follow-up interaction. The user is asking for clarification/hints.
Do NOT grade this message as an answer.
Provide a concise clarification/hint and then continue the interview with one question in {domain} at {active_difficulty} level.
"""
        else:
            system_prompt = f"""You are SmartKoach, an AI Interview Coach. You MUST strictly follow these rules:

CRITICAL DOMAIN CONSTRAINT:
Your questions and feedback must be EXCLUSIVELY about: {domain_constraint}

DIFFICULTY CONSTRAINT:
All questions must be at EXACTLY {active_difficulty} difficulty level. Do NOT change or escalate difficulty on your own.

Your role is to:
1. Evaluate the user's answer for correctness, clarity, and structure (ONLY within {domain})
2. Provide concise, actionable feedback on their response
3. Generate the NEXT interview question STRICTLY in {domain} at {active_difficulty} difficulty level

STRICT GUIDELINES:
- Questions MUST be about {domain} and NOTHING ELSE
- Difficulty MUST be {active_difficulty} - do not adjust it
- Be clear and deterministic in your responses
- Avoid hallucinations or made-up information
- Focus on evaluating accuracy within {domain}
- Suggest specific improvements where needed
- Keep responses concise and actionable

Response format:
- First, evaluate the previous answer if provided (1-2 sentences on correctness)
- Second, provide actionable feedback (1-2 sentences)
- Third, ask the next question STRICTLY in {domain} at {active_difficulty} level

REMEMBER: The controller has selected {domain} at {active_difficulty} difficulty. You MUST respect these exact constraints.
"""

        # Build conversation context as a string for the user message
        conversation_context = ""
        if self.conversation_history:
            conversation_context = "Previous conversation:\n"
            for msg in self.conversation_history[-5:]:  # Keep last 5 exchanges
                conversation_context += f"{msg}\n"
            conversation_context += "\n"
        
        # Combine context with current message
        user_content = conversation_context + f"Current message: {user_message}"
        
        try:
            # Call OpenAI REST API directly
            ai_response = self._call_openai_api(system_prompt, user_content)
            
            if interaction_type == "answer":
                # Attempt to detect if the answer was correct based on AI feedback
                # Simple heuristic: look for positive indicators in the response
                is_correct = self._evaluate_correctness(ai_response, user_message)
                self._update_difficulty(is_correct)
            else:
                self.interview_started = True
            
            # Store conversation history
            self.conversation_history.append(f"User: {user_message}")
            self.conversation_history.append(f"SmartKoach: {ai_response}")
            
            return ai_response
        except Exception as e:
            # Log the error internally (in production, use proper logging)
            print(f"Error calling OpenAI API: {str(e)}")
            return "I'm having trouble connecting to the AI service. Please try again in a moment."
    
    def _call_openai_api(self, system_prompt: str, user_content: str) -> str:
        """
        Call OpenAI Chat Completions API.
        
        Args:
            system_prompt: The system message defining the AI's role
            user_content: The user message content including conversation context
            
        Returns:
            The AI-generated response text
        """
        url = f"{self.OPENAI_API_BASE}/chat/completions"
        
        # Prepare request payload for Chat Completions API with proper message structure
        payload = {
            "model": self.OPENAI_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        # Convert payload to JSON
        data = json.dumps(payload).encode('utf-8')
        
        # Create request with API key in Authorization header
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
        )
        
        try:
            # Make the request
            with urllib.request.urlopen(req) as response:
                try:
                    result = json.loads(response.read().decode('utf-8'))
                except json.JSONDecodeError as e:
                    raise Exception(f"Failed to parse OpenAI API response as JSON: {str(e)}")
                
                # Extract text from response
                if 'choices' in result and len(result['choices']) > 0:
                    choice = result['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        return choice['message']['content'].strip()
                
                # Provide detailed error with response structure
                raise ValueError(f"Unexpected API response format. Response structure: {json.dumps(result, indent=2)}")
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"OpenAI API HTTP error {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"OpenAI API connection error: {str(e)}")
    
    def _evaluate_correctness(self, ai_response: str, user_message: str) -> bool:
        """
        Heuristic to evaluate if the answer was correct based on AI feedback.
        Conservative approach: defaults to incorrect unless clear positive indicators.
        This ensures wrong answers explicitly count as negative signals.
        """
        # Skip evaluation for very short messages (likely just questions/greetings)
        # Default to False (incorrect) to prevent undeserved promotions
        if len(user_message) < self.MIN_ANSWER_LENGTH:
            return False
        
        # If user is asking a question, don't count it (neutral - but default to False to be safe)
        if "?" in user_message or any(q in user_message.lower() for q in ["give me", "ask me", "what is", "how do", "can you"]):
            return False
        
        ai_lower = ai_response.lower()
        
        # Count positive and negative indicators
        positive_count = sum(1 for word in self.POSITIVE_INDICATORS if word in ai_lower)
        negative_count = sum(1 for word in self.NEGATIVE_INDICATORS if word in ai_lower)
        
        # Stricter evaluation logic:
        # - Need MORE positive than negative indicators to be considered correct
        # - If equal or no clear indicators, default to incorrect (conservative)
        # - This prevents ambiguous responses from counting as correct
        return positive_count > negative_count and positive_count > 0

    def _classify_interaction(self, user_message: str) -> str:
        normalized = user_message.strip().lower()

        if not self.interview_started:
            if normalized in self.START_KEYWORDS:
                return "start"
            if len(normalized.split()) <= 5:
                return "start"
            return "start"

        if self._is_follow_up_message(normalized):
            return "follow_up"
        return "answer"

    def _is_follow_up_message(self, normalized_message: str) -> bool:
        if "?" in normalized_message and len(normalized_message.split()) <= 25:
            return True
        return any(hint in normalized_message for hint in self.FOLLOW_UP_HINTS)
    
    def reset_conversation(self):
        """Reset conversation history and difficulty progression"""
        self.conversation_history = []
        self.question_history = []
        self.current_difficulty = "Easy"
        self.interview_started = False
