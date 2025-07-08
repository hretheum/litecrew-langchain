"""
Entity and Contextual Memory implementation.
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import spacy
from spacy.tokens import Doc

# Try to load spaCy model, fall back to simple extraction if not available
try:
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except:
    HAS_SPACY = False
    nlp = None


@dataclass
class Entity:
    """An entity extracted from text."""
    
    name: str
    type: str  # PERSON, ORG, LOCATION, etc.
    mentions: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=dict)  # relation_type -> [entity_names]
    context_snippets: List[str] = field(default_factory=list)
    confidence: float = 1.0
    
    def add_mention(self, mention: str, context: str) -> None:
        """Add a mention of this entity."""
        if mention not in self.mentions:
            self.mentions.append(mention)
        
        # Store context snippet
        context_snippet = self._extract_context_snippet(mention, context)
        if context_snippet and context_snippet not in self.context_snippets:
            self.context_snippets.append(context_snippet)
    
    def _extract_context_snippet(self, mention: str, context: str, window: int = 50) -> str:
        """Extract context around entity mention."""
        try:
            idx = context.lower().index(mention.lower())
            start = max(0, idx - window)
            end = min(len(context), idx + len(mention) + window)
            
            # Find sentence boundaries
            for i in range(start, 0, -1):
                if context[i] in '.!?':
                    start = i + 1
                    break
            
            for i in range(end, len(context)):
                if context[i] in '.!?':
                    end = i + 1
                    break
            
            return context[start:end].strip()
        except ValueError:
            return ""
    
    def add_relationship(self, relation_type: str, entity_name: str) -> None:
        """Add a relationship to another entity."""
        if relation_type not in self.relationships:
            self.relationships[relation_type] = []
        
        if entity_name not in self.relationships[relation_type]:
            self.relationships[relation_type].append(entity_name)
    
    def merge_with(self, other: 'Entity') -> None:
        """Merge another entity into this one."""
        # Merge mentions
        for mention in other.mentions:
            if mention not in self.mentions:
                self.mentions.append(mention)
        
        # Merge attributes
        self.attributes.update(other.attributes)
        
        # Merge relationships
        for rel_type, entities in other.relationships.items():
            for entity in entities:
                self.add_relationship(rel_type, entity)
        
        # Merge context snippets
        for snippet in other.context_snippets:
            if snippet not in self.context_snippets:
                self.context_snippets.append(snippet)
        
        # Update confidence (average)
        self.confidence = (self.confidence + other.confidence) / 2


class SimpleEntityExtractor:
    """Simple entity extraction without spaCy."""
    
    def __init__(self):
        # Common patterns for entity extraction
        self.patterns = {
            "PERSON": [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
                r'\bMr\.|Mrs\.|Ms\.|Dr\. [A-Z][a-z]+\b',  # Title Name
            ],
            "ORG": [
                r'\b[A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|Company|Corporation)\b',
                r'\b[A-Z][A-Z]+ [A-Z][a-z]+\b',  # ACRONYM Name
            ],
            "LOCATION": [
                r'\b(?:New|San|Los|Las) [A-Z][a-z]+\b',  # Common city prefixes
                r'\b[A-Z][a-z]+, [A-Z][a-z]+\b',  # City, State
            ]
        }
    
    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract entities using regex patterns."""
        entities = []
        
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entities.append((match.group(), entity_type))
        
        return entities


class EntityMemory:
    """Memory system for entity extraction and relationship tracking."""
    
    def __init__(
        self,
        enable_privacy: bool = True,
        cross_session: bool = False,
        session_id: Optional[str] = None
    ):
        """Initialize entity memory.
        
        Args:
            enable_privacy: Enable privacy controls (entity masking)
            cross_session: Enable cross-session memory
            session_id: Current session ID
        """
        self.enable_privacy = enable_privacy
        self.cross_session = cross_session
        self.session_id = session_id or "default"
        
        # Entity storage
        self.entities: Dict[str, Entity] = {}
        self.entity_aliases: Dict[str, str] = {}  # alias -> canonical name
        
        # Contextual layers
        self.contexts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Privacy controls
        self.masked_entities: Set[str] = set()
        
        # Initialize extractor
        if HAS_SPACY:
            self.extractor = nlp
        else:
            self.extractor = SimpleEntityExtractor()
    
    def extract_entities(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Entity]:
        """Extract entities from text.
        
        Args:
            text: Text to extract entities from
            metadata: Additional metadata for context
            
        Returns:
            List of extracted entities
        """
        extracted = []
        
        if HAS_SPACY and isinstance(self.extractor, type(nlp)):
            # Use spaCy
            doc = self.extractor(text)
            
            for ent in doc.ents:
                entity = self._get_or_create_entity(ent.text, ent.label_)
                entity.add_mention(ent.text, text)
                extracted.append(entity)
                
                # Extract attributes from dependency parsing
                self._extract_attributes(entity, ent, doc)
            
            # Extract relationships
            self._extract_relationships(doc)
            
        else:
            # Use simple extraction
            entities = self.extractor.extract_entities(text)
            
            for entity_text, entity_type in entities:
                entity = self._get_or_create_entity(entity_text, entity_type)
                entity.add_mention(entity_text, text)
                extracted.append(entity)
        
        # Add to contextual memory
        if metadata:
            context_entry = {
                "text": text,
                "entities": [e.name for e in extracted],
                "metadata": metadata,
                "session_id": self.session_id
            }
            
            for entity in extracted:
                self.contexts[entity.name].append(context_entry)
        
        return extracted
    
    def _get_or_create_entity(self, name: str, entity_type: str) -> Entity:
        """Get existing entity or create new one."""
        # Check aliases
        canonical_name = self.entity_aliases.get(name.lower(), name)
        
        if canonical_name in self.entities:
            return self.entities[canonical_name]
        
        # Create new entity
        entity = Entity(name=canonical_name, type=entity_type)
        self.entities[canonical_name] = entity
        
        # Add alias
        self.entity_aliases[name.lower()] = canonical_name
        
        return entity
    
    def _extract_attributes(self, entity: Entity, ent_span: Any, doc: Doc) -> None:
        """Extract entity attributes from dependency parsing."""
        if not HAS_SPACY:
            return
        
        # Look for descriptive adjectives
        for token in ent_span:
            for child in token.children:
                if child.dep_ == "amod":  # Adjectival modifier
                    if "descriptors" not in entity.attributes:
                        entity.attributes["descriptors"] = []
                    entity.attributes["descriptors"].append(child.text)
        
        # Look for appositives (e.g., "John, the CEO")
        for token in doc:
            if token.dep_ == "appos" and token.head.text in entity.mentions:
                entity.attributes["role"] = token.text
    
    def _extract_relationships(self, doc: Doc) -> None:
        """Extract relationships between entities."""
        if not HAS_SPACY:
            return
        
        entities_in_doc = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Look for subject-verb-object patterns
        for token in doc:
            if token.pos_ == "VERB":
                # Find subject
                subject = None
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subject = child.text
                        break
                
                # Find object
                obj = None
                for child in token.children:
                    if child.dep_ in ("dobj", "pobj"):
                        obj = child.text
                        break
                
                # Create relationship if both are entities
                if subject and obj:
                    subj_entity = self._find_entity_by_mention(subject)
                    obj_entity = self._find_entity_by_mention(obj)
                    
                    if subj_entity and obj_entity:
                        subj_entity.add_relationship(token.lemma_, obj_entity.name)
                        obj_entity.add_relationship(f"inverse_{token.lemma_}", subj_entity.name)
    
    def _find_entity_by_mention(self, mention: str) -> Optional[Entity]:
        """Find entity by mention text."""
        mention_lower = mention.lower()
        
        # Check direct match
        if mention in self.entities:
            return self.entities[mention]
        
        # Check aliases
        if mention_lower in self.entity_aliases:
            return self.entities[self.entity_aliases[mention_lower]]
        
        # Check partial matches
        for entity in self.entities.values():
            if mention_lower in [m.lower() for m in entity.mentions]:
                return entity
        
        return None
    
    def add_entity_alias(self, alias: str, canonical_name: str) -> None:
        """Add an alias for an entity."""
        self.entity_aliases[alias.lower()] = canonical_name
        
        # If entity exists, add alias as mention
        if canonical_name in self.entities:
            self.entities[canonical_name].mentions.append(alias)
    
    def get_entity(self, name: str) -> Optional[Entity]:
        """Get entity by name or alias."""
        # Check direct match
        if name in self.entities:
            return self.entities[name]
        
        # Check aliases
        canonical = self.entity_aliases.get(name.lower())
        if canonical:
            return self.entities.get(canonical)
        
        return None
    
    def get_related_entities(self, entity_name: str, relation_type: Optional[str] = None) -> List[Entity]:
        """Get entities related to a given entity."""
        entity = self.get_entity(entity_name)
        if not entity:
            return []
        
        related = []
        
        if relation_type:
            # Get specific relation type
            related_names = entity.relationships.get(relation_type, [])
            related = [self.get_entity(name) for name in related_names if self.get_entity(name)]
        else:
            # Get all related entities
            for rel_names in entity.relationships.values():
                for name in rel_names:
                    entity = self.get_entity(name)
                    if entity and entity not in related:
                        related.append(entity)
        
        return related
    
    def get_entity_context(self, entity_name: str, session_only: bool = True) -> List[Dict[str, Any]]:
        """Get contextual information for an entity."""
        if session_only and not self.cross_session:
            return [
                ctx for ctx in self.contexts.get(entity_name, [])
                if ctx.get("session_id") == self.session_id
            ]
        
        return self.contexts.get(entity_name, [])
    
    def mask_entity(self, entity_name: str) -> None:
        """Mark entity for privacy masking."""
        if self.enable_privacy:
            self.masked_entities.add(entity_name)
    
    def apply_privacy_mask(self, text: str) -> str:
        """Apply privacy masking to text."""
        if not self.enable_privacy:
            return text
        
        masked_text = text
        for entity_name in self.masked_entities:
            entity = self.get_entity(entity_name)
            if entity:
                # Mask all mentions
                for mention in entity.mentions:
                    mask = f"[{entity.type}]"
                    masked_text = masked_text.replace(mention, mask)
        
        return masked_text
    
    def get_entity_graph(self) -> Dict[str, Any]:
        """Get entity relationship graph."""
        nodes = []
        edges = []
        
        for entity in self.entities.values():
            nodes.append({
                "id": entity.name,
                "type": entity.type,
                "mentions": len(entity.mentions),
                "attributes": entity.attributes
            })
            
            for rel_type, related in entity.relationships.items():
                for related_name in related:
                    edges.append({
                        "source": entity.name,
                        "target": related_name,
                        "type": rel_type
                    })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_entities": len(self.entities),
            "total_relationships": len(edges)
        }
    
    def calculate_extraction_accuracy(self, ground_truth: List[Tuple[str, str]]) -> float:
        """Calculate entity extraction accuracy against ground truth.
        
        Args:
            ground_truth: List of (entity_name, entity_type) tuples
            
        Returns:
            Accuracy score (0-1)
        """
        if not ground_truth:
            return 1.0
        
        correct = 0
        for true_name, true_type in ground_truth:
            entity = self.get_entity(true_name)
            if entity and entity.type == true_type:
                correct += 1
        
        return correct / len(ground_truth)
    
    def export_entities(self) -> Dict[str, Any]:
        """Export entities for persistence."""
        return {
            "entities": {
                name: {
                    "type": entity.type,
                    "mentions": entity.mentions,
                    "attributes": entity.attributes,
                    "relationships": entity.relationships,
                    "confidence": entity.confidence
                }
                for name, entity in self.entities.items()
            },
            "aliases": self.entity_aliases,
            "contexts": dict(self.contexts),
            "masked_entities": list(self.masked_entities),
            "session_id": self.session_id
        }
    
    def import_entities(self, data: Dict[str, Any]) -> None:
        """Import entities from exported data."""
        # Clear existing data
        self.entities.clear()
        self.entity_aliases.clear()
        self.contexts.clear()
        self.masked_entities.clear()
        
        # Import entities
        for name, entity_data in data.get("entities", {}).items():
            entity = Entity(
                name=name,
                type=entity_data["type"],
                mentions=entity_data.get("mentions", []),
                attributes=entity_data.get("attributes", {}),
                relationships=entity_data.get("relationships", {}),
                confidence=entity_data.get("confidence", 1.0)
            )
            self.entities[name] = entity
        
        # Import other data
        self.entity_aliases = data.get("aliases", {})
        self.contexts = defaultdict(list, data.get("contexts", {}))
        self.masked_entities = set(data.get("masked_entities", []))
        
        # Only import session if cross-session is enabled
        if self.cross_session:
            self.session_id = data.get("session_id", self.session_id)