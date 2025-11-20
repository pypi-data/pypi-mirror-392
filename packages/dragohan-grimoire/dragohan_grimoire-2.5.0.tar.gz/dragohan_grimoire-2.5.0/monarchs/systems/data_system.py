"""
💀 DATA SYSTEM - Shadow Monarch Style 💀

Simple as fuck data processing pipeline:
- system(data) → process everything
- await system.run(data) → async process
- while system.works: print(system.current) → stream progress
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from .base import SystemBase, StageResult


class DataSystem(SystemBase):
    """
    💀 DATA PROCESSING SYSTEM - SHADOW MONARCH STYLE 💀
    
    Ultra-simple interface:
        system = summon_system("data")
        result = system(data)  # That's it!
    
    Or async:
        result = await system.run(data)
    
    Or streaming:
        system.run(data, stream=True)
        while system.works:
            print(f"Processing: {system.current}")
    """
    
    def __init__(self, runs_dir: str = "./runs"):
        super().__init__(runs_dir)
        
        # Agent instances (lazy-loaded)
        self._data_agent = None
        self._lead_agent = None
        self._ops_agent = None
        
        # Default configuration (can override in run())
        self.default_config = {
            "enrichment_concurrency": 5,
            "enrichment_rate_limit": 10,  # req/sec
            "retry_max": 4,
            "dedupe_threshold": 0.05,
            "dry_run": False,
            "industry": None
        }
    
    # ========== 💀 SHADOW MONARCH INTERFACE 💀 ==========
    
    async def _run_async(self, data: Any, **kwargs):
        """
        💀 CORE ASYNC IMPLEMENTATION 💀
        
        This is THE method that does everything.
        All other methods route here.
        
        Args:
            data: Input data (auto-detects format)
            **kwargs: Optional overrides:
                - run_name: Custom name (auto-detected from file)
                - dry_run: Skip enrichment
                - resume: Resume previous run
                - stream: Enable streaming
                - industry: Lead enrichment specialization
        """
        # Auto-detect run_name from data if it's a file
        run_name = kwargs.get('run_name')
        if not run_name:
            if isinstance(data, str):
                # It's a path or URL
                if not data.startswith('http'):
                    # It's a file path
                    run_name = Path(data).name
                else:
                    # It's a URL
                    run_name = data.split('/')[-1] or "web-data"
            else:
                run_name = None  # Will auto-generate
        
        # Extract config with defaults
        dry_run = kwargs.get('dry_run', self.default_config['dry_run'])
        resume = kwargs.get('resume', False)
        stream = kwargs.get('stream', False)
        industry = kwargs.get('industry', self.default_config['industry'])
        
        # Initialize run (auto-creates folder)
        self._init_run(run_name, resume=resume)
        
        # Enable streaming if requested
        if stream:
            self._set_streaming(True)
        
        try:
            # Load input data (auto-detects format)
            print("💀 Loading input...")
            data = await self._load_input(data)
            
            # Save original input
            self._save_stage("input", "01_input.json", data)
            
            # Run pipeline (with optional streaming)
            if stream:
                result = await self._run_pipeline_streaming(data, dry_run, industry)
            else:
                result = await self._run_pipeline(data, dry_run, industry)
            
            return result
            
        except Exception as e:
            print(f"\n❌ RUN FAILED: {e}")
            manifest = self._generate_manifest(status="failed")
            return manifest.to_dict()
        finally:
            # Always disable streaming when done
            if stream:
                self._set_streaming(False)
    
    # ========== INPUT LOADING (Auto-detects everything) ==========
    
    async def _load_input(self, data: Any) -> Any:
        """
        💀 UNIVERSAL INPUT LOADER 💀
        
        Handles:
        - File paths (JSON, CSV, etc.)
        - URLs (fetches automatically)
        - Python dicts/lists (pass-through)
        - Anything else (converts to list)
        """
        if isinstance(data, str):
            if data.startswith('http'):
                # It's a URL
                print(f"   🌐 Fetching from: {data}")
                agent = self._get_data_agent()
                return agent.web.get.data(data)
            else:
                # It's a file path
                print(f"   📁 Loading file: {data}")
                agent = self._get_data_agent()
                return agent.files.load(data)
        
        elif isinstance(data, (dict, list)):
            # Already Python data
            return data
        
        else:
            # Convert to list
            return [data] if data else []
    
    # ========== AGENT LOADING ==========
    
    def _get_data_agent(self):
        """Lazy-load Data monarch"""
        if self._data_agent is None:
            from monarchs import summon
            self._data_agent = summon("data")
        return self._data_agent
    
    def _get_lead_agent(self, industry: Optional[str] = None):
        """Lazy-load Lead monarch"""
        if self._lead_agent is None:
            from monarchs import summon
            self._lead_agent = summon("lead", industry=industry)
        return self._lead_agent
    
    # ========== PIPELINE EXECUTION ==========
    
    async def _run_pipeline(self, data: Any, dry_run: bool, industry: Optional[str]) -> Dict:
        """
        💀 STANDARD PIPELINE (no streaming) 💀
        """
        # Stage 1: Pre-clean
        data = await self._stage_preclean(data)
        
        # Stage 2: Normalize
        data = await self._stage_normalize(data)
        
        # Stage 3: Dedupe
        data = await self._stage_dedupe(data)
        
        # Stage 4: Validate
        valid_data, invalid_data = await self._stage_validate(data)
        
        # Stage 5: Enrich (skip if dry_run)
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
        
        # Stage 9: Generate manifest
        manifest = self._generate_manifest(status="completed")
        
        return manifest.to_dict()
    
    async def _run_pipeline_streaming(self, data: Any, dry_run: bool, industry: Optional[str]) -> Dict:
        """
        💀 STREAMING PIPELINE 💀
        
        Updates self._current at each stage for polling.
        """
        # Stage 1: Pre-clean
        self._update_stream({"stage": "preclean", "status": "running"})
        data = await self._stage_preclean(data)
        self._update_stream({"stage": "preclean", "status": "complete", "count": len(data) if isinstance(data, list) else 1})
        
        # Stage 2: Normalize
        self._update_stream({"stage": "normalize", "status": "running"})
        data = await self._stage_normalize(data)
        self._update_stream({"stage": "normalize", "status": "complete", "count": len(data) if isinstance(data, list) else 1})
        
        # Stage 3: Dedupe
        self._update_stream({"stage": "dedupe", "status": "running"})
        data = await self._stage_dedupe(data)
        self._update_stream({"stage": "dedupe", "status": "complete", "count": len(data) if isinstance(data, list) else 1})
        
        # Stage 4: Validate
        self._update_stream({"stage": "validate", "status": "running"})
        valid_data, invalid_data = await self._stage_validate(data)
        self._update_stream({"stage": "validate", "status": "complete", "valid": len(valid_data), "invalid": len(invalid_data)})
        
        # Stage 5: Enrich
        if not dry_run:
            self._update_stream({"stage": "enrich", "status": "running", "total": len(valid_data)})
            enriched_data = await self._stage_enrich(valid_data, industry)
            self._update_stream({"stage": "enrich", "status": "complete", "enriched": len(enriched_data)})
        else:
            enriched_data = valid_data
            self._update_stream({"stage": "enrich", "status": "skipped"})
        
        # Stage 6: Score
        self._update_stream({"stage": "score", "status": "running"})
        scored_data = await self._stage_score(enriched_data)
        self._update_stream({"stage": "score", "status": "complete"})
        
        # Stage 7: Insights
        self._update_stream({"stage": "insights", "status": "running"})
        insights = await self._stage_insights(scored_data, invalid_data)
        self._update_stream({"stage": "insights", "status": "complete"})
        
        # Stage 8: Export
        self._update_stream({"stage": "export", "status": "running"})
        exports = await self._stage_export(scored_data)
        self._update_stream({"stage": "export", "status": "complete"})
        
        # Final
        manifest = self._generate_manifest(status="completed")
        self._update_stream({"stage": "complete", "manifest": manifest.to_dict()})
        
        return manifest.to_dict()
    
    # ========== STAGE IMPLEMENTATIONS (simplified) ==========
    
    async def _stage_preclean(self, data: Any) -> Any:
        """Stage 1: Basic cleanup"""
        start = time.time()
        print("💀 Stage 1: Pre-clean...")
        
        try:
            # Remove nulls and empty items
            if isinstance(data, list):
                cleaned = [item for item in data if item and isinstance(item, dict)]
            elif isinstance(data, dict):
                cleaned = {k: v for k, v in data.items() if v is not None}
            else:
                cleaned = data
            
            # Save
            output_path = self._save_stage("preclean", "02_preclean.json", cleaned)
            
            # Record
            result = StageResult(
                stage_name="preclean",
                success=True,
                input_count=len(data) if isinstance(data, list) else 1,
                output_count=len(cleaned) if isinstance(cleaned, list) else 1,
                duration=time.time() - start,
                output_path=output_path
            )
            self._record_stage(result)
            
            print(f"   ✅ {result.output_count} items ({result.duration:.2f}s)")
            return cleaned
            
        except Exception as e:
            self._record_stage(StageResult(
                stage_name="preclean",
                success=False,
                input_count=len(data) if isinstance(data, list) else 1,
                output_count=0,
                duration=time.time() - start,
                error=str(e)
            ))
            raise
    
    async def _stage_normalize(self, data: Any) -> Any:
        """Stage 2: Deep normalization"""
        start = time.time()
        print("💀 Stage 2: Normalize...")
        
        try:
            agent = self._get_data_agent()
            
            # Use agent's normalize if available
            if hasattr(agent, 'normalize'):
                normalized = await agent.normalize(data)
            else:
                normalized = data
            
            # Save
            output_path = self._save_stage("normalize", "03_normalized.json", normalized)
            
            # Record
            result = StageResult(
                stage_name="normalize",
                success=True,
                input_count=len(data) if isinstance(data, list) else 1,
                output_count=len(normalized) if isinstance(normalized, list) else 1,
                duration=time.time() - start,
                output_path=output_path
            )
            self._record_stage(result)
            
            print(f"   ✅ {result.output_count} items ({result.duration:.2f}s)")
            return normalized
            
        except Exception as e:
            self._record_stage(StageResult(
                stage_name="normalize",
                success=False,
                input_count=len(data) if isinstance(data, list) else 1,
                output_count=0,
                duration=time.time() - start,
                error=str(e)
            ))
            raise
    
    async def _stage_dedupe(self, data: Any) -> Any:
        """Stage 3: Deduplication"""
        start = time.time()
        print("💀 Stage 3: Dedupe...")
        
        try:
            agent = self._get_data_agent()
            
            # Use agent's dedupe if available
            if hasattr(agent, 'dedupe'):
                deduped = await agent.dedupe(data, threshold=self.default_config['dedupe_threshold'])
            else:
                # Simple dedupe by converting to string
                if isinstance(data, list):
                    seen = set()
                    deduped = []
                    for item in data:
                        key = str(sorted(item.items())) if isinstance(item, dict) else str(item)
                        if key not in seen:
                            seen.add(key)
                            deduped.append(item)
                else:
                    deduped = data
            
            # Save
            output_path = self._save_stage("dedupe", "04_deduped.json", deduped)
            
            # Record
            result = StageResult(
                stage_name="dedupe",
                success=True,
                input_count=len(data) if isinstance(data, list) else 1,
                output_count=len(deduped) if isinstance(deduped, list) else 1,
                duration=time.time() - start,
                output_path=output_path,
                metadata={"duplicates_removed": (len(data) - len(deduped)) if isinstance(data, list) else 0}
            )
            self._record_stage(result)
            
            print(f"   ✅ {result.output_count} unique ({result.duration:.2f}s)")
            return deduped
            
        except Exception as e:
            self._record_stage(StageResult(
                stage_name="dedupe",
                success=False,
                input_count=len(data) if isinstance(data, list) else 1,
                output_count=0,
                duration=time.time() - start,
                error=str(e)
            ))
            raise
    
    async def _stage_validate(self, data: Any) -> tuple:
        """Stage 4: Validation"""
        start = time.time()
        print("💀 Stage 4: Validate...")
        
        try:
            if isinstance(data, list):
                valid_items = []
                invalid_items = []
                
                for item in data:
                    if self._is_valid_lead(item):
                        valid_items.append(item)
                    else:
                        invalid_items.append(item)
            else:
                valid_items = [data] if self._is_valid_lead(data) else []
                invalid_items = [] if valid_items else [data]
            
            # Save both
            valid_path = self._save_stage("valid", "05_valid.json", valid_items)
            invalid_path = self._save_stage("invalid", "06_invalid.json", invalid_items)
            
            # Record
            result = StageResult(
                stage_name="validate",
                success=True,
                input_count=len(data) if isinstance(data, list) else 1,
                output_count=len(valid_items),
                duration=time.time() - start,
                output_path=valid_path,
                metadata={"invalid_count": len(invalid_items)}
            )
            self._record_stage(result)
            
            print(f"   ✅ Valid: {len(valid_items)}, Invalid: {len(invalid_items)} ({result.duration:.2f}s)")
            return valid_items, invalid_items
            
        except Exception as e:
            self._record_stage(StageResult(
                stage_name="validate",
                success=False,
                input_count=len(data) if isinstance(data, list) else 1,
                output_count=0,
                duration=time.time() - start,
                error=str(e)
            ))
            raise
    
    def _is_valid_lead(self, item: Dict) -> bool:
        """Check if lead has minimum required fields"""
        if not isinstance(item, dict):
            return False
        
        # Require at least 2 of: name, email, phone, company
        key_fields = ['name', 'email', 'phone', 'company']
        present = sum(1 for field in key_fields if item.get(field))
        return present >= 2
    
    async def _stage_enrich(self, data: List[Dict], industry: Optional[str]) -> List[Dict]:
        """Stage 5: Lead enrichment"""
        start = time.time()
        print(f"💀 Stage 5: Enrich ({len(data)} leads)...")
        
        try:
            agent = self._get_lead_agent(industry)
            
            # Enrich with agent
            enriched = await agent.enrich(data)
            
            # Track cost
            if hasattr(agent, 'brain') and hasattr(agent.brain, 'session_cost'):
                self._track_cost("lead_enrichment", agent.brain.session_cost)
            
            # Save
            output_path = self._save_stage("enriched", "07_enriched.json", enriched)
            
            # Count successes
            success_count = sum(1 for r in enriched if not (isinstance(r, dict) and r.get('error')))
            
            # Record
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
            
            print(f"   ✅ {success_count}/{len(data)} enriched ({result.duration:.2f}s)")
            return enriched
            
        except Exception as e:
            self._record_stage(StageResult(
                stage_name="enrich",
                success=False,
                input_count=len(data),
                output_count=0,
                duration=time.time() - start,
                error=str(e)
            ))
            raise
    
    async def _stage_score(self, data: List[Dict]) -> List[Dict]:
        """Stage 6: Scoring"""
        start = time.time()
        print("💀 Stage 6: Score...")
        
        try:
            # Already scored during enrichment usually
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
            
            print(f"   ✅ Scored ({result.duration:.2f}s)")
            return data
            
        except Exception as e:
            self._record_stage(StageResult(
                stage_name="score",
                success=False,
                input_count=len(data),
                output_count=0,
                duration=time.time() - start,
                error=str(e)
            ))
            raise
    
    async def _stage_insights(self, scored_data: List[Dict], invalid_data: List[Dict]) -> Dict:
        """Stage 7: Generate insights"""
        start = time.time()
        print("💀 Stage 7: Insights...")
        
        try:
            # Basic insights
            insights = {
                "total_processed": len(scored_data) + len(invalid_data),
                "valid_count": len(scored_data),
                "invalid_count": len(invalid_data),
                "validation_rate": len(scored_data) / (len(scored_data) + len(invalid_data)) if (scored_data or invalid_data) else 0,
                "average_score": sum(item.get('score', 0) for item in scored_data) / len(scored_data) if scored_data else 0
            }
            
            # Try to get deeper insights from agent
            try:
                agent = self._get_data_agent()
                if hasattr(agent, 'analyze'):
                    analysis = await agent.analyze(scored_data)
                    insights.update(analysis)
            except:
                pass  # Non-critical
            
            # Save
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
            
            print(f"   ✅ Insights generated ({result.duration:.2f}s)")
            return insights
            
        except Exception as e:
            # Non-critical stage
            print(f"   ⚠️  Insights failed: {e}")
            return {}
    
    async def _stage_export(self, data: List[Dict]) -> Dict:
        """Stage 8: Export to multiple formats"""
        start = time.time()
        print("💀 Stage 8: Export...")
        
        try:
            # Save JSON
            json_path = self._save_stage("final_json", "10_final.json", data)
            
            # Save CSV
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
            
            print(f"   ✅ Exported ({result.duration:.2f}s)")
            return exports
            
        except Exception as e:
            self._record_stage(StageResult(
                stage_name="export",
                success=False,
                input_count=len(data),
                output_count=0,
                duration=time.time() - start,
                error=str(e)
            ))
            raise
    
    def _to_csv(self, data: List[Dict]) -> str:
        """Convert to CSV"""
        if not data:
            return ""
        
        # Get all keys
        keys = set()
        for item in data:
            if isinstance(item, dict):
                keys.update(item.keys())
        
        keys = sorted(keys)
        
        # Build CSV
        lines = [','.join(keys)]
        for item in data:
            if isinstance(item, dict):
                values = [str(item.get(k, '')) for k in keys]
                lines.append(','.join(values))
        
        return '\n'.join(lines)
