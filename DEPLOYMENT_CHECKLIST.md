# ✅ Deployment Checklist - AI DJ

Use this list to ensure everything is configured correctly before deployment.

## Pre-Deployment

### Installed Software

- [ ] Python 3.12+ installed
  ```powershell
  python --version
  ```

- [ ] Node.js 20+ installed
  ```powershell
  node --version
  ```

- [ ] AWS CLI installed and configured
  ```powershell
  aws --version
  aws sts get-caller-identity
  ```

- [ ] AWS CDK installed
  ```powershell
  cdk --version
  ```

- [ ] Git installed
  ```powershell
  git --version
  ```

### Accounts and Credentials

- [ ] Active AWS account
- [ ] AWS Access Key ID and Secret Access Key created
- [ ] AWS CLI configured with credentials
  ```powershell
  aws configure list
  ```

- [ ] Amazon Bedrock enabled in us-east-1
- [ ] Access to Claude 3 Sonnet approved in Bedrock
  - Verify at: https://console.aws.amazon.com/bedrock/ → Model access

- [ ] Spotify Developer App created
- [ ] Spotify Client ID obtained
- [ ] Spotify Client Secret obtained
- [ ] Redirect URIs configured in Spotify

- [ ] GitHub repository created
- [ ] Write access to the repository

### Local Configuration

- [ ] Project cloned/downloaded
- [ ] Python virtual environment created
  ```powershell
  python -m venv .venv
  ```

- [ ] Virtual environment activated
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- [ ] CDK dependencies installed
  ```powershell
  pip install -r requirements.txt
  ```

- [ ] Lambda dependencies installed
  ```powershell
  cd lambda_src
  pip install -r requirements.txt
  cd ..
  ```

## Local Deployment (Optional)

- [ ] Environment variables configured
  ```powershell
  $env:SPOTIFY_CLIENT_ID = "your_client_id"
  $env:SPOTIFY_CLIENT_SECRET = "your_client_secret"
  ```

- [ ] CDK Bootstrap executed (first time only)
  ```powershell
  cdk bootstrap
  ```

- [ ] CDK Synth executed without errors
  ```powershell
  cdk synth
  ```

- [ ] CDK Deploy executed successfully
  ```powershell
  cdk deploy
  ```

- [ ] API Endpoint obtained from output
- [ ] Lambda Function verified in AWS Console
- [ ] DynamoDB Table verified in AWS Console
- [ ] API Gateway verified in AWS Console

## GitHub Configuration

### Repository

- [ ] Code pushed to GitHub
  ```powershell
  git init
  git add .
  git commit -m "Initial commit"
  git branch -M main
  git remote add origin https://github.com/YOUR_USER/ai-dj.git
  git push -u origin main
  ```

### GitHub Actions Secrets

Go to: Settings → Secrets and variables → Actions → New repository secret

- [ ] `AWS_ACCESS_KEY_ID` configured
- [ ] `AWS_SECRET_ACCESS_KEY` configured
- [ ] `AWS_ACCOUNT_ID` configured (12 digits)
- [ ] `SPOTIFY_CLIENT_ID` configured
- [ ] `SPOTIFY_CLIENT_SECRET` configured

### Secret Verification

- [ ] 5 secrets listed in GitHub
- [ ] Secret names without typos
- [ ] Values copied correctly (no extra spaces)

## First Automatic Deployment

- [ ] Push to main branch performed
  ```powershell
  git push origin main
  ```

- [ ] GitHub Actions workflow started
  - Verify at: Repository → Actions

- [ ] Workflow completed successfully (✓ green)
- [ ] All workflow steps passed
- [ ] API Endpoint visible in workflow outputs

## Post-Deployment Verification

### AWS Resources

- [ ] Lambda Function exists
  ```powershell
  aws lambda get-function --function-name AI-DJ-Handler
  ```

- [ ] DynamoDB Table exists
  ```powershell
  aws dynamodb describe-table --table-name AI-DJ-Users
  ```

- [ ] API Gateway exists
  ```powershell
  aws apigatewayv2 get-apis
  ```

- [ ] CloudWatch Log Group exists
  ```powershell
  aws logs describe-log-groups --log-group-name-prefix /aws/lambda/AI-DJ-Handler
  ```

### IAM Permissions

- [ ] Lambda has permissions for DynamoDB
- [ ] Lambda has permissions for Bedrock
- [ ] Lambda has permissions for CloudWatch Logs

Verify at: AWS Console → Lambda → AI-DJ-Handler → Configuration → Permissions

### API Test

- [ ] API Endpoint responds (even with an auth error)
  ```powershell
  curl -X POST "https://your-endpoint/playlist" -H "Content-Type: application/json" -d '{}'
  ```

- [ ] Response received (200, 400, or 500)
- [ ] CORS headers present in response

### Logs and Monitoring

- [ ] Lambda logs visible in CloudWatch
  ```powershell
  aws logs tail /aws/lambda/AI-DJ-Handler --since 1h
  ```

- [ ] No critical errors in logs
- [ ] Lambda metrics visible in CloudWatch

## End-to-End Test (Requires Spotify Token)

- [ ] Spotify Access Token obtained (see SPOTIFY_AUTH_GUIDE.md)
- [ ] POST request to /playlist successful
- [ ] Playlist created on Spotify
- [ ] Playlist URL returned in response
- [ ] Record saved in DynamoDB
  ```powershell
  aws dynamodb get-item --table-name AI-DJ-Users --key '{"user_id":{"S":"test_user"}}'
  ```

## Production Configuration (Optional)

### Security

- [ ] API Gateway with authentication configured (API Key, Cognito, etc.)
- [ ] Rate limiting configured
- [ ] WAF configured (if necessary)
- [ ] Secrets Manager for sensitive credentials

### Monitoring

- [ ] CloudWatch Alarms configured
  - Lambda Errors > 5%
  - API Gateway 5XX > 1%
  - Lambda Duration > 50s
  - DynamoDB Throttled Requests > 0

- [ ] SNS Topic for notifications
- [ ] Email/SMS configured for alarms

### Optimization

- [ ] Lambda memory size adjusted based on usage
- [ ] Lambda timeout adjusted as needed
- [ ] DynamoDB capacity mode reviewed (on-demand vs provisioned)
- [ ] API Gateway caching enabled (if applicable)

### Backup and Recovery

- [ ] DynamoDB Point-in-time Recovery enabled
- [ ] Automatic backups configured
- [ ] Disaster recovery plan documented

## Documentation

- [ ] README.md updated with actual endpoint
- [ ] API_DOCUMENTATION.md reviewed
- [ ] ARCHITECTURE.md updated if changes were made
- [ ] Usage examples documented
- [ ] Troubleshooting guide updated

## Communication

- [ ] Team notified of deployment
- [ ] Documentation shared
- [ ] Access credentials distributed (if applicable)
- [ ] Maintenance schedule communicated

## Rollback Plan

- [ ] Rollback procedure documented
  ```powershell
  # Option 1: Revert commit and re-deploy
  git revert HEAD
  git push
  
  # Option 2: Destroy and re-deploy previous version
  cdk destroy
  git checkout <previous_commit>
  cdk deploy
  ```

- [ ] Backup of previous configuration saved
- [ ] Emergency contacts identified

## Continuous Maintenance Checklist

### Weekly

- [ ] Review error logs in CloudWatch
- [ ] Check usage metrics
- [ ] Review costs in AWS Cost Explorer

### Monthly

- [ ] Update Python dependencies
  ```powershell
  pip list --outdated
  ```

- [ ] Update AWS CDK
  ```powershell
  npm update -g aws-cdk
  ```

- [ ] Review and optimize costs
- [ ] Review IAM policies (principle of least privilege)

### Quarterly

- [ ] Review architecture and scalability
- [ ] Update documentation
- [ ] Perform load tests
- [ ] Review disaster recovery plan

## Notes

**Deployment Date**: _______________

**Deployed by**: _______________

**Deployed Version**: _______________

**API Endpoint**: _______________

**AWS Region**: _______________

**Observations**:
_______________________________________________
_______________________________________________
_______________________________________________

## Issues Found

| Issue | Solution | Date |
|----------|----------|-------|
|          |          |       |
|          |          |       |
|          |          |       |

## Support Contacts

- **AWS Support**: https://console.aws.amazon.com/support/
- **GitHub Support**: https://support.github.com/
- **Spotify Developer**: https://developer.spotify.com/support/
- **Internal Team**: _______________

---

**Deployment Status**: ⬜ Pending | ⬜ In Progress | ⬜ Completed | ⬜ Failed

**Approved by**: _______________

**Signature**: _______________
