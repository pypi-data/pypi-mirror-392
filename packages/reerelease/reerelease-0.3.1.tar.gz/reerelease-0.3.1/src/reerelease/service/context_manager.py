"""Management of Context objects: creation, discovery, synchronization, deletion.
Here is all file access logic for Contexts."""

import logging
import pathlib
import re
import shutil
from datetime import datetime
from typing import cast

from ..config import DEFAULTS, get_config
from ..core.context import Context
from ..errors import (
    AppError,
    ContextAlreadyExists,
    ContextCreationError,
    ContextDeletionError,
    ContextDiscoveryError,
    ContextUpdateError,
    InvalidContextName,
    InvalidTargetPath,
    NoContextFound,
)
from ..service.dsl.pipeline import DSLPipeline
from ..service.milestone_manager import MilestoneManager
from ..service.template_manager import TemplateManager
from ..validators.validate_context import (
    path_contains_context,
    validate_context,
    validate_context_name,
    validate_context_path,
)


class ContextManager:
    """Manager for Context objects: creation, discovery, synchronization, deletion.
    Here is all file access logic for Contexts."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("reerelease")
        self.cfg = get_config()
        self.required_files = []
        self.tm: TemplateManager = TemplateManager()

        # Load required files for a context from templates
        template_files = self.tm.get_templates("context")
        self.required_files = [output_name for _, output_name in template_files]
        if not self.required_files:
            # We can't proceed without required files
            raise FileNotFoundError("No templates found for category: 'context'")

        # Root context needs to exist
        self.rootctx: Context | None = None

    def discover(
        self,
        search_path: pathlib.Path = DEFAULTS.search_path,
        max_depth: int = DEFAULTS.search_depth,
    ) -> Context:
        """Discover contexts in the specified path and its subdirectories and update the root context
        Args:
            search_path: Root directory to search from
            max_depth: Maximum depth to search (0 = search_path only, no subdirs)
        Returns:
            The root Context object of the discovered tree
        Raises:
            NoContextFound: If no contexts are found
            ContextDiscoveryError: If discovery fails or root context cannot be determined
        """
        self.logger.debug(
            f"cm.discover called : search_path: {search_path}, max_depth: {max_depth}"
        )

        contexts = self.find(search_path=search_path.resolve(), max_depth=max_depth)

        # No contexts found
        if not contexts:
            raise NoContextFound("No context found", search_path=str(search_path))

        # 1. Build context tree: set parent pointers based on filesystem ancestry.
        # Normalize contexts to resolved paths and sort by path depth (shallow -> deep)
        resolved_pairs = [(pathlib.Path(ctx.filepath).resolve(), ctx) for ctx in contexts]
        resolved_pairs.sort(key=lambda pc: len(pc[0].parts))

        # processed holds earlier (shallower) contexts for ancestor lookup
        processed: list[tuple[pathlib.Path, Context]] = []
        for path, ctx in resolved_pairs:
            # Find nearest ancestor among processed (deepest processed path that is a prefix)
            nearest_parent = None
            for apath, actx in reversed(processed):
                try:
                    path.relative_to(apath)
                    nearest_parent = actx
                    break
                except Exception:
                    continue

            # Attach parent (anytree will set children automatically)
            ctx.parent = nearest_parent

            processed.append((path, ctx))

        # The root context is the first processed item with no parent (if any)
        self.rootctx = next((ctx for _path, ctx in processed if ctx.parent is None), None)

        # 2. Validate the entire context tree
        if self.rootctx is None:
            raise ContextDiscoveryError("Failed to determine root context")

        self.logger.debug(f"Discovered {len(contexts)} contexts, root: {self.rootctx}")

        self.validate_tree(self.rootctx)

        # 3. Load milestones for all contexts
        mm = MilestoneManager()
        all_contexts = [self.rootctx, *self.rootctx.descendants]
        for node in all_contexts:
            try:
                node.milestones = mm.read(node)
            except Exception as e:
                # If milestone reading fails, just log and continue with empty list
                self.logger.debug(f"Could not load milestones for {node.name}: {e}")
                node.milestones = []

        return self.rootctx

    def validate_tree(self, rootctx: Context) -> bool:
        """Validate the entire context tree starting from rootctx
        Args:
            rootctx: The root Context of the tree to validate
        Returns:
            True if all contexts in the tree are healthy, False otherwise"""
        self.logger.debug(f"cm.validate_tree called : root context: {rootctx}")

        all_healthy = True

        def validate_recursive(ctx: Context) -> None:
            nonlocal all_healthy
            issues = validate_context(ctx)
            if ctx.healthy is False or issues:
                all_healthy = False
                self.logger.warning(f"Context '{ctx.name}' has {len(issues)} issues")
            else:
                self.logger.debug(f"Context '{ctx.name}' is healthy")

            for child in ctx.children:
                validate_recursive(child)

        validate_recursive(rootctx)
        return all_healthy

    def find(
        self,
        search_path: pathlib.Path = DEFAULTS.search_path,
        max_depth: int = DEFAULTS.search_depth,
        name: str = "",
        nb: int = 0,
    ) -> list[Context]:
        """Find all contexts in a directory tree and return a list of Context objects.
        Each Context will have `name` and `path` populated. Other Context fields
        (healthy, children, milestones) are left to be computed by callers.

        Args:
            search_path: Root directory to search from
            max_depth: Maximum depth to search (0 = search_path only, no subdirs)
            name: Name pattern to match (supports wildcards)
            nb: Maximum number of contexts to find (0 = unlimited)
        Returns:
            List of discovered Context objects
        ---------------------------------------------------------------------------
        Note: This method uses a breadth-first search (BFS) to explore directories
        up to the specified max_depth. It avoids following symlinks that point
        outside the initial search_path tree to prevent infinite loops and
        unintended directory traversal.
        """

        self.logger.debug(
            f"cm.find called : search_path: {search_path}, max_depth: {max_depth}, name: '{name}', nb: {nb}"
        )

        detected_contexts: list[Context] = []
        base_resolved = search_path.resolve()

        # Queue stores tuples of (path, depth)
        queue = [(search_path, 0)]

        def match_name(pattern: str, candidate: str) -> bool:
            if pattern in ("", "*"):
                return True
            if "*" in pattern:
                regex = re.escape(pattern).replace(r"\*", ".*")
                return re.fullmatch(regex, candidate) is not None
            return bool(candidate.startswith(pattern))

        while queue:
            current_path, current_depth = queue.pop(0)

            if not current_path.is_dir():
                continue

            # Skip symlinks that point outside the search tree
            try:
                resolved = current_path.resolve()
                resolved.relative_to(base_resolved)
            except (ValueError, OSError):
                # Path is outside base_resolved or cannot be resolved
                self.logger.debug(f"Skipping external path: {current_path}")
                continue

            self.logger.debug(f"Searching for contexts in: {current_path} (depth: {current_depth})")

            # Check if this directory contains a context
            if path_contains_context(current_path):
                context_name = self.extract_context_name(current_path)
                if match_name(name, context_name):
                    ctx = Context(name=context_name, filepath=current_path.resolve())
                    detected_contexts.append(ctx)
                    self.logger.debug(f"Found context: {ctx.name} at {ctx.filepath}")

                    # Stop if we've found enough contexts
                    if nb > 0 and len(detected_contexts) >= nb:
                        break

            # Only explore subdirectories if we haven't reached max depth
            if max_depth is None or current_depth < max_depth:
                try:
                    subdirs = sorted([d for d in current_path.iterdir() if d.is_dir()])
                    # Add subdirectories with incremented depth
                    queue.extend((subdir, current_depth + 1) for subdir in subdirs)
                except (PermissionError, OSError):
                    # Skip directories we can't read
                    continue

        self.logger.info(f"Found all {len(detected_contexts)} contexts")
        return detected_contexts

    def create(
        self, path: pathlib.Path, name: str, inplace: bool = False, force: bool = False
    ) -> Context:
        """Create a new context at the specified path
        Args:
            path (pathlib.Path): The path where the context should be created.
            name (str): The name of the context.
            inplace (bool): Whether to create the context in place or in a subdirectory.
            force (bool): Whether to force creation even if the context already exists.
        Returns:
            The created Context object.
        Raises:
            InvalidContextName: If the context name is invalid.
            InvalidTargetPath: If the target path is invalid.
            ContextAlreadyExists: If a context already exists at the target path and force is False.
            ContextCreationError: If there are issues creating the context files or if the created context is invalid.
        """
        self.logger.debug(
            f"cm.create called: name: '{name}', filepath: '{path}', inplace: {inplace}, force:{force}"
        )

        # -- 1. Validate inputs -- #
        # Validate context name
        issues = validate_context_name(name)
        if issues:
            self.logger.warning(f"issues with name '{name}': {issues}")
            raise InvalidContextName("Invalid context name", issues=issues)

        # Create context path
        base_path = pathlib.Path(path)
        # When --inplace is given create files directly in the provided path,
        # otherwise create a subdirectory named after the context.
        target_path = base_path if inplace else (base_path / name)
        target_path = target_path.resolve()

        # We validate base path as both inplace or not create contexts in it
        issues = validate_context_path(base_path, mode="creation")
        if issues:
            self.logger.warning(f"issues with path '{base_path}': {issues}")
            raise InvalidTargetPath("Invalid target path", issues=issues)

        if not force:
            # Check that target_path doesn't already contains a context
            if path_contains_context(target_path):
                self.logger.warning(f"target path '{target_path}' already contains a context")
                raise ContextAlreadyExists(
                    "Overwriting not allowed",
                    issues=[f"Target path '{target_path}' already contains a context"],
                )

        self.logger.debug(f"target path '{target_path}' is clear for context '{name}' creation")

        # -- 2. create with templates -- #
        # Prepare template context
        template_context = {
            "context_name": name,
            "context_path": str(target_path),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
        }

        # Create files from templates
        try:
            self.logger.debug(f"template_context: {template_context}")
            self.tm.create_files_from_templates(
                category="context", template_context=template_context, target_path=target_path
            )
        except Exception as e:
            self.logger.error(f"Error creating context files: {e}")
            # Use typing.cast to satisfy the static type checker. At runtime this
            # is a no-op and preserves the original exception in the causes list
            # for nicer printing via AppError.__str__.
            ce = ContextCreationError(
                "Error creating context files", causes=cast(list[AppError], [e])
            )
            raise ce from e  # Raise with causes attached

        # -- 3. validate context -- #
        context = Context(name=name, filepath=target_path)
        issues = validate_context(context)
        if issues:
            self.logger.debug(f"issues with created context '{name}': {issues}")
            # Use a stable, test-expected message while still attaching detailed issues
            raise ContextCreationError("context is not valid", issues=issues)

        self.logger.info(f"created context: {context.name} at {context.filepath}")
        return context

    def delete(self, context: Context, delete_dir: bool = False, force: bool = False) -> None:
        """Delete a context and optionally its directory. This service only permits
        deletion of leaf contexts (no children). For non-leaf deletion the caller
        (CLI) should perform reparenting/moving of folders and then call delete.

        Args:
            context: Context node to delete
            delete_dir: If True, remove the context directory from filesystem
            force: If True, continue deletion even if some files/directories cannot be removed, raise at the end
        Raises:
            ContextDeletionError on invalid operations
        """

        self.logger.debug(
            f"cm.delete called: context: '{context}', delete_dir: {delete_dir}, force: {force}"
        )

        if not isinstance(context, Context):
            raise ContextDeletionError("Invalid context")
        # Only allow deleting leaves from the service layer to keep it simple and safe.
        if context.children:
            # Non-leaf deletion is not supported at the moment
            raise ContextDeletionError(
                f"Cannot delete non-leaf context '{context.name}'",
                issues=[f"{len(context.children)} children present"],
            )

        path = pathlib.Path(context.filepath)

        issues = []

        # Remove entire context directory from disk
        if delete_dir:
            try:
                if path.exists():
                    shutil.rmtree(path)
                    self.logger.info(f"Removed directory {path}")
                else:
                    self.logger.debug(f"Directory {path} does not exist, nothing to remove")
            except Exception as e:
                issue = f"Failed to remove directory {path}"
                issues.append(issue)  # record issue for reporting if force
                context.issues.append(issue)  # record in context itself
                self.logger.error(issue + f": {e}")  # log error if not force
                raise ContextDeletionError(issue, issues=[str(e)]) from e
        # Removing only the context files
        else:
            for fname in getattr(self, "required_files", []):
                file_path = path / fname
                if not file_path.exists():
                    # Nothing to remove
                    self.logger.debug(f"File {file_path} does not exist, nothing to remove")
                    continue
                try:
                    file_path.unlink()
                    self.logger.info(f"Removed file {file_path}")
                except Exception as e:
                    issue = f"Failed to remove file {file_path}"
                    issues.append(issue)  # record issue for reporting if force
                    context.issues.append(issue)  # record in context itself
                    if force:
                        self.logger.warning(issue + f": {e}")
                        continue  # continue to next file
                    else:
                        self.logger.error(issue + f": {e}")
                        raise ContextDeletionError(issue + f": {e}", issues=[str(e)]) from e

            if issues and force:
                raise ContextDeletionError(
                    f"Failed to remove files/folder for: {context.name}", issues=issues
                )

        # Detach node from tree if we didn't raise
        context.parent = None

        # Confirm deletion in logs: use `filepath` (Context has no `path` attr)
        self.logger.info(f"Deleted context: {context.name} at {context.filepath}")

    def update(
        self, context: Context, new_name: str, rename_folder: bool = True, force: bool = False
    ) -> Context:
        """Rename a context by updating all context files and optionally renaming the folder.

        Args:
            context: The Context object to rename
            new_name: The new name for the context
            rename_folder: If True, rename the folder if it matches/contains the old name
            force: If True, skip validation checks

        Returns:
            The updated Context object with the new name

        Raises:
            InvalidContextName: If the new name is invalid
            ContextUpdateError: If there are issues updating the context
        """
        self.logger.debug(
            f"cm.update called: context: '{context.name}' -> '{new_name}', "
            f"rename_folder: {rename_folder}, force: {force}"
        )

        old_name = context.name

        # Validate new name
        # TODO: why not validate when force
        if not force:
            issues = validate_context_name(new_name)
            if issues:
                self.logger.warning(f"Invalid new context name '{new_name}': {issues}")
                raise InvalidContextName("Invalid new context name", issues=issues)

        # Update all context files
        context_path = pathlib.Path(context.filepath)
        errors = []

        # Get template directory for DSL pipeline
        template_dir = self.tm.get_templates_dir()

        for filename in self.required_files:
            file_path = context_path / filename
            # TODO: maybe we should create missing files when force
            if not file_path.exists():
                issue = f"Required file not found: {file_path}"
                self.logger.warning(issue)
                errors.append(issue)
                if not force:
                    raise ContextUpdateError(issue, issues=[issue])
                continue

            try:
                # Get the template path for this file (e.g., context/readme.md.j2)
                template_name = f"context/{filename}.j2"
                template_path = self.tm.get_template_path(template_name)

                # Create pipeline for this context file
                pipeline = DSLPipeline.from_template(
                    template_path=template_path, template_dir=template_dir
                )

                # First parse the old content to get the old context_name value
                # (which may include suffixes like " roadmap" or " release notes")
                old_content = file_path.read_text(encoding="utf-8")
                old_memory = pipeline.parse(old_content)

                # Extract old context_name from parsed memory
                old_context_name_field = old_memory.fields.get("context_name")
                if old_context_name_field:
                    old_context_name = old_context_name_field.value
                    # Replace only the old_name part with new_name, preserving any suffix
                    # This handles patterns like "old_name roadmap" -> "new_name roadmap"
                    new_context_name = old_context_name.replace(old_name, new_name, 1)
                else:
                    # If field not found, use new_name directly
                    new_context_name = new_name

                # Update only the context_name field using DSL surgical edits
                # The DSL pipeline will preserve the original markdown format
                updated_content = pipeline.update_memory_file(
                    file_path, {"context_name": new_context_name}
                )

                # Additionally, replace any remaining occurrences of old_name in body text
                # This handles template-rendered content like "Welcome to the old_name project!"
                updated_content = updated_content.replace(old_name, new_name)

                # Write back the updated content
                file_path.write_text(updated_content, encoding="utf-8")
                self.logger.info(f"Updated context name in {file_path}")

            except Exception as e:
                issue = f"Failed to update file {file_path}: {e}"
                self.logger.error(issue)
                errors.append(issue)
                if not force:
                    raise ContextUpdateError(issue, issues=[str(e)]) from e

        # Rename folder if requested and applicable
        new_path = context_path
        if rename_folder and context_path.name == old_name:
            # Direct match: folder name equals context name
            new_path = context_path.parent / new_name
            try:
                context_path.rename(new_path)
                self.logger.info(f"Renamed folder from {context_path} to {new_path}")
            except Exception as e:
                issue = f"Failed to rename folder from {context_path} to {new_path}: {e}"
                self.logger.error(issue)
                errors.append(issue)
                if not force:
                    raise ContextUpdateError(issue, issues=[str(e)]) from e
        elif rename_folder and old_name in context_path.name:
            # Partial match: context name is part of folder name
            new_folder_name = context_path.name.replace(old_name, new_name)
            new_path = context_path.parent / new_folder_name
            try:
                context_path.rename(new_path)
                self.logger.info(
                    f"Renamed folder from {context_path} to {new_path} (partial match)"
                )
            except Exception as e:
                issue = f"Failed to rename folder from {context_path} to {new_path} (partial): {e}"
                self.logger.error(issue)
                errors.append(issue)
                if not force:
                    raise ContextUpdateError(issue, issues=[str(e)]) from e

        if errors and force:
            raise ContextUpdateError(
                f"Errors occurred while updating context '{old_name}' to '{new_name}'",
                issues=errors,
            )

        # Update the context object
        context.name = new_name
        context.filepath = new_path.resolve()

        self.logger.info(f"Successfully renamed context from '{old_name}' to '{new_name}'")
        return context

    # TODO: evolve this in a general read method, with specialized parser for different files
    def extract_context_name(self, context_path: pathlib.Path) -> str:
        """Extract context name from a context
        Currently try by reading readme, or defaulting to directory name."""

        self.logger.debug(f"cm.extract_context_name called for path: {context_path}")

        context_name = context_path.name  # Default to directory name

        # Look for a readme file to extract the context name
        for file in self.required_files:
            if "readme" in file.lower():
                readme_path = context_path / file
                try:
                    content = readme_path.read_text(encoding="utf-8")
                    # Simple extraction: look for first # heading
                    for line in content.split("\n"):
                        line = line.strip()  # Remove leading/trailing whitespace
                        if line.startswith("#") and len(line) > 1 and line[1].isspace():
                            # Extract everything after '# ' and strip whitespace
                            context_name = line[1:].strip()
                            break
                except Exception as e:
                    self.logger.debug(
                        f"Found readme file: {readme_path}. But couldn't read context name: {e}"
                    )
                break

        return context_name
