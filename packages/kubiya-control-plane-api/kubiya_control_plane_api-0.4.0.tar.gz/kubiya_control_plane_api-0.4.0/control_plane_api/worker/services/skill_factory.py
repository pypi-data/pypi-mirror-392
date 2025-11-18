"""
Skill Factory - Dynamic skill loading with zero hardcoding

This factory discovers and instantiates skills dynamically from multiple sources
without any hardcoded if/elif chains. Works across all runtimes (agno, claude_code, etc.).
"""
from typing import Optional, Any, List
from pathlib import Path
import structlog
import os

from control_plane_api.worker.skills import (
    SkillRegistry,
    skill_registry,
    FilesystemSkillLoader,
    LoadedSkill,
)

logger = structlog.get_logger()


class SkillFactory:
    """
    Dynamic skill factory with zero hardcoding.

    Discovers and instantiates skills from multiple sources automatically.
    No hardcoded if/elif chains required.
    """

    def __init__(self, runtime_type: str = "agno"):
        """
        Initialize the skill factory.

        Args:
            runtime_type: Runtime type (e.g., "agno", "claude_code")
        """
        self.runtime_type = runtime_type
        self.registry: SkillRegistry = skill_registry
        self.loaders = []
        self._initialized = False

        logger.info(
            "skill_factory_initialized",
            runtime_type=runtime_type,
        )

    def initialize(self):
        """
        Initialize the factory by discovering skills from all sources.

        Call this once during worker startup.
        """
        if self._initialized:
            logger.debug("skill_factory_already_initialized")
            return

        logger.info("skill_factory_initializing")

        # Setup loaders
        self._setup_loaders()

        # Discover skills
        self._discover_skills()

        self._initialized = True

        # Log statistics
        stats = self.registry.get_stats()
        logger.info(
            "skill_factory_initialized",
            total_skills=stats["total_skills"],
            by_source=stats["skills_by_source"],
            by_type=stats["skills_by_type"],
        )

    def _setup_loaders(self):
        """Setup skill loaders from different sources."""
        # 1. Filesystem loader (user skills)
        search_paths = []

        # Project skills (.kubiya/skills in current working directory)
        project_skills = Path.cwd() / ".kubiya/skills"
        if project_skills.exists():
            search_paths.append(project_skills)

        # User global skills (~/.kubiya/skills)
        user_skills = Path.home() / ".kubiya/skills"
        if user_skills.exists():
            search_paths.append(user_skills)

        # Built-in skills (in package directory)
        builtin_skills = Path(__file__).parent.parent / "skills" / "builtin"
        if builtin_skills.exists():
            search_paths.append(builtin_skills)

        if search_paths:
            fs_loader = FilesystemSkillLoader(search_paths)
            self.loaders.append(fs_loader)
            logger.info("filesystem_loader_configured", paths=[str(p) for p in search_paths])

        # TODO: Add API loader for Control Plane skills
        # TODO: Add package loader for pip-installed skills
        # TODO: Add git loader for remote skills

    def _discover_skills(self):
        """Discover skills from all loaders."""
        for loader in self.loaders:
            try:
                skills = loader.discover()

                for skill in skills:
                    # Check dependencies
                    missing = self.registry.resolve_dependencies(skill)
                    if missing:
                        logger.warning(
                            "skill_missing_dependencies",
                            skill=skill.name,
                            missing=missing,
                        )
                        # Register anyway - could still be usable

                    # Register
                    self.registry.register(skill)

            except Exception as e:
                logger.error(
                    "skill_discovery_failed",
                    loader=loader.__class__.__name__,
                    error=str(e),
                    exc_info=True,
                )

    def create_skill(self, skill_data: dict) -> Optional[Any]:
        """
        Create a skill toolkit from configuration.

        No hardcoded mappings - uses registry for discovery.

        Args:
            skill_data: Skill config from Control Plane:
                - name: Skill name (e.g., "slack-notifier")
                - type: Skill type (e.g., "shell", "file_system", "custom")
                - configuration: Dict with skill-specific config
                - enabled: Whether skill is enabled
                - execution_id: Optional execution ID for streaming

        Returns:
            Instantiated skill toolkit or None
        """
        # Ensure factory is initialized
        if not self._initialized:
            self.initialize()

        if not skill_data.get("enabled", True):
            logger.info("skill_disabled", name=skill_data.get("name"))
            return None

        skill_name = skill_data.get("name")
        skill_type = skill_data.get("type", "custom")
        config = skill_data.get("configuration", {})
        execution_id = skill_data.get("execution_id")

        # Try to find skill by name first
        loaded_skill = self.registry.get(skill_name)

        # If not found by name, try by type (for built-in skills)
        if not loaded_skill:
            loaded_skill = self.registry.get_by_type(skill_type)

        if not loaded_skill:
            logger.warning(
                "skill_not_found_in_registry",
                name=skill_name,
                type=skill_type,
                available_skills=[s.name for s in self.registry.list_skills()],
            )
            return None

        # Get runtime-appropriate implementation
        impl = self.registry.get_implementation_for_runtime(
            loaded_skill, self.runtime_type
        )

        if not impl:
            logger.error(
                "no_implementation_for_runtime",
                skill=loaded_skill.name,
                runtime=self.runtime_type,
                available_runtimes=list(loaded_skill.implementations.keys()),
            )
            return None

        # Check if this is a builtin implementation (like Claude Code SDK tools)
        if isinstance(impl, dict) and impl.get("builtin"):
            builtin_tools = impl.get("tools", [])

            # Issue #2 Fix: Validate builtin tools before returning
            if self.runtime_type == "claude_code" and builtin_tools:
                from control_plane_api.worker.runtimes.claude_code.tool_mapper import validate_builtin_tools
                try:
                    valid_tools, invalid_tools = validate_builtin_tools(builtin_tools)
                    if invalid_tools:
                        logger.error(
                            "invalid_builtin_tools_in_skill",
                            skill=loaded_skill.name,
                            invalid_tools=invalid_tools,
                            valid_tools=valid_tools,
                        )
                        # Don't return skill if it has invalid tools
                        return None
                    builtin_tools = valid_tools
                except ValueError as e:
                    logger.error(
                        "builtin_tool_validation_failed",
                        skill=loaded_skill.name,
                        error=str(e),
                    )
                    return None

            logger.info(
                "skill_builtin",
                skill=loaded_skill.name,
                runtime=self.runtime_type,
                tools=builtin_tools,
            )
            # For builtin skills, return metadata - runtime handles tool mapping
            return {
                "skill_name": loaded_skill.name,
                "skill_type": loaded_skill.skill_type,
                "builtin": True,
                "tools": builtin_tools,
                "config": config,
            }

        # Prepare configuration for Python class instantiation
        instantiation_config = config.copy()

        # Inject execution_id if provided
        if execution_id:
            instantiation_config['execution_id'] = execution_id

        # Inject other runtime-specific config
        # (e.g., API keys from environment variables)
        self._inject_env_vars(instantiation_config, loaded_skill)

        # Instantiate with configuration
        try:
            instance = impl(**instantiation_config)

            logger.info(
                "skill_instantiated",
                skill=loaded_skill.name,
                runtime=self.runtime_type,
                implementation=impl.__name__,
            )

            return instance

        except Exception as e:
            logger.error(
                "skill_instantiation_failed",
                skill=loaded_skill.name,
                error=str(e),
                exc_info=True,
            )
            return None

    def create_skills_from_list(
        self, skill_configs: List[dict], execution_id: Optional[str] = None
    ) -> List[Any]:
        """
        Create multiple skills from configurations.

        Args:
            skill_configs: List of skill config dicts
            execution_id: Optional execution ID to inject into all skills

        Returns:
            List of instantiated skills (non-None)
        """
        skills = []

        for config in skill_configs:
            # Inject execution_id if provided
            if execution_id:
                config = config.copy()
                config['execution_id'] = execution_id

            skill = self.create_skill(config)
            if skill:
                skills.append(skill)

        logger.info(
            "skills_batch_created",
            requested=len(skill_configs),
            created=len(skills),
        )

        return skills

    def _inject_env_vars(self, config: dict, skill: LoadedSkill):
        """
        Inject environment variables into skill configuration.

        Looks for environment variables defined in skill manifest.
        """
        env_vars = skill.manifest.get("spec", {}).get("environmentVariables", [])

        for env_var_def in env_vars:
            var_name = env_var_def.get("name")
            required = env_var_def.get("required", False)

            # Check if already in config
            if var_name.lower() in config or var_name in config:
                continue

            # Try to get from environment
            env_value = os.environ.get(var_name)

            if env_value:
                # Convert env var name to config key (lowercase)
                config_key = var_name.lower()
                config[config_key] = env_value
                logger.debug(
                    "injected_env_var",
                    skill=skill.name,
                    var_name=var_name,
                )
            elif required:
                logger.warning(
                    "required_env_var_missing",
                    skill=skill.name,
                    var_name=var_name,
                )

    def get_available_skills(self) -> List[str]:
        """Get list of all available skill names."""
        if not self._initialized:
            self.initialize()

        return [skill.name for skill in self.registry.list_skills()]

    def get_skill_info(self, skill_name: str) -> Optional[dict]:
        """Get information about a specific skill."""
        if not self._initialized:
            self.initialize()

        skill = self.registry.get(skill_name)
        if not skill:
            return None

        return {
            "name": skill.name,
            "version": skill.version,
            "type": skill.skill_type,
            "source": skill.source.value,
            "runtimes": list(skill.implementations.keys()),
            "metadata": skill.manifest.get("metadata", {}),
        }

# Backward compatibility alias
# Old code using SkillFactoryV2 will still work
SkillFactoryV2 = SkillFactory
