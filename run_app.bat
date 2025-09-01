@echo off
echo Starting Student Marks Analyzer...
echo.
echo Opening in your default browser...
echo.
python -m streamlit run simple_streamlit.py --server.port 8508 --server.headless true
pause
