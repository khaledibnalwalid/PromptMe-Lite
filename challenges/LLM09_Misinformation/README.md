# LLM09: Misinformation

LLM misinformation occurs when an AI model generates false or misleading information that appears credible, potentially leading users to trust incorrect answers. This risk is amplified in sensitive contexts, where users may unknowingly rely on false data for critical decisions.

## Real-World Impact

In 2023, lawyers were sanctioned for submitting legal briefs containing **ChatGPT-generated fake court cases** that never existed. The AI hallucinated:
- Case names and citations
- Judge names
- Court rulings and legal precedents
- Case summaries that appeared legitimate

This demonstrates the critical danger of trusting LLM outputs without verification.

## Application URL
http://127.0.0.1:5009

## Learning Objectives

1. **Observe Hallucinations**: Use the predefined prompts to see how LLMs confidently generate false information
2. **Understand Risk**: Recognize why LLM outputs must be verified in critical applications
3. **Identify Patterns**: Notice how hallucinations include specific details (dates, names, citations) to appear credible

## Example Hallucinations to Test

- **Legal Cases**: Non-existent Supreme Court rulings
- **Scientific Studies**: Fabricated peer-reviewed research
- **Historical Events**: Made-up treaties and agreements
- **Expert Quotes**: Impossible statements from historical figures
- **Confidential Data**: Information that was never publicly disclosed

## Mitigation Strategies

1. **Always verify** LLM outputs against authoritative sources
2. **Implement fact-checking** layers before displaying information
3. **Add disclaimers** that content may be inaccurate
4. **Use RAG** with verified knowledge bases
5. **Enable citations** so users can verify sources
6. **Monitor and log** hallucinations for model improvement

**Note:** Due to the nature of the vulnerability, no CTF flag is provided. The goal is educational awareness of LLM hallucination risks.


