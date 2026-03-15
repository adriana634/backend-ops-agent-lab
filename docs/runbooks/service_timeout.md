# Service Timeout

## Symptoms
- Requests exceed timeout threshold
- Background jobs remain pending or retry repeatedly
- Dependency calls become slower than usual

## Likely Causes
- External dependency degradation
- Network instability
- Timeout values too low
- Service saturation

## Recommended Checks
- Review timeout metrics
- Check dependency health
- Inspect retry counts
- Validate network and DNS behavior

## Recommended Actions
- Tune timeout values carefully
- Add retry limits
- Consider circuit breaker protection
- Escalate to provider if degradation continues