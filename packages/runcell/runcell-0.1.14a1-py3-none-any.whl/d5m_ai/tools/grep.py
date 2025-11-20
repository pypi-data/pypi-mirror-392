"""
Standalone Grep Tool

A robust grep implementation that searches for patterns in files.
Prefers ripgrep (rg) for better performance, falls back to standard grep if unavailable.
Supports regex patterns, context lines, file filtering, and various output modes.
"""

import os
import subprocess
import logging
import json
import shutil
from typing import Dict, Any, List, Optional, Tuple

# Content limits to prevent API overload
MAX_TOTAL_CONTENT_SIZE = 100 * 1024  # 100KB total content size
MAX_MATCH_CONTENT_LENGTH = 500  # Max characters per match line
TRUNCATION_MESSAGE = "... [content truncated]"


def _check_tool_available(tool: str) -> bool:
    """Check if a command-line tool is available."""
    return shutil.which(tool) is not None


def _build_ripgrep_command(args: Dict[str, Any], pattern: str, path: str) -> List[str]:
    """Build ripgrep command from arguments."""
    cmd = ['rg', '--json']
    
    # Add case insensitive flag
    if args.get('i') or args.get('-i'):
        cmd.append('-i')
    
    # Add context lines
    if args.get('A') or args.get('-A'):
        cmd.extend(['-A', str(args.get('A') or args.get('-A'))])
    if args.get('B') or args.get('-B'):
        cmd.extend(['-B', str(args.get('B') or args.get('-B'))])
    if args.get('C') or args.get('-C'):
        cmd.extend(['-C', str(args.get('C') or args.get('-C'))])
    
    # Add output mode
    output_mode = args.get('output_mode', 'content')
    if output_mode == 'files_with_matches':
        cmd.append('--files-with-matches')
    elif output_mode == 'count':
        cmd.append('--count')
    
    # Add file filtering
    if args.get('glob'):
        cmd.extend(['--glob', args.get('glob')])
    if args.get('type'):
        cmd.extend(['--type', args.get('type')])
    
    # Add multiline support
    if args.get('multiline'):
        cmd.extend(['-U', '--multiline-dotall'])
    
    # Add head limit
    head_limit = args.get('head_limit')
    if head_limit:
        cmd.extend(['--max-count', str(head_limit)])
    
    # Add pattern and path
    cmd.extend(['--regexp', pattern, path])
    
    return cmd


def _build_grep_command(args: Dict[str, Any], pattern: str, path: str) -> List[str]:
    """Build standard grep command from arguments."""
    cmd = ['grep', '-n', '-r']  # -n for line numbers, -r for recursive
    
    # Add case insensitive flag
    if args.get('i') or args.get('-i'):
        cmd.append('-i')
    
    # Add context lines
    if args.get('A') or args.get('-A'):
        cmd.extend(['-A', str(args.get('A') or args.get('-A'))])
    if args.get('B') or args.get('-B'):
        cmd.extend(['-B', str(args.get('B') or args.get('-B'))])
    if args.get('C') or args.get('-C'):
        cmd.extend(['-C', str(args.get('C') or args.get('-C'))])
    
    # Add output mode
    output_mode = args.get('output_mode', 'content')
    if output_mode == 'files_with_matches':
        cmd.append('-l')  # Files with matches
    elif output_mode == 'count':
        cmd.append('-c')  # Count mode
    
    # Add file filtering (grep doesn't have direct glob/type support, handled in post-processing)
    glob_pattern = args.get('glob')
    if glob_pattern:
        cmd.extend(['--include', glob_pattern])
    
    # Add pattern and path
    cmd.extend(['-E', pattern, path])
    
    return cmd


def _parse_ripgrep_output(stdout: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Parse ripgrep JSON output."""
    matches = []
    files_with_matches = []
    
    for line in stdout.strip().split('\n'):
        if not line:
            continue
        try:
            data = json.loads(line)
            msg_type = data.get('type')
            
            if msg_type == 'match':
                match_data = data.get('data', {})
                file_path = match_data.get('path', {}).get('text', '')
                line_number = match_data.get('line_number', 0)
                lines_text = match_data.get('lines', {}).get('text', '')
                
                matches.append({
                    'file': file_path,
                    'line_number': line_number,
                    'content': lines_text.rstrip('\n')
                })
                
                if file_path and file_path not in files_with_matches:
                    files_with_matches.append(file_path)
        except json.JSONDecodeError:
            continue
    
    return matches, files_with_matches


def _parse_grep_output(stdout: str, output_mode: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Parse standard grep output."""
    matches = []
    files_with_matches = []
    
    if output_mode == 'files_with_matches':
        # Each line is a filename
        for line in stdout.strip().split('\n'):
            if line:
                files_with_matches.append(line)
        return matches, files_with_matches
    
    # Parse content mode output (file:line:content)
    for line in stdout.strip().split('\n'):
        if not line:
            continue
        
        # Parse format: filename:line_number:content
        parts = line.split(':', 2)
        if len(parts) >= 3:
            file_path = parts[0]
            try:
                line_number = int(parts[1])
                content = parts[2]
                
                matches.append({
                    'file': file_path,
                    'line_number': line_number,
                    'content': content
                })
                
                if file_path not in files_with_matches:
                    files_with_matches.append(file_path)
            except ValueError:
                # Skip lines that don't match expected format
                continue
    
    return matches, files_with_matches


def _apply_content_limits(matches: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], bool, bool]:
    """
    Apply content limits to match results.
    
    Returns:
        Tuple of (limited_matches, was_content_truncated, was_list_truncated)
    """
    limited_matches = []
    total_size = 0
    was_content_truncated = False
    was_list_truncated = False
    
    for match in matches:
        content = match.get('content', '')
        
        # Truncate individual match content if too long
        if len(content) > MAX_MATCH_CONTENT_LENGTH:
            content = content[:MAX_MATCH_CONTENT_LENGTH] + TRUNCATION_MESSAGE
            was_content_truncated = True
        
        # Estimate size of this match entry (JSON overhead included)
        match_size = len(json.dumps({
            'file': match.get('file', ''),
            'line_number': match.get('line_number', 0),
            'content': content
        }))
        
        # Check if adding this match would exceed total size limit
        if total_size + match_size > MAX_TOTAL_CONTENT_SIZE:
            was_list_truncated = True
            break
        
        limited_matches.append({
            **match,
            'content': content
        })
        total_size += match_size
    
    return limited_matches, was_content_truncated, was_list_truncated


async def execute_grep_tool(args: Dict[str, Any]) -> str:
    """
    Execute the grep tool to search for patterns in files.
    Prefers ripgrep (rg) for performance, falls back to standard grep.
    
    Args:
        args: Dictionary containing:
            - pattern: The regex pattern to search for (required)
            - path: Directory or file path to search in (optional, defaults to current directory)
            - i: Case insensitive search (optional)
            - A: Number of lines to show after match (optional)
            - B: Number of lines to show before match (optional)
            - C: Number of lines to show before and after match (optional)
            - output_mode: "content", "files_with_matches", or "count" (optional, default: "content")
            - glob: Glob pattern to filter files (optional)
            - type: File type filter (optional)
            - head_limit: Limit output to first N results (optional)
            - multiline: Boolean for multiline mode (optional, ripgrep only)
    
    Returns:
        JSON string with search results or error message
    """
    pattern = args.get('pattern')
    if not pattern:
        return json.dumps({
            "result_type": "error",
            "summary": "Error: 'pattern' is required for grep tool"
        })

    path = args.get('path', '.')
    output_mode = args.get('output_mode', 'content')
    
    # Determine which tool to use
    use_ripgrep = _check_tool_available('rg')
    use_grep = _check_tool_available('grep')
    
    if not use_ripgrep and not use_grep:
        return json.dumps({
            "result_type": "error",
            "summary": "Error: Neither ripgrep (rg) nor grep is available on this system"
        })
    
    # Build command based on available tool
    if use_ripgrep:
        cmd = _build_ripgrep_command(args, pattern, path)
        tool_name = "ripgrep"
        logging.info(f"[GREP] Using ripgrep for search")
    else:
        cmd = _build_grep_command(args, pattern, path)
        tool_name = "grep"
        logging.info(f"[GREP] Using standard grep for search (ripgrep not available)")

    try:
        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Parse output based on tool used
        if use_ripgrep:
            matches, files_with_matches = _parse_ripgrep_output(result.stdout)
        else:
            matches, files_with_matches = _parse_grep_output(result.stdout, output_mode)
        
        # Apply head_limit if specified and not already handled by the tool
        head_limit = args.get('head_limit')
        if head_limit and not use_ripgrep:
            matches = matches[:head_limit]
        
        # Handle different output modes
        if output_mode == 'files_with_matches':
            # Apply size limits to file list
            if len(json.dumps(files_with_matches)) > MAX_TOTAL_CONTENT_SIZE:
                # Truncate file list
                truncated_files = []
                total_size = 0
                for file in files_with_matches:
                    file_size = len(file) + 10  # Include JSON overhead
                    if total_size + file_size > MAX_TOTAL_CONTENT_SIZE:
                        break
                    truncated_files.append(file)
                    total_size += file_size
                
                return json.dumps({
                    "result_type": "files",
                    "summary": f"Found {len(files_with_matches)} files with matches (showing {len(truncated_files)}, output truncated due to size limit)",
                    "files": truncated_files,
                    "truncated": True
                })
            
            return json.dumps({
                "result_type": "files",
                "summary": f"Found {len(files_with_matches)} files with matches",
                "files": files_with_matches
            })
        elif output_mode == 'count':
            # Count matches per file
            count_by_file = {}
            for match in matches:
                file = match['file']
                count_by_file[file] = count_by_file.get(file, 0) + 1
            
            return json.dumps({
                "result_type": "count",
                "summary": f"Found matches in {len(count_by_file)} files",
                "counts": count_by_file
            })
        else:
            # Default content mode - apply content limits
            original_count = len(matches)
            limited_matches, was_content_truncated, was_list_truncated = _apply_content_limits(matches)
            
            # Build summary message
            summary = f"Found {original_count} matching lines"
            if was_list_truncated:
                summary += f" (showing {len(limited_matches)} due to size limit)"
            elif was_content_truncated:
                summary += " (some content truncated)"
            
            result_data = {
                "result_type": "workspace_result",
                "summary": summary,
                "matches": limited_matches
            }
            
            if was_list_truncated or was_content_truncated:
                result_data["truncated"] = True
            
            return json.dumps(result_data)
            
    except subprocess.TimeoutExpired:
        logging.error(f"[GREP] Search timed out for pattern: {pattern}")
        return json.dumps({
            "result_type": "error",
            "summary": "Error: Search timed out (30 seconds)"
        })
    except Exception as e:
        logging.error(f"[GREP] Error executing {tool_name}: {e}")
        return json.dumps({
            "result_type": "error",
            "summary": f"Error executing {tool_name}: {str(e)}"
        })

