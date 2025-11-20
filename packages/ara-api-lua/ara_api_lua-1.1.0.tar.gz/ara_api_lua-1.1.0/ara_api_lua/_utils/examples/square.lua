print("=== SQUARE FLIGHT ===")
local result, err = ara:takeoff(1.5)
if err then print("Takeoff error: " .. err) end
sleep(5)

local path = {{1,0,1.5}, {1,1,1.5}, {0,1,1.5}, {0,0,1.5}}
for _, p in ipairs(path) do
    print(string.format("Move to: %.1f, %.1f, %.1f", p[1], p[2], p[3]))
    local result, err = ara:move_to(p[1], p[2], p[3])
    if err then print("Move error: " .. err) end
    sleep(2)
end

local result, err = ara:land()
if err then print("Land error: " .. err) end
print("Path completed")
