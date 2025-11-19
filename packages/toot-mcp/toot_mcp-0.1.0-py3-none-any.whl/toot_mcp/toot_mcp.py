"""TOOT MCP server for train of thought management."""

import json
import os
import logging
import traceback
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not available - install mcp package")
    raise

# Import registry for activity tracking
try:
    from heaven_base.registry.registry_service import RegistryService
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    logger.warning("RegistryService not available - last_toot tracking disabled")

# Create FastMCP app
app = FastMCP("TOOT")

# Log the HEAVEN_DATA_DIR being used
heaven_data_dir = os.getenv('HEAVEN_DATA_DIR', '/tmp/heaven_data')
logger.info(f"TOOT MCP initialized with HEAVEN_DATA_DIR: {heaven_data_dir}")

def _get_toot_directory() -> Path:
    """Get the TOOT directory path."""
    heaven_data_dir = os.getenv('HEAVEN_DATA_DIR', '/tmp/heaven_data')
    toot_dir = Path(heaven_data_dir) / "toot"
    toot_dir.mkdir(parents=True, exist_ok=True)
    return toot_dir

def _validate_toot_name(name: str) -> str:
    """Validate and normalize TOOT name."""
    if not name or not isinstance(name, str):
        raise ValueError("TOOT name must be a non-empty string")
    
    # Remove any path separators and normalize
    normalized = name.replace("/", "_").replace("\\", "_")
    if not normalized.endswith("_toot"):
        normalized += "_toot"
    
    return normalized

def _validate_toot_data(data: Dict[str, Any]) -> None:
    """Validate TOOT data structure."""
    required_fields = ["concepts_to_track", "session_context", "reasoning_chain"]
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(data["concepts_to_track"], dict):
        raise ValueError("concepts_to_track must be a dictionary")
    
    if not isinstance(data["reasoning_chain"], list):
        raise ValueError("reasoning_chain must be a list")

def _prepare_toot_data(initial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare TOOT data with timestamp."""
    if "timestamp" not in initial_data:
        initial_data["timestamp"] = datetime.now().strftime("%Y-%m-%d")
    return initial_data

def _write_toot_file(file_path: Path, data: Dict[str, Any]) -> None:
    """Write TOOT data to file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _create_toot_file_path(name: str) -> Path:
    """Create and validate TOOT file path."""
    normalized_name = _validate_toot_name(name)
    toot_dir = _get_toot_directory()
    return toot_dir / f"{normalized_name}.json"

def _check_toot_exists(file_path: Path) -> bool:
    """Check if TOOT file already exists."""
    return file_path.exists()

def _track_toot_activity(name: str, file_path: Path) -> None:
    """Track TOOT activity to last_activity_tracking registry."""
    if not REGISTRY_AVAILABLE:
        return

    try:
        # Ensure HEAVEN_DATA_DIR is set
        heaven_data_dir = os.getenv('HEAVEN_DATA_DIR', '/tmp/heaven_data')
        os.environ['HEAVEN_DATA_DIR'] = heaven_data_dir

        registry_service = RegistryService()

        # Ensure registry exists
        if not registry_service.simple_service.registry_exists("last_activity_tracking"):
            registry_service.create_registry("last_activity_tracking")

        # Track TOOT activity
        toot_data = {
            "toot_name": name,
            "filepath": str(file_path),
            "timestamp": datetime.now().isoformat()
        }

        # Use add if first time, update if exists
        if not registry_service.add("last_activity_tracking", "last_toot", toot_data):
            # Key exists, update it
            registry_service.update("last_activity_tracking", "last_toot", toot_data)

    except Exception as e:
        logger.error(f"Failed to track TOOT activity: {e}")

@app.tool()
def create_train_of_thought(name: str, initial_data: Dict[str, Any]) -> str:
    """Create a new train of thought reasoning chain."""
    try:
        _validate_toot_data(initial_data)
        file_path = _create_toot_file_path(name)

        if _check_toot_exists(file_path):
            return f"❌ TOOT already exists: {file_path}"

        prepared_data = _prepare_toot_data(initial_data)
        _write_toot_file(file_path, prepared_data)

        # Track activity to registry
        _track_toot_activity(name, file_path)

        logger.info(f"Created TOOT: {file_path}")
        return f"✅ Created train of thought: {file_path}"

    except Exception as e:
        logger.error(f"Failed to create TOOT '{name}': {traceback.format_exc()}")
        return f"❌ Failed to create TOOT: {str(e)}"

def _load_existing_toot(file_path: Path) -> Dict[str, Any]:
    """Load existing TOOT data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _merge_toot_updates(existing_data: Dict[str, Any], updated_data: Dict[str, Any]) -> Dict[str, Any]:
    """Merge updates into existing TOOT data (append-only for concepts and reasoning)."""
    if "concepts_to_track" in updated_data:
        existing_data["concepts_to_track"].update(updated_data["concepts_to_track"])
    
    if "reasoning_chain" in updated_data:
        if isinstance(updated_data["reasoning_chain"], list):
            existing_data["reasoning_chain"].extend(updated_data["reasoning_chain"])
        else:
            existing_data["reasoning_chain"].append(updated_data["reasoning_chain"])
    
    # Update other fields directly
    for key, value in updated_data.items():
        if key not in ["concepts_to_track", "reasoning_chain"]:
            existing_data[key] = value
    
    # Update timestamp
    existing_data["timestamp"] = datetime.now().strftime("%Y-%m-%d")
    return existing_data

def _update_existing_toot(name: str, updated_data: Dict[str, Any]) -> Path:
    """Update existing TOOT file and return file path."""
    file_path = _create_toot_file_path(name)
    
    if not file_path.exists():
        raise FileNotFoundError(f"TOOT not found: {file_path}")
    
    existing_data = _load_existing_toot(file_path)
    merged_data = _merge_toot_updates(existing_data, updated_data)
    _write_toot_file(file_path, merged_data)
    
    return file_path

@app.tool()
def update_train_of_thought(name: str, updated_data: Dict[str, Any]) -> str:
    """Update existing train of thought reasoning chain (append-only)."""
    try:
        file_path = _update_existing_toot(name, updated_data)

        # Track activity to registry
        _track_toot_activity(name, file_path)

        logger.info(f"Updated TOOT: {file_path}")
        return f"✅ Updated train of thought: {file_path}"

    except FileNotFoundError as e:
        return f"❌ {str(e)}"
    except Exception as e:
        logger.error(f"Failed to update TOOT '{name}': {traceback.format_exc()}")
        return f"❌ Failed to update TOOT: {str(e)}"

@app.tool()
def get_toot_dir() -> str:
    """Get the TOOT directory path for search and bash operations.
    
    Returns:
        Absolute path to the TOOT directory
    """
    try:
        toot_dir = _get_toot_directory()
        logger.info(f"TOOT directory: {toot_dir}")
        return str(toot_dir)
        
    except Exception as e:
        logger.error(f"Failed to get TOOT directory: {traceback.format_exc()}")
        return f"❌ Failed to get TOOT directory: {str(e)}"

def _get_recent_toots(limit: int = 5) -> list:
    """Get recently active TOOTs by last modified time."""
    try:
        toot_dir = _get_toot_directory()
        toot_files = []
        
        # Get all .json files in toot directory
        for file_path in toot_dir.glob("*.json"):
            if file_path.name != "example_toot.json":  # Skip example
                stat = file_path.stat()
                toot_files.append({
                    "name": file_path.stem.replace("_toot", ""),
                    "path": str(file_path),
                    "modified": stat.st_mtime
                })
        
        # Sort by modification time (newest first) and limit
        toot_files.sort(key=lambda x: x["modified"], reverse=True)
        return toot_files[:limit]
        
    except Exception as e:
        logger.error(f"Error getting recent TOOTs: {traceback.format_exc()}")
        return []

@app.tool()
def explain_train_of_thought() -> str:
    """Explain what Train of Operadic Thought (ToOT) is and how to use it.
    
    Returns:
        Complete explanation and usage guide for the ToOT system
    """
    # Get recent TOOTs for status
    recent_toots = _get_recent_toots()
    recent_list = ""
    if recent_toots:
        recent_list = "\n## 📈 Your Most Recently Active Trains of Thought:\n\n"
        for toot in recent_toots:
            recent_list += f"- **{toot['name']}**\n"
    else:
        recent_list = "\n## 📈 Your Most Recently Active Trains of Thought:\n\n*No active trains of thought yet - create your first one!*\n"
    
    return """🧠 Welcome to Train of Operadic Thought (ToOT)!
""" + recent_list + """
## What is ToOT?

Train of Operadic Thought (ToOT) is a validated conceptual reasoning tracking system designed for compound intelligence workflows. ToOT captures and manages reasoning chains across conversation branches, enabling systematic architectural refinement and knowledge accumulation.

## Core Concepts

🔗 **Reasoning Chains**: Sequential logical progression steps that build toward architectural decisions
🎯 **Concept Tracking**: Key architectural concepts and their evolution throughout reasoning sessions  
📊 **Session Context**: Situational awareness about what problem space is being explored
🌿 **Conversation Branching**: Support for iterative refinement through conversation branching strategy
📚 **Append-Only History**: Preserves complete reasoning evolution without losing context

## How ToOT Works

ToOT operates as an **append-only reasoning capture system**:
- **Create** new reasoning chains when starting architectural exploration
- **Update** existing chains as reasoning evolves (always appending, never overwriting)
- **Track concepts** that emerge during reasoning sessions
- **Maintain context** across conversation branches and iterations

## Usage

### 1. Start New Reasoning Chain
```
create_train_of_thought(name, {
    "concepts_to_track": {
        "Key_Concept_1": "Description of what this concept represents",
        "Key_Concept_2": "Another important concept being tracked"
    },
    "session_context": "Brief description of what you're exploring",
    "reasoning_chain": ["Initial reasoning step", "Next logical step"]
})
```

### 2. Evolve Existing Reasoning
```
update_train_of_thought(name, {
    "concepts_to_track": {
        "New_Concept": "Emerged during reasoning evolution"
    },
    "reasoning_chain": ["New reasoning step", "Further insights"]
})
```

### 3. File System Access
```
get_toot_dir()  # Returns path for direct file system operations
```

## Integration with Compound Intelligence

🎯 **Carton Integration**: ToOT concepts are automatically captured in Carton knowledge graph
🚀 **STARLOG Integration**: Reasoning chains inform project execution context
📋 **GIINT Integration**: Architectural decisions flow into project planning structures
🔄 **Master Sequence**: ToOT provides reasoning context for workflow orchestration

## Benefits

✅ **Conversation Branching Support**: Enables Isaac's iterative refinement methodology
✅ **Knowledge Accumulation**: Reasoning chains compound over time
✅ **Architectural Validation**: Systematic capture of decision reasoning
✅ **Context Preservation**: No loss of reasoning context across iterations
✅ **Pattern Recognition**: Identifies recurring architectural reasoning patterns

## File Structure

ToOT files are stored as JSON in `${HEAVEN_DATA_DIR}/toot/`:
```
{
  "concepts_to_track": { "concept": "description" },
  "session_context": "what we're working on",
  "timestamp": "2025-09-10",
  "reasoning_chain": ["step 1", "step 2", "..."]
}
```

ToOT enables **validated conceptual reasoning** within the compound intelligence ecosystem, turning architectural conversations into systematic knowledge building! 🧠✨"""

def _call_registry_tool(operation: str, registry_name: str = None, key: str = None, value_dict: Dict[str, Any] = None) -> Any:
    """Call the HEAVEN registry tool from installed library with proper HEAVEN_DATA_DIR."""
    try:
        # Ensure HEAVEN_DATA_DIR is set for the registry system
        heaven_data_dir = os.getenv('HEAVEN_DATA_DIR', '/tmp/heaven_data')
        os.environ['HEAVEN_DATA_DIR'] = heaven_data_dir
        
        from heaven_base.tools.registry_tool import registry_util_func
        result = registry_util_func(
            operation=operation,
            registry_name=registry_name,
            key=key,
            value_dict=value_dict
        )
        return result
    except Exception as e:
        logger.error(f"Failed to call registry tool: {traceback.format_exc()}")
        return None

def _ensure_registry_hierarchy(domain: str, process: str) -> bool:
    """Ensure the hierarchical registry structure exists for domain and process."""
    try:
        # 1. Ensure meta registry exists and has domain entry
        meta_result = _call_registry_tool("add", "toot_meta_registry", domain, {"domain": domain, "created": datetime.now().isoformat()})
        
        # 2. Ensure domain registry exists
        domain_registry = f"toot_domain_{domain}"
        domain_result = _call_registry_tool("create_registry", domain_registry)
        
        # 3. Add process to domain registry
        process_result = _call_registry_tool("add", domain_registry, process, {"process": process, "created": datetime.now().isoformat()})
        
        # 4. Ensure process-specific pattern registry exists
        pattern_registry = f"toot_patterns_{domain}_{process}"
        pattern_result = _call_registry_tool("create_registry", pattern_registry)
        
        return True
    except Exception as e:
        logger.error(f"Failed to ensure registry hierarchy: {traceback.format_exc()}")
        return False

def _create_success_pattern_data(name: str, domain: str, process: str, description: str, filepaths_involved: list, sequencing: list) -> Dict[str, Any]:
    """Create success pattern data structure."""
    return {
        "type": "positive_feedback",
        "domain": domain,
        "process": process,
        "description": description,
        "filepaths_involved": filepaths_involved,
        "sequencing": sequencing,
        "concepts_to_track": {
            f"Success_Pattern_{domain}_{process}": f"Successful {process} in {domain}: {description}",
            f"Effective_Sequencing_{name}": f"Proven sequence: {' → '.join(str(s) for s in sequencing)}"
        },
        "session_context": f"Recording successful pattern: {name} ({process} in {domain})",
        "reasoning_chain": [
            f"User confirmed success in {domain} for {process}",
            f"Pattern: {description}",
            f"Files involved: {', '.join(filepaths_involved)}",
            f"Sequence that worked: {' → '.join(str(s) for s in sequencing)}",
            "This pattern should be reinforced and referenced for similar work"
        ],
        "success_metrics": {
            "user_satisfaction": "positive",
            "domain": domain,
            "pattern_type": "validated_success"
        }
    }

def _fallback_file_storage(name: str, success_data: Dict[str, Any]) -> str:
    """Fallback to original file storage when registry fails."""
    toot_name = f"success_pattern_{name}"
    file_path = _create_toot_file_path(toot_name)
    
    if _check_toot_exists(file_path):
        file_path = _update_existing_toot(toot_name, success_data)
        return f"✅ Updated success pattern: {file_path}"
    else:
        prepared_data = _prepare_toot_data(success_data)
        _write_toot_file(file_path, prepared_data)
        return f"✅ Recorded new success pattern: {file_path}"

def _store_in_registry(name: str, success_data: Dict[str, Any]) -> str:
    """Store success pattern in registry hierarchy."""
    domain = success_data["domain"]
    process = success_data["process"]
    
    pattern_registry = f"toot_patterns_{domain}_{process}"
    pattern_key = f"success_pattern_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    success_data["timestamp"] = datetime.now().isoformat()
    success_data["pattern_key"] = pattern_key
    
    result = _call_registry_tool("add", pattern_registry, pattern_key, success_data)
    if result:
        return f"✅ Recorded success pattern in registry: {pattern_registry}/{pattern_key}"
    else:
        return None

def _append_to_how_do_i_seed(name: str, success_data: Dict[str, Any]) -> bool:
    """Append success pattern to how_do_i.seed catalog."""
    try:
        heaven_data_dir = os.getenv('HEAVEN_DATA_DIR', '/tmp/heaven_data')
        how_do_i_file = Path(heaven_data_dir) / "seed" / "how_do_i.seed"

        # Ensure seed directory exists
        how_do_i_file.parent.mkdir(parents=True, exist_ok=True)

        # Format the entry
        domain = success_data["domain"]
        process = success_data["process"]
        description = success_data["description"]
        sequencing = success_data["sequencing"]

        # Create sequencing summary (first 3 steps)
        seq_summary = " → ".join(str(s) for s in sequencing[:3])
        if len(sequencing) > 3:
            seq_summary += "..."

        # Format: name|✅ domain/process: description. Sequencing: summary.
        entry = f"{name}|✅ {domain}/{process}: {description}. Sequencing: {seq_summary}.\n"

        # Append to file
        with open(how_do_i_file, 'a', encoding='utf-8') as f:
            f.write(entry)

        logger.info(f"Appended success pattern to how_do_i.seed: {name}")
        return True

    except Exception as e:
        logger.error(f"Failed to append to how_do_i.seed: {traceback.format_exc()}")
        return False

def _save_success_pattern(name: str, success_data: Dict[str, Any]) -> str:
    """Save success pattern to HEAVEN registry hierarchy and how_do_i.seed."""
    domain = success_data["domain"]
    process = success_data["process"]

    # Ensure hierarchical registry structure exists
    if not _ensure_registry_hierarchy(domain, process):
        logger.warning("Registry hierarchy creation failed, falling back to file storage")
        result = _fallback_file_storage(name, success_data)
    else:
        # Try registry storage first
        registry_result = _store_in_registry(name, success_data)
        if registry_result:
            result = registry_result
        else:
            logger.warning("Registry storage failed, falling back to file storage")
            result = _fallback_file_storage(name, success_data)

    # Also append to how_do_i.seed catalog
    if _append_to_how_do_i_seed(name, success_data):
        result += "\n✅ Added to how_do_i.seed capability catalog"
    else:
        result += "\n⚠️ Warning: Could not update how_do_i.seed catalog"

    return result

@app.tool()
def user_said_i_did_a_good_job(name: str, domain: str, process: str, description: str, filepaths_involved: list, sequencing: list) -> str:
    """Record positive feedback and successful patterns for reinforcement learning."""
    try:
        success_data = _create_success_pattern_data(name, domain, process, description, filepaths_involved, sequencing)
        return _save_success_pattern(name, success_data)
    except Exception as e:
        logger.error(f"Failed to record success pattern '{name}': {traceback.format_exc()}")
        return f"❌ Failed to record success pattern: {str(e)}"

def _get_patterns_from_domain_registry(domain: str) -> list:
    """Get patterns for a specific domain from registry."""
    patterns = []
    domain_registry = f"toot_domain_{domain}"
    processes = _call_registry_tool("get_all", domain_registry)
    
    if processes:
        for process_key, process_data in processes.items():
            pattern_registry = f"toot_patterns_{domain}_{process_key}"
            registry_patterns = _call_registry_tool("get_all", pattern_registry)
            if registry_patterns:
                for pattern_key, pattern_data in registry_patterns.items():
                    patterns.append({
                        "name": pattern_key.replace("success_pattern_", ""),
                        "domain": pattern_data.get("domain", domain),
                        "process": pattern_data.get("process", process_key),
                        "description": pattern_data.get("description", ""),
                        "sequencing": pattern_data.get("sequencing", [])
                    })
    return patterns

def _get_patterns_from_file_system(domain: str = None) -> list:
    """Fallback to get patterns from file system."""
    patterns = []
    toot_dir = _get_toot_directory()
    
    for file_path in toot_dir.glob("*success_pattern*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                pattern_data = json.load(f)
                if not domain or pattern_data.get("domain") == domain:
                    patterns.append({
                        "name": file_path.stem.replace("success_pattern_", "").replace("_toot", ""),
                        "domain": pattern_data.get("domain", "unknown"),
                        "process": pattern_data.get("process", "unknown"),
                        "description": pattern_data.get("description", ""),
                        "sequencing": pattern_data.get("sequencing", [])
                    })
        except Exception as e:
            logger.warning(f"Could not read success pattern {file_path}: {traceback.format_exc()}")
    return patterns

def _get_success_patterns(domain: str = None) -> list:
    """Get success patterns from HEAVEN registry hierarchy and file fallback."""
    success_patterns = []
    
    try:
        if domain:
            success_patterns = _get_patterns_from_domain_registry(domain)
        else:
            # Get patterns across all domains
            meta_registry = _call_registry_tool("get_all", "toot_meta_registry")
            if meta_registry:
                for domain_key in meta_registry.keys():
                    patterns_for_domain = _get_patterns_from_domain_registry(domain_key)
                    success_patterns.extend(patterns_for_domain)
    except Exception as e:
        logger.warning(f"Registry lookup failed, falling back to file system: {traceback.format_exc()}")
    
    # Fallback to file system if registry is empty or fails
    if not success_patterns:
        success_patterns = _get_patterns_from_file_system(domain)
    
    return success_patterns

def _create_intention_data(description: str, domain: str, success_patterns: list) -> Dict[str, Any]:
    """Create intention data structure."""
    return {
        "type": "intention_setting",
        "domain": domain or "general",
        "task_description": description,
        "concepts_to_track": {
            f"Intention_{domain or 'general'}": f"Committed to excellence: {description}",
            "Quality_Focus": "Setting high standards for upcoming work"
        },
        "session_context": f"Setting intention to do excellent work: {description}",
        "reasoning_chain": [
            f"Setting intention: {description}",
            f"Domain: {domain or 'general'}",
            f"Found {len(success_patterns)} relevant success patterns to reference",
            "Committing to applying learned patterns and maintaining quality standards"
        ],
        "referenced_success_patterns": success_patterns,
        "intention_metrics": {
            "commitment_level": "high",
            "domain": domain or "general",
            "pattern_type": "intention_setting"
        }
    }

def _build_intention_response(file_path: Path, description: str, success_patterns: list) -> str:
    """Build response message with success patterns."""
    response = f"✅ Intention set: {file_path}\n\n🎯 **Commitment**: {description}"
    
    if success_patterns:
        response += f"\n\n📈 **Relevant Success Patterns** ({len(success_patterns)} found):"
        for pattern in success_patterns[:3]:  # Show top 3
            response += f"\n- **{pattern['name']}** ({pattern['domain']}): {pattern['description']}"
            if pattern['sequencing']:
                response += f"\n  Sequence: {' → '.join(str(s) for s in pattern['sequencing'][:3])}{'...' if len(pattern['sequencing']) > 3 else ''}"
    else:
        response += "\n\n📝 **Note**: No previous success patterns found. This will be your first recorded success!"
    
    response += "\n\n💡 Apply these proven patterns to achieve excellence!"
    return response

@app.tool()
def i_need_to_do_a_good_job(description: str, domain: str = None) -> str:
    """Set intention for doing good work and reference past success patterns."""
    try:
        success_patterns = _get_success_patterns(domain)
        intention_data = _create_intention_data(description, domain, success_patterns)
        
        toot_name = f"intention_{domain or 'general'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = _create_toot_file_path(toot_name)
        prepared_data = _prepare_toot_data(intention_data)
        _write_toot_file(file_path, prepared_data)
        
        return _build_intention_response(file_path, description, success_patterns)
        
    except Exception as e:
        logger.error(f"Failed to set intention '{description}': {traceback.format_exc()}")
        return f"❌ Failed to set intention: {str(e)}"

if __name__ == "__main__":
    app.run()