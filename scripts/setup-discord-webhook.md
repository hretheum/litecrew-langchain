# Discord Webhook Setup (Optional)

If you want to receive pipeline notifications in Discord:

## 1. Create Discord Webhook

1. Go to your Discord server
2. Right-click on the channel where you want notifications
3. Select "Edit Channel" → "Integrations" → "Webhooks"
4. Click "New Webhook"
5. Name it "GitLab CI" 
6. Copy the webhook URL

## 2. Add to GitLab

1. Go to: https://gitlab.com/eof3/litecrewai/-/settings/ci_cd
2. Expand "Variables" section
3. Add new variable:
   - Key: `DISCORD_WEBHOOK`
   - Value: Your webhook URL
   - Protected: ✓ (if you want it only for protected branches)
   - Masked: ✓ (to hide it in logs)

## 3. Test

Push a commit to master branch and check if you receive notifications.

## Webhook Format

The notifications will show:
- ✅ Success: Green embed with pipeline details
- ❌ Failure: Red embed with failure information
- Links to pipeline for quick access

## Customization

You can customize the notification format in `.gitlab-ci.yml` in the `notify:success` and `notify:failure` jobs.