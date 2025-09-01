# 🚀 Deployment Guide - Student Marks Analyzer

## Streamlit Cloud Deployment

### Prerequisites
- GitHub repository with your code
- Streamlit Community Cloud account

### Step 1: Prepare Your Repository

Make sure your repository contains:
- `streamlit_app.py` (main app file)
- `requirements.txt` (dependencies)
- `packages.txt` (optional, for system packages)
- `.streamlit/config.toml` (optional, for configuration)

### Step 2: Deploy to Streamlit Cloud

1. **Go to**: [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Fill in the details**:
   - **Repository**: `Niroop-10322/Student-Marks-Analyzer`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. **Click "Deploy"**

### Step 3: Access Your App

Once deployed, you'll get a URL like:
`https://your-app-name.streamlit.app`

## Local Development

### Run Locally
```bash
# Install dependencies
pip install streamlit pandas

# Run the app
streamlit run streamlit_app.py
```

### Run with Batch File (Windows)
```bash
.\run_app.bat
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Port Issues**: Use different ports if 8501 is busy
3. **File Not Found**: Ensure `streamlit_app.py` is in the root directory

### Streamlit Cloud Issues

1. **Deployment Fails**: Check the logs in Streamlit Cloud dashboard
2. **App Not Loading**: Verify the main file path is correct
3. **Dependencies Missing**: Update `requirements.txt`

## File Structure for Deployment

```
Student-Marks-Analyzer/
├── streamlit_app.py          # Main app file
├── requirements.txt          # Python dependencies
├── packages.txt             # System packages (optional)
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── README.md                # Project documentation
└── DEPLOYMENT.md            # This file
```

## Support

For issues:
- Check Streamlit Cloud logs
- Verify GitHub repository is public
- Ensure all files are committed and pushed
