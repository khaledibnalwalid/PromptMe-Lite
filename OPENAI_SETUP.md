# OpenAI API Setup Guide

This guide explains how to get an OpenAI API key for use with PromptMe.

## Step 1: Create OpenAI Account

1. Go to [https://platform.openai.com/signup](https://platform.openai.com/signup)
2. Sign up with your email or Google/Microsoft account
3. Verify your email address

## Step 2: Get API Key

1. Log in to [https://platform.openai.com](https://platform.openai.com)
2. Click on your profile icon (top right)
3. Select **"API keys"** from the dropdown
4. Click **"Create new secret key"**
5. Give it a name (e.g., "PromptMe-CTF")
6. Click **"Create secret key"**
7. **IMPORTANT:** Copy the key immediately and save it somewhere safe
   - You won't be able to see it again!
   - It looks like: `sk-proj-...` or `sk-...`

## Step 3: Add Billing (Required)

OpenAI requires a payment method even for small usage:

1. Go to [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)
2. Click **"Add payment method"**
3. Add a credit/debit card
4. Set a spending limit (recommended: $5-10 for testing)

**Cost estimate for PromptMe:**
- GPT-4o-mini: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
- Expected cost for 100 users: **< $1.00**
- Expected cost for testing: **< $0.10**

## Step 4: Add API Key to Configuration

Once you have your API key, add it to the `.env` file:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

See the main [README.md](README.md) for complete installation instructions.

## Security Notes

⚠️ **Never commit your API key to Git!**
- The `.env` file is already in `.gitignore`
- Never hardcode API keys in source code
- Rotate keys if accidentally exposed

## Cost Monitoring

- **Monitor usage:** https://platform.openai.com/usage
- **Set spending limits:** https://platform.openai.com/account/billing/limits

## Troubleshooting

### "OpenAI API key not found"
- Check that `OPENAI_API_KEY` is set in `.env` file
- Make sure there are no extra spaces around the key
- Verify the key is valid at https://platform.openai.com/api-keys

### "You exceeded your current quota"
- Add a payment method at https://platform.openai.com/account/billing
- Check your usage at https://platform.openai.com/usage

### "Rate limit exceeded"
- You're making too many requests too quickly
- Wait a minute and try again

---

For support:
- **OpenAI Documentation:** https://platform.openai.com/docs
- **OpenAI Community:** https://community.openai.com
