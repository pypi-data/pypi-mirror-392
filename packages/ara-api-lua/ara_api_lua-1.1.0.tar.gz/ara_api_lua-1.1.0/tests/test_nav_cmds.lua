print("=== TAKEOFF ===")
local result, err = ara:takeoff(1.5)
if err then
    print("Takeoff error: " .. err)
else
    print("Takeoff status: " .. result.status)
end

print("=== SPEED ===")
local result, err = ara:set_velocity(1, 1)
if err then
    print("Speed error: " .. err)
else
    print("Speed status: " .. result.status)
end
sleep(2)

print("=== MOVE ===")
local result, err = ara:move_to(1, 1, 1)
if err then
    print("Move error: " .. err)
else
    print("Move status: " .. result.status)
end

print("=== LAND ===")
local result, err = ara:land()
if err then
    print("Land error: " .. err)
else
    print("Land status: " .. result.status)
end
