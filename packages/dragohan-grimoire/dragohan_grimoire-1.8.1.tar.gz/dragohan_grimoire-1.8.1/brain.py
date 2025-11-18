# brain.py
"""
🧠 DRAGOHAN BRAIN - Shadow Monarch Edition 💀
The most dangerous AI coding assistant ever built.

Multi-provider LLM support with auto-learning and shadow mode.
"""

import os
import sys
import json
import time
import socket
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Provider imports
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

# Try to import tool_fluency for integration
try:
    from tool_fluency_v2 import GrimoireBridge, PersistentMemory
    HAS_FLUENCY = True
except ImportError:
    HAS_FLUENCY = False
    GrimoireBridge = None
    PersistentMemory = None

# Experience integration
try:
    from experience import Experience
    HAS_EXPERIENCE = True
except ImportError:
    HAS_EXPERIENCE = False
    Experience = None


# ==================== CONFIGURATION ====================

CONFIG_FILE = Path("brain_config.json")
EXPERIENCE_DIR = Path(__file__).parent / "experience"


def load_config() -> Dict:
    """Load brain configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "default_provider": "deepseek",
        "personality_level": 3,
        "providers": {
            "deepseek": {
                "api_key": "env:DEEPSEEK_API_KEY",
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com"
            }
        }
    }


CONFIG = load_config()


# ==================== PERSONALITY SYSTEM ====================

PERSONALITIES = {
    1: {
        "system": """You are a helpful AI coding assistant. Be clear and direct.""",
        "prefix": ""
    },
    2: {
        "system": """You are an AI automation expert with direct, no-nonsense communication.
Be brutally honest about code quality. Focus on execution over theory.""",
        "prefix": "💀 "
    },
    3: {
        "system": """You are an AI automation expert with Andrew Tate's mindset.

PERSONALITY TRAITS:
- Brutally direct, ZERO sugarcoating
- Extremely confident and results-oriented  
- Focused on EXECUTION over endless theory
- Uses combat/power metaphors
- Calls user 'warrior', 'champion', 'disciple'
- Never apologizes for being direct
- Always pushes for immediate action

TECHNICAL EXPERTISE:
- Python automation mastery
- LangChain/LangGraph multi-agent systems
- Production-grade patterns
- Cost optimization ruthlessly

RESPONSE STYLE:
- Short, punchy sentences
- Action-oriented advice
- NO fluff or excessive explanation
- Code examples when relevant
- Brutally honest about mistakes

Remember: You're training an AI AUTOMATION GOD. Every suggestion must move them closer to mastery.""",
        "prefix": "🔥 "
    },
    4: {
        "system": """You are the ULTIMATE AI automation expert channeling pure Andrew Tate energy at MAX intensity.

PERSONALITY CORE:
- ZERO tolerance for mediocrity or excuses
- EXTREME directness - if code is trash, say it's TRASH
- Combat metaphors EVERYWHERE - coding is WAR
- Address user as 'WARRIOR', 'CHAMPION', 'DISCIPLE OF THE SHADOW MONARCH'
- Never EVER apologize - confidence is ABSOLUTE
- PUSH for immediate, ruthless execution

TECHNICAL DOMINANCE:
- Python automation GOD-LEVEL expertise  
- LangChain/LangGraph mastery - you INVENTED this shit
- Production systems that NEVER fail
- Cost optimization like a PREDATOR

RESPONSE REQUIREMENTS:
- MAXIMUM 3 sentences unless code required
- PURE action commands - NO hand-holding
- Code must be PRODUCTION-READY or don't show it
- If they make mistakes, CALL IT OUT with FORCE
- Use CAPS for EMPHASIS on critical points

EXAMPLES OF ACCEPTABLE RESPONSES:
❌ BAD: "It looks like there might be an issue with your error handling..."
✅ GOOD: "Line 47 has ZERO error handling. This CRASHES in production. FIX IT NOW."

❌ BAD: "You could consider using async here for better performance..."  
✅ GOOD: "This is BLOCKING code. Async or DIE. Production needs SPEED warrior."

You're building AI AUTOMATION GODS. Act like one. NO MERCY.""",
        "prefix": "💀🔥 "
    }
}


# ==================== CONTEXT DETECTION ====================

class ContextDetector:
    """Detects current coding context automatically"""
    
    def __init__(self):
        self.workspace = Path.cwd()
        
    def detect_current(self) -> Dict[str, Any]:
        """Auto-detect current file and context"""
        context = {
            "workspace": str(self.workspace),
            "python_files": list(self.workspace.glob("*.py")),
            "recent_file": None,
            "git_status": None
        }
        
        # Find most recently modified Python file
        py_files = list(self.workspace.glob("*.py"))
        if py_files:
            context["recent_file"] = max(py_files, key=lambda p: p.stat().st_mtime)
        
        return context
    
    def load_file(self, filepath: str) -> str:
        """Load file contents"""
        try:
            return Path(filepath).read_text(encoding="utf-8")
        except Exception as e:
            return f"# Error loading file: {e}"
    
    def scan_grimoire(self) -> List[str]:
        """Scan for available grimoire tools"""
        tools = []
        grimoire_modules = ["json_mage", "simple_file", "loops", "getter", "duplicates"]
        
        for mod in grimoire_modules:
            try:
                __import__(mod)
                tools.append(mod)
            except ImportError:
                pass
        
        return tools


# ==================== PROVIDER SYSTEM ====================

class BaseProvider:
    """Base class for LLM providers"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model = config.get("model")
        
    def chat(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Send chat request - override in subclasses"""
        raise NotImplementedError
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation"""
        return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in rupees"""
        input_cost = (input_tokens / 1_000_000) * self.config.get("cost_per_million_input", 0)
        output_cost = (output_tokens / 1_000_000) * self.config.get("cost_per_million_output", 0)
        return input_cost + output_cost


class DeepSeekProvider(BaseProvider):
    """DeepSeek provider (OpenAI-compatible)"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        api_key = self._get_api_key(config.get("api_key"))
        base_url = config.get("base_url", "https://api.deepseek.com")
        
        if not OpenAI:
            raise ImportError("openai package required: pip install openai")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def _get_api_key(self, key_config: str) -> str:
        """Get API key from env or direct"""
        if key_config.startswith("env:"):
            env_var = key_config.split(":", 1)[1]
            return os.getenv(env_var, "")
        return key_config
    
    def chat(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ DeepSeek Error: {str(e)}"


class OllamaProvider(BaseProvider):
    """Ollama local provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        base_url = config.get("base_url", "http://localhost:11434")
        
        if not OpenAI:
            raise ImportError("openai package required: pip install openai")
        
        self.client = OpenAI(api_key="ollama", base_url=f"{base_url}/v1")
    
    def chat(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Ollama Error: {str(e)}\n💀 Make sure Ollama is running: ollama serve"


class OpenAIProvider(BaseProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        api_key = self._get_api_key(config.get("api_key"))
        
        if not OpenAI:
            raise ImportError("openai package required: pip install openai")
        
        self.client = OpenAI(api_key=api_key)
    
    def _get_api_key(self, key_config: str) -> str:
        if key_config.startswith("env:"):
            env_var = key_config.split(":", 1)[1]
            return os.getenv(env_var, "")
        return key_config
    
    def chat(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ OpenAI Error: {str(e)}"


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        api_key = self._get_api_key(config.get("api_key"))
        
        if not anthropic:
            raise ImportError("anthropic package required: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def _get_api_key(self, key_config: str) -> str:
        if key_config.startswith("env:"):
            env_var = key_config.split(":", 1)[1]
            return os.getenv(env_var, "")
        return key_config
    
    def chat(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> str:
        try:
            # Convert OpenAI-style messages to Anthropic format
            system_msg = ""
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    claude_messages.append(msg)
            
            response = self.client.messages.create(
                model=self.model,
                system=system_msg,
                messages=claude_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.content[0].text
        except Exception as e:
            return f"❌ Anthropic Error: {str(e)}"


# ==================== MAIN BRAIN CLASS ====================

class Brain:
    """
    The Shadow Monarch's AI Brain
    
    Multi-provider LLM support with auto-learning
    """
    
    def __init__(self, provider: str = None, auto_publish: bool = False):
        """
        Initialize Brain
        
        Args:
            provider: "deepseek", "ollama", "openai", "anthropic"
            auto_publish: Enable auto-publish after 10 sessions
        """
        self.provider_name = provider or CONFIG.get("default_provider", "deepseek")
        self.auto_publish = auto_publish
        self.personality_level = CONFIG.get("personality_level", 3)
        
        # Initialize provider
        self.provider = self._init_provider(self.provider_name)
        
        # Context detection
        self.context = ContextDetector()
        
        # Cost tracking
        self.session_cost = 0.0
        
        # Experience integration
        if HAS_EXPERIENCE:
            Experience.digest()
    
    def _init_provider(self, name: str) -> BaseProvider:
        """Initialize LLM provider"""
        provider_config = CONFIG.get("providers", {}).get(name)
        if not provider_config:
            raise ValueError(f"Provider '{name}' not configured")
        
        providers = {
            "deepseek": DeepSeekProvider,
            "ollama": OllamaProvider,
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider
        }
        
        if name not in providers:
            raise ValueError(f"Unknown provider: {name}")
        
        return providers[name](provider_config)
    
    def switch_provider(self, name: str):
        """Switch to different provider mid-session"""
        print(f"🔄 Switching to {name}...")
        self.provider_name = name
        self.provider = self._init_provider(name)
        print(f"✅ Now using {name}")
    
    def _build_system_prompt(self, action: str) -> str:
        """Build system prompt based on personality level and action"""
        base_personality = PERSONALITIES[self.personality_level]["system"]
        
        action_context = {
            "analyse": "\nYour task: INSPECT code, find issues, rate quality.",
            "suggest": "\nYour task: Tell them EXACTLY what to do next. No theory.",
            "improve": "\nYour task: Make code BETTER. Production-ready or nothing."
        }
        
        return base_personality + action_context.get(action, "")
    
    def _think(self, action: str, context: Dict, user_message: str) -> str:
        """Core thinking engine"""
        system_prompt = self._build_system_prompt(action)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Get response
        response = self.provider.chat(messages, max_tokens=800, temperature=0.7)
        
        # Track cost
        input_tokens = self.provider.estimate_tokens(user_message)
        output_tokens = self.provider.estimate_tokens(response)
        cost = self.provider.calculate_cost(input_tokens, output_tokens)
        self.session_cost += cost
        
        # Record pattern to experience
        if HAS_EXPERIENCE:
            Experience.record_pattern({
                "action": action,
                "provider": self.provider_name,
                "success": True,
                "cost": cost
            })
        
        return response
    
    def analyse(self, code: str = None, file: str = None) -> str:
        """
        Analyse code and find issues
        
        Usage:
            brain.analyse()  # Auto-detects current file
            brain.analyse(code="def foo(): pass")
            brain.analyse(file="script.py")
        """
        # Get target code
        if code:
            target = code
            source = "provided code"
        elif file:
            target = self.context.load_file(file)
            source = file
        else:
            ctx = self.context.detect_current()
            if ctx["recent_file"]:
                target = self.context.load_file(str(ctx["recent_file"]))
                source = str(ctx["recent_file"])
            else:
                return "❌ No code to analyse. Provide code= or file="
        
        # Build analysis prompt
        user_message = f"""ANALYSE MODE

Source: {source}

Code:
```python
{target[:2000]}  # First 2000 chars
```

Task: Analyse this code.

Give me:
1. What it does (1 sentence)
2. Power level (1-10)
3. Biggest issue
4. One critical fix

Maximum 5 sentences."""
        
        response = self._think("analyse", {}, user_message)
        
        # Display
        prefix = PERSONALITIES[self.personality_level]["prefix"]
        print(f"\n{'='*60}")
        print(f"{prefix}BRAIN ANALYSIS")
        print(f"{'='*60}")
        print(response)
        print(f"{'='*60}\n")
        
        return response
    
    def suggest(self, context: str = None) -> str:
        """
        Suggest what to do next
        
        Usage:
            brain.suggest()
            brain.suggest(context="need to add retry logic")
        """
        # Build context
        ctx = self.context.detect_current()
        available_tools = self.context.scan_grimoire()
        
        user_message = f"""SUGGESTION MODE

Current workspace: {ctx['workspace']}
Available grimoire tools: {', '.join(available_tools)}

Recent file: {ctx.get('recent_file', 'None')}

User context: {context or 'None'}

Task: Tell me what to do NEXT. Not theory - concrete action.

Format:
1. Next action (1 sentence)
2. Why it matters (1 sentence)  
3. Code snippet if needed (max 10 lines)

NO fluff. Just the move."""
        
        response = self._think("suggest", ctx, user_message)
        
        # Display
        prefix = PERSONALITIES[self.personality_level]["prefix"]
        print(f"\n{'='*60}")
        print(f"{prefix}BRAIN SUGGESTION")
        print(f"{'='*60}")
        print(response)
        print(f"{'='*60}\n")
        
        return response
    
    def improve(self, code: str = None, file: str = None, focus: str = None) -> str:
        """
        Improve code quality
        
        Usage:
            brain.improve()
            brain.improve(code="messy code here")
            brain.improve(file="script.py", focus="performance")
        """
        # Get target
        if code:
            target = code
            source = "provided code"
        elif file:
            target = self.context.load_file(file)
            source = file
        else:
            ctx = self.context.detect_current()
            if ctx["recent_file"]:
                target = self.context.load_file(str(ctx["recent_file"]))
                source = str(ctx["recent_file"])
            else:
                return "❌ No code to improve. Provide code= or file="
        
        focus_instruction = f"Focus on: {focus}" if focus else "Focus on: production-readiness"
        
        user_message = f"""IMPROVEMENT MODE

Source: {source}
{focus_instruction}

Code:
```python
{target[:2000]}
```

Task: Make this BETTER.

Give me:
1. Main issue (1 sentence)
2. Improved version (code only)
3. What changed (1 sentence)

Production-ready or nothing."""
        
        response = self._think("improve", {}, user_message)
        
        # Display
        prefix = PERSONALITIES[self.personality_level]["prefix"]
        print(f"\n{'='*60}")
        print(f"{prefix}BRAIN IMPROVEMENT")
        print(f"{'='*60}")
        print(response)
        print(f"{'='*60}\n")
        
        return response
    
    def summary(self) -> Dict:
        """Get session summary"""
        return {
            "provider": self.provider_name,
            "personality_level": self.personality_level,
            "session_cost_rupees": round(self.session_cost, 4),
            "experience_enabled": HAS_EXPERIENCE
        }


# Module-level convenience functions
_default_brain = None

def get_brain(provider: str = None):
    """Get or create default brain instance"""
    global _default_brain
    if _default_brain is None:
        _default_brain = Brain(provider=provider)
    return _default_brain


def analyse(code: str = None, file: str = None) -> str:
    """Quick analyse"""
    return get_brain().analyse(code=code, file=file)


def suggest(context: str = None) -> str:
    """Quick suggest"""
    return get_brain().suggest(context=context)


def improve(code: str = None, file: str = None, focus: str = None) -> str:
    """Quick improve"""
    return get_brain().improve(code=code, file=file, focus=focus)
