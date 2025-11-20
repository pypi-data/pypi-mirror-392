-- Скрипт для тестирования всех MSP методов
print("==========================================================")
print("           ARA API - MSP Telemetry Test")
print("==========================================================")
print()

-- Функция для красивого вывода таблиц
local function print_table(t, indent)
    indent = indent or 0
    local prefix = string.rep("  ", indent)

    if type(t) ~= "table" then
        print(prefix .. tostring(t))
        return
    end

    for k, v in pairs(t) do
        if type(v) == "table" then
            print(prefix .. tostring(k) .. ":")
            print_table(v, indent + 1)
        else
            print(prefix .. tostring(k) .. ": " .. tostring(v))
        end
    end
end

-- Функция для вызова метода и красивого вывода
local function test_method(name, method_func)
    print("----------------------------------------------------------")
    print("[*] " .. name)
    print("----------------------------------------------------------")

    local result, err = method_func()

    if err then
        print("[ERROR] " .. err)
    else
        print("[OK] Success:")
        print_table(result, 1)
    end
    print()
end

-- Тестируем все MSP методы
print("Starting MSP telemetry tests...")
print()

-- 1. IMU Data (Gyro, Accelerometer, Magnetometer)
test_method("IMU Data", function()
    return ara:get_imu_data()
end)

-- 2. Attitude (Roll, Pitch, Yaw)
test_method("Attitude", function()
    return ara:get_attitude()
end)

-- 3. Altitude
test_method("Altitude", function()
    return ara:get_altitude()
end)

-- 4. Position
test_method("Position", function()
    return ara:get_position()
end)

-- 5. Optical Flow
test_method("Optical Flow", function()
    return ara:get_optical_flow()
end)

-- 6. Motor Status
test_method("Motor Status", function()
    return ara:get_motor()
end)

-- 7. Analog Data (Voltage, Current, RSSI)
test_method("Analog Data", function()
    return ara:get_analog()
end)

print("==========================================================")
print("           MSP Telemetry Test Complete")
print("==========================================================")
