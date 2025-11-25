#!/usr/bin/env python3
"""
Backup existing datasets before regeneration.
Creates timestamped backups of training, validation, and test datasets.
"""

import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dl_config import DATA_DIR, TRAINING_DATA_DIR, VALIDATION_DATA_DIR, TEST_DATA_DIR


def backup_datasets(backup_dir: Path = None, verbose: bool = True) -> bool:
    """
    Backup all existing datasets to a timestamped directory.
    
    Args:
        backup_dir: Custom backup directory (optional)
        verbose: Print progress messages
        
    Returns:
        True if backup successful, False otherwise
    """
    # Create backup directory with timestamp
    if backup_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = DATA_DIR / f"backup_{timestamp}"
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print(f"Backing up datasets to: {backup_dir}")
        print("=" * 60)
    
    # Directories to backup
    dirs_to_backup = [
        ("training", TRAINING_DATA_DIR),
        ("validation", VALIDATION_DATA_DIR),
        ("test", TEST_DATA_DIR)
    ]
    
    backed_up_count = 0
    total_size = 0
    
    for name, source_dir in dirs_to_backup:
        if not source_dir.exists():
            if verbose:
                print(f"⚠ {name.capitalize()} directory not found: {source_dir}")
            continue
        
        # Check if directory has any files
        files = list(source_dir.glob("*"))
        if not files:
            if verbose:
                print(f"⚠ {name.capitalize()} directory is empty: {source_dir}")
            continue
        
        # Create backup subdirectory
        backup_subdir = backup_dir / name
        backup_subdir.mkdir(parents=True, exist_ok=True)
        
        # Copy all files
        for file_path in files:
            if file_path.is_file():
                dest_path = backup_subdir / file_path.name
                shutil.copy2(file_path, dest_path)
                
                file_size = file_path.stat().st_size
                total_size += file_size
                
                if verbose:
                    size_mb = file_size / (1024 * 1024)
                    print(f"✓ Backed up: {file_path.name} ({size_mb:.1f} MB)")
        
        backed_up_count += 1
    
    if backed_up_count == 0:
        if verbose:
            print("\n✗ No datasets found to backup")
        return False
    
    if verbose:
        total_size_mb = total_size / (1024 * 1024)
        print("=" * 60)
        print(f"✓ Backup complete!")
        print(f"  Backed up {backed_up_count} dataset(s)")
        print(f"  Total size: {total_size_mb:.1f} MB")
        print(f"  Location: {backup_dir}")
    
    return True


def list_backups(verbose: bool = True) -> list:
    """
    List all existing backups.
    
    Args:
        verbose: Print backup information
        
    Returns:
        List of backup directory paths
    """
    backup_dirs = sorted(DATA_DIR.glob("backup_*"))
    
    if verbose:
        if not backup_dirs:
            print("No backups found")
        else:
            print(f"Found {len(backup_dirs)} backup(s):")
            print("=" * 60)
            
            for backup_dir in backup_dirs:
                # Calculate total size
                total_size = sum(
                    f.stat().st_size 
                    for f in backup_dir.rglob("*") 
                    if f.is_file()
                )
                size_mb = total_size / (1024 * 1024)
                
                # Get timestamp from directory name
                timestamp_str = backup_dir.name.replace("backup_", "")
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    time_str = timestamp_str
                
                print(f"  {backup_dir.name}")
                print(f"    Time: {time_str}")
                print(f"    Size: {size_mb:.1f} MB")
                print(f"    Path: {backup_dir}")
                print()
    
    return backup_dirs


def restore_backup(backup_dir: Path, verbose: bool = True) -> bool:
    """
    Restore datasets from a backup directory.
    
    Args:
        backup_dir: Path to backup directory
        verbose: Print progress messages
        
    Returns:
        True if restore successful, False otherwise
    """
    if not backup_dir.exists():
        if verbose:
            print(f"✗ Backup directory not found: {backup_dir}")
        return False
    
    if verbose:
        print(f"Restoring datasets from: {backup_dir}")
        print("=" * 60)
    
    # Directories to restore
    restore_mapping = [
        ("training", TRAINING_DATA_DIR),
        ("validation", VALIDATION_DATA_DIR),
        ("test", TEST_DATA_DIR)
    ]
    
    restored_count = 0
    
    for name, dest_dir in restore_mapping:
        source_subdir = backup_dir / name
        
        if not source_subdir.exists():
            if verbose:
                print(f"⚠ {name.capitalize()} backup not found: {source_subdir}")
            continue
        
        # Create destination directory
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all files
        files = list(source_subdir.glob("*"))
        for file_path in files:
            if file_path.is_file():
                dest_path = dest_dir / file_path.name
                shutil.copy2(file_path, dest_path)
                
                if verbose:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    print(f"✓ Restored: {file_path.name} ({size_mb:.1f} MB)")
        
        restored_count += 1
    
    if restored_count == 0:
        if verbose:
            print("\n✗ No datasets found in backup")
        return False
    
    if verbose:
        print("=" * 60)
        print(f"✓ Restore complete!")
        print(f"  Restored {restored_count} dataset(s)")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Backup and restore datasets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backup current datasets
  python backup_datasets.py
  
  # List all backups
  python backup_datasets.py --list
  
  # Restore from specific backup
  python backup_datasets.py --restore data/backup_20231123_120000
        """
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all existing backups'
    )
    parser.add_argument(
        '--restore',
        type=str,
        metavar='BACKUP_DIR',
        help='Restore datasets from specified backup directory'
    )
    parser.add_argument(
        '--backup-dir',
        type=str,
        metavar='DIR',
        help='Custom backup directory path'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output messages'
    )
    
    args = parser.parse_args()
    verbose = not args.quiet
    
    try:
        if args.list:
            # List backups
            list_backups(verbose=verbose)
        
        elif args.restore:
            # Restore from backup
            backup_path = Path(args.restore)
            success = restore_backup(backup_path, verbose=verbose)
            sys.exit(0 if success else 1)
        
        else:
            # Create backup
            backup_dir = Path(args.backup_dir) if args.backup_dir else None
            success = backup_datasets(backup_dir=backup_dir, verbose=verbose)
            sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
