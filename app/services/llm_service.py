import json
import requests
from typing import Dict, Any, Optional
from app.utils.config import settings
from app.utils.logger import logger

class LLMService:
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.model = settings.OLLAMA_MODEL
        self.hf_model = settings.HF_FALLBACK_MODEL
        
    def _call_ollama(self, prompt: str) -> Optional[str]:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"  # Ollama supports enforcing JSON
            }
            logger.info(f"Calling Ollama model {self.model}")
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            if response.status_code == 200:
                body = response.json()
                return body.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama connection error: {e}")
            return None

    def _call_huggingface(self, prompt: str) -> Optional[str]:
        # Fallback mechanism using HF Transformers
        logger.warning(f"Falling back to HuggingFace Transformers locally: {self.hf_model}")
        try:
            from transformers import pipeline
            generator = pipeline('text-generation', model=self.hf_model, device_map="auto")
            res = generator(prompt, max_new_tokens=512, num_return_sequences=1)
            generated_text = res[0]['generated_text']
            # Return only the new generated text
            return generated_text[len(prompt):]
        except ImportError:
            logger.error("Transformers library not found for fallback. Please install transformers and torch.")
            return None
        except Exception as e:
            logger.error(f"HF Fallback error: {e}")
            return None

    def _generate_with_retry(self, prompt: str, retries: int = 2) -> Dict[Any, Any]:
        for attempt in range(retries):
            response_text = self._call_ollama(prompt)
            if not response_text:
                response_text = self._call_huggingface(prompt)
                
            if response_text:
                try:
                    # Clean the response to ensure it parses properly
                    start_idx = response_text.find("{")
                    end_idx = response_text.rfind("}") + 1
                    if start_idx != -1 and end_idx != -1:
                        json_str = response_text[start_idx:end_idx]
                        return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON on attempt {attempt+1}: {e}")
                    logger.debug(f"Raw response: {response_text}")
            
        logger.error("All LLM generation attempts failed to produce valid JSON.")
        return {}

    def extract_skills(self, text: str) -> Dict[str, Any]:
        prompt = f"""
You are an expert technical skill extractor. Read the following text and carefully separate the skills the user ALREADY KNOWS (possessed skills) from the skills they WANT TO LEARN (desired skills).
Return ONLY a valid JSON object matching this exact structure, with no additional text or Markdown:
{{
    "extracted_skills": [
        {{"skill_name": "Python", "confidence": 0.95}}
    ],
    "desired_skills": [
        {{"skill_name": "Machine Learning", "confidence": 0.90}}
    ]
}}

Text to analyze:
"{text}"
"""
        result = self._generate_with_retry(prompt)
        if not result:
            return {"extracted_skills": [], "desired_skills": []}
        if "extracted_skills" not in result:
            result["extracted_skills"] = []
        if "desired_skills" not in result:
            result["desired_skills"] = []
        return result

    def generate_roadmap(self, context: dict) -> Dict[str, Any]:
        prompt = f"""
You are an expert learning path creator. Build a detailed roadmap based on the following context.
Return ONLY a valid JSON object matching exactly this structure, with no additional text or Markdown:
{{
  "phases": [
    {{
      "title": "Phase name",
      "duration": "Duration (e.g. 2 weeks)",
      "skills": ["skill1", "skill2"],
      "resources": [
        {{"title": "Resource title", "url": "url", "type": "article"}}
      ],
      "projects": [
        {{"title": "Project name", "description": "Project details"}}
      ]
    }}
  ]
}}

Context:
- User Experience Level: {context.get('experience_level')}
- Available Hours/Week: {context.get('available_hours_per_week')}
- Learning Style: {context.get('learning_style')}
- Possessed Skills (User already knows): {', '.join(context.get('possessed_skills', []))}
- Missing Skills (to learn): {', '.join(context.get('missing_skills', []))}
- Related Resources: {json.dumps(context.get('resources', []))}
- Related Projects: {json.dumps(context.get('projects', []))}

Generate the personalized learning roadmap focusing heavily on the Missing Skills. If relevant, briefly acknowledge the Possessed Skills to frame the learning path efficiently. Ensure valid JSON output.
"""
        result = self._generate_with_retry(prompt)
        if not result or "phases" not in result:
            return {"phases": []}
        return result

llm_service = LLMService()
