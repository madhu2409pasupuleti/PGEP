#!/usr/bin/env python3
"""
PGEP Folder Analyzer and Organizer
This script analyzes your local PGEP folder and categorizes files
into: Fundamentals, Intermediate, Advanced, Projects, Assignments, and Resources
"""

import os
import shutil
import json
from pathlib import Path
from collections import defaultdict

class PGEPOrganizer:
    def __init__(self, source_dir, target_dir):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.categorized_files = defaultdict(list)
        self.uncategorized_files = []
        
        # Keywords for categorization
        self.keywords = {
            'fundamentals': ['fundamental', 'basics', 'intro', 'basic', 'level1', 'l1', 'beginner', 'foundation'],
            'intermediate': ['intermediate', 'level2', 'l2', 'moderate', 'mid'],
            'advanced': ['advanced', 'level3', 'l3', 'expert', 'complex', 'hard'],
            'projects': ['project', 'final', 'complete', 'capstone', 'app', 'application'],
            'assignments': ['assignment', 'hw', 'homework', 'quiz', 'exam', 'assessment', 'exercise'],
            'resources': ['resource', 'reference', 'document', 'doc', 'textbook', 'notes', 'tutorial', 'guide', 'README']
        }
        
        # File extensions mapping
        self.file_types = {
            'code': ['.py', '.java', '.cpp', '.js', '.ts', '.go', '.rs', '.c', '.rb', '.php', '.cs'],
            'notebook': ['.ipynb', '.Rmd'],
            'documents': ['.pdf', '.txt', '.md', '.docx', '.doc', '.xlsx', '.xls'],
            'web': ['.html', '.css', '.xml', '.json', '.yaml', '.yml'],
            'data': ['.csv', '.json', '.sql', '.db'],
            'images': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp'],
            'archives': ['.zip', '.tar', '.gz', '.rar']
        }
    
    def get_file_type(self, filepath):
        """Determine file type based on extension"""
        ext = Path(filepath).suffix.lower()
        for file_type, extensions in self.file_types.items():
            if ext in extensions:
                return file_type
        return 'other'
    
    def categorize_file(self, filename, filepath):
        """Categorize file based on name and path"""
        name_lower = filename.lower()
        path_lower = str(filepath).lower()
        
        # Check filename and path for keywords
        combined_text = f"{name_lower} {path_lower}"
        
        for category, keywords in self.keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
        
        return None
    
    def analyze_folder(self):
        """Analyze the local PGEP folder"""
        print(f"\n📂 Analyzing folder: {self.source_dir}")
        print("=" * 60)
        
        if not self.source_dir.exists():
            print(f"❌ Error: Folder not found at {self.source_dir}")
            return False
        
        file_count = 0
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                filepath = Path(root) / file
                category = self.categorize_file(file, filepath)
                file_type = self.get_file_type(file)
                
                file_info = {
                    'name': file,
                    'path': str(filepath),
                    'type': file_type,
                    'category': category or 'uncategorized'
                }
                
                if category:
                    self.categorized_files[category].append(file_info)
                else:
                    self.uncategorized_files.append(file_info)
                
                file_count += 1
        
        print(f"✅ Found {file_count} files\n")
        self._print_categorization_summary()
        return True
    
    def _print_categorization_summary(self):
        """Print summary of categorized files"""
        print("📊 CATEGORIZATION SUMMARY")
        print("=" * 60)
        
        for category in ['fundamentals', 'intermediate', 'advanced', 'projects', 'assignments', 'resources']:
            files = self.categorized_files[category]
            if files:
                print(f"\n🗂️  {category.upper()} ({len(files)} files)")
                print("-" * 60)
                for file_info in files:
                    print(f"  • {file_info['name']}")
                    print(f"    └─ Type: {file_info['type']}, Path: {file_info['path'][:50]}...")
        
        if self.uncategorized_files:
            print(f"\n⚠️  UNCATEGORIZED ({len(self.uncategorized_files)} files)")
            print("-" * 60)
            for file_info in self.uncategorized_files:
                print(f"  • {file_info['name']}")
                print(f"    └─ Type: {file_info['type']}, Path: {file_info['path'][:50]}...")
    
    def export_report(self, output_file='pgep_categorization_report.json'):
        """Export categorization report"""
        report = {
            'source_directory': str(self.source_dir),
            'target_directory': str(self.target_dir),
            'categorized_files': dict(self.categorized_files),
            'uncategorized_files': self.uncategorized_files,
            'summary': {
                'fundamentals': len(self.categorized_files['fundamentals']),
                'intermediate': len(self.categorized_files['intermediate']),
                'advanced': len(self.categorized_files['advanced']),
                'projects': len(self.categorized_files['projects']),
                'assignments': len(self.categorized_files['assignments']),
                'resources': len(self.categorized_files['resources']),
                'uncategorized': len(self.uncategorized_files),
                'total': sum(len(v) for v in self.categorized_files.values()) + len(self.uncategorized_files)
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report saved to: {output_file}")
        return report
    
    def create_copy_instructions(self):
        """Generate instructions for moving files"""
        instructions = []
        
        print("\n\n📝 MANUAL MOVE INSTRUCTIONS")
        print("=" * 60)
        print("\nSince automated moving requires local access, here are the commands to run:\n")
        
        for category in ['fundamentals', 'intermediate', 'advanced', 'projects', 'assignments', 'resources']:
            files = self.categorized_files[category]
            if files:
                folder_map = {
                    'fundamentals': '01-Fundamentals',
                    'intermediate': '02-Intermediate',
                    'advanced': '03-Advanced',
                    'projects': '04-Projects',
                    'assignments': '05-Assignments',
                    'resources': '06-Resources'
                }
                
                print(f"\n# {category.upper()}")
                print(f"# Move to: {folder_map[category]}/")
                for file_info in files:
                    source = file_info['path']
                    target_folder = folder_map[category]
                    print(f"# mv '{source}' ./{target_folder}/")


def main():
    # Configuration
    SOURCE_DIR = '/Users/madhu/Desktop/PGEP'  # Change this to your actual path
    TARGET_DIR = '.'  # Current directory (your local repo)
    
    print("\n" + "=" * 60)
    print("🚀 PGEP FOLDER ANALYZER & ORGANIZER")
    print("=" * 60)
    
    # Create organizer instance
    organizer = PGEPOrganizer(SOURCE_DIR, TARGET_DIR)
    
    # Analyze folder
    if organizer.analyze_folder():
        # Export report
        organizer.export_report('pgep_analysis_report.json')
        
        # Print move instructions
        organizer.create_copy_instructions()
        
        print("\n\n" + "=" * 60)
        print("✅ NEXT STEPS:")
        print("=" * 60)
        print("""
1. Review the categorization report: pgep_analysis_report.json
2. Adjust any miscategorized files in the report
3. Run the git commands to move files to appropriate folders
4. Commit and push to GitHub:
   
   git add .
   git commit -m "Add PGEP exercises and resources"
   git push origin main
        """)
        print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
