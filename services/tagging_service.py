from typing import List


class TaggingService:
    """AI-powered auto-tagging service for opportunities"""
    
    # Keyword-based tagging rules (simulating AI classification)
    TAG_KEYWORDS = {
        "technology": ["tech", "software", "ai", "machine learning", "ml", "data", "cloud", "saas", "fintech", "healthtech"],
        "funding": ["funding", "investment", "capital", "seed", "series", "venture", "equity", "grant", "subsidy"],
        "accelerator": ["accelerator", "incubator", "mentorship", "cohort", "program"],
        "competition": ["competition", "hackathon", "challenge", "contest", "pitch"],
        "women": ["women", "female", "ladies", "women-led", "women-founded"],
        "social": ["social", "impact", "sustainability", "climate", "environment", "green"],
        "healthcare": ["health", "medical", "pharma", "biotech", "healthcare"],
        "education": ["education", "edtech", "learning", "student", "school"],
        "agriculture": ["agri", "farm", "agriculture", "rural"],
        "retail": ["retail", "ecommerce", "e-commerce", "consumer", "b2c"],
    }
    
    @classmethod
    def generate_tags(cls, title: str, description: str = "", existing_tags: str = "") -> str:
        """
        Generate relevant tags based on title and description
        
        Args:
            title: Opportunity title
            description: Additional description text
            existing_tags: Existing tags to preserve
            
        Returns:
            Comma-separated string of tags
        """
        text = f"{title} {description}".lower()
        tags = set()
        
        # Preserve existing tags
        if existing_tags:
            tags.update([tag.strip().lower() for tag in existing_tags.split(",")])
        
        # Generate new tags based on keywords
        for tag, keywords in cls.TAG_KEYWORDS.items():
            if tag not in tags:  # Don't duplicate existing tags
                for keyword in keywords:
                    if keyword in text:
                        tags.add(tag)
                        break
        
        return ",".join(sorted(tags)) if tags else "general"
    
    @classmethod
    def classify_stage(cls, title: str, description: str = "") -> str:
        """
        Classify startup stage based on opportunity details
        
        Args:
            title: Opportunity title
            description: Additional description text
            
        Returns:
            Startup stage classification
        """
        text = f"{title} {description}".lower()
        
        stage_rules = [
            ("idea", ["idea", "concept", "prototype", "mvp", "early"]),
            ("seed", ["seed", "pre-seed", "angel", "early stage", "startup"]),
            ("series-a", ["series a", "growth", "scaling", "post-seed"]),
            ("series-b", ["series b", "expansion", "late stage"]),
            ("series-c", ["series c", "ipo", "exit", "mature"]),
            ("any", ["any stage", "all stages", "open"]),
        ]
        
        for stage, keywords in stage_rules:
            for keyword in keywords:
                if keyword in text:
                    return stage
        
        return "any"
    
    @classmethod
    def detect_funding_range(cls, title: str, description: str = "") -> str:
        """
        Detect funding range from opportunity details
        
        Args:
            title: Opportunity title
            description: Additional description text
            
        Returns:
            Funding range classification
        """
        text = f"{title} {description}".lower()
        
        funding_rules = [
            ("up-to-1L", ["up to 1 lakh", "₹1 lakh", "100000", "1,00,000"]),
            ("1L-5L", ["1 lakh to 5 lakh", "₹1-5 lakh", "100000-500000"]),
            ("5L-10L", ["5 lakh to 10 lakh", "₹5-10 lakh", "500000-1000000"]),
            ("10L-25L", ["10 lakh to 25 lakh", "₹10-25 lakh", "10-25 lakhs"]),
            ("25L-50L", ["25 lakh to 50 lakh", "₹25-50 lakh", "25-50 lakhs"]),
            ("50L-1Cr", ["50 lakh to 1 crore", "₹50 lakh-1 crore", "50 lakhs-1 crore"]),
            ("1Cr-5Cr", ["1 crore to 5 crore", "₹1-5 crore", "1-5 crores"]),
            ("5Cr-10Cr", ["5 crore to 10 crore", "₹5-10 crore", "5-10 crores"]),
            ("10Cr+", ["10 crore", "₹10 crore+", "10+ crores"]),
            ("not-specified", ["not specified", "see source", "tbd"]),
        ]
        
        for range_name, keywords in funding_rules:
            for keyword in keywords:
                if keyword in text:
                    return range_name
        
        return "not-specified"
    
    @classmethod
    def detect_location_type(cls, location: str) -> str:
        """
        Detect if opportunity is remote, on-site, or hybrid
        
        Args:
            location: Location string from scraper
            
        Returns:
            "remote", "on-site", "hybrid", or "unknown"
        """
        location_lower = location.lower()
        
        if "remote" in location_lower or "virtual" in location_lower or "online" in location_lower:
            return "remote"
        elif "hybrid" in location_lower or "flexible" in location_lower:
            return "hybrid"
        elif location_lower and location_lower not in ["global", "worldwide", "see source"]:
            return "on-site"
        
        return "unknown"
