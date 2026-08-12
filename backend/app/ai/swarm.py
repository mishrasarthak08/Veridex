import asyncio
import uuid
import datetime
from typing import Dict, Any, Optional

# We will inject the ConnectionManager to stream logs
class SwarmEngine:
    def __init__(self, ws_manager=None):
        self.ws_manager = ws_manager
        self.tasks: Dict[str, asyncio.Task] = {}

    async def emit_log(self, swarm_id: str, message: str, agent_name: str = "System"):
        """Emit a real-time log to all connected clients."""
        if not self.ws_manager:
            return
            
        payload = {
            "type": "terminal_log",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "agent": agent_name,
            "message": message,
            "swarm_id": swarm_id
        }
        await self.ws_manager.broadcast(payload)
        
        # Also emit timeline events for the execution timeline
        timeline_payload = {
            "type": "timeline_event",
            "event": {
                "id": str(uuid.uuid4()),
                "timestamp": payload["timestamp"],
                "agent": agent_name,
                "action": "Execution Step",
                "details": message,
                "status": "success"
            }
        }
        await self.ws_manager.broadcast(timeline_payload)

    async def _agent_triage(self, swarm_id: str):
        await self.emit_log(swarm_id, "[TriageAgent] Starting triage process...", "Triage")
        await asyncio.sleep(1.5)
        await self.emit_log(swarm_id, "[TriageAgent] Analyzed incoming payload. Routing to Researcher.", "Triage")
        
    async def _agent_researcher(self, swarm_id: str, chaos_mode: bool = False):
        await self.emit_log(swarm_id, "[ResearcherAgent] Booting up search modules...", "Researcher")
        await asyncio.sleep(2)
        
        if chaos_mode:
            await self.emit_log(swarm_id, "🚨 [ResearcherAgent] CRITICAL FAILURE: OutOfMemoryError. Node terminated.", "System")
            await asyncio.sleep(1)
            await self._agent_recovery(swarm_id)
            return

        await self.emit_log(swarm_id, "[ResearcherAgent] Searching Confluence for API schemas...", "Researcher")
        await asyncio.sleep(2)
        await self.emit_log(swarm_id, "[ResearcherAgent] Found 3 matching documents. Extracting vectors.", "Researcher")
        
    async def _agent_recovery(self, swarm_id: str):
        await self.emit_log(swarm_id, "[RecoveryAgent] Intializing failover protocols...", "Recovery")
        await asyncio.sleep(2)
        await self.emit_log(swarm_id, "[RecoveryAgent] Resuming task from last checkpoint.", "Recovery")
        await asyncio.sleep(1)
        await self.emit_log(swarm_id, "[RecoveryAgent] Found 3 matching documents. Extracting vectors.", "Recovery")

    async def _run_swarm(self, swarm_id: str, config: Dict[str, Any]):
        chaos_mode = config.get("chaos_mode", False)
        try:
            mode_str = " (CHAOS MODE)" if chaos_mode else ""
            await self.emit_log(swarm_id, f"Initializing Swarm Engine for Swarm ID: {swarm_id}{mode_str}...")
            await asyncio.sleep(1)
            
            # Step 1: Triage
            await self._agent_triage(swarm_id)
            
            # Step 2: Research
            await self._agent_researcher(swarm_id, chaos_mode)
            
            await self.emit_log(swarm_id, f"Swarm Engine execution complete for {swarm_id}.")
        except Exception as e:
            await self.emit_log(swarm_id, f"ERROR: {str(e)}", "System")

    def trigger_swarm(self, config: Dict[str, Any]) -> str:
        """Start a swarm execution and return the tracking ID."""
        swarm_id = f"swarm_{uuid.uuid4().hex[:8]}"
        task = asyncio.create_task(self._run_swarm(swarm_id, config))
        self.tasks[swarm_id] = task
        return swarm_id

# Global singleton instance
swarm_engine = SwarmEngine()
