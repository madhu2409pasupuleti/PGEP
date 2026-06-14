#!/usr/bin/env python3
"""
PGEP File Mover Script
Automatically moves categorized files to appropriate folders in the repo
Based on pgep_analysis_report.json
"""

import os
import shutil
import json
from pathlib import Path

class PGEPFileMover:
    def __init__(self, source_base, target_base, report_file):
        self.source_base = Path(source_base)
        self.target_base = Path(target_base)
        self.report_file = report_file
        self.category_folders = {
            'fundamentals': '01-Fundamentals',
            'intermediate': '02-Intermediate',
            'advanced': '03-Advanced',
            'projects': '04-Projects',
            'assignments': '05-Assignments',
            'resources': '06-Resources'
        }
        self.move_report = {
            'successful': [],
            'failed': [],
            'skipped': []
        }
    
    def load_report(self):
        """Load the categorization report"""
        if not Path(self.report_file).exists():
            print(f"❌ Report file not found: {self.report_file}")
            return None
        
        with open(self.report_file, 'r') as f:
            return json.load(f)
    
    def should_skip_file(self, filename, filepath):
        """Determine if file should be skipped"""
        skip_patterns = [
            '.DS_Store',
            '__pycache__',
            '.pyc',
            '.git',
            '.ipynb_checkpoints',
            'organize_pgep.py',
            'pgep_analysis_report.json',
            'pgep_file_mover.py'
        ]
        
        filename_lower = str(filename).lower()
        filepath_lower = str(filepath).lower()
        
        for pattern in skip_patterns:
            if pattern in filename_lower or pattern in filepath_lower:
                return True
        
        return False
    
    def copy_file(self, source, destination):
        """Copy file with error handling"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            # Create destination directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            return True
        except Exception as e:
            print(f"  ❌ Error copying: {e}")
            return False
    
    def move_categorized_files(self):
        """Move all categorized files to appropriate folders"""
        report = self.load_report()
        if not report:
            return False
        
        print("\n" + "=" * 70)
        print("🚀 MOVING CATEGORIZED PGEP FILES")
        print("=" * 70 + "\n")
        
        total_files = 0
        
        for category, files in report['categorized_files'].items():
            if not files:
                continue
            
            target_folder = self.category_folders[category]
            target_path = self.target_base / target_folder
            
            print(f"\n📂 {category.upper()} → {target_folder}")
            print(f"   ({len(files)} files)")
            print("-" * 70)
            
            for file_info in files:
                filename = file_info['name']
                source_path = file_info['path']
                
                # Skip system files
                if self.should_skip_file(filename, source_path):
                    print(f"  ⏭️  Skipped: {filename} (system file)")
                    self.move_report['skipped'].append(filename)
                    continue
                
                # Copy file
                dest_file = target_path / filename
                
                if self.copy_file(source_path, dest_file):
                    print(f"  ✅ {filename}")
                    self.move_report['successful'].append({
                        'source': source_path,
                        'destination': str(dest_file),
                        'category': category
                    })
                    total_files += 1
                else:
                    print(f"  ❌ {filename}")
                    self.move_report['failed'].append({
                        'source': source_path,
                        'category': category,
                        'reason': 'Copy failed'
                    })
        
        return total_files
    
    def print_summary(self):
        """Print move operation summary"""
        print("\n\n" + "=" * 70)
        print("📊 MOVE OPERATION SUMMARY")
        print("=" * 70)
        
        successful = len(self.move_report['successful'])
        failed = len(self.move_report['failed'])
        skipped = len(self.move_report['skipped'])
        total = successful + failed + skipped
        
        print(f"\n✅ Successfully moved: {successful} files")
        print(f"❌ Failed to move: {failed} files")
        print(f"⏭️  Skipped: {skipped} files")
        print(f"📈 Total processed: {total} files")
        
        if failed > 0:
            print(f"\n⚠️  Failed files:")
            for item in self.move_report['failed']:
                print(f"  • {item['source']}")
                print(f"    Reason: {item['reason']}")
        
        return successful
    
    def save_move_report(self, output_file='pgep_move_report.json'):
        """Save detailed move report"""
        with open(output_file, 'w') as f:
            json.dump(self.move_report, f, indent=2)
        
        print(f"\n💾 Move report saved to: {output_file}")


def main():
    # Configuration
    SOURCE_BASE = '/Users/madhu/Desktop/PGEP'
    TARGET_BASE = '/Users/madhu/Desktop/PGEP/PGEP'  # Your local repo
    REPORT_FILE = 'pgep_analysis_report.json'
    
    print("\n" + "=" * 70)
    print("🔧 PGEP FILE MOVER")
    print("=" * 70)
    
    # Initialize mover
    mover = PGEPFileMover(SOURCE_BASE, TARGET_BASE, REPORT_FILE)
    
    # Move files
    moved_count = mover.move_categorized_files()
    
    # Print summary
    mover.print_summary()
    
    # Save report
    mover.save_move_report()
    
    print("\n" + "=" * 70)
    print("✅ NEXT STEPS:")
    print("=" * 70)
    print("""
1. Review the move report: pgep_move_report.json
2. Verify files are in correct folders:
   
   ls -la PGEP/01-Fundamentals/
   ls -la PGEP/04-Projects/
   ls -la PGEP/05-Assignments/
   ls -la PGEP/06-Resources/

3. Commit and push to GitHub:
   
   cd PGEP
   git add .
   git commit -m "Add categorized PGEP files to respective folders"
   git push origin main
    """)
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
