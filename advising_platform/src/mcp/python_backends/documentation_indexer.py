#!/usr/bin/env python3
"""
Documentation Indexer MCP Backend

Automatically indexes folders for MkDocs integration and creates navigation structure.
Supports:
- Automatic folder scanning
- Markdown file detection
- Navigation YAML generation
- MkDocs configuration updates
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import yaml
import re
from datetime import datetime

def create_mkdocs_nav_entry(folder_path: Path, base_path: Path) -> Dict[str, Any]:
    """Create navigation entry for a folder"""
    relative_path = folder_path.relative_to(base_path)
    folder_name = folder_path.name
    
    # Clean folder name for display
    display_name = folder_name.replace('[', '').replace(']', '').replace('-', ' ').title()
    
    nav_entry = {
        "title": display_name,
        "path": str(relative_path),
        "files": [],
        "subfolders": []
    }
    
    # Scan for markdown files
    for md_file in folder_path.glob("*.md"):
        file_entry = {
            "title": extract_title_from_md(md_file),
            "path": str(md_file.relative_to(base_path)),
            "size": md_file.stat().st_size,
            "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
        }
        nav_entry["files"].append(file_entry)
    
    # Recursively scan subfolders
    for subfolder in folder_path.iterdir():
        if subfolder.is_dir() and not subfolder.name.startswith('.'):
            subfolder_entry = create_mkdocs_nav_entry(subfolder, base_path)
            nav_entry["subfolders"].append(subfolder_entry)
    
    return nav_entry

def extract_title_from_md(md_file: Path) -> str:
    """Extract title from markdown file"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for H1 title
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()
            
        # Look for title in frontmatter
        frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            try:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                if 'title' in frontmatter:
                    return frontmatter['title']
            except:
                pass
                
        # Fall back to filename
        return md_file.stem.replace('_', ' ').replace('-', ' ').title()
        
    except Exception:
        return md_file.stem.replace('_', ' ').replace('-', ' ').title()

def create_mkdocs_config(nav_structure: Dict[str, Any], output_path: Path) -> Dict[str, Any]:
    """Create or update MkDocs configuration"""
    
    config = {
        "site_name": "Heroes-GPT Documentation",
        "site_description": "Comprehensive analysis and documentation system",
        "theme": {
            "name": "material",
            "features": [
                "navigation.tabs",
                "navigation.sections",
                "navigation.expand",
                "search.highlight",
                "search.share"
            ],
            "palette": {
                "scheme": "default",
                "primary": "indigo",
                "accent": "indigo"
            }
        },
        "markdown_extensions": [
            "admonition",
            "codehilite",
            "pymdownx.details",
            "pymdownx.superfences",
            "pymdownx.tabbed",
            "toc"
        ],
        "nav": build_nav_from_structure(nav_structure)
    }
    
    # Write config to file
    config_file = output_path / "mkdocs.yml"
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    return config

def build_nav_from_structure(nav_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build navigation structure for MkDocs"""
    nav = []
    
    # Add main sections
    if nav_structure.get("files"):
        for file_entry in nav_structure["files"]:
            nav.append({file_entry["title"]: file_entry["path"]})
    
    # Add subfolders
    for subfolder in nav_structure.get("subfolders", []):
        if subfolder["files"] or subfolder["subfolders"]:
            subfolder_nav = build_nav_from_structure(subfolder)
            if subfolder_nav:
                nav.append({subfolder["title"]: subfolder_nav})
    
    return nav

def index_folder_for_documentation(params: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to index a folder for documentation"""
    try:
        folder_path = Path(params.get("folder_path", ""))
        if not folder_path.exists():
            return {
                "success": False,
                "error": f"Folder not found: {folder_path}",
                "error_type": "path_not_found"
            }
        
        output_path = Path(params.get("output_path", folder_path.parent))
        include_subfolders = params.get("include_subfolders", True)
        
        # Create navigation structure
        nav_structure = create_mkdocs_nav_entry(folder_path, folder_path.parent)
        
        # Generate index file
        index_content = generate_index_content(nav_structure)
        index_file = folder_path / "README.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        # Create MkDocs configuration
        mkdocs_config = create_mkdocs_config(nav_structure, output_path)
        
        # Create docs structure for MkDocs
        docs_path = output_path / "docs"
        docs_path.mkdir(exist_ok=True)
        
        # Copy files to docs structure
        copy_to_docs_structure(folder_path, docs_path)
        
        return {
            "success": True,
            "nav_structure": nav_structure,
            "mkdocs_config_path": str(output_path / "mkdocs.yml"),
            "index_file_path": str(index_file),
            "docs_path": str(docs_path),
            "total_files": count_files_recursive(nav_structure),
            "folders_indexed": count_folders_recursive(nav_structure)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "processing_error"
        }

def generate_index_content(nav_structure: Dict[str, Any]) -> str:
    """Generate index content for the folder"""
    content = f"""# {nav_structure['title']} Documentation

This documentation is automatically generated and indexed for MkDocs.

## Contents

"""
    
    # Add file listings
    if nav_structure.get("files"):
        content += "### Files\n\n"
        for file_entry in nav_structure["files"]:
            content += f"- [{file_entry['title']}]({file_entry['path']})\n"
        content += "\n"
    
    # Add subfolder listings
    if nav_structure.get("subfolders"):
        content += "### Folders\n\n"
        for subfolder in nav_structure["subfolders"]:
            file_count = count_files_recursive(subfolder)
            content += f"- **{subfolder['title']}** ({file_count} files)\n"
        content += "\n"
    
    content += f"""
---

*Documentation indexed on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Total files: {count_files_recursive(nav_structure)}*
"""
    
    return content

def copy_to_docs_structure(source_path: Path, docs_path: Path):
    """Copy files to MkDocs docs structure"""
    import shutil
    
    for item in source_path.rglob("*"):
        if item.is_file() and item.suffix == ".md":
            relative_path = item.relative_to(source_path)
            target_path = docs_path / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_path)

def count_files_recursive(nav_structure: Dict[str, Any]) -> int:
    """Count total files recursively"""
    count = len(nav_structure.get("files", []))
    for subfolder in nav_structure.get("subfolders", []):
        count += count_files_recursive(subfolder)
    return count

def count_folders_recursive(nav_structure: Dict[str, Any]) -> int:
    """Count total folders recursively"""
    count = len(nav_structure.get("subfolders", []))
    for subfolder in nav_structure.get("subfolders", []):
        count += count_folders_recursive(subfolder)
    return count

def main():
    """Main entry point for MCP backend"""
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python documentation_indexer.py '<json_params>'",
            "help": {
                "description": "Index folders for MkDocs documentation",
                "parameters": {
                    "folder_path": "Path to folder to index (required)",
                    "output_path": "Path for output files (optional, defaults to parent of folder_path)",
                    "include_subfolders": "Whether to include subfolders (optional, default: true)"
                },
                "example": {
                    "folder_path": "[projects]/[heroes-gpt-bot]/clients",
                    "output_path": "docs",
                    "include_subfolders": True
                }
            }
        }))
        return
    
    try:
        params = json.loads(sys.argv[1])
        result = index_folder_for_documentation(params)
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON parameters: {e}",
            "error_type": "json_decode_error"
        }))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Unexpected error: {e}",
            "error_type": "unexpected_error"
        }))

if __name__ == "__main__":
    main()