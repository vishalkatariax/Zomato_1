# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

Build an AI-powered restaurant recommendation service inspired by Zomato. The system should combine structured restaurant data with a Large Language Model (LLM) to deliver personalized, useful, and natural-language recommendations based on user preferences.

## Objective

Design and implement an application that can:

- Accept user preferences such as location, budget, cuisine, and minimum rating.
- Use a real-world restaurant dataset.
- Generate personalized recommendations using an LLM.
- Present recommendations in a clear, user-friendly format.

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face:  
  [https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract and normalize key fields, including:
  - Restaurant name
  - Location
  - Cuisine
  - Estimated cost
  - Rating

### 2. User Input Collection

Capture the following preferences from the user:

- Location (for example: Delhi, Bangalore)
- Budget range (low, medium, high)
- Preferred cuisine (for example: Italian, Chinese)
- Minimum acceptable rating
- Optional preferences (for example: family-friendly, quick service)

### 3. Integration Layer

- Filter and prepare restaurant records based on user inputs.
- Pass shortlisted structured data into an LLM prompt.
- Use prompt design that helps the LLM compare and rank restaurant options effectively.

### 4. Recommendation Engine

Use the LLM to:

- Rank restaurants by relevance to user preferences.
- Explain why each recommendation is a good fit.
- Optionally provide a short summary of top choices.

### 5. Output Presentation

Display top recommendations in an easy-to-read format with:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation

## Related Document

For the detailed phase-wise architecture, see `Docs/phased-architecture.md`.
For detailed project edge cases and test guidance, see `Docs/edge-cases.md`.
