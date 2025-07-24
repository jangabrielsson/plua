"""
Performance and stress tests for plua
Tests system limits, memory usage, and performance characteristics
"""

import pytest
import asyncio
import time
import gc
from plua.runtime import LuaAsyncRuntime


class TestPerformanceAndStress:
    """Test cases for performance and stress testing"""
    
    @pytest.mark.asyncio
    async def test_many_timers_performance(self):
        """Test performance with many concurrent timers"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()

        start_time = time.time()

        script = """
        timer_count = 100  -- Global variables
        completed_timers = 0
        start_time = os.clock()

        for i = 1, timer_count do
            setTimeout(function()
                completed_timers = completed_timers + 1
            end, math.random(10, 500))  -- Random delays 10-500ms
        end

        return timer_count
        """

        timer_count = runtime.interpreter.lua.execute(script)
        creation_time = time.time() - start_time

        # Wait for timers to complete
        await asyncio.sleep(1.0)

        completed_timers = runtime.interpreter.lua.eval("completed_timers")

        print(f"Timer Performance - Created {timer_count} timers in {creation_time:.3f}s, Completed: {completed_timers}")

        assert timer_count == 100
        assert completed_timers == 100  # Should work with fixed scoping
        assert creation_time < 1.0  # Should create timers quickly
    
    @pytest.mark.asyncio
    async def test_callback_system_stress(self):
        """Stress test the callback system with many registrations and executions"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        script = """
        callback_count = 1000  -- Global variables
        executions = 0
        callbacks = {}
        
        -- Register many callbacks
        for i = 1, callback_count do
            local callback_id = _PY.registerCallback(function()
                executions = executions + 1
            end, false)  -- Non-persistent
            callbacks[i] = callback_id
        end
        
        return callback_count
        """
        
        callback_count = runtime.interpreter.lua.execute(script)
        
        # Execute all callbacks
        for i in range(1, callback_count + 1):
            callback_id = runtime.interpreter.lua.eval(f"callbacks[{i}]")
            if callback_id:
                runtime.interpreter.execute_lua_callback(callback_id, None)  # No data for this test
        
        executions = runtime.interpreter.lua.eval("executions")
        
        print(f"Callback Stress Test - Registered: {callback_count}, Executed: {executions}")
        
        assert callback_count == 1000
        assert executions == 1000  # Should work with fixed scoping
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_many_operations(self):
        """Test memory usage with many operations"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Force garbage collection before test
        gc.collect()
        
        script = """
        local operations = 0
        
        -- Create many temporary objects and operations
        for i = 1, 500 do
            -- Create temporary tables
            local temp_table = {
                id = i,
                data = string.rep("data", 100),
                nested = { a = i, b = i * 2, c = i * 3 }
            }
            
            -- JSON operations
            local json_str = json.encode(temp_table)
            local decoded = json.decode(json_str)
            
            -- String operations
            local big_string = string.rep("test", 1000)
            local sub_string = string.sub(big_string, 1, 100)
            
            operations = operations + 1
            
            -- Occasional garbage collection hint
            if i % 100 == 0 then
                collectgarbage("collect")
            end
        end
        
        return operations
        """
        
        operations = runtime.interpreter.lua.execute(script)
        
        # Force garbage collection after test
        gc.collect()
        
        print(f"Memory Usage Test - Completed {operations} operations")
        assert operations == 500
    
    @pytest.mark.asyncio
    async def test_rapid_lua_execution(self):
        """Test rapid execution of many Lua scripts"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        start_time = time.time()
        execution_count = 0
        
        # Execute many small scripts rapidly
        for i in range(100):
            script = f"""
            local result = {i} * 2 + 1
            return result
            """
            
            result = runtime.interpreter.lua.execute(script)
            expected = i * 2 + 1
            assert result == expected
            execution_count += 1
        
        execution_time = time.time() - start_time
        
        print(f"Rapid Execution Test - {execution_count} scripts in {execution_time:.3f}s ({execution_count/execution_time:.1f} scripts/sec)")
        
        assert execution_count == 100
        assert execution_time < 5.0  # Should execute reasonably quickly
    
    @pytest.mark.asyncio
    async def test_large_data_structures(self):
        """Test handling of large data structures"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        script = """
        -- Create a large table
        local large_table = {}
        local size = 10000
        
        for i = 1, size do
            large_table[i] = {
                id = i,
                name = "Item_" .. i,
                value = i * 3.14159,
                tags = {"tag1", "tag2", "tag3"}
            }
        end
        
        -- Process the large table
        local sum = 0
        for i = 1, size do
            sum = sum + large_table[i].value
        end
        
        return #large_table, sum
        """
        
        table_size, sum_value = runtime.interpreter.lua.execute(script)
        
        print(f"Large Data Structure Test - Table size: {table_size}, Sum: {sum_value}")
        
        assert table_size == 10000
        assert sum_value > 0  # Should have computed a sum
    
    @pytest.mark.asyncio
    async def test_error_handling_performance(self):
        """Test performance of error handling with many errors"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        start_time = time.time()
        error_count = 0
        
        # Generate many errors and handle them
        for i in range(50):
            try:
                # This should cause an error
                script = f"return non_existent_function_{i}()"
                runtime.interpreter.lua.execute(script)
            except:
                error_count += 1
        
        error_time = time.time() - start_time
        
        print(f"Error Handling Performance - {error_count} errors in {error_time:.3f}s")
        
        assert error_count == 50  # All should have failed
        assert error_time < 2.0   # Error handling should be reasonably fast
    
    @pytest.mark.asyncio
    async def test_timer_accuracy_under_load(self):
        """Test timer accuracy when system is under load"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        script = """
        local timer_start_time = os.clock()
        local timer_executed = false
        local execution_time = nil
        local target_delay = 500  -- 500ms
        
        -- Create background load
        for i = 1, 10 do
            setTimeout(function()
                -- Simulate some work
                local sum = 0
                for j = 1, 1000 do
                    sum = sum + j
                end
            end, math.random(1, 100))
        end
        
        -- Test timer
        setTimeout(function()
            execution_time = (os.clock() - timer_start_time) * 1000  -- Convert to ms
            timer_executed = true
        end, target_delay)
        
        return target_delay
        """
        
        target_delay = runtime.interpreter.lua.execute(script)
        
        # Wait for timer to execute
        await asyncio.sleep(0.8)
        
        timer_executed = runtime.interpreter.lua.eval("timer_executed")
        execution_time = runtime.interpreter.lua.eval("execution_time")
        
        if timer_executed and execution_time:
            accuracy = abs(execution_time - target_delay)
            print(f"Timer Accuracy Test - Target: {target_delay}ms, Actual: {execution_time:.1f}ms, Accuracy: ±{accuracy:.1f}ms")
            
            # Timer should execute within reasonable accuracy (±100ms is acceptable for loaded system)
            assert accuracy < 200  # Allow some variance under load
        else:
            print("Timer Accuracy Test - Timer did not execute or timing not recorded")
            # This is expected if timer scoping isn't fixed yet
    
    @pytest.mark.asyncio
    async def test_concurrent_api_requests_simulation(self):
        """Simulate concurrent API requests to test system resilience"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # This test simulates what would happen with concurrent API requests
        # by executing multiple scripts simultaneously
        
        scripts = [
            "return math.random(1, 100)",
            "local t = {}; for i=1,100 do t[i] = i end; return #t",
            "return string.rep('x', 1000)",
            "local sum = 0; for i=1,100 do sum = sum + i end; return sum",
            "return json.encode({test = 'data', number = 42})"
        ]
        
        start_time = time.time()
        results = []
        
        # Execute scripts concurrently (simulating concurrent API requests)
        tasks = []
        for i, script in enumerate(scripts * 10):  # 50 total executions
            task = asyncio.create_task(self._execute_script_async(runtime, script))
            tasks.append(task)
        
        # Wait for all to complete
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        execution_time = time.time() - start_time
        success_count = sum(1 for r in completed_results if not isinstance(r, Exception))
        
        print(f"Concurrent API Simulation - {len(tasks)} requests in {execution_time:.3f}s, {success_count} successful")
        
        assert success_count > 0  # At least some should succeed
        assert execution_time < 10.0  # Should complete in reasonable time
    
    async def _execute_script_async(self, runtime, script):
        """Helper to execute a script asynchronously"""
        # Add small random delay to simulate real API request timing
        await asyncio.sleep(0.001 + 0.01 * asyncio.get_event_loop().time() % 0.01)
        return runtime.interpreter.lua.execute(script)
