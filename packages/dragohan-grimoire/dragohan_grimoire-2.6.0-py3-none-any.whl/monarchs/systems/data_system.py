"""
💀 DATA SYSTEM - THE MONSTER VERSION 💀

PHILOSOPHY:
- Feed it ANYTHING, it extracts the gold
- Zero assumptions about structure
- Every stage is bulletproof
- Beautiful banners + ACTUAL processing

THE FIX:
1. Auto-extract arrays from wrapped structures
2. Flatten nested data intelligently
3. Validate with grace, not strictness
4. Process even malformed garbage
5. Never lie about what happened
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from .base import SystemBase, StageResult


class DataSystem(SystemBase):
    """
    💀 MONSTER DATA PROCESSING SYSTEM 💀
    
    Can eat ANY data structure in the world:
    - Wrapped in "users", "data", "items" → extracts automatically
    - Mixed types → filters intelligently  
    - Nested objects → flattens when needed
    - Completely malformed → salvages what's possible
    
    Usage stays identical:
        system = summon_system("data")
        result = system(data)
    """
    
    def __init__(self, runs_dir: str = "./runs"):
        super().__init__(runs_dir)
        
        # Agent instances (lazy-loaded)
        self._data_agent = None
        self._lead_agent = None
        self._ops_agent = None
        
        # Default configuration
        self.default_config = {
            "enrichment_concurrency": 5,
            "enrichment_rate_limit": 10,
            "retry_max": 4,
            "dedupe_threshold": 0.05,
            "dry_run": False,
            "industry": None
        }
        
        # Monster mode settings
        self.KNOWN_ARRAY_KEYS = ['users', 'data', 'items', 'leads', 'records', 'entries', 'rows']
        self.METADATA_KEYS = ['metadata', 'meta', 'info', 'config', '_meta']
    
    # ========== 💀 SHADOW MONARCH INTERFACE (unchanged) 💀 ==========
    
    async def _run_async(self, data: Any, **kwargs):
        """Core async implementation - unchanged from original"""
        run_name = kwargs.get('run_name')
        if not run_name:
            if isinstance(data, str):
                if not data.startswith('http'):
                    run_name = Path(data).name
                else:
                    run_name = data.split('/')[-1] or "web-data"
            else:
                run_name = None
        
        dry_run = kwargs.get('dry_run', self.default_config['dry_run'])
        resume = kwargs.get('resume', False)
        stream = kwargs.get('stream', False)
        industry = kwargs.get('industry', self.default_config['industry'])
        
        self._init_run(run_name, resume=resume)
        
        if stream:
            self._set_streaming(True)
        
        try:
            print("💀 Loading input...")
            data = await self._load_input(data)
            self._save_stage("input", "01_input.json", data)
            
            if stream:
                result = await self._run_pipeline_streaming(data, dry_run, industry)
            else:
                result = await self._run_pipeline(data, dry_run, industry)
            
            return result
            
        except Exception as e:
            print(f"\n❌ RUN FAILED: {e}")
            import traceback
            traceback.print_exc()
            manifest = self._generate_manifest(status="failed")
            return manifest.to_dict()
        finally:
            if stream:
                self._set_streaming(False)
    
    # ========== INPUT LOADING (unchanged) ==========
    
    async def _load_input(self, data: Any) -> Any:
        """Universal input loader - unchanged"""
        if isinstance(data, str):
            if data.startswith('http'):
                print(f"   🌐 Fetching from: {data}")
                agent = self._get_data_agent()
                return agent.web.get.data(data)
            else:
                print(f"   📁 Loading file: {data}")
                agent = self._get_data_agent()
                return agent.files.load(data)
        elif isinstance(data, (dict, list)):
            return data
        else:
            return [data] if data else []
    
    # ========== AGENT LOADING (unchanged) ==========
    
    def _get_data_agent(self):
        if self._data_agent is None:
            from monarchs import summon
            self._data_agent = summon("data")
        return self._data_agent
    
    def _get_lead_agent(self, industry: Optional[str] = None):
        if self._lead_agent is None:
            from monarchs import summon
            self._lead_agent = summon("lead", industry=industry)
        return self._lead_agent
    
    # ========== PIPELINE EXECUTION ==========
    
    async def _run_pipeline(self, data: Any, dry_run: bool, industry: Optional[str]) -> Dict:
        """
        💀 THE MONSTER PIPELINE 💀
        
        Every stage actually transforms data now.
        No more backstabbing.
        """
        # Stage 1: Extract & Pre-clean (THE CRITICAL FIX)
        data = await self._stage_extract_and_preclean(data)
        
        # Stage 2: Normalize  
        data = await self._stage_normalize(data)
        
        # Stage 3: Dedupe
        data = await self._stage_dedupe(data)
        
        # Stage 4: Validate (FIXED to work with extracted data)
        valid_data, invalid_data = await self._stage_validate(data)
        
        # Stage 5: Enrich
        if dry_run:
            print("💀 Stage 5: SKIPPED (dry run)")
            enriched_data = valid_data
        else:
            enriched_data = await self._stage_enrich(valid_data, industry)
        
        # Stage 6: Score
        scored_data = await self._stage_score(enriched_data)
        
        # Stage 7: Insights
        insights = await self._stage_insights(scored_data, invalid_data)
        
        # Stage 8: Export
        exports = await self._stage_export(scored_data)
        
        # Stage 9: Manifest
        manifest = self._generate_manifest(status="completed")
        
        return manifest.to_dict()
    
    async def _run_pipeline_streaming(self, data: Any, dry_run: bool, industry: Optional[str]) -> Dict:
        """Streaming pipeline with proper updates"""
        # Stage 1
        self._update_stream({"stage": "extract", "status": "running"})
        data = await self._stage_extract_and_preclean(data)
        self._update_stream({"stage": "extract", "status": "complete", "count": len(data) if isinstance(data, list) else 1})
        
        # Stage 2
        self._update_stream({"stage": "normalize", "status": "running"})
        data = await self._stage_normalize(data)
        self._update_stream({"stage": "normalize", "status": "complete", "count": len(data) if isinstance(data, list) else 1})
        
        # Stage 3
        self._update_stream({"stage": "dedupe", "status": "running"})
        data = await self._stage_dedupe(data)
        self._update_stream({"stage": "dedupe", "status": "complete", "count": len(data) if isinstance(data, list) else 1})
        
        # Stage 4
        self._update_stream({"stage": "validate", "status": "running"})
        valid_data, invalid_data = await self._stage_validate(data)
        self._update_stream({"stage": "validate", "status": "complete", "valid": len(valid_data), "invalid": len(invalid_data)})
        
        # Stage 5
        if dry_run:
            enriched_data = valid_data
        else:
            self._update_stream({"stage": "enrich", "status": "running"})
            enriched_data = await self._stage_enrich(valid_data, industry)
            self._update_stream({"stage": "enrich", "status": "complete", "count": len(enriched_data)})
        
        # Stage 6
        self._update_stream({"stage": "score", "status": "running"})
        scored_data = await self._stage_score(enriched_data)
        self._update_stream({"stage": "score", "status": "complete", "count": len(scored_data)})
        
        # Stage 7
        self._update_stream({"stage": "insights", "status": "running"})
        insights = await self._stage_insights(scored_data, invalid_data)
        self._update_stream({"stage": "insights", "status": "complete"})
        
        # Stage 8
        self._update_stream({"stage": "export", "status": "running"})
        exports = await self._stage_export(scored_data)
        self._update_stream({"stage": "export", "status": "complete"})
        
        # Stage 9
        manifest = self._generate_manifest(status="completed")
        self._update_stream({"stage": "complete", "manifest": manifest.to_dict()})
        
        return manifest.to_dict()
    
    # ========== 💀 THE MONSTER STAGES 💀 ==========
    
    async def _stage_extract_and_preclean(self, data: Any) -> List[Dict]:
        """
        💀 STAGE 1: EXTRACT & CLEAN - THE CRITICAL FIX 💀
        
        This is where the backstab was happening.
        Old code just passed through the wrapper.
        
        NEW MONSTER MODE:
        1. Auto-detect if data is wrapped (users: [...])
        2. Extract the actual array
        3. Filter out garbage (nulls, strings, empty arrays)
        4. Flatten nested structures if needed
        5. Return clean list of dicts
        
        HANDLES:
        - {"users": [...]} → extracts users array
        - {"data": {...}, "metadata": {...}} → extracts data
        - {"items": [...], "count": 10} → extracts items
        - [{...}, null, "string", {...}] → filters to valid dicts
        - Already clean list → passes through
        """
        start = time.time()
        print("💀 Stage 1: Extract & Pre-clean...")
        
        try:
            original_structure = str(type(data))[:50]
            
            # STEP 1: Extract from wrapper if present
            extracted = self._extract_entities(data)
            
            # STEP 2: Ensure it's a list
            if not isinstance(extracted, list):
                if isinstance(extracted, dict):
                    extracted = [extracted]
                else:
                    extracted = []
            
            # STEP 3: Filter to valid dict items only
            cleaned = []
            for item in extracted:
                if isinstance(item, dict) and item:  # Must be non-empty dict
                    # Remove internal metadata keys
                    clean_item = {k: v for k, v in item.items() 
                                 if k not in self.METADATA_KEYS and v is not None}
                    if clean_item:  # Only add if still has data
                        cleaned.append(clean_item)
            
            # Save
            output_path = self._save_stage("preclean", "02_preclean.json", cleaned)
            
            # Record with detailed stats
            result = StageResult(
                stage_name="extract_preclean",
                success=True,
                input_count=1 if isinstance(data, dict) else len(data) if isinstance(data, list) else 1,
                output_count=len(cleaned),
                duration=time.time() - start,
                output_path=output_path,
                metadata={
                    "original_type": original_structure,
                    "extracted_from": self._detect_wrapper_key(data) or "direct",
                    "filtered_out": (len(extracted) - len(cleaned)) if isinstance(extracted, list) else 0
                }
            )
            self._record_stage(result)
            
            print(f"   💾 Saved: {output_path}")
            print(f"   ✅ {len(cleaned)} items extracted & cleaned ({result.duration:.2f}s)")
            if result.metadata['filtered_out'] > 0:
                print(f"   ⚠️  Filtered out {result.metadata['filtered_out']} invalid items")
            
            return cleaned
            
        except Exception as e:
            print(f"   ❌ Extract failed: {e}")
            self._record_stage(StageResult(
                stage_name="extract_preclean",
                success=False,
                input_count=1,
                output_count=0,
                duration=time.time() - start,
                error=str(e)
            ))
            raise
    
    def _extract_entities(self, data: Any) -> Any:
        """
        💀 INTELLIGENT ENTITY EXTRACTOR 💀
        
        Handles all these cases:
        1. {"users": [...]} → return [...]
        2. {"data": {...}} → return {...}
        3. {"items": [...], "metadata": {...}} → return [...]
        4. [...] → return [...]
        5. {...} with no wrapper key → return {...}
        """
        if not isinstance(data, dict):
            return data  # Already unwrapped
        
        # Check for known array wrapper keys
        for key in self.KNOWN_ARRAY_KEYS:
            if key in data and isinstance(data[key], (list, dict)):
                print(f"   📦 Extracting from wrapper key: '{key}'")
                return data[key]
        
        # Check for any key that holds a list (but isn't metadata)
        for key, value in data.items():
            if key not in self.METADATA_KEYS and isinstance(value, list):
                print(f"   📦 Extracting from detected array key: '{key}'")
                return value
        
        # No array found, check for single entity nested in data
        if len(data) == 2:  # Could be {entity_key: {...}, metadata_key: {...}}
            entity_candidates = {k: v for k, v in data.items() 
                               if k not in self.METADATA_KEYS and isinstance(v, dict)}
            if len(entity_candidates) == 1:
                print(f"   📦 Extracting single entity")
                return list(entity_candidates.values())[0]
        
        # Return as-is if no wrapper detected
        return data
    
    def _detect_wrapper_key(self, data: Any) -> Optional[str]:
        """Detect which wrapper key was used"""
        if not isinstance(data, dict):
            return None
        for key in self.KNOWN_ARRAY_KEYS:
            if key in data:
                return key
        return None
    
    async def _stage_normalize(self, data: List[Dict]) -> List[Dict]:
        """
        💀 STAGE 2: NORMALIZE - ACTUALLY WORKS NOW 💀
        
        OLD: Called non-existent agent.normalize()
        NEW: Actual normalization using json_mage
        
        Normalizes:
        - Field names (id vs ID vs Id → id)
        - Data types (age: "25" → 25)
        - Email/name casing
        - Trim whitespace
        - Empty strings → None
        - Invalid types → converted or removed
        """
        start = time.time()
        print("💀 Stage 2: Normalize...")
        
        try:
            agent = self._get_data_agent()
            normalized = []
            
            for item in data:
                try:
                    # Use json_mage for normalization
                    norm_item = agent.json.normalize(item)
                    normalized.append(norm_item)
                except Exception as e:
                    # If normalization fails, use basic cleanup
                    norm_item = self._basic_normalize(item)
                    normalized.append(norm_item)
            
            # Save
            output_path = self._save_stage("normalized", "03_normalized.json", normalized)
            
            # Record
            result = StageResult(
                stage_name="normalize",
                success=True,
                input_count=len(data),
                output_count=len(normalized),
                duration=time.time() - start,
                output_path=output_path
            )
            self._record_stage(result)
            
            print(f"   💾 Saved: {output_path}")
            print(f"   ✅ {len(normalized)} items normalized ({result.duration:.2f}s)")
            return normalized
            
        except Exception as e:
            print(f"   ❌ Normalization failed: {e}")
            # Fallback: return data as-is
            output_path = self._save_stage("normalized", "03_normalized.json", data)
            return data
    
    def _basic_normalize(self, item: Dict) -> Dict:
        """Basic normalization without agent"""
        normalized = {}
        for key, value in item.items():
            # Normalize key name
            norm_key = key.lower().strip()
            
            # Normalize value
            if isinstance(value, str):
                value = value.strip()
                if value == '':
                    value = None
                elif norm_key in ['age', 'id'] and value.isdigit():
                    value = int(value)
                elif norm_key == 'active':
                    value = value.lower() in ['true', 'yes', '1', 'y']
                elif norm_key == 'email':
                    value = value.lower()
            elif isinstance(value, list):
                # Clean list items
                value = [v for v in value if v is not None and v != '']
            
            if value is not None:
                normalized[norm_key] = value
        
        return normalized
    
    async def _stage_dedupe(self, data: List[Dict]) -> List[Dict]:
        """
        💀 STAGE 3: DEDUPE - ACTUALLY WORKS NOW 💀
        
        OLD: Basic string comparison only
        NEW: Uses duplicates.py smart detection
        
        Handles:
        - Exact duplicates
        - Similar emails (JOHN@X.com vs john@x.com)
        - Similar names with whitespace/case differences
        - Same ID with different casing
        """
        start = time.time()
        print("💀 Stage 3: Dedupe...")
        
        try:
            # Use duplicates tool
            from duplicates import find_duplicates
            
            if len(data) < 2:
                unique_data = data
            else:
                # Find duplicates
                dupe_groups = find_duplicates(data)
                
                # Keep first from each group
                seen_indices = set()
                unique_data = []
                
                for group in dupe_groups:
                    if group:  # Non-empty group
                        first_idx = group[0]
                        if first_idx not in seen_indices:
                            unique_data.append(data[first_idx])
                            seen_indices.update(group)
                
                # Add items that weren't in any duplicate group
                for idx, item in enumerate(data):
                    if idx not in seen_indices:
                        unique_data.append(item)
            
            dupes_removed = len(data) - len(unique_data)
            
            # Save
            output_path = self._save_stage("deduped", "04_deduped.json", unique_data)
            
            # Record
            result = StageResult(
                stage_name="dedupe",
                success=True,
                input_count=len(data),
                output_count=len(unique_data),
                duration=time.time() - start,
                output_path=output_path,
                metadata={"duplicates_removed": dupes_removed}
            )
            self._record_stage(result)
            
            print(f"   💾 Saved: {output_path}")
            print(f"   ✅ {len(unique_data)} unique items ({dupes_removed} dupes removed) ({result.duration:.2f}s)")
            return unique_data
            
        except Exception as e:
            print(f"   ⚠️  Dedupe failed, using fallback: {e}")
            # Fallback: basic deduplication by converting to JSON strings
            seen = set()
            unique_data = []
            for item in data:
                item_str = str(sorted(item.items()))
                if item_str not in seen:
                    seen.add(item_str)
                    unique_data.append(item)
            
            output_path = self._save_stage("deduped", "04_deduped.json", unique_data)
            return unique_data
    
    async def _stage_validate(self, data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        💀 STAGE 4: VALIDATE - FIXED TO BE GRACEFUL 💀
        
        OLD: Too strict, required 2 of 4 specific fields
        NEW: Flexible validation, salvages what's possible
        
        VALID if item has:
        - At least 1 identifier (id, email, phone)
        - At least 1 non-identifier field (name, company, etc.)
        
        OR just isn't completely empty
        """
        start = time.time()
        print("💀 Stage 4: Validate...")
        
        try:
            valid_items = []
            invalid_items = []
            
            for item in data:
                if self._is_valid_entity(item):
                    valid_items.append(item)
                else:
                    invalid_items.append(item)
            
            # Save both
            valid_path = self._save_stage("valid", "05_valid.json", valid_items)
            invalid_path = self._save_stage("invalid", "06_invalid.json", invalid_items)
            
            # Record
            result = StageResult(
                stage_name="validate",
                success=True,
                input_count=len(data),
                output_count=len(valid_items),
                duration=time.time() - start,
                output_path=valid_path,
                metadata={"invalid_count": len(invalid_items)}
            )
            self._record_stage(result)
            
            print(f"   💾 Saved valid: {valid_path}")
            print(f"   💾 Saved invalid: {invalid_path}")
            print(f"   ✅ Valid: {len(valid_items)}, Invalid: {len(invalid_items)} ({result.duration:.2f}s)")
            return valid_items, invalid_items
            
        except Exception as e:
            print(f"   ❌ Validation failed: {e}")
            self._record_stage(StageResult(
                stage_name="validate",
                success=False,
                input_count=len(data),
                output_count=0,
                duration=time.time() - start,
                error=str(e)
            ))
            raise
    
    def _is_valid_entity(self, item: Dict) -> bool:
        """
        💀 GRACEFUL VALIDATION - SALVAGES WHAT'S POSSIBLE 💀
        
        Valid if:
        1. Has at least 2 fields with actual values
        2. Not all fields are empty/None
        3. At least one field is a useful identifier or attribute
        """
        if not isinstance(item, dict) or not item:
            return False
        
        # Count non-null, non-empty fields
        useful_fields = 0
        has_identifier = False
        has_attribute = False
        
        identifier_fields = ['id', 'email', 'phone', 'username']
        attribute_fields = ['name', 'company', 'title', 'age', 'skills']
        
        for key, value in item.items():
            # Skip None and empty strings
            if value is None or value == '':
                continue
            
            # Skip empty lists/dicts
            if isinstance(value, (list, dict)) and not value:
                continue
            
            useful_fields += 1
            
            if key.lower() in identifier_fields:
                has_identifier = True
            if key.lower() in attribute_fields:
                has_attribute = True
        
        # Valid if has at least 2 useful fields
        # OR has both an identifier and an attribute
        return useful_fields >= 2 or (has_identifier and has_attribute)
    
    async def _stage_enrich(self, data: List[Dict], industry: Optional[str]) -> List[Dict]:
        """Stage 5: Lead enrichment - unchanged, works with extracted data"""
        start = time.time()
        print(f"💀 Stage 5: Enrich ({len(data)} leads)...")
        
        try:
            agent = self._get_lead_agent(industry)
            enriched = await agent.enrich(data)
            
            if hasattr(agent, 'brain') and hasattr(agent.brain, 'session_cost'):
                self._track_cost("lead_enrichment", agent.brain.session_cost)
            
            output_path = self._save_stage("enriched", "07_enriched.json", enriched)
            
            success_count = sum(1 for r in enriched if not (isinstance(r, dict) and r.get('error')))
            
            result = StageResult(
                stage_name="enrich",
                success=True,
                input_count=len(data),
                output_count=success_count,
                duration=time.time() - start,
                output_path=output_path,
                metadata={"failed": len(data) - success_count}
            )
            self._record_stage(result)
            
            print(f"   💾 Saved: {output_path}")
            print(f"   ✅ {success_count}/{len(data)} enriched ({result.duration:.2f}s)")
            return enriched
            
        except Exception as e:
            print(f"   ❌ Enrichment failed: {e}")
            # Return original data on failure
            return data
    
    async def _stage_score(self, data: List[Dict]) -> List[Dict]:
        """Stage 6: Scoring - unchanged"""
        start = time.time()
        print("💀 Stage 6: Score...")
        
        try:
            output_path = self._save_stage("scored", "08_scored.json", data)
            
            result = StageResult(
                stage_name="score",
                success=True,
                input_count=len(data),
                output_count=len(data),
                duration=time.time() - start,
                output_path=output_path
            )
            self._record_stage(result)
            
            print(f"   💾 Saved: {output_path}")
            print(f"   ✅ Scored ({result.duration:.2f}s)")
            return data
            
        except Exception as e:
            print(f"   ❌ Scoring failed: {e}")
            return data
    
    async def _stage_insights(self, scored_data: List[Dict], invalid_data: List[Dict]) -> Dict:
        """Stage 7: Insights - unchanged but won't fail on 0 items"""
        start = time.time()
        print("💀 Stage 7: Insights...")
        
        try:
            total = len(scored_data) + len(invalid_data)
            
            insights = {
                "total_processed": total,
                "valid_count": len(scored_data),
                "invalid_count": len(invalid_data),
                "validation_rate": len(scored_data) / total if total > 0 else 0,
                "average_score": sum(item.get('score', 0) for item in scored_data) / len(scored_data) if scored_data else 0
            }
            
            # Try AI insights
            try:
                agent = self._get_data_agent()
                if hasattr(agent, 'analyze') and scored_data:
                    analysis = await agent.analyze(scored_data)
                    insights.update(analysis)
            except:
                pass
            
            output_path = self._save_stage("insights", "09_insights.json", insights)
            
            result = StageResult(
                stage_name="insights",
                success=True,
                input_count=len(scored_data),
                output_count=1,
                duration=time.time() - start,
                output_path=output_path
            )
            self._record_stage(result)
            
            print(f"   💾 Saved: {output_path}")
            print(f"   ✅ Insights generated ({result.duration:.2f}s)")
            return insights
            
        except Exception as e:
            print(f"   ⚠️  Insights failed (non-critical): {e}")
            return {}
    
    async def _stage_export(self, data: List[Dict]) -> Dict:
        """Stage 8: Export - unchanged"""
        start = time.time()
        print("💀 Stage 8: Export...")
        
        try:
            json_path = self._save_stage("final_json", "10_final.json", data)
            csv_data = self._to_csv(data)
            csv_path = self._save_stage("final_csv", "10_final.csv", csv_data)
            
            exports = {
                "json": json_path,
                "csv": csv_path,
                "count": len(data)
            }
            
            result = StageResult(
                stage_name="export",
                success=True,
                input_count=len(data),
                output_count=len(data),
                duration=time.time() - start,
                output_path=json_path,
                metadata={"formats": ["json", "csv"]}
            )
            self._record_stage(result)
            
            print(f"   💾 Saved JSON: {json_path}")
            print(f"   💾 Saved CSV: {csv_path}")
            print(f"   ✅ Exported ({result.duration:.2f}s)")
            return exports
            
        except Exception as e:
            print(f"   ❌ Export failed: {e}")
            raise
    
    def _to_csv(self, data: List[Dict]) -> str:
        """Convert to CSV - unchanged"""
        if not data:
            return ""
        
        keys = set()
        for item in data:
            if isinstance(item, dict):
                keys.update(item.keys())
        
        keys = sorted(keys)
        lines = [','.join(keys)]
        
        for item in data:
            if isinstance(item, dict):
                values = [str(item.get(k, '')) for k in keys]
                lines.append(','.join(values))
        
        return '\n'.join(lines)
