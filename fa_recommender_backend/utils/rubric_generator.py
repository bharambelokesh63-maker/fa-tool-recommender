import random

class RubricGenerator:
    def __init__(self):
        self.bloom_criteria = {
            'Remember': ['Recall facts', 'List items', 'Define terms', 'Identify concepts'],
            'Understand': ['Explain concepts', 'Summarize content', 'Interpret information', 'Compare ideas'],
            'Apply': ['Use knowledge in new situations', 'Solve problems', 'Implement procedures', 'Demonstrate skills'],
            'Analyze': ['Break down information', 'Examine relationships', 'Compare and contrast', 'Identify patterns'],
            'Evaluate': ['Make judgments', 'Critique ideas', 'Assess quality', 'Justify decisions'],
            'Create': ['Design solutions', 'Generate new ideas', 'Develop plans', 'Construct products']
        }
        
        self.fa_tool_criteria = {
            'Quiz': {
                'criteria': ['Accuracy of answers', 'Speed of completion', 'Understanding of concepts'],
                'weightage': [40, 20, 40]
            },
            'Project': {
                'criteria': ['Innovation and creativity', 'Technical implementation', 'Documentation quality', 'Presentation'],
                'weightage': [25, 30, 25, 20]
            },
            'Lab Work': {
                'criteria': ['Experimental setup', 'Data collection', 'Analysis and interpretation', 'Safety protocols'],
                'weightage': [25, 25, 35, 15]
            },
            'Case Study': {
                'criteria': ['Problem identification', 'Analysis depth', 'Solution feasibility', 'Critical thinking'],
                'weightage': [20, 30, 30, 20]
            },
            'Group Work': {
                'criteria': ['Collaboration', 'Individual contribution', 'Final output quality', 'Communication'],
                'weightage': [25, 25, 30, 20]
            },
            'Presentation / PPT': {
                'criteria': ['Content quality', 'Visual design', 'Delivery and communication', 'Time management'],
                'weightage': [35, 20, 35, 10]
            },
            'Written Paper': {
                'criteria': ['Content accuracy', 'Writing clarity', 'Structure and organization', 'References and citations'],
                'weightage': [40, 25, 25, 10]
            },
            'Role Play': {
                'criteria': ['Character understanding', 'Scenario execution', 'Learning demonstration', 'Creativity'],
                'weightage': [25, 25, 30, 20]
            },
            'Poster Presentation': {
                'criteria': ['Visual appeal', 'Content clarity', 'Information accuracy', 'Presentation skills'],
                'weightage': [25, 30, 25, 20]
            },
            'Viva / Oral Test': {
                'criteria': ['Knowledge depth', 'Communication skills', 'Confidence', 'Question handling'],
                'weightage': [40, 20, 20, 20]
            },
            'Reflection Journal': {
                'criteria': ['Self-reflection depth', 'Learning insights', 'Writing quality', 'Regular entries'],
                'weightage': [30, 30, 20, 20]
            },
            'Open Book Test': {
                'criteria': ['Information utilization', 'Problem-solving approach', 'Time management', 'Answer quality'],
                'weightage': [30, 30, 20, 20]
            }
        }
    
    def generate_rubric(self, assessment_name, fa_tool, total_marks, bloom_level):
        """Generate a comprehensive rubric for the given parameters"""
        
        # Get tool-specific criteria
        tool_config = self.fa_tool_criteria.get(fa_tool, self.fa_tool_criteria['Quiz'])
        criteria = tool_config['criteria']
        weightage = tool_config['weightage']
        
        # Calculate marks distribution
        marks_distribution = []
        remaining_marks = total_marks
        
        for i, (criterion, weight) in enumerate(zip(criteria, weightage)):
            if i == len(criteria) - 1:  # Last criterion gets remaining marks
                criterion_marks = remaining_marks
            else:
                criterion_marks = round((weight / 100) * total_marks)
                remaining_marks -= criterion_marks
            
            marks_distribution.append(criterion_marks)
        
        # Generate performance levels
        performance_levels = ['Excellent (90-100%)', 'Good (75-89%)', 'Satisfactory (60-74%)', 'Needs Improvement (Below 60%)']
        
        # Build rubric structure
        rubric = {
            'assessment_name': assessment_name,
            'fa_tool': fa_tool,
            'bloom_level': bloom_level,
            'total_marks': total_marks,
            'criteria': []
        }
        
        for i, (criterion, marks) in enumerate(zip(criteria, marks_distribution)):
            criterion_rubric = {
                'criterion': criterion,
                'marks': marks,
                'levels': self._generate_performance_levels(criterion, marks, bloom_level)
            }
            rubric['criteria'].append(criterion_rubric)
        
        # Add Bloom's taxonomy integration
        rubric['bloom_integration'] = self._integrate_bloom_taxonomy(bloom_level, fa_tool)
        
        return rubric
    
    def _generate_performance_levels(self, criterion, total_marks, bloom_level):
        """Generate performance level descriptions for a criterion"""
        levels = []
        
        # Define performance percentages
        percentages = [90, 75, 60, 0]  # Excellent, Good, Satisfactory, Needs Improvement
        
        for i, percentage in enumerate(percentages):
            if i < len(percentages) - 1:
                marks = round((percentage / 100) * total_marks)
                next_percentage = percentages[i + 1] + 1 if i < len(percentages) - 1 else 0
                range_text = f"{next_percentage}-{percentage}%" if i > 0 else f"{percentage}-100%"
            else:
                marks = 0
                range_text = "0-59%"
            
            level_description = self._get_level_description(criterion, i, bloom_level)
            
            levels.append({
                'level': ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement'][i],
                'range': range_text,
                'marks': marks,
                'description': level_description
            })
        
        return levels
    
    def _get_level_description(self, criterion, level_index, bloom_level):
        """Generate description for each performance level"""
        descriptions = {
            'Excellent': {
                'Accuracy of answers': 'All answers are correct with detailed explanations',
                'Content quality': 'Exceptional depth and breadth of content with innovative insights',
                'Technical implementation': 'Flawless execution with advanced techniques',
                'Collaboration': 'Outstanding teamwork and leadership skills demonstrated',
                'Knowledge depth': 'Comprehensive understanding with ability to extend concepts'
            },
            'Good': {
                'Accuracy of answers': 'Most answers correct with good explanations',
                'Content quality': 'Good content with clear understanding',
                'Technical implementation': 'Solid implementation with minor areas for improvement',
                'Collaboration': 'Effective participation and good teamwork',
                'Knowledge depth': 'Good understanding with minor gaps'
            },
            'Satisfactory': {
                'Accuracy of answers': 'Basic answers with some correct elements',
                'Content quality': 'Adequate content meeting minimum requirements',
                'Technical implementation': 'Basic implementation with room for improvement',
                'Collaboration': 'Participated but limited contribution',
                'Knowledge depth': 'Basic understanding with some confusion'
            },
            'Needs Improvement': {
                'Accuracy of answers': 'Many incorrect answers or incomplete responses',
                'Content quality': 'Insufficient content or significant gaps',
                'Technical implementation': 'Poor implementation with major issues',
                'Collaboration': 'Limited participation or disruptive behavior',
                'Knowledge depth': 'Minimal understanding with major gaps'
            }
        }
        
        level_name = ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement'][level_index]
        
        # Try to find specific description, fallback to generic
        if criterion in descriptions[level_name]:
            return descriptions[level_name][criterion]
        else:
            # Generate based on bloom level and criterion
            return self._generate_generic_description(criterion, level_name, bloom_level)
    
    def _generate_generic_description(self, criterion, level_name, bloom_level):
        """Generate generic description based on criterion and level"""
        bloom_verbs = {
            'Remember': ['recall', 'identify', 'list', 'define'],
            'Understand': ['explain', 'describe', 'summarize', 'interpret'],
            'Apply': ['apply', 'use', 'implement', 'demonstrate'],
            'Analyze': ['analyze', 'examine', 'compare', 'break down'],
            'Evaluate': ['evaluate', 'assess', 'critique', 'judge'],
            'Create': ['create', 'design', 'develop', 'generate']
        }
        
        level_qualifiers = {
            'Excellent': 'exceptionally well',
            'Good': 'effectively',
            'Satisfactory': 'adequately',
            'Needs Improvement': 'with significant gaps'
        }
        
        verb = random.choice(bloom_verbs.get(bloom_level, bloom_verbs['Apply']))
        qualifier = level_qualifiers[level_name]
        
        return f"Can {verb} {criterion.lower()} {qualifier}"
    
    def _integrate_bloom_taxonomy(self, bloom_level, fa_tool):
        """Integrate Bloom's taxonomy with FA tool"""
        integration = {
            'target_level': bloom_level,
            'alignment': f"This {fa_tool} is designed to assess {bloom_level} level skills",
            'cognitive_processes': self.bloom_criteria.get(bloom_level, []),
            'assessment_focus': f"Students will be evaluated on their ability to {bloom_level.lower()} through {fa_tool.lower()}"
        }
        
        return integration
    
    def generate_rubric_html(self, rubric_data):
        """Generate HTML representation of the rubric"""
        html = f"""
        <div class="rubric-container">
            <h2>Assessment Rubric: {rubric_data['assessment_name']}</h2>
            <div class="rubric-info">
                <p><strong>FA Tool:</strong> {rubric_data['fa_tool']}</p>
                <p><strong>Bloom's Level:</strong> {rubric_data['bloom_level']}</p>
                <p><strong>Total Marks:</strong> {rubric_data['total_marks']}</p>
            </div>
            
            <table class="rubric-table">
                <thead>
                    <tr>
                        <th>Criteria</th>
                        <th>Marks</th>
                        <th>Excellent</th>
                        <th>Good</th>
                        <th>Satisfactory</th>
                        <th>Needs Improvement</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for criterion in rubric_data['criteria']:
            html += f"""
                    <tr>
                        <td><strong>{criterion['criterion']}</strong></td>
                        <td>{criterion['marks']}</td>
            """
            
            for level in criterion['levels']:
                html += f"""
                        <td>
                            <div class="level-info">
                                <strong>{level['range']}</strong><br>
                                <span class="marks">({level['marks']} marks)</span><br>
                                <p>{level['description']}</p>
                            </div>
                        </td>
                """
            
            html += "</tr>"
        
        html += """
                </tbody>
            </table>
            
            <div class="bloom-integration">
                <h3>Bloom's Taxonomy Integration</h3>
                <p><strong>Target Level:</strong> {}</p>
                <p><strong>Assessment Focus:</strong> {}</p>
            </div>
        </div>
        """.format(
            rubric_data['bloom_integration']['target_level'],
            rubric_data['bloom_integration']['assessment_focus']
        )
        
        return html

# Usage example
if __name__ == "__main__":
    generator = RubricGenerator()
    
    # Generate sample rubric
    rubric = generator.generate_rubric(
        assessment_name="Data Structures Quiz",
        fa_tool="Quiz",
        total_marks=20,
        bloom_level="Apply"
    )
    
    print("Generated Rubric:")
    print(f"Assessment: {rubric['assessment_name']}")
    print(f"FA Tool: {rubric['fa_tool']}")
    print(f"Total Marks: {rubric['total_marks']}")
    print("\nCriteria:")
    
    for criterion in rubric['criteria']:
        print(f"\n{criterion['criterion']} ({criterion['marks']} marks)")
        for level in criterion['levels']:
            print(f"  {level['level']}: {level['description']} ({level['marks']} marks)")