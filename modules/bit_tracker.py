"""
BhoolamMind v1.5 - Bit Tracker
Identifies potential comedy gold and funny patterns from Bhoola's thoughts
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple
from .database import BhoolamindDB

class BitTracker:
    def __init__(self):
        self.db = BhoolamindDB()
        
        # Comedy pattern indicators
        self.humor_patterns = {
            "wordplay": [
                r"why do.*say.*\?",
                r"kya.*hoti hai\?",
                r"matlab.*kya.*",
                r".*sounds like.*",
                r".*rhymes with.*"
            ],
            "observations": [
                r"maine.*observe.*kiya",
                r"funny thing.*",
                r"weird.*hai.*",
                r"strange.*behavior.*",
                r"logically.*makes no sense"
            ],
            "stoner_logic": [
                r"think about it.*",
                r"technically.*",
                r"philosophically.*",
                r"if you really.*",
                r"what if.*"
            ],
            "bhoola_moments": [
                r"bhool.*gaya.*",
                r"memory.*loss.*",
                r"kya bol.*raha.*tha.*",
                r"wait.*what.*",
                r"abhi.*kya.*kar.*raha.*tha"
            ],
            "hinglish_gold": [
                r".*yaar.*",
                r".*matlab.*",
                r".*basically.*",
                r".*obviously.*",
                r".*literally.*"
            ]
        }
        
        # Emotional intensity markers
        self.intensity_markers = {
            "high": ["hilarious", "brilliant", "genius", "fucking", "amazing"],
            "medium": ["funny", "interesting", "weird", "strange"],
            "low": ["okay", "maybe", "perhaps", "slightly"]
        }
    
    def analyze_text(self, text: str, source: str = "manual") -> Dict:
        """Analyze text for comedy potential and patterns"""
        analysis = {
            "text": text,
            "source": source,
            "bit_worthy": False,
            "humor_categories": [],
            "intensity": 1,
            "tags": [],
            "patterns_found": [],
            "timestamp": datetime.now().isoformat()
        }
        
        text_lower = text.lower()
        
        # Check for humor patterns
        for category, patterns in self.humor_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    analysis["humor_categories"].append(category)
                    analysis["patterns_found"].append({
                        "category": category,
                        "pattern": pattern,
                        "match": re.search(pattern, text_lower).group()
                    })
        
        # Calculate intensity
        intensity_score = 1
        for level, markers in self.intensity_markers.items():
            for marker in markers:
                if marker in text_lower:
                    if level == "high":
                        intensity_score = max(intensity_score, 3)
                    elif level == "medium":
                        intensity_score = max(intensity_score, 2)
        
        analysis["intensity"] = intensity_score
        
        # Determine if bit-worthy
        bit_worthy_criteria = [
            len(analysis["humor_categories"]) >= 2,  # Multiple humor types
            intensity_score >= 2,  # Medium+ intensity
            len(text.split()) >= 8,  # Substantial content
            any(cat in ["wordplay", "observations"] for cat in analysis["humor_categories"])
        ]
        
        analysis["bit_worthy"] = sum(bit_worthy_criteria) >= 2
        
        # Generate tags
        tags = []
        tags.extend(analysis["humor_categories"])
        if analysis["bit_worthy"]:
            tags.append("bit-worthy")
        if "bhoola_moments" in analysis["humor_categories"]:
            tags.append("bhoola-moment")
        if intensity_score >= 3:
            tags.append("high-energy")
        
        analysis["tags"] = ",".join(tags)
        
        return analysis
    
    def process_and_store(self, text: str, source: str = "manual") -> int:
        """Analyze text and store in database"""
        analysis = self.analyze_text(text, source)
        
        # Store in database
        interaction_id = self.db.add_interaction(
            text=analysis["text"],
            source=analysis["source"],
            tags=analysis["tags"],
            emotion="amused" if analysis["bit_worthy"] else None,
            intensity=analysis["intensity"],
            bit_worthy=analysis["bit_worthy"]
        )
        
        # Update pattern frequencies
        for pattern_info in analysis["patterns_found"]:
            self.db.update_pattern_frequency(
                pattern_text=pattern_info["match"],
                pattern_type=pattern_info["category"]
            )
        
        # Log the analysis
        if analysis["bit_worthy"]:
            print(f"🎭 BIT WORTHY DETECTED: {text[:50]}...")
            print(f"   Categories: {', '.join(analysis['humor_categories'])}")
            print(f"   Intensity: {analysis['intensity']}/3")
        
        return interaction_id
    
    def get_todays_bits(self) -> List[Dict]:
        """Get today's bit-worthy content"""
        return self.db.get_bit_worthy_collection()
    
    def analyze_humor_evolution(self, days: int = 30) -> Dict:
        """Analyze how humor patterns are evolving"""
        recent_interactions = self.db.get_recent_interactions(limit=100, days=days)
        
        evolution = {
            "period_days": days,
            "total_interactions": len(recent_interactions),
            "bit_worthy_count": 0,
            "category_trends": {},
            "intensity_distribution": {"low": 0, "medium": 0, "high": 0},
            "top_patterns": []
        }
        
        for interaction in recent_interactions:
            if interaction[6]:  # bit_worthy column
                evolution["bit_worthy_count"] += 1
            
            # Parse tags for categories
            if interaction[3]:  # tags column
                tags = interaction[3].split(",")
                for tag in tags:
                    tag = tag.strip()
                    if tag in evolution["category_trends"]:
                        evolution["category_trends"][tag] += 1
                    else:
                        evolution["category_trends"][tag] = 1
            
            # Intensity distribution
            intensity = interaction[5]  # intensity column
            if intensity == 1:
                evolution["intensity_distribution"]["low"] += 1
            elif intensity == 2:
                evolution["intensity_distribution"]["medium"] += 1
            else:
                evolution["intensity_distribution"]["high"] += 1
        
        return evolution
    
    def suggest_bit_development(self, text: str) -> List[str]:
        """Suggest ways to develop a bit further"""
        analysis = self.analyze_text(text)
        suggestions = []
        
        if "wordplay" in analysis["humor_categories"]:
            suggestions.append("Expand the wordplay - find more similar sounding words")
            suggestions.append("Try the opposite perspective - what if the word made perfect sense?")
        
        if "observations" in analysis["humor_categories"]:
            suggestions.append("Add personal experience - when did you first notice this?")
            suggestions.append("Exaggerate the observation - what's the most extreme version?")
        
        if "stoner_logic" in analysis["humor_categories"]:
            suggestions.append("Follow the logic to its absurd conclusion")
            suggestions.append("Add 'scientific' explanations that make no sense")
        
        if "bhoola_moments" in analysis["humor_categories"]:
            suggestions.append("Chain memory failures - what else did you forget?")
            suggestions.append("Make it relatable - everyone has these moments")
        
        if not suggestions:
            suggestions.append("Try connecting to a personal story")
            suggestions.append("Add a unexpected twist or punchline")
            suggestions.append("Use Hinglish mixing for added authenticity")
        
        return suggestions

# Test the bit tracker
if __name__ == "__main__":
    tracker = BitTracker()
    
    # Test samples
    test_texts = [
        "Yaar, why do people say 'break a leg' for good luck? Matlab bone fracture good luck hai?",
        "Maine observe kiya hai - every time I look for my phone, it's in my hand",
        "Think about it, if mirrors reverse left and right, why not up and down?",
        "Bhool gaya main kya bolne wala tha... wait, that's literally the bit",
        "Gotu kola liya but still can't remember where I kept my keys"
    ]
    
    print("🧠 BhoolamMind Bit Tracker Test Results:\n")
    
    for text in test_texts:
        result = tracker.analyze_text(text)
        print(f"Text: {text}")
        print(f"Bit Worthy: {'✅' if result['bit_worthy'] else '❌'}")
        print(f"Categories: {', '.join(result['humor_categories'])}")
        print(f"Intensity: {result['intensity']}/3")
        print("-" * 50)
    
    print(f"\n📊 Humor Evolution Analysis:")
    evolution = tracker.analyze_humor_evolution(days=30)
    print(json.dumps(evolution, indent=2))
