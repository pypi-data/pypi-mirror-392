-- examples/aruco_flight.lua
print("=== ARUCO FLIGHT ===")
local result, err = ara:takeoff(1.5)
if err then print("Takeoff error: " .. err) end
sleep(5)

local result, err = ara:set_velocity(1.5, 0)  -- вперед
if err then print("Velocity error: " .. err) end
sleep(2)
local result, err = ara:set_velocity(-0.5, 0)  -- замедление
if err then print("Velocity error: " .. err) end
sleep(2)
local result, err = ara:set_velocity(0, -1.5)  -- влево
if err then print("Velocity error: " .. err) end
sleep(4)
local result, err = ara:set_velocity(0, 0.5)  -- замедление
if err then print("Velocity error: " .. err) end
sleep(2)

for i = 1, 5 do
    local markers, err = ara:get_aruco_markers()
    if err then
        print("Aruco error: " .. err)
    elseif #markers > 0 then
        print("Found " .. #markers .. " markers")
        for _, m in ipairs(markers) do
            print(string.format("  ID: %d at (%.2f, %.2f, %.2f)",
                m.id, m.position.x, m.position.y, m.position.z))
        end
    else
        print("No markers")
    end
    sleep(0.5)
end

local result, err = ara:land()
if err then print("Land error: " .. err) end
