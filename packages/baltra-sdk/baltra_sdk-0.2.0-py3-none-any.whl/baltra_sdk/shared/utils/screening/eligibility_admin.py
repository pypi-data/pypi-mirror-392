"""
Eligibility Administration Functions

This module provides administrative functions to review and manage eligibility evaluations
for quality control purposes.
"""

import logging
from typing import Dict, List, Optional
from .sql_utils import (
    get_eligibility_evaluations_for_review,
    update_manual_review_result,
    get_eligibility_accuracy_stats
)


def get_pending_reviews(company_id: int = None, limit: int = 50) -> List[Dict]:
    """
    Get eligibility evaluations that are pending manual review.
    
    Args:
        company_id (int, optional): Filter by company
        limit (int): Maximum number of records to return
        
    Returns:
        List[Dict]: List of pending evaluations with candidate and role details
    """
    try:
        evaluations = get_eligibility_evaluations_for_review(
            company_id=company_id,
            manual_review_status='pending',
            limit=limit
        )
        
        logging.info(f"Retrieved {len(evaluations)} pending eligibility reviews")
        return evaluations
        
    except Exception as e:
        logging.error(f"Error retrieving pending reviews: {e}")
        return []


def review_evaluation(evaluation_id: int, is_correct: bool) -> bool:
    """
    Submit a manual review for an eligibility evaluation.
    
    Args:
        evaluation_id (int): The evaluation ID to review
        is_correct (bool): True if AI decision was correct, False if incorrect
        
    Returns:
        bool: True if review was successfully submitted
    """
    try:
        success = update_manual_review_result(
            evaluation_id=evaluation_id,
            manual_review_result=is_correct
        )
        
        if success:
            logging.info(f"Successfully reviewed evaluation {evaluation_id}: correct={is_correct}")
        else:
            logging.warning(f"Failed to update review for evaluation {evaluation_id}")
            
        return success
        
    except Exception as e:
        logging.error(f"Error submitting review for evaluation {evaluation_id}: {e}")
        return False


def get_accuracy_report(company_id: int = None, days_back: int = 30) -> Dict:
    """
    Get accuracy statistics for eligibility evaluations.
    
    Args:
        company_id (int, optional): Filter by company
        days_back (int): Number of days to look back
        
    Returns:
        Dict: Accuracy statistics and metrics
    """
    try:
        stats = get_eligibility_accuracy_stats(company_id=company_id, days_back=days_back)
        
        # Add some additional calculated metrics
        if stats['total_reviewed'] > 0:
            stats['false_positive_rate'] = round((stats['false_positives'] / stats['total_reviewed']) * 100, 2)
            stats['false_negative_rate'] = round((stats['false_negatives'] / stats['total_reviewed']) * 100, 2)
        else:
            stats['false_positive_rate'] = 0.0
            stats['false_negative_rate'] = 0.0
            
        logging.info(f"Generated accuracy report: {stats['accuracy']}% accuracy over {days_back} days")
        return stats
        
    except Exception as e:
        logging.error(f"Error generating accuracy report: {e}")
        return {
            'total_reviewed': 0,
            'accuracy': 0.0,
            'error': str(e)
        }


def format_evaluation_for_review(evaluation: Dict) -> str:
    """
    Format an eligibility evaluation for human-readable review.
    
    Args:
        evaluation (Dict): The evaluation record from the database
        
    Returns:
        str: Formatted text for review
    """
    try:
        candidate_name = evaluation.get('candidate_name', 'Unknown')
        candidate_phone = evaluation.get('candidate_phone', 'Unknown')
        role_name = evaluation.get('role_name', 'Unknown')
        is_eligible = evaluation.get('is_eligible', False)
        ai_reasoning = evaluation.get('ai_reasoning', 'No reasoning provided')
        evaluation_date = evaluation.get('evaluation_date', 'Unknown')
        
        # Format questions and answers
        qa_text = ""
        questions_and_answers = evaluation.get('questions_and_answers', {})
        if questions_and_answers:
            qa_text = "\n\nQUESTIONS & ANSWERS:\n"
            for question_id, qa_data in questions_and_answers.items():
                question_text = qa_data.get('question_text', 'Unknown question')
                answer_text = qa_data.get('answer_text', 'No answer')
                qa_text += f"Q: {question_text}\nA: {answer_text}\n\n"
        
        # Format eligibility criteria
        criteria_text = ""
        eligibility_criteria = evaluation.get('eligibility_criteria', {})
        if eligibility_criteria:
            criteria_text = "\nROLE CRITERIA:\n"
            for question_id, requirement in eligibility_criteria.items():
                criteria_text += f"• {requirement}\n"
        
        formatted_text = f"""
ELIGIBILITY EVALUATION REVIEW
{'='*50}

Evaluation ID: {evaluation.get('evaluation_id')}
Date: {evaluation_date}

CANDIDATE:
- Name: {candidate_name}
- Phone: {candidate_phone}
- ID: {evaluation.get('candidate_id')}

ROLE:
- Name: {role_name}
- ID: {evaluation.get('role_id')}

AI DECISION: {'✅ ELIGIBLE' if is_eligible else '❌ NOT ELIGIBLE'}

AI REASONING:
{ai_reasoning}
{criteria_text}
{qa_text}
REVIEW INSTRUCTIONS:
- Check if the AI's decision aligns with the role criteria
- Verify that the candidate's answers support the decision
- Consider if the reasoning is sound and complete
"""
        
        return formatted_text.strip()
        
    except Exception as e:
        logging.error(f"Error formatting evaluation {evaluation.get('evaluation_id', 'unknown')}: {e}")
        return f"Error formatting evaluation: {str(e)}"


def batch_review_evaluations(reviews: List[Dict]) -> Dict:
    """
    Submit multiple reviews in batch.
    
    Args:
        reviews (List[Dict]): List of reviews with format:
            [{"evaluation_id": int, "is_correct": bool}, ...]
            
    Returns:
        Dict: Results summary with success/failure counts
    """
    results = {
        'total_submitted': len(reviews),
        'successful': 0,
        'failed': 0,
        'errors': []
    }
    
    for review in reviews:
        try:
            success = review_evaluation(
                evaluation_id=review['evaluation_id'],
                is_correct=review['is_correct']
            )
            
            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to submit review for evaluation {review['evaluation_id']}")
                
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Error reviewing evaluation {review.get('evaluation_id', 'unknown')}: {str(e)}")
    
    logging.info(f"Batch review completed: {results['successful']}/{results['total_submitted']} successful")
    return results


def generate_review_summary_report(company_id: int = None, days_back: int = 7) -> str:
    """
    Generate a summary report of recent eligibility evaluations and their review status.
    
    Args:
        company_id (int, optional): Filter by company
        days_back (int): Number of days to look back
        
    Returns:
        str: Formatted summary report
    """
    try:
        # Get accuracy stats
        accuracy_stats = get_accuracy_report(company_id=company_id, days_back=days_back)
        
        # Get pending reviews count
        pending_reviews = get_pending_reviews(company_id=company_id, limit=1000)  # Get all pending
        pending_count = len(pending_reviews)
        
        report = f"""
ELIGIBILITY EVALUATION SUMMARY REPORT
{'='*50}

Period: Last {days_back} days
Company: {'All' if company_id is None else f'ID {company_id}'}
Generated: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}

ACCURACY STATISTICS:
- Total Reviewed: {accuracy_stats.get('total_reviewed', 0)}
- Overall Accuracy: {accuracy_stats.get('accuracy', 0)}%
- Correct Predictions: {accuracy_stats.get('correct_predictions', 0)}
- Incorrect Predictions: {accuracy_stats.get('incorrect_predictions', 0)}

ERROR BREAKDOWN:
- False Positives: {accuracy_stats.get('false_positives', 0)} ({accuracy_stats.get('false_positive_rate', 0)}%)
  (AI said eligible, should be not eligible)
- False Negatives: {accuracy_stats.get('false_negatives', 0)} ({accuracy_stats.get('false_negative_rate', 0)}%)
  (AI said not eligible, should be eligible)

PENDING REVIEWS:
- Evaluations awaiting review: {pending_count}

RECOMMENDATIONS:
"""
        
        # Add recommendations based on stats
        if accuracy_stats.get('total_reviewed', 0) < 10:
            report += "- Review more evaluations to get statistically significant results\n"
        
        if accuracy_stats.get('accuracy', 0) < 80:
            report += "- AI accuracy is below 80% - consider reviewing prompts or criteria\n"
        
        if accuracy_stats.get('false_positive_rate', 0) > 15:
            report += "- High false positive rate - AI may be too lenient in eligibility decisions\n"
        
        if accuracy_stats.get('false_negative_rate', 0) > 15:
            report += "- High false negative rate - AI may be too strict in eligibility decisions\n"
        
        if pending_count > 50:
            report += f"- Large backlog of {pending_count} pending reviews - consider increasing review capacity\n"
        
        if accuracy_stats.get('total_reviewed', 0) == 0:
            report += "- No reviews completed yet - start reviewing evaluations to track AI accuracy\n"
        
        return report.strip()
        
    except Exception as e:
        logging.error(f"Error generating summary report: {e}")
        return f"Error generating report: {str(e)}"
