# 🚀 Vercel Deployment Commands

## Quick Deployment Guide

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy the Project
```bash
# Navigate to project directory
cd d:\Animal-classification

# Test deployment readiness
python test_deployment.py

# Deploy to Vercel
vercel

# For production deployment
vercel --prod
```

### 4. Configuration During Deployment
When prompted by Vercel CLI:
- **Link to existing project?** Choose "N" for new project
- **Project name:** `animal-classification` (or your preferred name)
- **Directory:** `.` (current directory)
- **Override settings?** Choose "N" (use vercel.json)

## Expected Deployment URL
After deployment, you'll get a URL like:
- `https://animal-classification-xyz.vercel.app`

## Testing the Deployed Application

### 1. Test the Web Interface
- Visit your deployment URL
- Upload an animal image
- Verify classification results

### 2. Test API Endpoints
```bash
# Health check
curl https://your-app.vercel.app/health

# Get available classes
curl https://your-app.vercel.app/classes

# Test prediction (replace with your URL)
curl -X POST https://your-app.vercel.app/predict \
  -F "file=@path/to/animal/image.jpg"
```

## Monitoring and Logs
- Visit Vercel dashboard: https://vercel.com/dashboard
- Select your project
- View function logs and performance metrics

## Troubleshooting Common Issues

### Issue: Cold Start Timeouts
**Solution**: Upgrade to Vercel Pro for better performance

### Issue: Model Loading Errors
**Solution**: Check function logs in Vercel dashboard

### Issue: File Path Errors
**Solution**: Verify all file paths are relative to project root

## Environment Variables (if needed)
If you need to add environment variables:
1. Go to Vercel dashboard
2. Select project → Settings → Environment Variables
3. Add required variables

## Updating the Deployment
```bash
# After making changes, redeploy with:
vercel --prod
```

---

**🎉 Your Animal Classification app is now ready for Vercel deployment!**
