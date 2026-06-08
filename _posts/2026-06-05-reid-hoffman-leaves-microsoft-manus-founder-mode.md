---
layout: post
title: "Reid Hoffman Leaves Microsoft's Board to Go \"Founder Mode\" with Startup Manus"
date: 2026-06-05
banner:
    image: /assets/images/covers/ales-nesetril-Im7lZjxeLhg-unsplash.jpg
author: zane.deng
categories: [AI Coding]
tags: [AI Agent, Founder Mode, Drug Discovery, Reid Hoffman, Manus]
---

*This article is part of the daily AI Coding newsletter. For more in-depth technical analysis and code examples, subscribe to our newsletter.*

## Introduction

Reid Hoffman, the legendary entrepreneur often dubbed "the rules-setter of Silicon Valley," has made a striking career move—leaving Microsoft's board after a decade of service to join AI drug discovery startup Manus as a co-founder. This decision marks not only a new chapter in Hoffman's personal career but also profoundly reflects the rise of "Founder Mode" as an emerging management paradigm in today's AI industry.

---

## 1. Background and Relationship Mapping

### 1.1 Reid Hoffman's Position in Silicon Valley

Reid Hoffman is one of the most influential figures in Silicon Valley, with a legendary track record:

| Company/Role | Period | Significance |
|-------------|--------|---------------|
| PayPal Early Member | 2000-2002 | Co-founded with Peter Thiel, Elon Musk |
| LinkedIn Co-founder & CEO | 2002-2008 | IPO in 2008, acquired by Microsoft for $26.2B in 2016 |
| Greylock Partners Partner | Investment career | Invested in Airbnb, Facebook, and other tech giants |
| OpenAI Early Investor | 2015-2023 | Witnessed the rise of GPT series models |
| Microsoft Board Member | 2016-2026 | Ten-year tenure, witnessed Microsoft's AI transformation |

### 1.2 Key Transaction Timeline

```
2016 ── Microsoft acquires LinkedIn for $26.2 billion
          │
          └──► Hoffman joins Microsoft's board
                    │
2019 ───────────────┴─── Microsoft invests first $1 billion in OpenAI
                              │
2023 ──────────────────────────┴─── Hoffman exits OpenAI board due to conflicts
                                        │
2023 ───────────────────────────────────┴─── Microsoft signs $650M "non-acquisition acquisition" with Inflection AI
                                                  │ (hires co-founder Mustafa Suleyman)
                                                  │
2026 ────────────────────────────────────────────┴─── Hoffman leaves Microsoft board, joins Manus
```

### 1.3 The Cumulative Effect of Conflict of Interest

Hoffman's cross-board memberships across multiple AI-related entities created governance challenges:

1. **LinkedIn Acquisition**: As the founder of the company Microsoft acquired, Hoffman received substantial proceeds
2. **OpenAI Investment**: Hoffman simultaneously served on both OpenAI's and Microsoft's boards, creating concerns about potential conflict of interest as the two companies deepened their partnership
3. **Inflection AI Deal**: Microsoft paid $650 million to "employ" the Inflection team, while Hoffman was an investor in Inflection

This layered relationship structure ultimately led Hoffman to step down from the OpenAI board in 2023.

---

## 2. Manus: A Emerging Force in AI Drug Discovery

### 2.1 Company Overview

| Item | Details |
|------|---------|
| Company Name | Manus |
| Founders | Reid Hoffman (Co-founder & Chairman), Dr. Siddhartha Mukherjee (CEO) |
| Domain | AI-powered drug discovery |
| Funding | Over $50 million (multiple seed rounds) |
| Key Investors | Reid Hoffman, General Catalyst |
| Technical Core | Move 37 AI—AI that surpasses human creativity in chemistry |

### 2.2 Move 37 AI Technical Deep-Dive

Manus's core technology is called **Move 37 AI**, a name that alludes to AI's "37th move" in the game of Go—an analogy to AlphaGo's famous move 37 that revolutionized go theory. In Go, AI discovered a move that human players had never imagined, fundamentally changing how the game is played.

**Core Capabilities of Move 37 AI:**

```python
# Pseudocode example: Move 37 AI's molecular generation logic
class Move37MolecularGenerator:
    """
    Move 37 AI Core Algorithm
    Goal: Surpass human creativity in molecular design
    """
    
    def __init__(self, target_cancer_type: str):
        self.target = target_cancer_type
        # Pre-trained on millions of known molecular structures
        self.molecule_encoder = MolecularTransformer()
        # Curiosity-driven exploration via reinforcement learning
        self.curiosity_drive = CuriosityDrivenOptimizer()
    
    def generate_novel_compound(self) -> MolecularStructure:
        # Stage 1: Target-conditional generation
        candidate = self.molecule_encoder.generate(
            target=self.target,
            constraints=ChemicalConstraints()
        )
        
        # Stage 2: Reinforcement learning optimization (beyond human intuition)
        optimized = self.curiosity_drive.optimize(
            molecule=candidate,
            reward_function=self.efficacy_score
        )
        
        # Stage 3: Synthesis feasibility validation
        if self.synthetic_accessibility(optimized) > 0.7:
            return optimized
        return self.generate_novel_compound()
```

### 2.3 Traditional vs AI-Powered Drug Discovery

| Dimension | Traditional Drug Discovery | Manus Move 37 AI |
|-----------|---------------------------|------------------|
| Development Timeline | 10-15 years | Expected 50%+ reduction |
| Cost | $2-3 billion per drug | Expected 80%+ reduction |
| Molecular Library Scale | Millions of compounds | Billions of virtual compounds |
| Target Discovery | Manual screening | AI-driven prediction |
| Creativity | Limited by human expert experience | Surpasses human intuition |

---

## 3. The Rise of "Founder Mode"

### 3.1 What is "Founder Mode"?

"Founder Mode" is a management philosophy contrasting with professional management specialization, emphasizing the founder's absolute control over company direction. This concept was reintroduced by Y Combinator founder Paul Graham in 2023 and sparked widespread discussion in Silicon Valley's startup community.

**Core Characteristics of Founder Mode:**

```python
# Founder Mode vs Professional Management Mode
class CompanyManagementModel:
    
    def founder_mode(self):
        return {
            "decision_making": "Fast, founder-led",
            "product_vision": "Founder has clear control",
            "execution": "Cross-functional direct intervention",
            "hiring": "Only hire the best",
            "meetings": "Founder high-frequency participation",
            "innovation": "Tolerate risk, encourage breakthroughs"
        }
    
    def professional_mode(self):
        return {
            "decision_making": "Hierarchical approval, committee decisions",
            "product_vision": "Interpreted by professional managers",
            "execution": "Clear departmental divisions",
            "hiring": "Hire per budget",
            "meetings": "Delegated to teams",
            "innovation": "Avoid risk, optimize existing business"
        }
```

### 3.2 Why Does Hoffman Need "Founder Mode"?

Hoffman stated in a recent episode of his Possible podcast:

> "One thing I realized in the past month is that we see Manus making such huge progress. I need to get back into founder mode."

**The Logic Behind This:**

1. **AI Startup Competition Pace**: The AI field is advancing rapidly, requiring founder-level高频介入
2. **Technical Uncertainty**: Move 37 AI is still in early stages, requiring founder to control technical direction
3. **Strategic Resource Allocation**: Resource coordination with General Catalyst requires founder perspective
4. **Investor Confidence**: Hoffman's full-time involvement is crucial for subsequent fundraising

---

## 4. Implications for the AI Coding Domain

### 4.1 AI Agent Applications in Drug Discovery

The Manus case demonstrates successful AI Agent application in vertical domains. Here's a simplified example of AI Agent design patterns in drug discovery scenarios:

```python
"""
AI Agent Design Pattern in Drug Discovery
Reference: Manus's Move 37 AI Architecture
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class AgentState(Enum):
    ANALYZING = "analyzing"
    GENERATING = "generating"
    VALIDATING = "validating"
    SYNTHESIZING = "synthesizing"

@dataclass
class MolecularStructure:
    smiles: str  # Simplified Molecular Input Line Entry System
    binding_affinity: float
    toxicity_score: float
    synthetic_score: float

class DrugDiscoveryAgent:
    """
    Drug Discovery AI Agent
    Simulating Manus Move 37 AI's Core Process
    """
    
    def __init__(self, target_disease: str):
        self.target_disease = target_disease
        self.state = AgentState.ANALYZING
        self.knowledge_base = self._load_biomolecular_knowledge()
    
    def _load_biomolecular_knowledge(self):
        """Load biomolecular knowledge base"""
        return {}
    
    def discover_drug(self, target_protein: str) -> List[MolecularStructure]:
        """
        Core Discovery Process:
        1. Analyze target structure
        2. Generate candidate molecules
        3. Validate pharmacokinetic properties
        4. Assess synthesis feasibility
        """
        candidates = []
        
        # Stage 1: Target analysis
        protein_structure = self._analyze_protein(target_protein)
        
        # Stage 2: Generate candidate molecules (surpassing human creativity)
        raw_candidates = self._generate_molecules(protein_structure)
        
        # Stage 3: Multi-round optimization
        for candidate in raw_candidates:
            if self._passes_filters(candidate):
                candidates.append(candidate)
        
        return candidates[:10]
    
    def _analyze_protein(self, protein: str) -> dict:
        """Use AlphaFold-like models to predict protein structure"""
        return {"structure": "predicted", "binding_sites": []}
    
    def _generate_molecules(self, protein_info: dict) -> List[MolecularStructure]:
        """Use generative AI to generate new molecules"""
        return []
    
    def _passes_filters(self, molecule: MolecularStructure) -> bool:
        """Multi-dimensional filtering"""
        return (
            molecule.binding_affinity > 0.8 and
            molecule.toxicity_score < 0.2 and
            molecule.synthetic_score > 0.7
        )
```

### 4.2 Analogies in the AI Coding Domain

The Manus and Hoffman collaboration model highly resonates with development trends in the AI Coding domain:

| Domain | Drug Discovery (Manus) | AI Coding (e.g., Cursor, Copilot) |
|--------|----------------------|----------------------------------|
| Core AI Capability | Molecular generation and optimization | Code generation and optimization |
| Human Creativity Role | Provide biological insights | Provide architectural design decisions |
| AI's Role | Explore chemical space | Explore code space |
| Validation Stage | Wet lab validation | Unit test validation |
| Breakthrough Potential | New drug categories | New programming paradigms |

---

## 5. Microsoft's Deep Connection with the AI Industry

### 5.1 Microsoft's AI Investment Portfolio

Hoffman's departure from Microsoft's board actually reflects the breadth and complexity of Microsoft's AI布局:

```
Microsoft AI Investment Portfolio (2015-2026)
├── OpenAI (2019 $1 billion investment, cumulative >$13 billion)
│   ├── Exclusive cloud provider for GPT series models
│   └── Core of Azure OpenAI Service
├── Inflection AI (2023 $650M "non-acquisition acquisition")
│   └── Hired co-founder Mustafa Suleyman and team
├── LinkedIn (2016 $26.2 billion acquisition)
│   └── Core asset for Microsoft's-to-B strategy
└── GitHub (2018 $7.5 billion acquisition)
    └── Copilot's carrier platform
```

### 5.2 Hoffman's "Exit" and "Entry"

| Departure | Join | Strategic Logic |
|-----------|------|----------------|
| Microsoft Board | Manus Co-founder | From investor/advisor to一线创业者 |
| OpenAI Board | - | Eliminate conflict of interest, focus on new project |
| Inflection AI Investor | - | Shift to more breakthrough-oriented Manus |
| LinkedIn Founder Identity | - | History completed, seeking new chapter |

---

## 6. Technical Deep-Dive: Why is AI Drug Discovery Exploding Now?

### 6.1 Three Technical Pillars

AI drug discovery breakthroughs are built on three major technological advances:

**1. Pretrained Large Models Applied to Molecular Representation**

```python
# Evolution of molecular representation learning
"""
Traditional method: SMILES string representation
        ↓
Evolutionary method: Molecular Graph Neural Networks (GNN)
        ↓
State-of-the-art: Molecular Language Models (Molecular LM)
         - Similar to LLM predicting tokens, predicting molecular properties
         - Captures substructure-level semantic information
"""

class MolecularLanguageModel:
    """
    Molecular Language Model Architecture
    Input: SMILES or molecular graphs
    Output: Molecular property prediction, new molecule generation
    """
    
    def __init__(self, model_size="large"):
        self.encoder = self._build_molecular_encoder()
        self.decoder = self._build_molecular_decoder()
        # Pre-trained on PubChem, ChEMBL and other large-scale chemical databases
        self.pretraining_data = "billions of molecules"
    
    def generate(self, target_property: dict) -> str:
        """Generate new molecules based on target properties"""
        pass
```

**2. Reinforcement Learning-Driven Molecular Optimization**

Traditional optimization methods are inefficient in chemical space, while reinforcement learning can:

- Efficiently explore billions of virtual compound libraries
- Simultaneously optimize multiple objectives (efficacy, toxicity, drug-likeness)
- Discover molecular modification paths that human experts struggle to conceive

**3. Breakthroughs in Protein Structure Prediction Models like AlphaFold**

AlphaFold 2 (2020) and subsequent versions completely changed the target analysis process:

| Traditional Process | AlphaFold Era |
|--------------------|--------------|
| Protein crystal structure determination (years) | Predicted structure (hours) |
| Requires expensive experimental equipment | Pure computation |
| Only covers known structures | Theoretically covers all proteins |

### 6.2 Moore's Law Applied to Drug Discovery

The cost curve of AI drug discovery is following in the footsteps of Moore's Law:

```
Cost ($)
^
|  Traditional Pharma
|  │
|              │ AI Pharma (exponential decline)
|              │ │
|_______________│_______________│________________► Time
  2010          2020          2030 (expected)
 
Cost per drug: $2-3 billion → expected <$500 million
```

---

## 7. Industry Impact and Future Outlook

### 7.1 Implications for the AI Startup Ecosystem

1. **Vertical specialization is key to AI落地**: Manus focuses on cancer treatment, avoiding direct competition with major pharmaceutical companies
2. **Value of Founder Mode in the AI era**: High technical uncertainty requires rapid founder decision-making
3. **"Non-Acquisition Acquisition" model**: Microsoft's deal with Inflection may be replicated by more major companies

### 7.2 Potential Challenges and Risks

| Risk Category | Specific Risk | Mitigation Strategy |
|--------------|--------------|-------------------|
| Technical Risk | Clinical trial failure | Partner with traditional pharma |
| Regulatory Risk | FDA approval | Early regulatory affairs布局 |
| Business Risk | Competition from Big Pharma | Focus on niche segments |
| Talent Risk | Shortage of AI + biology talent | University partnerships |

---

## Conclusion

Reid Hoffman's departure from Microsoft's board to join Manus marks a new phase in AI entrepreneurship. This event is not merely a personnel change but a renewed confirmation of "Founder Mode's" value in the AI era.

**Key Takeaways:**

1. **Personal Level**: Hoffman's career trajectory reflects how top investors judge the direction of AI transformation
2. **Technical Level**: Move 37 AI represents the latest progress in AI drug discovery—surpassing human creativity in chemical exploration
3. **Business Level**: Manus adopts "Co-founder + Professional CEO" model, balancing entrepreneurial passion with operational expertise
4. **Industry Level**: AI vertical落地 (drug discovery, code generation, etc.) is accelerating

For practitioners in the AI Coding domain, the Manus case provides an important reference: when AI demonstrates creativity surpassing humans in specific domains (such as chemistry, code), "Founder Mode" management philosophy and rapid technical roadmap iteration will become key to competitiveness.

---

*Related Topics: AI Agent, MCP (Model Context Protocol), AI Drug Discovery, Founder Mode, Generative AI*