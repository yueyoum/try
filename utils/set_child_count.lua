local pKey = KEYS[1]
local cKey = KEYS[2]
local pid = ARGV[1]
local ppid = nil

local x = redis.call('hexists', cKey, pid)

if x == 0 then
    redis.call('hset', cKey, pid, 0)
end

while true do
    ppid = redis.call('hget', pKey, pid)
    if not ppid or ppid == '0' then
        break
    end
    redis.call('hincrby', cKey, ppid, 1)
    pid = ppid
end
return 'ok'

