// minimal api wrapper
export async function getDevices(){
  const res = await fetch('/api/devices')
  return res.json()
}

export async function controlDevice(device_id, device_type, action, params){
  const res = await fetch('/api/device/control',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({device_id, device_type, action, params})
  })
  return res.json()
}
