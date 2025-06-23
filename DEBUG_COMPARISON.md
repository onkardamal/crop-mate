# CropMate Comparison Debugging Guide

## 🔍 How to Debug Crop Comparison Issues

If the crop comparison tab is not working properly, follow these steps to identify and fix the issue:

### 1. Check Browser Console
1. Open the CropMate application in your browser
2. Navigate to the "Compare Crops" page
3. Right-click and select "Inspect" or press F12
4. Go to the "Console" tab
5. Look for any red error messages

### 2. Common Issues and Solutions

#### Issue: Images not loading
**Symptoms**: Crop images show as broken or default crop image
**Solution**: 
- Check that all image files exist in `static/images/`
- Verify image filenames match the crop names exactly
- Images should be: `rice.png`, `maize.png`, `apple.png`, etc.

#### Issue: Can't select crops
**Symptoms**: Clicking on crop cards doesn't work
**Solution**:
- Check if JavaScript is enabled in your browser
- Look for JavaScript errors in the console
- Try refreshing the page

#### Issue: Comparison not showing
**Symptoms**: Selected 2 crops but comparison doesn't appear
**Solution**:
- Check the browser console for API errors
- Verify the server is running (`python app.py`)
- Check if the API endpoints are working

### 3. Test the APIs Manually

Open these URLs in your browser to test the APIs:

1. **Crops List**: `http://localhost:5000/api/crops`
2. **Individual Crop**: `http://localhost:5000/api/crops/Rice`
3. **Compare Page**: `http://localhost:5000/compare`

### 4. Run the Test Script

```bash
python test_compare.py
```

This will test all the comparison functionality and show you what's working.

### 5. Expected Behavior

When working correctly, the crop comparison should:

1. **Load crop cards**: Display all 22 crops with images
2. **Allow selection**: Click to select up to 2 crops
3. **Show selection indicator**: Display selected crops at the top
4. **Generate comparison**: Show detailed comparison when 2 crops are selected
5. **Display charts**: Show climate suitability and profitability charts
6. **Show map**: Display growing regions on an interactive map

### 6. Troubleshooting Steps

1. **Restart the server**:
   ```bash
   python app.py
   ```

2. **Clear browser cache**: Press Ctrl+F5 to hard refresh

3. **Check dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Test with different browsers**: Try Chrome, Firefox, or Edge

### 7. Known Working Combinations

These crop combinations should work:
- Rice vs Maize
- Apple vs Banana
- Cotton vs Jute
- Coconut vs Papaya

### 8. If Still Not Working

1. Check the server logs for errors
2. Verify all files are in the correct locations
3. Ensure the virtual environment is activated
4. Try running the startup script: `python start.py`

### 9. Contact Information

If you're still experiencing issues, please provide:
- Browser and version
- Error messages from console
- Steps to reproduce the issue
- Screenshots if possible

---

**Remember**: The comparison feature requires JavaScript to be enabled and the server to be running properly. 