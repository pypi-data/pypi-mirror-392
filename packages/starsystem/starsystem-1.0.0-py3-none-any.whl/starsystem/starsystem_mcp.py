#!/usr/bin/env python3
"""
STARSYSTEM MCP Server - Master help system for Isaac's compound intelligence architecture

Provides unified understanding and configuration for the entire STARSYSTEM ecosystem.
Uses HEAVEN registry system with full reference resolution support.
"""

import os
import sys
import json
import traceback
import logging
from pathlib import Path
from fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from heaven_base.registry.registry_service import RegistryService
except ImportError as e:
    logger.error(f"Failed to import RegistryService: {e}")
    logger.error(traceback.format_exc())
    RegistryService = None

# Import Mission system
from . import mission

# Import Reward system
import starsystem_reward_system as reward_system

# Initialize MCP
mcp = FastMCP("STARSYSTEM")

@mcp.tool()
def help_me_understand_the_entire_system() -> str:
    """
    Get comprehensive overview of the entire STARSYSTEM compound intelligence architecture.
    
    Retrieves the master system definition from starsystem_help registry with full 
    reference resolution support including registry_key_ref, registry_object_ref, 
    and registry_all_ref patterns.
    
    Returns:
        Complete system definition with all registry references resolved
    """
    try:
        if not RegistryService:
            return """# 🌟 STARSYSTEM - Registry Service Not Available

Error: Could not import HEAVEN registry system. This means the HEAVEN framework 
is not properly installed or accessible.

Please ensure:
1. HEAVEN framework is installed at /home/GOD/heaven-framework-repo
2. heaven_base package is properly installed
3. Registry system dependencies are available

STARSYSTEM Components (when registry is available):
- STARSYSTEM__SEED (identity/perception management)
- STARSYSTEM__STARLOG (project workflow memory)
- STARSYSTEM__GIINT_STARPORT (cognitive separation engine)
- STARSYSTEM__CARTON (knowledge storage with Neo4j)
- STARSYSTEM__WAYPOINT (learning journey navigation)
- STARSYSTEM__HEAVEN (agent orchestration framework)

Master Sequence: SEED → STARLOG → Starship Flight Configs → Subchains"""

        # Initialize registry service
        registry_service = RegistryService()
        logger.info("Accessing starsystem_help registry for system definition")
        
        # Get the master system definition with full reference resolution
        system_def = registry_service.get("starsystem_help", "starsystem_def")
        
        if system_def:
            logger.info("Successfully retrieved system definition from starsystem_help registry")
            return system_def
        else:
            logger.warning("System definition not found in starsystem_help registry")
            return """# 🌟 STARSYSTEM - System Definition Not Found

The starsystem_help registry is accessible but the system definition is missing.

Available registries: {}

To populate the system definition, use:
registry_tool(operation="add", registry_name="starsystem_help", key="starsystem_def", value_str="...")

Core STARSYSTEM Components:
- STARSYSTEM__SEED: Identity unification and perception management
- STARSYSTEM__STARLOG: Project workflow memory and orchestration
- STARSYSTEM__GIINT_STARPORT: Cognitive separation for multi-fire intelligence
- STARSYSTEM__CARTON: Knowledge storage with Neo4j graph relationships
- STARSYSTEM__WAYPOINT: Systematic learning journey navigation
- STARSYSTEM__HEAVEN: Multi-agent orchestration and tool coordination

Master Workflow: SEED → STARLOG → Starship Flight → Subchains[GIINT|Waypoint|Carton|HEAVEN|...]""".format(
                ', '.join(registry_service.list_registries())
            )
            
    except Exception as e:
        logger.error(f"Error accessing STARSYSTEM registry: {e}")
        logger.error(traceback.format_exc())
        return f"""# 🌟 STARSYSTEM - Registry Access Error

Error accessing starsystem_help registry: {str(e)}

This indicates an issue with the HEAVEN registry system. The registry system
provides powerful reference resolution including:

• registry_key_ref=<registry>:<key> → "@<registry>/<key>" (locator strings)
• registry_object_ref=<registry>:<key> → resolved value with recursive resolution  
• registry_all_ref=<registry> → entire registry contents with resolution

Debug Information:
- Registry service import: {'Success' if RegistryService else 'Failed'}
- Error details: {str(e)}

Full traceback:
{traceback.format_exc()}

Please verify HEAVEN framework installation and registry system availability."""

@mcp.tool()
def check_selfplay_logs(last_n: int = 10) -> str:
    """
    Check OMNISANC Self-Play System logs to see current mode and recent events.

    This tool provides visibility into what OMNISANC is doing by reading the event
    logs from the matryoshka registries. Shows:
    - Recent validation decisions
    - Current mode transitions
    - Tool blocks and why
    - Error events

    Args:
        last_n: Number of recent events to show (default: 10)

    Returns:
        Formatted log output showing recent OMNISANC activity
    """
    try:
        if not RegistryService:
            return "❌ Registry Service not available - cannot read OMNISANC logs"

        from datetime import datetime
        registry_service = RegistryService()
        today = datetime.now().strftime("%Y-%m-%d")

        # Read from all three event registries
        all_events = []

        for registry_base in ["home_events", "mission_events", "session_events"]:
            events = reward_system.get_events_from_registry(registry_service, registry_base, today)
            all_events.extend(events)

        # Sort by timestamp
        all_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Take last N events
        recent_events = all_events[:last_n]

        if not recent_events:
            return f"""# 🛡️ OMNISANC Self-Play Logs

No events logged today ({today}).

This means either:
- No tool calls have been made yet today
- Event logging system hasn't been triggered
- Event registries haven't been created yet

Current mode: Unknown (no events to analyze)"""

        # Format output
        output = [f"# 🛡️ OMNISANC Self-Play Logs (Last {len(recent_events)} events)"]
        output.append(f"\n**Date**: {today}")
        output.append(f"**Total events today**: {len(all_events)}")

        # Determine current mode from most recent event
        latest_mode = recent_events[0].get("mode", "UNKNOWN")
        output.append(f"**Current Mode**: {latest_mode}")
        output.append("\n## Recent Events:\n")

        for i, event in enumerate(recent_events, 1):
            timestamp = event.get("timestamp", "unknown")
            tool_name = event.get("tool_name", "unknown")
            allowed = event.get("allowed", False)
            mode = event.get("mode", "unknown")
            reason = event.get("reason", "")
            registry = event.get("_registry", "unknown")

            status_emoji = "✅" if allowed else "🚫"

            output.append(f"{i}. {status_emoji} **{tool_name}**")
            output.append(f"   - Time: {timestamp}")
            output.append(f"   - Mode: {mode}")
            output.append(f"   - Registry: {registry}")

            if not allowed and reason:
                output.append(f"   - Blocked: {reason[:100]}")
            elif reason and "error" in reason.lower():
                output.append(f"   - Note: {reason[:100]}")

            output.append("")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error reading OMNISANC logs: {e}")
        logger.error(traceback.format_exc())
        return f"""# 🛡️ OMNISANC Self-Play Logs - Error

Failed to read event logs: {str(e)}

This could mean:
- Event registries don't exist yet
- Registry system issue
- Permission problem

Error details:
{traceback.format_exc()}"""


@mcp.tool()
def toggle_omnisanc(enable: bool = None) -> str:
    """
    Toggle OMNISANC enforcement on/off for development.

    OMNISANC has a global kill switch that disables all validation when needed.
    This is essential for development work on the hooks system itself.

    Args:
        enable: True to enable OMNISANC, False to disable it, None to check status

    Returns:
        Current OMNISANC status
    """
    kill_switch_file = "/tmp/heaven_data/omnisanc_core/.omnisanc_disabled"

    try:
        os.makedirs(os.path.dirname(kill_switch_file), exist_ok=True)

        if enable is None:
            # Check status
            is_disabled = os.path.exists(kill_switch_file)
            status = "DISABLED ⛔" if is_disabled else "ENABLED ✅"
            return f"""# 🛡️ OMNISANC Status

Current Status: {status}

OMNISANC enforces workflow validation including:
- HOME/Journey mode separation
- Waypoint sequence enforcement
- Session management rules
- Mission tracking

Use toggle_omnisanc(enable=False) to disable for development work.
Use toggle_omnisanc(enable=True) to re-enable enforcement."""

        elif enable:
            # Enable OMNISANC (remove kill switch file)
            if os.path.exists(kill_switch_file):
                os.remove(kill_switch_file)
                return "✅ OMNISANC ENABLED - All workflow validation active"
            else:
                return "✅ OMNISANC already enabled"

        else:
            # Disable OMNISANC (create kill switch file)
            with open(kill_switch_file, 'w') as f:
                f.write("OMNISANC disabled for development")
            return "⛔ OMNISANC DISABLED - All tools allowed, no validation"

    except Exception as e:
        logger.error(f"Error toggling OMNISANC: {e}")
        return f"❌ Error toggling OMNISANC: {str(e)}"


@mcp.tool()
def view_mission_config(mission_id: str) -> str:
    """
    View complete mission configuration including all sessions and current progress.

    Shows the entire mission blueprint with:
    - Mission metadata (name, description, domain, status)
    - All session steps (original + any injected steps)
    - Current progress (which step we're on)
    - Session status (pending/in_progress/completed)
    - Timestamps

    Args:
        mission_id: Mission identifier

    Returns:
        Formatted mission configuration display
    """
    try:
        loaded_mission = mission.load_mission(mission_id)
        if not loaded_mission:
            return f"❌ Mission '{mission_id}' not found"

        output = [f"# 🎯 Mission Configuration: {loaded_mission.name}"]
        output.append("")
        output.append(f"**Mission ID:** {loaded_mission.mission_id}")
        output.append(f"**Status:** {loaded_mission.status}")
        output.append(f"**Domain:** {loaded_mission.domain} / {loaded_mission.subdomain}")
        output.append(f"**Description:** {loaded_mission.description}")
        output.append("")
        output.append(f"**Created:** {loaded_mission.created_at}")
        if loaded_mission.started_at:
            output.append(f"**Started:** {loaded_mission.started_at}")
        if loaded_mission.completed_at:
            output.append(f"**Completed:** {loaded_mission.completed_at}")
        output.append("")

        # Progress
        total_sessions = len(loaded_mission.session_sequence)
        current = loaded_mission.current_step
        output.append(f"**Progress:** Step {current + 1}/{total_sessions}")
        output.append("")

        # Session sequence
        output.append("## 📋 Session Sequence")
        output.append("")

        for idx, session in enumerate(loaded_mission.session_sequence):
            marker = "→" if idx == current else " "
            status_icon = "✅" if session.status == "completed" else "🔄" if session.status == "in_progress" else "⏸️"

            output.append(f"{marker} **Step {idx + 1}:** {status_icon} {session.status.upper()}")
            output.append(f"   - Project: {session.project_path}")
            output.append(f"   - Flight: {session.flight_config}")

            if session.started_at:
                output.append(f"   - Started: {session.started_at}")
            if session.completed_at:
                output.append(f"   - Completed: {session.completed_at}")
            if session.notes:
                output.append(f"   - Notes: {session.notes}")
            output.append("")

        # Metrics
        output.append("## 📊 Metrics")
        output.append(f"- Sessions Completed: {loaded_mission.metrics.sessions_completed}")
        output.append(f"- Sessions Aborted: {loaded_mission.metrics.sessions_aborted}")
        output.append(f"- Total Duration: {loaded_mission.metrics.total_duration_minutes:.1f} minutes")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error viewing mission config: {e}")
        return f"❌ Error viewing mission: {str(e)}"


@mcp.tool()
def complete_mission(mission_id: str, notes: str = "") -> str:
    """
    Mark a mission as completed.

    Completes the mission by:
    - Setting status to "completed"
    - Recording completion timestamp
    - Updating metrics
    - Resetting course state to HOME

    Args:
        mission_id: Mission identifier
        notes: Optional completion notes

    Returns:
        Completion confirmation
    """
    try:
        loaded_mission = mission.load_mission(mission_id)
        if not loaded_mission:
            return f"❌ Mission '{mission_id}' not found"

        if loaded_mission.status == "completed":
            return f"✅ Mission '{mission_id}' already completed"

        # Validation: Check all sessions are completed
        pending_sessions = [
            s for s in loaded_mission.session_sequence
            if s.status in ["pending", "in_progress"]
        ]
        
        if pending_sessions:
            pending_info = "\n".join([
                f"  - Step {i}: {s.project_path} with {s.flight_config} (status: {s.status})"
                for i, s in enumerate(loaded_mission.session_sequence)
                if s.status in ["pending", "in_progress"]
            ])
            return f"""❌ Cannot complete mission: {len(pending_sessions)} session(s) not completed

**Pending/In-Progress Sessions:**
{pending_info}

All sessions must be completed before mission can be marked complete."""

        # Validation passed - all sessions completed
        # Update mission
        from datetime import datetime
        loaded_mission.status = "completed"
        loaded_mission.completed_at = datetime.now().isoformat()

        # Save mission
        mission.save_mission(loaded_mission)

        # Reset course state to HOME
        course_state_file = "/tmp/heaven_data/omnisanc_core/.course_state"
        try:
            with open(course_state_file, 'r') as f:
                state = json.load(f)

            state["mission_active"] = False
            state["mission_id"] = None
            state["mission_step"] = 0
            state["course_plotted"] = False
            state["flight_selected"] = False

            with open(course_state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not reset course state: {e}")

        return f"""✅ Mission Completed: {loaded_mission.name}

**Mission ID:** {mission_id}
**Completed At:** {loaded_mission.completed_at}
**Sessions Completed:** {loaded_mission.metrics.sessions_completed}
**Total Duration:** {loaded_mission.metrics.total_duration_minutes:.1f} minutes

{f'**Notes:** {notes}' if notes else ''}

🏠 Course reset to HOME mode"""

    except Exception as e:
        logger.error(f"Error completing mission: {e}")
        return f"❌ Error completing mission: {str(e)}"


@mcp.tool()
def get_fitness_score(date: str = None) -> str:
    """
    Get current fitness score and reward breakdown.

    Shows:
    - Fitness score (overall usage reward)
    - Level (fitness as integer)
    - XP (total accumulated rewards)
    - Breakdown by home/session/mission rewards
    - Quality factor

    Args:
        date: Date to compute fitness for (YYYY-MM-DD), defaults to today

    Returns:
        Formatted fitness report
    """
    try:
        if not RegistryService:
            return "❌ Registry Service not available - cannot compute fitness"

        from datetime import datetime
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        registry_service = RegistryService()
        fitness_data = reward_system.compute_fitness(registry_service, date)

        output = [
            "# 🎯 Fitness Score Report",
            "",
            f"**Date**: {date}",
            f"**Fitness**: {fitness_data['fitness']:.2f}",
            f"**Level**: {fitness_data['level']}",
            f"**XP**: {fitness_data['xp']:.2f}",
            "",
            "## Reward Breakdown:",
            "",
            f"- **Home Rewards**: {fitness_data['breakdown']['home_rewards']:.2f} (1x multiplier)",
            f"- **Session Rewards**: {fitness_data['breakdown']['session_rewards']:.2f} (3x multiplier)",
            f"- **Mission Rewards**: {fitness_data['breakdown']['mission_rewards']:.2f} (10x multiplier)",
            f"- **Quality Factor**: {fitness_data['breakdown']['quality_factor']:.2%}",
            "",
            "**Formula**: Fitness = (Home + Session + Mission) × Quality Factor",
            "",
            "Use starsystem.check_selfplay_logs() to see recent events."
        ]

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error computing fitness: {e}")
        logger.error(traceback.format_exc())
        return f"""# 🎯 Fitness Score - Error

Failed to compute fitness: {str(e)}

Error details:
{traceback.format_exc()}"""


@mcp.tool()
def query_scores_with_neo4j() -> str:
    """
    Get instructions for querying fitness scores from Neo4j graph database.

    Scores are persisted to Neo4j after sessions/missions complete via the
    scoring_persistence.py hook. This tool provides the schema, namespace info,
    and example queries for accessing historical score data.

    Returns:
        Complete guide to querying the score namespace in Neo4j
    """
    guide = """# 🔍 Querying Fitness Scores from Neo4j

## Prerequisites

You need **HEAVEN Framework Toolbox** equipped to query Neo4j.
Use: `omnitool('Neo4jTool', parameters={...})`

## Neo4j Score Namespace Schema

**Nodes**:
- `:Session` - Individual work sessions
  - Properties: id, project_path, timestamp, date
- `:Mission` - Mission executions
  - Properties: id, completed_at
- `:Project` - STARLOG projects
  - Properties: path
- `:ScoreEntry` - Fitness score records
  - Properties: id, type, raw_score, fitness, level, xp, timestamp, computation_trace

**Relationships**:
- `(:Session)-[:IN_PROJECT]->(:Project)`
- `(:ScoreEntry)-[:SCORED]->(:Session | :Mission)`

## Example Queries

### 1. Get Recent Sessions with Scores
```python
omnitool('Neo4jTool', parameters={
    "query": '''
        MATCH (s:Session)-[:IN_PROJECT]->(p:Project)
        MATCH (score:ScoreEntry)-[:SCORED]->(s)
        RETURN s.id, s.date, p.path, score.fitness, score.level, score.xp
        ORDER BY s.timestamp DESC
        LIMIT 10
    '''
})
```

### 2. Fitness Trends by Date
```python
omnitool('Neo4jTool', parameters={
    "query": '''
        MATCH (score:ScoreEntry)-[:SCORED]->(s:Session)
        RETURN s.date,
               avg(score.fitness) as avg_fitness,
               max(score.fitness) as max_fitness,
               min(score.fitness) as min_fitness,
               count(s) as session_count
        GROUP BY s.date
        ORDER BY s.date DESC
    '''
})
```

### 3. Project Performance Comparison
```python
omnitool('Neo4jTool', parameters={
    "query": '''
        MATCH (s:Session)-[:IN_PROJECT]->(p:Project)
        MATCH (score:ScoreEntry)-[:SCORED]->(s)
        RETURN p.path,
               count(s) as total_sessions,
               avg(score.fitness) as avg_fitness,
               sum(score.xp) as total_xp
        GROUP BY p.path
        ORDER BY avg_fitness DESC
    '''
})
```

### 4. Get Specific Project History
```python
omnitool('Neo4jTool', parameters={
    "query": '''
        MATCH (s:Session)-[:IN_PROJECT]->(p:Project)
        MATCH (score:ScoreEntry)-[:SCORED]->(s)
        WHERE p.path = $project_path
        RETURN s.date, score.fitness, score.level
        ORDER BY s.timestamp DESC
    ''',
    "params": {"project_path": "/your/project/path"}
})
```

### 5. Mission Scores
```python
omnitool('Neo4jTool', parameters={
    "query": '''
        MATCH (score:ScoreEntry)-[:SCORED]->(m:Mission)
        RETURN m.id, m.completed_at, score.fitness, score.level
        ORDER BY m.completed_at DESC
    '''
})
```

## Visualize in Neo4j Browser

Add `"visualize": true` to open query in Neo4j Browser:
```python
omnitool('Neo4jTool', parameters={
    "query": "MATCH (s:Session)-[:IN_PROJECT]->(p:Project) RETURN s, p LIMIT 25",
    "visualize": true
})
```

## Notes

- Scores are written by `scoring_persistence.py` PostToolUse hook
- Triggered after: end_starlog, complete_mission, mission_request_extraction
- All scores include computation_trace (JSON breakdown of rewards)
- Use get_fitness_score() for live computation, Neo4j for historical analysis
"""
    return guide


@mcp.tool()
def create_mission_type(
    mission_type_id: str,
    name: str,
    domain: str,
    subdomain: str,
    description: str,
    session_sequence: list,
    required_variables: list,
    category: str = None,
    optional_variables: list = None,
    defaults: dict = None
) -> str:
    """
    Create a reusable mission type template

    Mission types are templates stored in HEAVEN registries that can be rendered
    with variables to create concrete missions.

    Args:
        mission_type_id: Unique identifier for this mission type
        name: Human-readable name
        domain: Mission domain (used for registry naming, e.g., 'feature_development')
        subdomain: Subdomain value or template with ${variables}
        description: Description template with ${variables}
        session_sequence: List of session dicts with ${variables} in values
        required_variables: List of variable names that must be provided
        category: Optional category for organization (defaults to domain)
        optional_variables: List of variable names with defaults
        defaults: Default values for optional variables

    Returns:
        Creation result with mission_type_id
    """
    from . import mission_types
    result = mission_types.create_mission_type(
        mission_type_id=mission_type_id,
        name=name,
        domain=domain,
        subdomain=subdomain,
        description=description,
        session_sequence=session_sequence,
        required_variables=required_variables,
        category=category,
        optional_variables=optional_variables,
        defaults=defaults
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def mission_select_menu(domain: str = None, page: int = 1) -> str:
    """
    Browse available mission types with pagination (like starship.fly())

    If no domain specified, shows available domains.
    If domain specified, shows mission types in that domain with pagination.

    Args:
        domain: Optional domain filter (shows domains if None)
        page: Page number for pagination (default 1)

    Returns:
        Formatted mission type listing with instructions for creating missions
    """
    from . import mission_types
    return mission_types.mission_select_menu(domain=domain, page=page)


@mcp.tool()
def mission_create(
    mission_id: str,
    name: str = None,
    description: str = None,
    domain: str = None,
    subdomain: str = None,
    session_sequence: list = None,
    mission_type: str = None,
    mission_type_domain: str = None,
    variables: dict = None
) -> str:
    """
    Create a new mission definition at HOME mode

    Two modes:
    1. Manual: Provide name, description, domain, subdomain, session_sequence
    2. From template: Provide mission_type, mission_type_domain, variables

    Args:
        mission_id: Unique mission identifier (e.g., 'auth_feature_implementation')
        name: Human-readable mission name (manual mode)
        description: Mission description and goals (manual mode)
        domain: Mission domain (manual mode, e.g., 'feature_development')
        subdomain: Mission subdomain (manual mode, e.g., 'authentication')
        session_sequence: List of session dicts with 'project_path' and 'flight_config' (manual mode)
        mission_type: Mission type template ID (template mode)
        mission_type_domain: Domain containing the mission type (template mode)
        variables: Variables to substitute in template (template mode)

    Returns:
        Mission creation result with mission_id and next steps
    """
    result = mission.create_mission(
        mission_id=mission_id,
        name=name,
        description=description,
        domain=domain,
        subdomain=subdomain,
        session_sequence=session_sequence,
        mission_type=mission_type,
        mission_type_domain=mission_type_domain,
        variables=variables
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def mission_start(mission_id: str) -> str:
    """
    Activate a mission from HOME mode

    Transitions from HOME → Journey with mission enforcement activated.
    OMNISANC Core will enforce the mission session sequence.

    Args:
        mission_id: Mission to activate

    Returns:
        Mission activation result with first session details
    """
    result = mission.start_mission(mission_id)
    return json.dumps(result, indent=2)


@mcp.tool()
def mission_get_status(mission_id: str) -> str:
    """
    Get current mission status and progress

    Shows current step, session details, metrics, and overall progress.

    Args:
        mission_id: Mission to query

    Returns:
        Mission status with current step and session details
    """
    result = mission.get_mission_status(mission_id)
    return json.dumps(result, indent=2)


@mcp.tool()
def mission_inject_step(
    mission_id: str,
    project_path: str,
    flight_config: str,
    notes: str = None
) -> str:
    """
    Inject a new step BEFORE the current step in mission sequence

    When you hit an obstacle or discover a prerequisite, inject a step to handle it.
    The injected step must be completed before continuing with the original sequence.

    Args:
        mission_id: Mission to modify
        project_path: Project path for new step
        flight_config: Flight config for new step
        notes: Optional notes about why step was injected

    Returns:
        Injection result with updated step index
    """
    result = mission.inject_mission_step(
        mission_id=mission_id,
        project_path=project_path,
        flight_config=flight_config,
        notes=notes
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def mission_report_progress(mission_id: str) -> str:
    """
    Report successful completion of current mission step and advance to next

    Call this when you've successfully completed a mission step. Marks current
    session as completed, increments to next step, and checks if mission is complete.

    Args:
        mission_id: Mission to update

    Returns:
        Progress report with next session info or completion status
    """
    result = mission.report_mission_progress(mission_id)
    return json.dumps(result, indent=2)


@mcp.tool()
def mission_request_extraction(mission_id: str) -> str:
    """
    Extract mission learnings and reset to HOME

    Analyzes mission execution, generates failure report with learnings,
    and resets system state to HOME mode for clean restart.

    Use this when a mission fails or needs to be abandoned - it captures
    what worked, what didn't, and provides insights for refining the mission template.

    Args:
        mission_id: Mission to extract

    Returns:
        Extraction report with learnings and reset confirmation
    """
    result = mission.request_mission_extraction(mission_id)
    return json.dumps(result, indent=2)


@mcp.tool()
def mission_list(status_filter: str = None) -> str:
    """
    List all missions, optionally filtered by status

    Shows available missions with basic info for mission management.

    Args:
        status_filter: Optional status to filter by (pending, active, completed, extracted)

    Returns:
        List of missions with basic info
    """
    result = mission.list_missions(status_filter)
    return json.dumps(result, indent=2)


def main():
    """Entry point for starsystem-server console script"""
    mcp.run()

if __name__ == "__main__":
    main()