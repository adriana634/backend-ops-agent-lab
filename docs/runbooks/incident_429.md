# HTTP 429 from External Provider

## Symptoms
- Repeated HTTP 429 responses
- Increased latency in billing-related operations
- Failed requests during traffic spikes

## Likely Causes
- Provider-side rate limiting
- Retry strategy too aggressive
- Missing backoff or jitter
- Sudden concurrency increase

## Recommended Checks
- Review request volume
- Check retry and concurrency settings
- Confirm provider quotas or rate limits

## Recommended Actions
- Reduce retry aggressiveness
- Add exponential backoff
- Add jitter
- Lower concurrency if necessary