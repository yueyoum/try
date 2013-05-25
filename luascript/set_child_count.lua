local parentKey = KEYS[1]
local childCountKey = KEYS[2]
local pid = ARGV[1]
local ppid = nil

local x = redis.call('hexists', childCountKey, pid)

if x == 0 then
    redis.call('hset', childCountKey, pid, 0)
end

while true do
    ppid = redis.call('hget', parentKey, pid)
    if ppid == false or ppid == '0' then
        break
    end
    redis.call('hincrby', childCountKey, ppid, 1)
    pid = ppid
end
return 'ok'

