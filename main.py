from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
from typing import Dict, Optional
import json
from datetime import datetime

from stress_tests import CPUStressTester
from cpu_monitor import StressTestMonitor

app = FastAPI(title="CPU Stress Testing Dashboard", version="1.0.0")

# Initialize global components
stress_tester = CPUStressTester()
monitor = StressTestMonitor()

# Store test results
test_results_history = []
current_test_status = {"running": False, "test_name": None, "progress": 0}

# Templates
templates = Jinja2Templates(directory="templates")

# Create templates directory if it doesn't exist
import os
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    system_info = monitor.cpu_monitor.get_system_info()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "system_info": system_info,
        "test_results": test_results_history[-10:] if test_results_history else []
    })


@app.get("/api/system-info")
async def get_system_info():
    """Get detailed system information"""
    return monitor.cpu_monitor.get_system_info()


@app.get("/api/current-metrics")
async def get_current_metrics():
    """Get current CPU and memory metrics"""
    current_metrics = monitor.cpu_monitor.get_current_metrics()
    return {
        "timestamp": current_metrics.timestamp.isoformat(),
        "cpu_percent": current_metrics.cpu_percent,
        "cpu_freq": current_metrics.cpu_freq,
        "memory_percent": current_metrics.memory_percent,
        "memory_used_gb": current_metrics.memory_used,
        "memory_total_gb": current_metrics.memory_total,
        "temperature": current_metrics.temperature
    }


@app.get("/api/test-status")
async def get_test_status():
    """Get current test status"""
    if current_test_status["running"]:
        realtime_metrics = monitor.get_realtime_metrics()
        return {**current_test_status, **realtime_metrics}
    return current_test_status


@app.post("/api/stress-test/prime")
async def run_prime_stress_test(background_tasks: BackgroundTasks, max_number: int = 1000000):
    """Run prime number generation stress test"""
    if current_test_status["running"]:
        return JSONResponse({"error": "A test is already running"}, status_code=400)
    
    background_tasks.add_task(execute_stress_test, "prime", {"max_number": max_number})
    return {"message": "Prime stress test started", "max_number": max_number}


@app.post("/api/stress-test/matrix")
async def run_matrix_stress_test(background_tasks: BackgroundTasks, size: int = 1000):
    """Run matrix multiplication stress test"""
    if current_test_status["running"]:
        return JSONResponse({"error": "A test is already running"}, status_code=400)
    
    background_tasks.add_task(execute_stress_test, "matrix", {"size": size})
    return {"message": "Matrix stress test started", "size": size}


@app.post("/api/stress-test/fibonacci")
async def run_fibonacci_stress_test(background_tasks: BackgroundTasks, max_n: int = 50000):
    """Run Fibonacci sequence stress test"""
    if current_test_status["running"]:
        return JSONResponse({"error": "A test is already running"}, status_code=400)
    
    background_tasks.add_task(execute_stress_test, "fibonacci", {"max_n": max_n})
    return {"message": "Fibonacci stress test started", "max_n": max_n}


@app.post("/api/stress-test/sorting")
async def run_sorting_stress_test(background_tasks: BackgroundTasks, array_size: int = 100000):
    """Run sorting algorithms stress test"""
    if current_test_status["running"]:
        return JSONResponse({"error": "A test is already running"}, status_code=400)
    
    background_tasks.add_task(execute_stress_test, "sorting", {"array_size": array_size})
    return {"message": "Sorting stress test started", "array_size": array_size}


@app.post("/api/stress-test/monte-carlo")
async def run_monte_carlo_stress_test(background_tasks: BackgroundTasks, iterations: int = 10000000):
    """Run Monte Carlo π calculation stress test"""
    if current_test_status["running"]:
        return JSONResponse({"error": "A test is already running"}, status_code=400)
    
    background_tasks.add_task(execute_stress_test, "monte_carlo", {"total_iterations": iterations})
    return {"message": "Monte Carlo stress test started", "iterations": iterations}





@app.get("/api/test-results")
async def get_test_results():
    """Get test results history"""
    return {"results": test_results_history}


@app.get("/api/test-results/{test_id}")
async def get_test_result(test_id: str):
    """Get specific test result"""
    for result in test_results_history:
        if result.get("test_id") == test_id:
            return result
    return JSONResponse({"error": "Test result not found"}, status_code=404)


@app.delete("/api/test-results")
async def clear_test_results():
    """Clear test results history"""
    global test_results_history
    test_results_history.clear()
    return {"message": "Test results cleared"}


async def execute_stress_test(test_type: str, params: Dict):
    """Execute a stress test in the background"""
    global current_test_status, test_results_history
    
    test_id = f"{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    current_test_status.update({
        "running": True,
        "test_name": test_type,
        "test_id": test_id,
        "progress": 0
    })
    
    try:
        # Start monitoring
        monitor.start_stress_test_monitoring(test_type)
        
        # Run the appropriate test
        if test_type == "prime":
            result = stress_tester.test_prime_generation(**params)
        elif test_type == "matrix":
            result = stress_tester.test_matrix_multiplication(**params)
        elif test_type == "fibonacci":
            result = stress_tester.test_fibonacci_sequence(**params)
        elif test_type == "sorting":
            result = stress_tester.test_sorting_algorithms(**params)
        elif test_type == "monte_carlo":
            result = stress_tester.test_monte_carlo_pi(**params)
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        # Stop monitoring and get metrics
        monitoring_results = monitor.stop_stress_test_monitoring()
        
        # Combine results
        final_result = {
            "test_id": test_id,
            "test_type": test_type,
            "parameters": params,
            "timestamp": datetime.now().isoformat(),
            "test_results": result,
            "monitoring_results": monitoring_results
        }
        
        # Store results
        test_results_history.append(final_result)
        
        # Keep only last 50 results
        if len(test_results_history) > 50:
            test_results_history.pop(0)
        
    except Exception as e:
        error_result = {
            "test_id": test_id,
            "test_type": test_type,
            "parameters": params,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "monitoring_results": monitor.stop_stress_test_monitoring()
        }
        test_results_history.append(error_result)
    
    finally:
        # Reset test status
        current_test_status.update({
            "running": False,
            "test_name": None,
            "test_id": None,
            "progress": 0
        })


@app.get("/api/metrics/export")
async def export_metrics():
    """Export monitoring metrics to JSON file"""
    filename = monitor.cpu_monitor.export_metrics()
    return {"message": f"Metrics exported to {filename}", "filename": filename}


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket):
    """WebSocket endpoint for real-time metrics"""
    await websocket.accept()
    
    try:
        while True:
            # Send current metrics
            current_metrics = await get_current_metrics()
            test_status = await get_test_status()
            
            await websocket.send_json({
                "type": "metrics",
                "data": current_metrics,
                "test_status": test_status
            })
            
            await asyncio.sleep(1)  # Send updates every second
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    # Create a simple HTML template if templates don't exist
    dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>CPU Stress Testing Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .test-buttons { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 20px; }
        .test-btn { padding: 15px; background: #3498db; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
        .test-btn:hover { background: #2980b9; }
        .test-btn:disabled { background: #bdc3c7; cursor: not-allowed; }
        .status { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .results { background: white; padding: 20px; border-radius: 8px; }
        .progress-bar { width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: #27ae60; transition: width 0.3s ease; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CPU Stress Testing Dashboard</h1>
            <p>Test your CPU performance with parallel algorithms</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>System Info</h3>
                <div id="system-info">
                    <p>CPU Cores: {{ system_info.cpu.logical_cores }}</p>
                    <p>Memory: {{ "%.1f"|format(system_info.memory.total_gb) }} GB</p>
                    <p>Uptime: {{ system_info.uptime_hours }} hours</p>
                </div>
            </div>
            
            <div class="metric-card">
                <h3>Current Metrics</h3>
                <div id="current-metrics">
                    <p>CPU Usage: <span id="cpu-usage">0%</span></p>
                    <p>Memory Usage: <span id="memory-usage">0%</span></p>
                    <p>Temperature: <span id="temperature">N/A</span></p>
                </div>
            </div>
        </div>
        
        <div class="test-buttons">
            <button class="test-btn" onclick="runTest('prime')">Prime Generation</button>
            <button class="test-btn" onclick="runTest('matrix')">Matrix Multiplication</button>
            <button class="test-btn" onclick="runTest('fibonacci')">Fibonacci Sequence</button>
            <button class="test-btn" onclick="runTest('sorting')">Parallel Sorting</button>
            <button class="test-btn" onclick="runTest('monte-carlo')">Monte Carlo π</button>
        </div>
        
        <div class="status">
            <h3>Test Status</h3>
            <div id="test-status">Ready to run tests</div>
            <div class="progress-bar" style="display: none;">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
        </div>
        
        <div class="results">
            <h3>Recent Test Results</h3>
            <div id="test-results">
                {% for result in test_results %}
                <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 4px;">
                    <strong>{{ result.test_type }}</strong> - {{ result.timestamp }}
                    <br>Execution time: {{ "%.2f"|format(result.test_results.execution_time) }}s
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        let currentTest = null;
        
        async function runTest(testType) {
            if (currentTest) {
                alert('A test is already running!');
                return;
            }
            
            const buttons = document.querySelectorAll('.test-btn');
            buttons.forEach(btn => btn.disabled = true);
            
            try {
                const response = await fetch(`/api/stress-test/${testType}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (response.ok) {
                    currentTest = testType;
                    document.getElementById('test-status').textContent = `Running ${testType} test...`;
                    document.querySelector('.progress-bar').style.display = 'block';
                    monitorTest();
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.error}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            } finally {
                if (!currentTest) {
                    buttons.forEach(btn => btn.disabled = false);
                }
            }
        }
        
        async function monitorTest() {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch('/api/test-status');
                    const status = await response.json();
                    
                    if (!status.running) {
                        clearInterval(interval);
                        currentTest = null;
                        document.getElementById('test-status').textContent = 'Test completed!';
                        document.querySelector('.progress-bar').style.display = 'none';
                        
                        const buttons = document.querySelectorAll('.test-btn');
                        buttons.forEach(btn => btn.disabled = false);
                        
                        // Refresh results
                        location.reload();
                    } else {
                        document.getElementById('test-status').textContent = 
                            `Running ${status.test_name} test... (${status.test_duration?.toFixed(1)}s)`;
                    }
                } catch (error) {
                    console.error('Error monitoring test:', error);
                }
            }, 1000);
        }
        
        // Update metrics every 2 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/current-metrics');
                const metrics = await response.json();
                
                document.getElementById('cpu-usage').textContent = `${metrics.cpu_percent.toFixed(1)}%`;
                document.getElementById('memory-usage').textContent = `${metrics.memory_percent.toFixed(1)}%`;
                document.getElementById('temperature').textContent = 
                    metrics.temperature ? `${metrics.temperature.toFixed(1)}°C` : 'N/A';
            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }, 2000);
    </script>
</body>
</html>
    """
    
    with open("templates/dashboard.html", "w") as f:
        f.write(dashboard_html)
    
    print("🚀 Starting CPU Stress Testing Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔧 API documentation at: http://localhost:8000/docs")
    print(f"💻 Detected {stress_tester.cpu_count} CPU cores")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")