print("=== TAKEOFF & LAND ===")
local result, err = ara:takeoff(1.5)
if err then
    print("Takeoff error: " .. err)
else
    print("Takeoff status: " .. result.status)
end
sleep(5)
local result, err = ara:land()
if err then
    print("Land error: " .. err)
else
    print("Land status: " .. result.status)
end
print("Test completed")
