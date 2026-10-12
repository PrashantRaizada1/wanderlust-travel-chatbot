"""
Ragas Evaluation for Travel Chatbot
RUBRIC: Evaluation Framework (RAGAS) (8 marks total)
- RAGAS evaluation implemented (3 marks)
- Golden dataset created (2 marks)
- All four metrics computed (2 marks)
- Results saved with pass/fail logic (1 mark)

TASK: Implement Ragas evaluation with 4 metrics
"""
import os
import json
import logging
import asyncio
import pandas as pd
from pathlib import Path
from typing import List, Dict

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

from src.search_engine import TravelSearchEngine
from src.config import Config

# HINT: Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluation")


class TravelChatbotEvaluator:
    """Evaluates Travel Chatbot using Ragas metrics"""
    
    def __init__(self):
        # HINT: Initialize search engine and golden dataset path
        self.engine = ___() 
        self.golden_dataset_path = Path("___") / "___"  # HINT: "data", "golden_dataset.json"
    
    def load_golden_dataset(self) -> List[Dict]:
        """
        Load golden dataset for evaluation
        
        HINT: Check if file exists, if not create sample dataset
        """
        if not self.golden_dataset_path.___(): 
            logger.warning(f"Golden dataset not found at {self.golden_dataset_path}")
            logger.info("Creating sample golden dataset...")
            return self.___()  
        
        with open(self.golden_dataset_path, '___') as f: 
            return json.___(f)  
    
    def _create_sample_dataset(self) -> List[Dict]:
        """
        Create sample golden dataset if not exists
        
        HINT: Create list of dicts with 'question' and 'ground_truth' keys
        Save to golden_dataset_path
        """
        sample_data = [
            {
                "question": "___",  # HINT: "What are the baggage allowance rules for international flights?"
                "ground_truth": "___"  # HINT: Appropriate ground truth answer
            },
            {
                "question": "___",  # HINT: "What is Air India's cancellation policy?"
                "ground_truth": "___"  # HINT: Appropriate ground truth answer
            },
            {
                "question": "___",  # HINT: "Do I need a visa to travel from India to UK?"
                "ground_truth": "___"  # HINT: Appropriate ground truth answer
            },
            {
                "question": "___",  # HINT: "What are the refund policies for flight cancellations?"
                "ground_truth": "___"  # HINT: Appropriate ground truth answer
            },
            {
                "question": "___",  # HINT: "What documents do I need for international travel?"
                "ground_truth": "___"  # HINT: Appropriate ground truth answer
            }
        ]
        
        # HINT: Save sample dataset
        self.golden_dataset_path.parent.mkdir(exist_ok=True)
        with open(self.golden_dataset_path, '___') as f:  
            json.___(sample_data, f, indent=2)
        
        logger.info(f"Sample golden dataset saved to {self.golden_dataset_path}")
        return sample_data
    
    def generate_responses(self, questions: List[str]) -> tuple:
        """
        Generate responses for questions
        
        HINT: For each question:
        1. Search for documents
        2. Synthesize response
        3. Collect contexts
        Return (answers, contexts)
        """
        answers = []
        contexts = []
        
        for question in questions:
            logger.info(f"Generating answer for: {question}")
            
            try:
                # HINT: Search for relevant documents
                docs, _ = self.engine.___(question, k=___) 
                
                # HINT: Generate answer
                answer = self.engine.___(docs, question)
                
                # HINT: Collect contexts (retrieved documents)
                context_texts = [doc.___ for doc in docs]
                
                answers.___(answer)
                contexts.append(___) 
                
            except Exception as e:
                logger.error(f"Error generating answer for '{question}': {e}")
                answers.append("___") 
                contexts.append([])
        
        return answers, contexts
    
    async def run_ragas_evaluation(self):
        """
        Run Ragas evaluation
        
        HINT: This method should:
        1. Load golden dataset
        2. Generate responses
        3. Prepare dataset dict
        4. Run Ragas evaluation with 4 metrics
        5. Save results
        """
        logger.info("=" * 70)
        logger.info("Starting Ragas Evaluation...")
        logger.info("=" * 70)
        
        # HINT: Load golden dataset
        golden_data = self.___()  
        
        if not golden_data:
            logger.error("No evaluation data available")
            return None
        
        logger.info(f"Loaded {len(golden_data)} test cases")
        
        # HINT: Extract questions and ground truths
        questions = [item["___"] for item in golden_data] 
        ground_truths = [[item["___"]] for item in golden_data] 
        
        # HINT: Generate answers and contexts
        logger.info("\nGenerating responses...")
        answers, contexts = self.___(questions) 
        
        # HINT: Prepare dataset for Ragas
        dataset_dict = {
            "question": ___,  
            "answer": ___,   
            "contexts": ___,  
            "ground_truth": ___  
        }
        
        # HINT: Create HuggingFace Dataset
        hf_dataset = Dataset.___(dataset_dict) 
        
        logger.info("\nRunning Ragas metrics...")
        logger.info("Metrics: faithfulness, answer_relevancy, context_precision, context_recall")
        
        # HINT: Run evaluation
        try:
            results = evaluate(
                hf_dataset,
                metrics=[
                    ___,  # HINT: faithfulness
                    ___,  # HINT: answer_relevancy
                    ___,  # HINT: context_precision
                    ___   # HINT: context_recall
                ],
            )
            
            logger.info("\n" + "=" * 70)
            logger.info("EVALUATION RESULTS")
            logger.info("=" * 70)
            logger.info(f"\nRagas Scores:")
            logger.info(f"  Faithfulness:       {results['___']:.4f}")  
            logger.info(f"  Answer Relevancy:   {results['___']:.4f}")   
            logger.info(f"  Context Precision:  {results['___']:.4f}") 
            logger.info(f"  Context Recall:     {results['___']:.4f}")  
            logger.info("=" * 70)
            
            # HINT: Save detailed results
            self.___(results, dataset_dict)  # HINT: _save_results
            
            return results
            
        except Exception as e:
            logger.error(f"Ragas evaluation failed: {e}")
            logger.error("Make sure you have OPENAI_API_KEY set for Ragas to work")
            return None
    
    def _save_results(self, results: dict, dataset_dict: dict):
        """
        Save evaluation results to file
        
        HINT: Save summary JSON and detailed CSV
        """
        output_dir = Path("___")  # HINT: "reports"
        output_dir.mkdir(exist_ok=True)
        
        # HINT: Save summary
        summary = {
            "faithfulness": float(results.get('___', 0)),  # HINT: 'faithfulness'
            "answer_relevancy": float(results.get('___', 0)),  # HINT: 'answer_relevancy'
            "context_precision": float(results.get('___', 0)),  # HINT: 'context_precision'
            "context_recall": float(results.get('___', 0)),  # HINT: 'context_recall'
            "total_test_cases": len(dataset_dict["question"])
        }
        
        summary_path = output_dir / "___"  # HINT: "evaluation_summary.json"
        with open(summary_path, '___') as f:  # HINT: 'w'
            json.___(summary, f, indent=2)  # HINT: dump
        
        logger.info(f"\n✅ Evaluation summary saved to {summary_path}")
        
        # HINT: Save detailed results
        detailed_df = pd.DataFrame(___)  # HINT: dataset_dict
        detailed_path = output_dir / "___"  # HINT: "evaluation_detailed.csv"
        detailed_df.to_csv(detailed_path, index=False)
        
        logger.info(f"✅ Detailed results saved to {detailed_path}")
    
    def run(self):
        """Run evaluation (sync wrapper)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.___())


def run_evaluation():
    """
    Main evaluation function
    
    HINT: Run evaluator and check if results pass thresholds
    """
    evaluator = ___()  
    results = evaluator.___() 
    
    if results:
        # HINT: Check if evaluation passes minimum thresholds
        min_faithfulness = ___  
        min_relevancy = ___ 
        
        passed = (
            results.get('___', 0) >= min_faithfulness and  
            results.get('___', 0) >= min_relevancy 
        )
        
        if passed:
            logger.info("\n✅ EVALUATION PASSED")
            return 0
        else:
            logger.warning("\n⚠️  EVALUATION BELOW THRESHOLDS")
            return 1
    else:
        logger.error("\n❌ EVALUATION FAILED")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = run_evaluation()
    sys.exit(exit_code)