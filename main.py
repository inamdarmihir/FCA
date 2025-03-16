import os
import argparse
import pandas as pd
from data_generator import save_dataset
from train_model import train_models, evaluate_on_examples
from test_patterns import test_pattern, load_models
from fca_cleaner import process_fca_patterns, clean_fca_pattern, validate_pattern_structure

def main():
    """Main function to run the FCA pattern cleaning pipeline"""
    parser = argparse.ArgumentParser(description='FCA Pattern Cleaner')
    parser.add_argument('--generate', type=int, default=0, help='Generate synthetic dataset with specified number of samples')
    parser.add_argument('--train', action='store_true', help='Train models on the generated dataset')
    parser.add_argument('--tune', action='store_true', help='Tune hyperparameters during training')
    parser.add_argument('--test', action='store_true', help='Test models on example patterns')
    parser.add_argument('--process', type=str, help='Process patterns from an input file and save to an output file')
    parser.add_argument('--output', type=str, default='cleaned_patterns.csv', help='Output file for processed patterns')
    parser.add_argument('--clean', type=str, help='Clean a single pattern and print the result')
    parser.add_argument('--evaluate', action='store_true', help='Evaluate models on examples from the prompt')
    parser.add_argument('--batch', type=str, help='Process a batch of patterns from a text file (one pattern per line)')
    
    args = parser.parse_args()
    
    if args.generate > 0:
        print(f"Generating synthetic dataset with {args.generate} samples...")
        save_dataset('fca_patterns.csv', args.generate, include_edge_cases=True)
    
    if args.train:
        print("Training models...")
        train_models(num_samples=args.generate if args.generate > 0 else 10000, tune_hyperparams=args.tune)
    
    if args.evaluate:
        print("Evaluating models on examples from the prompt...")
        evaluate_on_examples()
    
    if args.test:
        print("Testing models on example patterns...")
        garbage_model, spacing_model, vectorizer, scaler = load_models()
        if all([garbage_model, spacing_model, vectorizer, scaler]):
            # Test patterns from the prompt
            patterns = [
                "BOM WY LON BA PAR OPDQ7LP AI NYC 1000.00 NUC 1000.00 END",  # Has garbage
                "DEL AI BO M BA LON 1000.00 NUC 1000.00 END",  # Has spacing issues
            ]
            
            # Add more test patterns
            patterns.extend([
                "JFK AA LHR BA CDG AF FCO 500.00 NUC 500.00 END",  # Valid pattern
                "SFO UA LHR QX123Z BA CDG 750.50 NUC 750.50 END",  # Has garbage
                "NYC DL A MS TER DAM 800.00 NUC 800.00 END",  # Has spacing issues
                "LAX AA L ON BA PAR 123ABC AF ROM 900.00 NUC 900.00 END",  # Has both issues
            ])
            
            for pattern in patterns:
                test_pattern(pattern, garbage_model, spacing_model, vectorizer, scaler)
    
    if args.process:
        print(f"Processing patterns from {args.process}...")
        process_fca_patterns(args.process, args.output)
    
    if args.clean:
        pattern = args.clean
        print(f"Original pattern: {pattern}")
        cleaned = clean_fca_pattern(pattern)
        print(f"Cleaned pattern: {cleaned}")
        is_valid, message = validate_pattern_structure(cleaned)
        print(f"Validation: {'Valid' if is_valid else 'Invalid'} - {message}")
        
        # If models are available, also predict issues
        try:
            garbage_model, spacing_model, vectorizer, scaler = load_models()
            if all([garbage_model, spacing_model, vectorizer, scaler]):
                from test_patterns import predict_issues
                has_garbage, has_spacing, garbage_prob, spacing_prob = predict_issues(
                    pattern, garbage_model, spacing_model, vectorizer, scaler
                )
                print(f"Model predictions: Has garbage: {has_garbage}, Has spacing issues: {has_spacing}")
                if garbage_prob is not None:
                    print(f"Garbage probability: {garbage_prob:.4f}")
                if spacing_prob is not None:
                    print(f"Spacing probability: {spacing_prob:.4f}")
        except:
            print("Models not available for prediction.")
    
    if args.batch:
        if not os.path.exists(args.batch):
            print(f"Error: File {args.batch} not found.")
            return
        
        # Read patterns from file
        with open(args.batch, 'r') as f:
            patterns = [line.strip() for line in f if line.strip()]
        
        if not patterns:
            print("No patterns found in the file.")
            return
        
        print(f"Processing {len(patterns)} patterns...")
        
        # Clean each pattern
        results = []
        for i, pattern in enumerate(patterns):
            print(f"Processing pattern {i+1}/{len(patterns)}")
            cleaned = clean_fca_pattern(pattern)
            is_valid, message = validate_pattern_structure(cleaned)
            
            results.append({
                'original': pattern,
                'cleaned': cleaned,
                'is_valid': is_valid,
                'message': message
            })
        
        # Save results to CSV
        output_file = args.output if args.output else 'batch_results.csv'
        pd.DataFrame(results).to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
        
        # Print summary
        valid_count = sum(1 for r in results if r['is_valid'])
        print(f"Successfully cleaned {valid_count} out of {len(patterns)} patterns ({valid_count/len(patterns)*100:.2f}%)")

if __name__ == "__main__":
    main() 