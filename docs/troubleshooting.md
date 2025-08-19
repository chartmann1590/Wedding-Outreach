# Troubleshooting Guide

Common issues and solutions for the Wedding Outreach application.

## Installation Issues

### Python Version Issues

**Problem**: `ModuleNotFoundError` or compatibility errors
**Solution**: Ensure you're using Python 3.8 or higher
```bash
python --version
# Should show 3.8.x or higher
```

### Dependency Installation Fails

**Problem**: `pip install -r requirements.txt` fails
**Solutions**:
1. Upgrade pip: `python -m pip install --upgrade pip`
2. Use virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install packages individually if bulk install fails

## Application Issues

### Database Errors

**Problem**: SQLite database errors or "database is locked"
**Solutions**:
1. Delete the database file and restart: `rm wedding_outreach.db`
2. Check file permissions
3. Ensure only one instance is running

### Port Already in Use

**Problem**: `Address already in use` error on port 5000
**Solutions**:
1. Kill existing process: `lsof -ti:5000 | xargs kill -9` (Unix/Mac)
2. Use different port: Set environment variable `PORT=5001`
3. On Windows: `netstat -ano | findstr :5000` then `taskkill /PID <PID> /F`

### Template Not Found Errors

**Problem**: `TemplateNotFound` exception
**Solution**: Ensure you're running from the project root directory where `templates/` folder exists

## Docker Issues

### Docker Build Fails

**Problem**: Docker build command fails
**Solutions**:
1. Check Docker is running: `docker version`
2. Verify Dockerfile exists in project root
3. Check available disk space
4. Try: `docker system prune` to clean up space

### Container Won't Start

**Problem**: Docker container exits immediately
**Solutions**:
1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Check port conflicts: `docker-compose down && docker-compose up`

## Google Sheets Integration

### CSV Import Issues

**Problem**: CSV upload fails or imports incorrect data
**Solutions**:
1. Ensure CSV has proper headers (Name, Address, Notes, Facebook)
2. Check file encoding (should be UTF-8)
3. Remove any special characters or formatting
4. Try smaller CSV files to test

### Google Sheets URL Issues

**Problem**: "Invalid Google Sheets URL format" error
**Solution**: Ensure the sheets URL is publicly accessible and properly formatted:
- Should contain `/spreadsheets/d/[ID]`
- Sheet should be published or shared with view access

## AI Integration (Ollama)

### Ollama Connection Fails

**Problem**: Cannot connect to Ollama server
**Solutions**:
1. Ensure Ollama is installed and running
2. Check Ollama is accessible at configured URL
3. Try default URL: `http://localhost:11434`
4. Verify firewall settings

### Message Generation Fails

**Problem**: AI message generation returns errors
**Solutions**:
1. Check Ollama model is downloaded: `ollama list`
2. Try simpler model like `llama2`
3. Ensure sufficient system memory
4. Fall back to manual message templates

## Facebook Messenger Integration

### Links Not Working

**Problem**: Messenger links don't open correctly
**Solutions**:
1. Facebook profile URLs should be complete
2. Try different Facebook URL formats
3. Use Facebook username instead of full URL
4. Test links manually in browser first

## Performance Issues

### Slow Response Times

**Problem**: Application responds slowly
**Solutions**:
1. Check system resources (CPU, memory)
2. Reduce guest list size for testing
3. Disable AI features temporarily
4. Use SQLite browser to check database size

### Memory Usage High

**Problem**: High memory consumption
**Solutions**:
1. Restart the application
2. Check for memory leaks in custom code
3. Reduce concurrent operations
4. Use Docker to limit memory usage

## Getting Additional Help

If you're still experiencing issues:

1. **Check GitHub Issues**: [Repository Issues](https://github.com/chartmann1590/Wedding-Outreach/issues)
2. **Enable Debug Mode**: Set `debug=True` in `app.py` for detailed error messages
3. **Check Logs**: Look at application logs for specific error messages
4. **Create New Issue**: Include:
   - Operating system and version
   - Python version
   - Full error message
   - Steps to reproduce
   - Expected vs actual behavior

## Debug Mode

To enable detailed logging:

```python
# In app.py
app.run(debug=True, host="0.0.0.0", port=5000)
```

**Warning**: Never enable debug mode in production!